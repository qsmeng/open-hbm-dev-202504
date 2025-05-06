# 认证授权API文档

## 目录
- [用户注册](#用户注册)
- [用户登录](#用户登录)
- [检查登录状态](#检查登录状态)
- [密码重置](#密码重置)
- [错误码](#错误码)

## 基础信息
### 请求头
```
Authorization: Bearer {token}
Content-Type: application/json
```

### 响应格式
```json
{
  "success": true,
  "code": "SUCCESS",
  "message": "操作成功",
  "data": {},
  "timestamp": 1714387200
}
```

## 用户注册
```http
POST /api/auth/register
```
请求体：
```json
{
  "username": "string(4-20位)",
  "email": "string(有效邮箱格式)",
  "password": "string(至少8位，包含大小写字母和数字)"
}
```
响应：
```json
{
  "success": true,
  "code": "SUCCESS",
  "message": "注册成功",
  "data": null,
  "timestamp": 1714387200
}
```

## 用户登录
```http
POST /api/auth/login
```
请求体：
```json
{
  "username": "string",
  "password": "string"
}
```
响应：
```json
{
  "access_token": "string(JWT令牌)",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": "string",
    "username": "string",
    "avatar": "string(头像URL)",
    "experience": 0
  }
}
```

## 检查登录状态
```http
GET /api/auth/check
```
请求头：
```
Authorization: Bearer {token}
```
响应：
```json
{
  "is_authenticated": true,
  "user": {
    "id": "string",
    "username": "string",
    "avatar": "string(头像URL)",
    "experience": 0,
    "energy": 100
  }
}
```

## 密码重置
```http
POST /api/auth/reset-password
```
请求体：
```json
{
  "email": "string(注册邮箱)"
}
```
响应：
```json
{
  "message": "密码重置链接已发送至您的邮箱",
  "dev_note": "实际项目中链接应通过邮件发送"
}
```

## 错误码
| 错误码 | HTTP状态码 | 描述 |
|--------|------------|------|
| USER_EXISTS | 400 | 用户名或邮箱已存在 |
| INVALID_CREDENTIALS | 401 | 用户名或密码错误 |
| EMAIL_NOT_FOUND | 404 | 邮箱未注册 |
| DB_ERROR | 500 | 数据库错误 |
| INVALID_TOKEN | 403 | 无效令牌 |
