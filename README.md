# Simple file server

## Usage

1. install requirements

`pip install fastapi uvicorn`

2. create server

```python file_server.py --static_path {path} --port {port} --prefix {url_prefix}```

**required**: `--static_path`
**deault**: 
  - `--port`  `8000`
  - `--prefix` `/`

also you can run as python module:

```bash
$ mv file_server.py  path_to_your_python_lib_path/site-packages/
$ python -m file_server --static_path {path}

```

## 为什么要写这个脚本
为什么不直接`python -m http.server`,很简单，
1. http.server 只能单线程下载，有人在下别人就下不了;而且速度不知道为啥慢的不行
2. http.server 不支持url二级路径, 当我用nginx反向代理时就用不了了
3. 拿fastapi练练手
