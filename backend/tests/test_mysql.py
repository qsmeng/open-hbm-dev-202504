"""
MySQL数据库操作测试模块
======================

测试backend/database/hbm_mysql.py中的DBOperator功能

测试内容:
1. 会话管理
2. CRUD操作
3. 事务处理
"""

import unittest
import os
from sqlalchemy.exc import SQLAlchemyError
from backend.database.hbm_mysql import DBOperator, db_session
from backend.database.models import User

# 测试数据库配置
os.environ.update({
    'MYSQL_HOST': 'localhost',
    'MYSQL_PORT': '3306',
    'MYSQL_USER': 'hbm_user',
    'MYSQL_PASSWORD': 'hbm_password',
    'MYSQL_DATABASE': 'hbm_db'
})

class TestDBOperator(unittest.TestCase):
    """测试DBOperator数据库操作"""
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        # 直接使用.env中的数据库配置
        DATABASE_URL = (
            f"mysql+mysqlconnector://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@"
            f"{os.getenv('MYSQL_HOST')}:{os.getenv('MYSQL_PORT')}/{os.getenv('MYSQL_DATABASE')}"
        )
        
        # 创建测试引擎和会话
        cls.engine = create_engine(DATABASE_URL, pool_pre_ping=True)
        cls.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=cls.engine)
        
        # 重写db_session依赖
        def override_db_session():
            try:
                db = cls.SessionLocal()
                yield db
            finally:
                db.close()
                
        app.dependency_overrides[db_session] = override_db_session
        
        # 初始化测试数据库
        Base.metadata.create_all(cls.engine)
    
    def setUp(self):
        """每个测试前清空测试数据"""
        with db_session() as session:
            session.query(User).delete()
            session.commit()
    
    def test_session_management(self):
        """测试会话管理"""
        try:
            with db_session() as session:
                # 执行简单查询验证连接
                result = session.execute(text("SELECT 1")).fetchone()
                self.assertEqual(result[0], 1, "数据库连接验证失败")
                self.assertTrue(session.is_active, "会话未激活")
        except SQLAlchemyError as e:
            self.fail(f"会话管理失败: {e}")
        except Exception as e:
            self.fail(f"未知错误: {str(e)}")
    
    def test_create_operation(self):
        """测试创建记录"""
        test_user = {
            "username": "test_user",
            "email": "test@example.com",
            "password_hash": "hashed_password"
        }
        
        user = DBOperator.create(User, **test_user)
        self.assertIsNotNone(user.id, "创建记录失败")
        self.assertEqual(user.username, "test_user", "用户名不匹配")
    
    def test_query_operation(self):
        """测试查询记录"""
        # 先创建测试数据
        DBOperator.create(User, username="query_test", email="query@test.com", password_hash="hash")
        
        # 测试查询
        user = DBOperator.get_one(User, username="query_test")
        self.assertIsNotNone(user, "查询记录失败")
        self.assertEqual(user.email, "query@test.com", "邮箱不匹配")
    
    def test_update_operation(self):
        """测试更新记录"""
        # 创建测试数据
        user = DBOperator.create(User, username="update_test", email="update@test.com", password_hash="hash")
        
        # 更新数据
        DBOperator.update(User, {"username": "update_test"}, email="updated@test.com")
        
        # 验证更新
        updated = DBOperator.get_one(User, username="update_test")
        self.assertEqual(updated.email, "updated@test.com", "更新失败")
    
    def test_delete_operation(self):
        """测试删除记录"""
        # 创建测试数据
        DBOperator.create(User, username="delete_test", email="delete@test.com", password_hash="hash")
        
        # 删除数据
        count = DBOperator.delete(User, username="delete_test")
        self.assertEqual(count, 1, "删除记录数不符")
        
        # 验证删除
        deleted = DBOperator.get_one(User, username="delete_test")
        self.assertIsNone(deleted, "记录未删除")

if __name__ == "__main__":
    unittest.main()
