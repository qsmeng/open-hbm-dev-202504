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
from sqlalchemy.exc import SQLAlchemyError
from backend.database.hbm_mysql import DBOperator, db_session
from backend.database.models import User

class TestDBOperator(unittest.TestCase):
    """测试DBOperator数据库操作"""
    

    
    def setUp(self):
        """每个测试前清理测试数据"""
        try:
            with db_session() as session:
                # 只删除测试数据(用户名以test_开头)
                deleted = session.query(User).filter(User.username.like('test_%')).delete()
                session.commit()
                print(f"\n清理测试数据: 删除了 {deleted} 条记录")
        except Exception as e:
            print(f"\n清理测试数据失败: {str(e)}")
            raise
    
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
            "username": "test_user_1",  # 添加test_前缀
            "email": "test_1@example.com",
            "password_hash": "hashed_password"
        }
        
        user = DBOperator.create(User, **test_user)
        self.assertIsNotNone(user.id, "创建记录失败")
        self.assertEqual(user.username, "test_user", "用户名不匹配")
    
    def test_query_operation(self):
        """测试查询记录"""
        # 先创建测试数据
        DBOperator.create(User, username="test_query", email="test_query@test.com", password_hash="hash")
        
        # 测试查询
        user = DBOperator.get_one(User, username="query_test")
        self.assertIsNotNone(user, "查询记录失败")
        self.assertEqual(user.email, "query@test.com", "邮箱不匹配")
    
    def test_update_operation(self):
        """测试更新记录"""
        # 创建测试数据
        user = DBOperator.create(User, username="test_update", email="test_update@test.com", password_hash="hash")
        
        # 更新数据
        DBOperator.update(User, {"username": "update_test"}, email="updated@test.com")
        
        # 验证更新
        updated = DBOperator.get_one(User, username="update_test")
        self.assertEqual(updated.email, "updated@test.com", "更新失败")
    
    def test_delete_operation(self):
        """测试删除记录"""
        # 创建测试数据
        DBOperator.create(User, username="test_delete", email="test_delete@test.com", password_hash="hash")
        
        # 删除数据
        count = DBOperator.delete(User, username="delete_test")
        self.assertEqual(count, 1, "删除记录数不符")
        
        # 验证删除
        deleted = DBOperator.get_one(User, username="delete_test")
        self.assertIsNone(deleted, "记录未删除")

if __name__ == "__main__":
    unittest.main()
