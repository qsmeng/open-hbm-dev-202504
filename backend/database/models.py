"""
数据库模型定义模块
=================

包含所有数据库模型的基础类和表定义
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Column, Integer, String, DateTime, 
    func, BigInteger, ForeignKey,
    Date, Boolean, Enum, Text
)
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    """用户表模型"""
    __tablename__ = 'users'
    
    id = Column(String(36), primary_key=True)
    username = Column(String(32), unique=True, nullable=False)
    password_hash = Column(String(64), nullable=False)
    email = Column(String(32), unique=True)
    phone_number = Column(String(15), unique=True)
    status = Column(Integer, default=0)
    gender = Column(String(1), default='o')
    birthdate = Column(Date)
    country = Column(String(100))
    city = Column(String(100))
    invite_code = Column(String(16))
    is_verified = Column(Boolean, default=False)
    last_login_at = Column(DateTime)
    login_ip = Column(String(45))
    experience = Column(Integer, default=0)
    current_level = Column(Integer, default=1)
    energy = Column(Integer, default=256)
    max_energy = Column(Integer, default=256)
    energy_recovery_at = Column(DateTime)
    score = Column(Integer, default=0)
    game_count = Column(Integer, default=0)
    avatar_url = Column(String(255))
    yesterday_rank = Column(Integer)
    last_game_uuid = Column(String(36))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    energy_logs = relationship("EnergyLog", backref="user")
    experience_logs = relationship("ExperienceLog", backref="user")

    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"

class EnergyLog(Base):
    """用户体力变化日志"""
    __tablename__ = 'energy_logs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(36), ForeignKey('users.id'))
    change_amount = Column(Integer, nullable=False)
    remaining = Column(Integer, nullable=False)
    change_reason = Column(String(50), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

class ExperienceLog(Base):
    """用户资历变化日志"""
    __tablename__ = 'experience_logs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(36), ForeignKey('users.id'))
    change_amount = Column(BigInteger, nullable=False)
    remaining = Column(BigInteger, nullable=False)
    change_reason = Column(String(50), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

class Space(Base):
    """空间表模型"""
    __tablename__ = 'spaces'
    
    id = Column(String(36), primary_key=True)
    type = Column(Enum('temp', 'stable', 'fixed', name='space_types'), nullable=False)
    author_id = Column(String(36), nullable=False)
    title = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    heat = Column(Integer, default=0)
    stability = Column(Integer, default=100)
    turns_left = Column(Integer, default=10)
    creator_id = Column(String(36), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index('idx_creator', 'creator_id'),
        Index('idx_type', 'type')
    )

class Reply(Base):
    """回复表模型"""
    __tablename__ = 'replies'
    
    id = Column(String(36), primary_key=True)
    space_id = Column(String(36), nullable=False)
    parent_id = Column(String(36))
    author_id = Column(String(36), nullable=False)
    content = Column(Text, nullable=False)
    floor_num = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index('idx_space', 'space_id'),
        Index('idx_parent', 'parent_id'),
        UniqueConstraint('space_id', 'floor_num', name='uq_space_floor')
    )

class Treasure(Base):
    """卡牌表模型"""
    __tablename__ = 'treasures'
    
    id = Column(String(36), primary_key=True)
    name = Column(String(100), nullable=False)
    effect = Column(Text, nullable=False)
    strength = Column(Integer, nullable=False)
    is_replica = Column(Boolean, default=False)
    deviation = Column(Integer, default=0)
    heat = Column(Integer, default=0)
    owner_id = Column(String(36), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index('idx_owner', 'owner_id'),
    )

class ServerConfig(Base):
    """服务器配置表模型"""
    __tablename__ = 'server_configs'
    
    id = Column(Integer, primary_key=True)
    config_key = Column(String(50), nullable=False)
    config_value = Column(String(255), nullable=False)
    data_type = Column(Enum('int', 'string', 'bool', name='config_types'), nullable=False)
    description = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint('config_key', name='uq_config_key'),
    )
