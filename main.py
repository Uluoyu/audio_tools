import os
import sys
import time
from typing import Awaitable, Callable

import uvicorn
from api.audio_api import audio_router
from config.log_config import logger
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
app.include_router(audio_router)


# 配置静态文件目录
def get_resource_path(relative_path: str) -> str:
    """在开发环境或打包环境下，正确获取资源文件的路径"""
    base_path = getattr(sys, '_MEIPASS', os.path.abspath('.'))
    return os.path.join(base_path, relative_path)


# 使用 get_resource_path 获取静态文件的路径
static_dir = get_resource_path('static')

# 确保 static_dir 是一个字符串
static_dir = str(static_dir)
logger.info(f'静态文件路径: {static_dir}')

# 配置静态文件目录
app.mount('/static', StaticFiles(directory=static_dir), name='static')

# 初始化模板引擎
templates = Jinja2Templates(directory='templates')


@app.get('/audio', response_class=HTMLResponse)
async def audio(request: Request) -> HTMLResponse:
    return templates.TemplateResponse('audio.html', {'request': request})


@app.middleware('http')
async def log_requests(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    # 记录请求地址
    logger.info(f'Request URL: {request.url}')

    # 记录请求开始时间
    start_time = time.time()

    # 处理请求
    response = await call_next(request)

    # 计算处理请求所花费的时间
    process_time = time.time() - start_time

    # 记录响应状态码
    logger.info(f'Response status: {response.status_code}, Processing time: {process_time:.2f}s')

    return response


# 启动 FastAPI 应用
if __name__ == '__main__':
    logger.info('FastAPI application is starting')  # 启动时记录日志
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=False, log_config=None)
