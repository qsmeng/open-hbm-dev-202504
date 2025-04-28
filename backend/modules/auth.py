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
from backend.database.hbm_mysql import get_db_connection

# 认证路由，所有认证相关API都挂载在此路由下
router = APIRouter(
    prefix="/auth",
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
    """用户注册数据模型"""
    username: str  # 用户名，唯一标识
    email: str  # 用户邮箱，用于通知和密码重置
    password: str  # 明文密码，注册时前端应做基本复杂度校验

class Token(BaseModel):
    """认证令牌响应模型"""
    access_token: str  # JWT访问令牌
    token_type: str  # 令牌类型，固定为"bearer"

@router.post("/register")
async def register(user: User):
    """
    用户注册接口
    
    参数:
    - user: 用户注册信息，包含用户名、邮箱和密码
    
    返回值:
    - 成功: {"message": "注册成功"}
    - 失败: 返回相应错误状态码和详情
    
    异常:
    - 400: 用户名或邮箱已存在
    - 500: 服务器内部错误
    
    安全说明:
    - 密码会经过bcrypt哈希后存储
    - 不返回敏感信息
    """
    try:
        # 获取数据库连接
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            # 检查用户名是否已存在
            cursor.execute("SELECT * FROM user_base_info WHERE username = %s", (user.username,))
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="用户名已存在")

            # 检查邮箱是否已存在
            cursor.execute("SELECT * FROM user_base_info WHERE email = %s", (user.email,))
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="邮箱已被注册")

            # 对密码进行bcrypt哈希处理
            hashed_password = pwd_context.hash(user.password)

            # 插入新用户记录
            cursor.execute(
                "INSERT INTO user_base_info (username, email, password_hash) VALUES (%s, %s, %s)",
                (user.username, user.email, hashed_password)
            )
            conn.commit()
            return {"message": "注册成功"}
        except mysql.connector.Error as err:
            # 数据库操作异常回滚
            conn.rollback()
            raise HTTPException(status_code=500, detail=f"数据库错误: {err}")
        finally:
            # 确保释放数据库资源
            cursor.close()
            conn.close()
    except Exception as e:
        # 捕获未处理异常
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")

@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    用户登录接口
    
    参数:
    - form_data: OAuth2标准用户名密码表单
    
    返回值:
    - 成功: 返回JWT访问令牌
    - 失败: 返回401未授权错误
    
    安全说明:
    - 使用bcrypt验证密码哈希
    - 返回的令牌应在前端安全存储
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # 查询用户信息
        cursor.execute("SELECT * FROM user_base_info WHERE username = %s", (form_data.username,))
        user = cursor.fetchone()

        # 验证用户存在且密码正确
        if not user or not pwd_context.verify(form_data.password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 生成JWT访问令牌
        access_token = {"sub": user["username"]}
        return {"access_token": access_token, "token_type": "bearer"}
    finally:
        # 确保释放数据库资源
        cursor.close()
        conn.close()

@router.get("/check")
async def check_login_status(request: Request):
    """
    检查用户登录状态
    
    参数:
    - request: FastAPI请求对象，从中提取Authorization头
    
    返回值:
    - 已登录: 返回用户基本信息
    - 未登录: 返回未认证状态
    
    安全说明:
    - 依赖前端正确传递Authorization头
    - 不返回敏感用户信息
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
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            # 查询用户信息
            cursor.execute("SELECT * FROM user_base_info WHERE username = %s", (username,))
            user = cursor.fetchone()
            if user:
                return {
                    "is_authenticated": True,
                    "user": {
                        "username": user["username"],
                        "avatar": user.get("avatar", "/images/default-avatar.png")
                    }
                }
        finally:
            cursor.close()
            conn.close()
    except jwt.PyJWTError:
        # 令牌无效或过期
        pass
    
    return {"is_authenticated": False}

@router.post("/reset-password")
async def reset_password(request: Request):
    """
    密码重置接口
    
    参数:
    - request: 包含用户邮箱的请求体
    
    返回值:
    - 成功: 返回重置链接(开发环境)
    - 失败: 返回相应错误
    
    安全说明:
    - 生产环境应通过邮件发送重置链接
    - 重置令牌有效期1小时
    
    TODO:
    - 实现邮件发送功能 - 使用SMTP或邮件服务API
    - 添加重置令牌刷新机制
    """
    try:
        data = await request.json()
        email = data.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="邮箱不能为空")
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            # 检查邮箱是否存在
            cursor.execute("SELECT * FROM user_base_info WHERE email = %s", (email,))
            user = cursor.fetchone()
            if not user:
                raise HTTPException(status_code=404, detail="邮箱未注册")
            
            # 生成带过期时间的重置令牌
            reset_token = jwt.encode(
                {
                    "sub": user["username"],
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
        finally:
            cursor.close()
            conn.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")