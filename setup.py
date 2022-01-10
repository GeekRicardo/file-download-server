from setuptools import setup

setup(
    name="file_download_server",
    version="1.0.4",
    packages=["."],
    author="Ricardo",
    author_email="GeekRicardozzZ@gmail.com",
    url="https://github.com/GeekRicardo/file-download-server",
    install_requires=["fastapi", "uvicorn"],
    description="A simple file server",
)
