#!/usr/bin python
# -*- encoding: utf-8 -*-
"""
@File    :   file_server.py
@Time    :   2021/12/27 19:56:49
@Author  :   Ricardo
@Version :   1.0
@Contact :   bj.zhang@tianrang-inc.com
@Desc    :   文件下载服务器
"""

# here put the import lib
import uvicorn
import os
import sys
import argparse
from glob import glob
from fastapi import FastAPI
from starlette.responses import FileResponse, HTMLResponse, Response

parser = argparse.ArgumentParser()
parser.add_argument(
    "--static_path", type=str, required=True, help="path to static files."
)
parser.add_argument(
    "--prefix",
    type=str,
    default="/",
    help="url prefix eg:\033[31m/\033[0mstatic\033[31m/\033[0m [\033[31mtwo / !!\033[0m]",
)
parser.add_argument("--port", type=int, default=8080, help="port")
args = parser.parse_args()

if not args.prefix[0] == args.prefix[-1] == "/":
    print(
        "prefix error! must start with \033[31m/\033[0m and end with \033[31m/\033[0m"
    )
    sys.exit(1)

app = FastAPI()
static_path = os.path.abspath(args.static_path)


@app.get("/robots.txt")
def robots_txt():
    return Response("""User-Agent: *
Disallow: /""")

@app.get(args.prefix)
def index():
    html = get_file_list(static_path)
    return HTMLResponse(html)


@app.get(args.prefix + "{filename:path}")
async def get_file(filename: str):
    print(filename)
    path = os.path.join(static_path, filename)
    if not os.path.exists(path):
        return {"success": False, "msg": "文件不存在！"}
    elif os.path.isdir(path):
        return HTMLResponse(get_file_list(path))
    response = FileResponse(path)
    return response

def get_file_list(path):
    sub_path = [it for it in path.replace(static_path, "").rsplit("/") if it]
    return """<html><head><style>span:hover{{background-color:#f2f2f2}}</style></head><body><h2>{0}</h2><ul>{1}</ul></body></html>""".format(
        "→".join(
            ['<a href="/"><span> / </span></a>']
            + [
                f'<a href="{args.prefix}{"/".join([_ for _ in sub_path[:sub_path.index(it) + 1]])}"><span>{it}</span></a>'
                for it in sub_path
            ]
        ),
        "\n".join(
            [
                "<li><a href='{0}{1}'>{0}{1}</a></li>".format(
                    os.path.basename(it), "/" if os.path.isdir(it) else ""
                )
                for it in glob(path + "/*")
            ],
        ),
    )


if __name__ == "__main__":
    uvicorn.run(app, debug=True, host="0.0.0.0", port=args.port)
