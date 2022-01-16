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
import uvicorn
import os
import time
import sys
import argparse
import hashlib
from glob import glob
from fastapi import FastAPI, UploadFile, File
from starlette.responses import FileResponse, HTMLResponse, Response


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
    def index(t: int = 0):
        html = get_file_list(static_path, t)
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
    async def get_file(filename: str):
        path = os.path.join(static_path, filename)
        if not os.path.exists(path):
            return Response(
                content="file not exists!",
                status_code=404,
            )
        elif os.path.isdir(path):
            return HTMLResponse(get_file_list(path))
        response = FileResponse(path)
        return response

    def get_file_list(path, show_time=0):
        sub_path = [it for it in path.replace(static_path, "").rsplit("/") if it]
        return """<html><head><style>span:hover{{background-color:#f2f2f2}}li{{weight:70%;}}</style></head><body><h2>{0}</h2><ul>{1}</ul></body></html>""".format(
            "→".join(
                [f'<a href="{prefix}"><span> / </span></a>']
                + [
                    f'<a href="{prefix}{"/".join([_ for _ in sub_path[:sub_path.index(it) + 1]])}"><span>{it}</span></a>'
                    for it in sub_path
                ]
            ),
            "\n".join(
                [
                    "<li><a href='{0}{1}'>{0}{1}</a>{2}</li>".format(
                        os.path.basename(it),
                        "/" if os.path.isdir(it) else "",
                        TimeStampToTime(os.path.getmtime(it)) if show_time != 0 else "",
                    )
                    for it in glob(path + "/*")
                ],
            ),
        )

    uvicorn.run(app, debug=True, host="0.0.0.0", port=port)


if __name__ == "__main__":
    static_path, prefix, port = parse_args()
    server(static_path, prefix, port)
