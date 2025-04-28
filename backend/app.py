"""
FastAPI应用主入口
================

配置和管理FastAPI应用的核心设置和中间件。

主要功能:
- 配置CORS跨域设置
- 挂载所有API路由
- 请求日志记录
- 开发服务器启动

环境要求:
- Python 3.7+
- FastAPI
- Uvicorn

安全注意事项:
1. 生产环境应限制CORS允许的源
2. 应配置HTTPS
3. 敏感路由需要认证
"""

import os
import sys
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

# 将项目根目录添加到Python路径，确保模块导入正常
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.api import router as api_router

# 创建FastAPI应用实例
app = FastAPI(
    title="HBM API服务",
    description="提供游戏后端API服务",
    version="0.1.0"
)

# 配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境允许所有源，生产环境应限制
    allow_credentials=True,  # 允许携带凭据
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有请求头
)

# 挂载API路由到/api路径下
app.include_router(
    api_router,
    prefix="/api",  # 路由前缀
)

@app.middleware("http")
async def log_request_url(request: Request, call_next):
    """
    请求日志中间件
    
    功能:
    - 记录所有进入的请求URL
    - 开发调试使用
    
    参数:
    - request: 请求对象
    - call_next: 下一个中间件或路由处理函数
    
    返回值:
    - 响应对象
    """
    print(f"Request URL: {request.url}")  # 开发环境日志
    response = await call_next(request)
    return response

if __name__ == "__main__":
    """开发服务器启动入口"""
    import uvicorn
    # 启动Uvicorn服务器
    uvicorn.run(
        app,
        host="0.0.0.0",  # 监听所有网络接口
        port=8000,  # 服务端口
        reload=True  # 开发模式自动重载
    )