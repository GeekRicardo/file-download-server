from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse
from pathlib import Path
import shutil

from .logger import logger

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
async def read_root():
    return templates.TemplateResponse("index.html", {"request": {}})

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        file_location = f"{file.filename}"
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(file.file, file_object)
    except Exception as e:
        logger.exception("upload %s failed, exception: %s", file.filename, e)
    return {"info": f"file '{file.filename}' uploaded on server"}
