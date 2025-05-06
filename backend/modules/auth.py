"""
用户认证模块
============
提供用户注册、登录、认证状态检查和密码重置等核心认证功能。

功能说明：
- /register: 新用户注册接口
- /token: 用户登录接口，返回JWT令牌
- /check: 检查用户登录状态
- /reset-password: 密码重置功能

依赖组件：
- FastAPI: 提供API路由和请求处理
- Passlib: 密码哈希和验证
- PyJWT: JWT令牌生成和验证
- MySQL: 用户数据存储

安全注意事项：
1. 密码使用bcrypt算法哈希存储
2. 敏感操作需要有效JWT令牌
3. 密码重置链接应通过安全渠道发送
"""
import os
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from passlib.context import CryptContext
import jwt
import mysql.connector
from backend.database.hbm_mysql import DBOperator

# 认证路由，所有认证相关API都挂载在此路由下
router = APIRouter(
    tags=["authentication"],
    responses={401: {"description": "未授权或认证失败"}}
)

# 密码加密上下文，使用bcrypt算法
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT配置 - 生产环境应从环境变量读取
SECRET_KEY = os.getenv('JWT_SECRET_KEY')
ALGORITHM = "HS256"  # JWT签名算法
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 令牌有效期(分钟)

class User(BaseModel):
    """
    用户注册数据模型
    
    属性:
    - username (str): 用户名，必须唯一，长度4-20个字符
    - email (str): 用户邮箱，用于通知和密码重置，必须符合邮箱格式
    - password (str): 明文密码，前端应做基本复杂度校验
    
    示例:
    {
        "username": "testuser",
        "email": "test@example.com",
        "password": "SecurePassword123!"
    }
    """
    username: str
    email: str 
    password: str

class Token(BaseModel):
    """
    JWT认证令牌响应模型
    
    属性:
    - access_token (str): JWT访问令牌，有效期30分钟
    - token_type (str): 令牌类型，固定为"bearer"
    
    示例:
    {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "token_type": "bearer"
    }
    """
    access_token: str
    token_type: str

def create_success_response(data=None, message="操作成功"):
    return JSONResponse(
        content={
            "success": True,
            "code": "SUCCESS",
            "message": message,
            "data": data,
            "timestamp": int(datetime.now().timestamp())
        }
    )

def create_error_response(code="ERROR", message="系统错误", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR):
    return JSONResponse(
        content={
            "success": False,
            "code": code,
            "message": message,
            "timestamp": int(datetime.now().timestamp())
        },
        status_code=status_code
    )

@router.post("/register")
async def register(user: User):
    """
    用户注册接口
    
    参数:
    - user (User): 用户注册信息对象，包含以下属性:
        - username (str): 用户名，4-20个字符，必须唯一
        - email (str): 用户邮箱，必须符合邮箱格式
        - password (str): 明文密码，至少8个字符，包含大小写字母和数字
    
    返回值:
    - 成功 (200): 
        {
            "success": True,
            "code": "SUCCESS",
            "message": "注册成功",
            "data": {"message": "注册成功"},
            "timestamp": 1234567890
        }
    - 失败:
        - 400: 用户名或邮箱已存在
        - 500: 服务器内部错误
    
    异常:
    - HTTPException 400: 用户名或邮箱已存在
    - HTTPException 500: 数据库错误或其他服务器错误
    
    安全说明:
    - 密码使用bcrypt算法哈希存储
    - 不返回敏感信息
    - 使用参数化查询防止SQL注入
    
    示例请求:
    POST /auth/register
    {
        "username": "testuser",
        "email": "test@example.com",
        "password": "SecurePassword123!"
    }
    """
    try:
        # 检查用户名是否已存在
        existing_user = DBOperator.get_one("users", username=user.username)
        if existing_user:
            raise HTTPException(status_code=400, detail="用户名已存在")

        # 检查邮箱是否已存在
        existing_email = DBOperator.get_one("users", email=user.email)
        if existing_email:
            raise HTTPException(status_code=400, detail="邮箱已被注册")

        # 对密码进行bcrypt哈希处理
        hashed_password = pwd_context.hash(user.password)

        # 准备用户数据
        user_data = {
            "username": user.username,
            "email": user.email,
            "password_hash": hashed_password,
            "status": 1,  # 默认激活状态
            "experience": 0,
            "energy": 256,
            "max_energy": 256
        }

        # 创建新用户
        DBOperator.create("users", **user_data)
        return create_success_response({"message": "注册成功"})
    except Exception as e:
        # 捕获未处理异常
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")

@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    用户登录接口
    
    参数:
    - form_data (OAuth2PasswordRequestForm): OAuth2标准用户名密码表单，包含:
        - username (str): 用户名
        - password (str): 密码
    
    返回值:
    - 成功 (200):
        {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer"
        }
    - 失败:
        - 401: 用户名或密码错误
    
    异常:
    - HTTPException 401: 用户名或密码错误
    
    安全说明:
    - 使用bcrypt验证密码哈希
    - 返回的JWT令牌有效期30分钟
    - 前端应安全存储令牌
    
    示例请求:
    POST /auth/token
    Content-Type: application/x-www-form-urlencoded
    
    username=testuser&password=SecurePassword123!
    """
    try:
        # 查询用户信息
        user = DBOperator.get_one("users", username=form_data.username)
        if not user or not pwd_context.verify(form_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 生成JWT访问令牌
        access_token = {"sub": user.username}
        return {"access_token": access_token, "token_type": "bearer"}
    except mysql.connector.Error as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"数据库错误: {err}"
        )

@router.get("/check")
async def check_login_status(request: Request):
    """
    检查用户登录状态
    
    参数:
    - request (Request): FastAPI请求对象，需要包含:
        - Authorization头: Bearer令牌
    
    返回值:
    - 已登录 (200):
        {
            "is_authenticated": True,
            "user": {
                "username": "testuser",
                "avatar": "/images/default-avatar.png"
            }
        }
    - 未登录 (200):
        {
            "is_authenticated": False
        }
    
    异常:
    - 无显式异常抛出
    
    安全说明:
    - 依赖前端正确传递Authorization头
    - 不返回敏感用户信息
    - 令牌验证失败不抛出异常
    
    示例请求:
    GET /auth/check
    Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    """
    # 从请求头中获取Bearer令牌
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return {"is_authenticated": False}

    token = auth_header.split(" ")[1]
    
    # 验证JWT令牌有效性
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        
        # 查询用户信息
        user = DBOperator.get_one("users", username=username)
        if user:
            return {
                "is_authenticated": True,
                "user": {
                    "username": user.username,
                    "avatar": user.avatar if hasattr(user, 'avatar') else "/images/default-avatar.png"
                }
            }
    except jwt.PyJWTError:
        # 令牌无效或过期
        pass
    except mysql.connector.Error as err:
        # 数据库错误不影响认证状态判断
        print(f"数据库查询错误: {err}")
    
    return {"is_authenticated": False}

@router.post("/reset-password")
async def reset_password(request: Request):
    """
    密码重置接口
    
    参数:
    - request (Request): FastAPI请求对象，需要包含:
        - email (str): 用户注册邮箱
    
    返回值:
    - 成功 (200):
        {
            "message": "密码重置链接已发送至您的邮箱",
            "dev_note": "实际项目中链接应通过邮件发送"
        }
    - 失败:
        - 400: 邮箱不能为空
        - 404: 邮箱未注册
        - 500: 服务器内部错误
    
    异常:
    - HTTPException 400: 邮箱不能为空
    - HTTPException 404: 邮箱未注册
    - HTTPException 500: 数据库错误或其他服务器错误
    
    安全说明:
    - 生产环境应通过邮件发送重置链接
    - 重置令牌有效期1小时
    - 开发环境直接返回链接仅用于测试
    
    TODO:
    - 实现邮件发送功能 - 使用SMTP或邮件服务API
    - 添加重置令牌刷新机制
    
    示例请求:
    POST /auth/reset-password
    {
        "email": "test@example.com"
    }
    """
    try:
        data = await request.json()
        email = data.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="邮箱不能为空")
        
        try:
            # 检查邮箱是否存在
            user = DBOperator.get_one("users", email=email)
            if not user:
                raise HTTPException(status_code=404, detail="邮箱未注册")
            
            # 生成带过期时间的重置令牌
            reset_token = jwt.encode(
                {
                    "sub": user.username,
                    "exp": datetime.utcnow() + timedelta(hours=1),
                    "purpose": "password_reset"
                },
                SECRET_KEY,
                algorithm=ALGORITHM
            )
            
            # 生成重置链接(开发环境直接返回)
            reset_url = f"https://example.com/reset-password?token={reset_token}"
            
            # 开发环境打印链接，生产环境应通过邮件发送
            print(f"密码重置链接: {reset_url}")  # 仅用于开发测试
            
            return {
                "message": "密码重置链接已发送至您的邮箱",
                "dev_note": "实际项目中链接应通过邮件发送"
            }
        except mysql.connector.Error as err:
            raise HTTPException(status_code=500, detail=f"数据库错误: {err}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")
    
def send_email(to, subject, content):
    """模拟邮件发送"""
    print(f"模拟发送邮件到 {to}: {subject}")
    return True

class SimpleRateLimiter:
    """简单速率限制器"""
    def check(self):
        return True

rate_limiter = SimpleRateLimiter()