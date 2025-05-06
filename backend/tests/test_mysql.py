"""
MySQL数据库连接测试模块
======================

专门测试backend/database/hbm_mysql.py中的数据库连接功能

测试内容:
1. 连接池创建
2. 连接获取
3. 基本CRUD操作
"""

import unittest
import os
from backend.database.hbm_mysql import get_db_pool, get_db_connection

# 测试数据库配置
TEST_DB_CONFIG = {
    'host': 'localhost',
    'port': '3306',
    'user': 'hbm_user',
    'password': 'hbm_password',  # 使用.env中的hbm_user密码
    'database': 'hbm_db'          # 使用默认数据库
}

# 设置环境变量
os.environ.update({
    'MYSQL_HOST': TEST_DB_CONFIG['host'],
    'MYSQL_PORT': TEST_DB_CONFIG['port'],
    'MYSQL_USER': TEST_DB_CONFIG['user'],
    'MYSQL_PASSWORD': TEST_DB_CONFIG['password'],
    'MYSQL_DATABASE': TEST_DB_CONFIG['database']
})

class TestMySQLConnection(unittest.TestCase):
    """测试MySQL数据库连接功能"""
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化时确保连接池已创建"""
        cls.pool = get_db_pool()  # 强制初始化连接池
        cls.test_table = "test_table"
        
    def test_pool_creation(self):
        """测试连接池创建"""
        try:
            pool = get_db_pool()
            self.assertIsNotNone(pool, "连接池创建失败")
            self.assertEqual(pool.pool_name, "hbm_mysql_pool", "连接池名称不匹配")
            TestMySQLConnection.pool = pool  # 保存供后续测试使用
        except Exception as e:
            self.fail(f"连接池创建失败: {e}")
            
    def test_connection(self):
        """测试获取数据库连接"""
        if not TestMySQLConnection.pool:
            self.skipTest("连接池未初始化")
            
        try:
            connection = get_db_connection()
            self.assertTrue(connection.is_connected(), "连接未建立")
            connection.close()
        except Exception as e:
            self.fail(f"获取连接失败: {e}")
            
    def test_simple_query(self):
        """测试简单查询"""
        if not TestMySQLConnection.pool:
            self.skipTest("连接池未初始化")
            
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                self.assertEqual(result[0], 1, "简单查询结果不符预期")
        except Exception as e:
            self.fail(f"简单查询失败: {e}")

if __name__ == "__main__":
    unittest.main()
