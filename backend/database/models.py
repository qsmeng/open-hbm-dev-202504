"""
数据库模型定义模块
=================

包含所有数据库模型的基础类和表定义
"""

from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import (
    Column, Integer, String, DateTime, 
    func, BigInteger, ForeignKey,
    Date, Boolean, Enum, Text,
    Index, UniqueConstraint
)

Base = declarative_base()

class User(Base):
    """用户表模型"""
    __tablename__ = 'users'
    
    id = Column(String(36), primary_key=True, comment='用户ID')
    username = Column(String(32), unique=True, nullable=False, comment='用户名(登录用)')
    password_hash = Column(String(64), nullable=False, comment='密码哈希')
    email = Column(String(32), unique=True, comment='电子邮箱(登录用)')
    phone_number = Column(String(15), unique=True, comment='电话号码(登录用)')
    status = Column(Integer, default=0, comment='账号状态: 0-未激活, 1-已激活')
    gender = Column(String(1), default='o', comment='性别: m-男, f-女, o-其他')
    birthdate = Column(Date, comment='出生日期')
    country = Column(String(100), comment='国家')
    city = Column(String(100), comment='城市')
    invite_code = Column(String(16), comment='邀请码')
    is_verified = Column(Boolean, default=False, comment='是否实名认证')
    last_login_at = Column(DateTime, comment='最后登录时间')
    login_ip = Column(String(45), comment='最后登录IP')
    experience = Column(Integer, default=0, comment='总经验值')
    current_level = Column(Integer, default=1, comment='当前等级')
    energy = Column(Integer, default=256, comment='当前体力值')
    max_energy = Column(Integer, default=256, comment='最大体力值')
    energy_recovery_at = Column(DateTime, comment='体力恢复时间')
    score = Column(Integer, default=0, comment='游戏分数')
    game_count = Column(Integer, default=0, comment='游戏局数')
    avatar_url = Column(String(255), comment='头像URL')
    yesterday_rank = Column(Integer, comment='昨日排名')
    last_game_uuid = Column(String(36), comment='最近游戏UUID')
    created_at = Column(DateTime, server_default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')

    energy_logs = relationship("EnergyLog", backref="user")
    experience_logs = relationship("ExperienceLog", backref="user")

    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"

class EnergyLog(Base):
    """用户体力变化日志"""
    __tablename__ = 'energy_logs'
    
    id = Column(Integer, primary_key=True, comment='日志ID')
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False, comment='关联用户ID')
    change_value = Column(Integer, nullable=False, comment='体力变化值')
    current_value = Column(Integer, nullable=False, comment='变化后体力值')
    action_type = Column(Enum('explore','attack','recover','use', name='action_types'), nullable=False, comment='动作类型')
    related_id = Column(String(36), comment='关联对象ID')
    created_at = Column(DateTime, server_default=func.now(), comment='创建时间')

    __table_args__ = (
        Index('idx_user', 'user_id'),
        Index('idx_created', 'created_at')
    )

class ExperienceLog(Base):
    """用户资历变化日志"""
    __tablename__ = 'experience_logs'
    
    id = Column(String(36), primary_key=True, comment='日志ID')
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False, comment='关联用户ID')
    experience_change = Column(Integer, nullable=False, comment='经验变化值')
    current_experience = Column(Integer, nullable=False, comment='变化后经验值')
    source_type = Column(Enum('achievement','game','system', name='source_types'), nullable=False, comment='经验来源类型')
    source_id = Column(String(36), comment='来源对象ID')
    description = Column(Text, comment='描述信息')
    created_at = Column(DateTime, server_default=func.now(), comment='创建时间')

    __table_args__ = (
        Index('idx_user', 'user_id'),
        Index('idx_source', 'source_type', 'source_id')
    )

class Space(Base):
    """空间表模型"""
    __tablename__ = 'spaces'
    
    id = Column(String(36), primary_key=True, comment='空间ID')
    type = Column(Enum('temp', 'stable', 'fixed', name='space_types'), nullable=False, comment='空间类型')
    author_id = Column(String(36), nullable=False, comment='作者ID')
    title = Column(String(100), nullable=False, comment='空间标题')
    content = Column(Text, nullable=False, comment='空间内容')
    heat = Column(Integer, default=0, comment='空间热度')
    stability = Column(Integer, default=100, comment='空间稳定度')
    turns_left = Column(Integer, default=10, comment='剩余回合数')
    creator_id = Column(String(36), nullable=False, comment='创建者ID')
    created_at = Column(DateTime, server_default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')

    __table_args__ = (
        Index('idx_creator', 'creator_id'),
        Index('idx_type', 'type')
    )

class Reply(Base):
    """回复表模型"""
    __tablename__ = 'replies'
    
    id = Column(String(36), primary_key=True, comment='回复ID')
    space_id = Column(String(36), nullable=False, comment='所属空间ID')
    parent_id = Column(String(36), comment='父回复ID')
    author_id = Column(String(36), nullable=False, comment='作者ID')
    content = Column(Text, nullable=False, comment='回复内容')
    floor_num = Column(Integer, nullable=False, comment='楼层号')
    created_at = Column(DateTime, server_default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')

    __table_args__ = (
        Index('idx_space', 'space_id'),
        Index('idx_parent', 'parent_id'),
        UniqueConstraint('space_id', 'floor_num', name='uq_space_floor')
    )

class Treasure(Base):
    """卡牌表模型"""
    __tablename__ = 'treasures'
    
    id = Column(String(36), primary_key=True, comment='卡牌ID')
    name = Column(String(100), nullable=False, comment='卡牌名称')
    effect = Column(Text, nullable=False, comment='卡牌效果')
    strength = Column(Integer, nullable=False, comment='卡牌强度')
    is_replica = Column(Boolean, default=False, comment='是否为复制品')
    deviation = Column(Integer, default=0, comment='偏离度')
    heat = Column(Integer, default=0, comment='热度值')
    owner_id = Column(String(36), nullable=False, comment='拥有者ID')
    created_at = Column(DateTime, server_default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')

    __table_args__ = (
        Index('idx_owner', 'owner_id'),
    )

class ServerConfig(Base):
    """服务器配置表模型"""
    __tablename__ = 'server_configs'
    
    id = Column(Integer, primary_key=True, comment='配置ID')
    config_key = Column(String(50), nullable=False, comment='配置键名')
    config_value = Column(String(255), nullable=False, comment='配置值')
    data_type = Column(Enum('int', 'string', 'bool', name='config_types'), nullable=False, comment='数据类型')
    description = Column(String(255), comment='配置描述')
    created_at = Column(DateTime, server_default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')

    __table_args__ = (
        UniqueConstraint('config_key', name='uq_config_key'),
    )