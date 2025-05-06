import os
import sys
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from backend.app import app
from backend.database.models import Base

class TestAuth(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 配置SQLite内存数据库
        cls.engine = create_engine('sqlite:///:memory:')
        cls.Session = sessionmaker(bind=cls.engine)
        Base.metadata.create_all(cls.engine)
        
        # 替换应用的数据库会话
        app.dependency_overrides[get_db] = lambda: cls.Session()
        
        cls.client = TestClient(app)
        cls.test_user = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPassword123!"
        }

    @classmethod
    def tearDownClass(cls):
        # 清理数据库
        Base.metadata.drop_all(cls.engine)
    """增强版认证模块测试，包含更多测试用例和清理逻辑"""
    """简化版认证模块测试，不依赖pytest"""
    """测试认证模块功能"""
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        # 使用相同的MySQL配置
        DATABASE_URL = (
            f"mysql+mysqlconnector://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@"
            f"{os.getenv('MYSQL_HOST')}:{os.getenv('MYSQL_PORT')}/{os.getenv('MYSQL_DATABASE')}_test"
        )
        
        # 创建测试引擎和会话
        engine = create_engine(DATABASE_URL)
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        # 重写依赖
        def override_get_db():
            try:
                db = TestingSessionLocal()
                yield db
            finally:
                db.close()
                
        app.dependency_overrides[get_db] = override_get_db
        
        cls.client = TestClient(app)
        cls.test_user = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPassword123!"
        }
        
        # 初始化测试数据库
        Base.metadata.create_all(engine)
    
    @patch('backend.modules.auth.send_email')
    def test_register_success(self, mock_email):
        """测试用户成功注册"""
        mock_email.return_value = True
        response = self.client.post("/api/auth/register", json=self.test_user)
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json())
        self.assertEqual(response.json()["message"], "注册成功")

    def test_register_duplicate(self):
        """测试重复用户名注册"""
        # 先注册一次
        self.client.post("/api/auth/register", json=self.test_user)
        # 再次尝试注册
        response = self.client.post("/api/auth/register", json=self.test_user)
        self.assertEqual(response.status_code, 400)
        self.assertIn("detail", response.json())

    def test_login_success(self):
        """测试用户成功登录"""
        # 先注册用户
        self.client.post("/api/auth/register", json=self.test_user)
        # 测试登录
        response = self.client.post("/api/auth/token",
            data={
                "username": self.test_user["username"],
                "password": self.test_user["password"]
            })
        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.json())
        self.assertIn("token_type", response.json())

    def test_login_failure(self):
        """测试用户登录失败"""
        response = self.client.post("/api/auth/token",
            data={
                "username": "wronguser",
                "password": "wrongpassword"
            })
        self.assertEqual(response.status_code, 401)
        self.assertIn("detail", response.json())

    def test_register_invalid_inputs(self):
        """测试各种无效输入注册"""
        test_cases = [
            ("short_pw", "user1", "user1@test.com", "12345"),
            ("invalid_email", "user2", "not-an-email", "ValidPass123!"),
            ("missing_field", "", "user3@test.com", "ValidPass123!")
        ]
        for case in test_cases:
            with self.subTest(case=case[0]):
                _, username, email, password = case
                response = self.client.post("/api/auth/register",
                    json={"username": username, "email": email, "password": password})
                self.assertEqual(response.status_code, 400)

    @patch('backend.modules.auth.rate_limiter.check')
    def test_login_bruteforce(self, mock_limiter):
        """测试暴力破解防护"""
        mock_limiter.return_value = False  # 模拟达到限制
        response = self.client.post("/api/auth/token",
            data={"username": "nonexist", "password": "wrong"})
        self.assertEqual(response.status_code, 429)

    @classmethod
    def tearDownClass(cls):
        """测试完成后清理测试数据库"""
        DATABASE_URL = (
            f"mysql+mysqlconnector://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@"
            f"{os.getenv('MYSQL_HOST')}:{os.getenv('MYSQL_PORT')}/{os.getenv('MYSQL_DATABASE')}_test"
        )
        engine = create_engine(DATABASE_URL)
        Base.metadata.drop_all(engine)
        app.dependency_overrides.clear()

if __name__ == "__main__":
    unittest.main()