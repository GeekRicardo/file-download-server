import os
import argparse

import uvicorn
from fastapi import FastAPI, APIRouter
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from . import image_server, upload #,download

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))

apps = {
    "image_server": [image_server.app, image_server.image_router],
    # "download": download.app,
    "upload": upload.app,
}

templates = Jinja2Templates(directory=os.path.join(_BASE_DIR, "templates"))

parser = argparse.ArgumentParser()
parser.add_argument("app", choices=apps.keys(), help="The FastAPI application to run")
parser.add_argument("--port", "-p", default=3001, type=int, help="The port to run the FastAPI application on")
parser.add_argument("--path", "-d", default=os.getcwd(), type=str, help="path")
parser.add_argument("--prefix", "-a", default='', type=str, help="The prefix to add to all routes")

if __name__ == "__main__":
    args = parser.parse_args()

    app = apps[args.app][0]
    router = apps[args.app][1]

    os.chdir(args.path)

    if args.prefix:
        # router = APIRouter(prefix=args.prefix)
        # router.include_router(router)
        app = FastAPI()
        app.mount(f"{args.prefix}/static", StaticFiles(directory=os.path.join(_BASE_DIR, "static")), name="static")
        app.include_router(router, prefix=args.prefix)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=args.port,
    )
