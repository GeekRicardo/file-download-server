from setuptools import setup
import platform

python_version = int("".join(platform.python_version().split(".")[:2]))

setup(
    name="file_download_server",
    version="1.0.8",
    packages=["."],
    author="Ricardo",
    author_email="GeekRicardozzZ@gmail.com",
    url="https://github.com/GeekRicardo/file-download-server",
    install_requires=["fastapi", "python-multipart", "uvicorn~=" + ("0.16.0" if python_version == 36 else "0.17.0")],
    description="A simple file server",
)
