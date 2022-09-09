#!/usr/bin python
# -*- encoding: utf-8 -*-
"""
@File    :   file_server.py
@Time    :   2021/12/27 19:56:49
@Author  :   Ricardo
@Version :   1.0.2
@Contact :   bj.zhang@tianrang-inc.com
@Desc    :   文件下载服务器
"""

# here put the import lib
from email.utils import formatdate
import re
import stat
import uvicorn
import os
import time
import sys
import argparse
import hashlib
from glob import glob
from urllib.parse import quote
from mimetypes import guess_type

from fastapi import FastAPI, UploadFile, File, Request
from starlette.responses import FileResponse, HTMLResponse, Response, StreamingResponse


def parse_args():
    print(__name__)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d", "--static_path", type=str, required=True, help="path to static files."
    )
    parser.add_argument(
        "--prefix",
        type=str,
        default="/",
        help="url prefix eg:\033[31m/\033[0mstatic\033[31m/\033[0m [\033[31mtwo / !!\033[0m]",
    )
    parser.add_argument("--port", type=int, default=8000, help="port")
    args = parser.parse_args()
    return args.static_path, args.prefix, args.port


def TimeStampToTime(timestamp):
    timeStruct = time.localtime(timestamp)
    return time.strftime("%Y-%m-%d %H:%M:%S", timeStruct)


def file_iterator(file_path, offset, chunk_size):
    """
    文件生成器
    :param file_path: 文件绝对路径
    :param offset: 文件读取的起始位置
    :param chunk_size: 文件读取的块大小
    :return: yield
    """
    with open(file_path, "rb") as f:
        f.seek(offset, os.SEEK_SET)
        while True:
            data = f.read(chunk_size)
            if data:
                yield data
            else:
                break


def server(static_path, prefix="/", port=8000):
    if not prefix[0] == prefix[-1] == "/":
        print(
            "prefix error! must start with \033[31m/\033[0m and end with \033[31m/\033[0m"
        )
        sys.exit(1)

    static_path = os.path.abspath(static_path)

    app = FastAPI()

    @app.get("/robots.txt")
    def robots_txt():
        return Response(
            """User-Agent: *
    Disallow: /"""
        )

    @app.get(prefix)
    def index(show_time: bool = False, dd=""):
        html = get_file_list(static_path, show_time, dd)
        return HTMLResponse(html)

    @app.get(prefix + "upload")
    def upload_page():
        return HTMLResponse(
            """<form action="/upload" method="post" enctype="multipart/form-data">
            <input type="file" name="file" id="file">
            <input type="submit" value="上传">
        </form>"""
        )

    @app.post(prefix + "upload")
    async def uploads(file: UploadFile = File(...)):

        image_bytes = await file.read()
        file_name = file.filename
        save_path = os.path.join(static_path, file_name)
        if not os.path.exists(save_path):
            with open(save_path, "wb") as f:
                f.write(image_bytes)
        return Response(status_code=200, content=file_name)

    @app.get(prefix + "md5/{filename:path}")
    async def md5(filename: str):
        path = os.path.join(static_path, filename)
        if not os.path.exists(path):
            return Response(
                content="file not exists!",
                status_code=404,
            )
        elif os.path.isdir(path):
            return Response(content="is a directory")

        with open(path, "rb") as f:
            data = f.read()
        file_md5 = hashlib.md5(data).hexdigest()
        response = Response(content=file_md5)
        return response

    @app.get(prefix + "{filename:path}")
    async def get_file(request: Request, filename: str, show_time=False, dd=""):
        path = os.path.join(static_path, filename)
        if not os.path.exists(path):
            return Response(
                content="file not exists!",
                status_code=404,
            )
        elif os.path.isdir(path):
            return HTMLResponse(get_file_list(path, show_time, dd))

        # 断点续传
        stat_result = os.stat(path)
        content_type, encoding = guess_type(path)
        content_type = content_type or "application/octet-stream"
        if dd == "1":
            content_type = "application/octet-stream"

        range_str = request.headers.get("range", "")
        range_match = re.search(r"bytes=(\d+)-(\d+)", range_str, re.S) or re.search(
            r"bytes=(\d+)-", range_str, re.S
        )
        if range_match:
            start_bytes = int(range_match.group(1))
            end_bytes = (
                int(range_match.group(2))
                if range_match.lastindex == 2
                else stat_result.st_size - 1
            )
        else:
            start_bytes = 0
            end_bytes = stat_result.st_size - 1
        # 这里 content_length 表示剩余待传输的文件字节长度
        content_length = (
            stat_result.st_size - start_bytes
            if stat.S_ISREG(stat_result.st_mode)
            else stat_result.st_size
        )
        # 构建文件名称
        name, *suffix = filename.rsplit(".", 1)
        suffix = f".{suffix[0]}" if suffix else ""
        filename = quote(f"{name}{suffix}")  # 文件名编码，防止中文名报错
        # 打开文件从起始位置开始分片读取文件
        return StreamingResponse(
            file_iterator(path, start_bytes, 1024 * 1024 * 1),  # 每次读取 1M
            media_type=content_type,
            headers={
                "content-disposition": f'attachment; filename="{filename}"',
                "accept-ranges": "bytes",
                "connection": "keep-alive",
                "content-length": str(content_length),
                "content-range": f"bytes {start_bytes}-{end_bytes}/{stat_result.st_size}",
                "last-modified": formatdate(stat_result.st_mtime, usegmt=True),
            },
            status_code=206 if start_bytes > 0 else 200,
        )

    def get_file_list(path, show_time: bool = False, dd: str = ""):
        sub_path = [it for it in path.replace(static_path, "").rsplit("/") if it]
        return """<html><head><style>span:hover{{background-color:#f2f2f2}}li{{weight:70%;}}</style></head><body><h2>{0}</h2><ul>{1}</ul></body></html>""".format(
            "→".join(
                [f'<a href="{prefix}"><span> / </span></a>']
                + [
                    f'<a href="{prefix}{"/".join([_ for _ in sub_path[:sub_path.index(it) + 1]])}/"><span>{it}</span></a>'
                    for it in sub_path
                ]
            ),
            "\n".join(
                [
                    "<li><a href='{0}{1}{3}'>{0}{1}</a>{2}</li>".format(
                        os.path.basename(it),
                        "/" if os.path.isdir(it) else "",
                        TimeStampToTime(os.path.getmtime(it)) if show_time != 0 else "",
                        "?"
                        + "&".join(["dd=" + dd, "show_time=" + str(show_time).lower()])
                        if dd or show_time
                        else "",
                    )
                    for it in glob(path + "/*")
                ],
            ),
        )

    uvicorn.run(app, debug=True, host="0.0.0.0", port=port)


if __name__ == "__main__":
    static_path, prefix, port = parse_args()
    server(static_path, prefix, port)
