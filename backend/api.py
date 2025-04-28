"""
API路由主入口模块
=================

集中管理所有API路由的注册和配置。

当前功能:
- 注册认证相关路由到/api/auth路径

未来扩展:
- 可在此添加其他模块的路由注册
- 可配置全局中间件
- 可添加全局异常处理

安全注意事项:
1. 所有路由需通过认证中间件
2. 生产环境应启用HTTPS
"""

from fastapi import APIRouter
from .modules.auth import router as auth_router

# 主路由实例，所有API路由都将挂载在此路由下
router = APIRouter()

# 注册认证路由到/api/auth路径
# 所有/auth开头的请求将由auth_router处理
router.include_router(
    auth_router,
    prefix="/auth",  # 路由前缀
    tags=["auth"]    # OpenAPI分组标签
)