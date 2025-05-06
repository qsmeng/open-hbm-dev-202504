import os
import sys
import unittest
import requests
from fastapi.testclient import TestClient

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from backend.app import app

class TestAuth(unittest.TestCase):
    """简化版认证模块测试，不依赖pytest"""
    """测试认证模块功能"""
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        cls.client = TestClient(app)
        cls.base_url = "http://localhost:8000/api/auth"
        # 测试用户数据
        cls.test_user = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPassword123!"
        }
    
    def test_register_success(self):
        """测试用户成功注册"""
        response = requests.post(
            f"{self.base_url}/register",
            json=self.test_user
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json())
        self.assertEqual(response.json()["message"], "注册成功")

    def test_register_duplicate(self):
        """测试重复用户名注册"""
        # 先注册一次
        requests.post(f"{self.base_url}/register", json=self.test_user)
        # 再次尝试注册相同用户
        response = requests.post(
            f"{self.base_url}/register",
            json=self.test_user
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("detail", response.json())

    def test_login_success(self):
        """测试用户成功登录"""
        # 先注册用户
        requests.post(f"{self.base_url}/register", json=self.test_user)
        # 测试登录
        response = requests.post(
            f"{self.base_url}/token",
            data={
                "username": self.test_user["username"],
                "password": self.test_user["password"]
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.json())
        self.assertIn("token_type", response.json())

    def test_login_failure(self):
        """测试用户登录失败"""
        response = requests.post(
            f"{self.base_url}/token",
            data={
                "username": "wronguser",
                "password": "wrongpassword"
            }
        )
        self.assertEqual(response.status_code, 401)
        self.assertIn("detail", response.json())

    def test_check_status(self):
        """测试检查登录状态"""
        # 先登录获取token
        login_res = requests.post(
            f"{self.base_url}/token",
            data={
                "username": self.test_user["username"],
                "password": self.test_user["password"]
            }
        )
        token = login_res.json()["access_token"]
        # 测试检查状态
        response = requests.get(
            f"{self.base_url}/check",
            headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("is_authenticated", response.json())
        self.assertTrue(response.json()["is_authenticated"])

    def test_reset_password(self):
        """测试密码重置功能"""
        response = requests.post(
            f"{self.base_url}/reset-password",
            json={"email": self.test_user["email"]}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json())

if __name__ == "__main__":
    unittest.main()