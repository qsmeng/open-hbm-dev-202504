"""
MySQL数据库操作模块(优化版)
=======================

基于SQLAlchemy ORM重构的数据库操作模块，提供更高效的CRUD接口和事务管理
"""

from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import SQLAlchemyError
import os

# 数据库配置(从环境变量获取，带默认值)
DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'mysql'),
    'port': os.getenv('MYSQL_PORT', '3306'),
    'user': os.getenv('MYSQL_USER', 'hbm_user'),
    'password': os.getenv('MYSQL_PASSWORD', 'hbm_password'),
    'database': os.getenv('MYSQL_DATABASE', 'hbm_db')
}

DATABASE_URL = (
    f"mysql+mysqlconnector://{DB_CONFIG['user']}:{DB_CONFIG['password']}@"
    f"{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
)

# 创建引擎和会话工厂
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600
)
SessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)

@contextmanager
def db_session():
    """提供数据库会话的上下文管理器"""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

class DBOperator:
    """数据库操作封装类"""
    
    @staticmethod
    def get_one(model, **filters):
        """获取单个记录"""
        with db_session() as session:
            return session.query(model).filter_by(**filters).first()

    @staticmethod
    def get_all(model, **filters):
        """获取多个记录"""
        with db_session() as session:
            return session.query(model).filter_by(**filters).all()

    @staticmethod
    def create(model, **data):
        """创建记录"""
        with db_session() as session:
            instance = model(**data)
            session.add(instance)
            session.flush()
            return instance

    @staticmethod
    def bulk_create(model, data_list):
        """批量创建记录"""
        with db_session() as session:
            instances = [model(**data) for data in data_list]
            session.bulk_save_objects(instances)
            session.flush()
            return instances

    @staticmethod
    def update(model, filters, **data):
        """更新记录"""
        with db_session() as session:
            instances = session.query(model).filter_by(**filters)
            instances.update(data, synchronize_session=False)
            return instances.all()

    @staticmethod
    def delete(model, **filters):
        """删除记录"""
        with db_session() as session:
            instances = session.query(model).filter_by(**filters)
            count = instances.delete(synchronize_session=False)
            return count

    @staticmethod
    def execute_raw(sql, params=None):
        """执行原生SQL"""
        with db_session() as session:
            return session.execute(sql, params or {})

if __name__ == "__main__":
    """模块测试"""
    from backend.database.models import User
    # 测试新接口
    with db_session() as session:
        user = User(username="test", email="test@example.com")
        session.add(user)
        session.commit()
        print("测试成功")
