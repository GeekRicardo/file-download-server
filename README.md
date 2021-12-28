# Simple file server

## Usage

1. install requirements

`pip install fastapi uvicorn`

2. create server

```python file_server.py --static_path {path} --port {port} --prefix {url_prefix}```

**required**: `--static_path`

also you run as python module:

```bash
$ mv file_server.py  path_to_your_python_lib_path/site-packages/
$ python -m file_server --static_path {path}

```
