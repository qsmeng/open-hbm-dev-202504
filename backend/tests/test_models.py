"""
数据库模型测试模块
=================

包含所有数据库模型的测试用例
"""

import unittest
from datetime import datetime
from backend.database.models import Base, User, Space, Reply, Treasure, ServerConfig
from backend.database.hbm_mysql import engine, SessionLocal

class TestModels(unittest.TestCase):
    """数据库模型测试类"""

    @classmethod
    def setUpClass(cls):
        """创建测试数据库表"""
        Base.metadata.create_all(engine)
        cls.session = SessionLocal()

    @classmethod
    def tearDownClass(cls):
        """删除测试数据库表"""
        cls.session.close()
        Base.metadata.drop_all(engine)

    def setUp(self):
        """每个测试前重置session"""
        self.session.rollback()

    def test_user_model(self):
        """测试用户模型"""
        # 创建测试用户
        user = User(
            id="test_user_1",
            username="testuser",
            password_hash="hashed_password",
            email="test@example.com"
        )
        self.session.add(user)
        self.session.commit()

        # 验证用户创建
        db_user = self.session.query(User).filter_by(username="testuser").first()
        self.assertIsNotNone(db_user)
        self.assertEqual(db_user.email, "test@example.com")

    def test_space_model(self):
        """测试空间模型"""
        # 创建测试空间
        space = Space(
            id="test_space_1",
            type="temp",
            author_id="test_author",
            title="Test Space",
            content="Test content",
            creator_id="test_creator"
        )
        self.session.add(space)
        self.session.commit()

        # 验证空间创建
        db_space = self.session.query(Space).filter_by(title="Test Space").first()
        self.assertIsNotNone(db_space)
        self.assertEqual(db_space.type, "temp")

    def test_reply_model(self):
        """测试回复模型"""
        # 创建测试回复
        reply = Reply(
            id="test_reply_1",
            space_id="test_space_1",
            author_id="test_user_1",
            content="Test reply",
            floor_num=1
        )
        self.session.add(reply)
        self.session.commit()

        # 验证回复创建
        db_reply = self.session.query(Reply).filter_by(space_id="test_space_1").first()
        self.assertIsNotNone(db_reply)
        self.assertEqual(db_reply.floor_num, 1)

    def test_treasure_model(self):
        """测试卡牌模型"""
        # 创建测试卡牌
        treasure = Treasure(
            id="test_treasure_1",
            name="Test Card",
            effect="Test effect",
            strength=100,
            owner_id="test_user_1"
        )
        self.session.add(treasure)
        self.session.commit()

        # 验证卡牌创建
        db_treasure = self.session.query(Treasure).filter_by(name="Test Card").first()
        self.assertIsNotNone(db_treasure)
        self.assertEqual(db_treasure.strength, 100)

    def test_server_config_model(self):
        """测试服务器配置模型"""
        # 创建测试配置
        config = ServerConfig(
            config_key="test_config",
            config_value="100",
            data_type="int",
            description="Test config"
        )
        self.session.add(config)
        self.session.commit()

        # 验证配置创建
        db_config = self.session.query(ServerConfig).filter_by(config_key="test_config").first()
        self.assertIsNotNone(db_config)
        self.assertEqual(db_config.data_type, "int")

    def test_user_relationships(self):
        """测试用户关系"""
        # 创建测试用户和日志
        user = User(
            id="test_user_2",
            username="testuser2",
            password_hash="hashed_password2",
            email="test2@example.com"
        )
        energy_log = EnergyLog(
            user_id="test_user_2",
            change_amount=10,
            remaining=100,
            change_reason="test"
        )
        self.session.add(user)
        self.session.add(energy_log)
        self.session.commit()

        # 验证关系
        db_user = self.session.query(User).filter_by(username="testuser2").first()
        self.assertEqual(len(db_user.energy_logs), 1)
        self.assertEqual(db_user.energy_logs[0].change_amount, 10)

if __name__ == "__main__":
    unittest.main()
