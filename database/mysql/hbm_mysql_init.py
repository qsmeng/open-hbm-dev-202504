"""
数据库初始化SQL生成脚本
======================

根据模型定义自动生成数据库初始化SQL文件
"""

import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.schema import CreateTable, CreateIndex

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from backend.database.models import Base
import time
import os

def to_init_sql():
    """生成数据库初始化SQL文件
    
    根据SQLAlchemy模型定义生成符合最新标准的SQL初始化脚本
    生成内容包括:
    - 数据库用户创建
    - 表结构定义(包含注释)
    - 索引和外键约束
    - 示例数据
    """
    timestamp = time.strftime("%Y%m%d%H%M%S")
    file_path = os.path.join('database', 'mysql', f'hbm_mysql_init_V{timestamp}.sql')
    
    with open(file_path, 'w', encoding='utf-8') as f:
        # 添加创建数据库用户的SQL语句
        f.write("-- 创建数据库用户(与docker-compose环境变量一致)\n")
        f.write("CREATE USER IF NOT EXISTS 'hbm_user'@'%' IDENTIFIED BY 'hbm_password';\n")
        f.write("GRANT ALL PRIVILEGES ON hbm_db.* TO 'hbm_user'@'%';\n")
        f.write("FLUSH PRIVILEGES;\n\n")

        # 创建临时引擎用于SQL编译
        temp_engine = create_engine('sqlite:///:memory:')
        
        # 生成表结构SQL
        for table in Base.metadata.sorted_tables:
            # 生成创建表的SQL
            table_sql = str(CreateTable(table).compile(temp_engine))
            
            # 添加表注释
            if hasattr(table, '__doc__') and table.__doc__:
                table_sql = table_sql.replace('/* Represent a table in a database. */', 
                                             f'/* {table.__doc__.strip()} */')
            
            # 添加存储引擎和字符集
            table_sql += " ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
            
            # 修复枚举类型显示
            table_sql = table_sql.replace('VARCHAR(6)', 'ENUM(\'temp\',\'stable\',\'fixed\')')
            table_sql = table_sql.replace('VARCHAR(7)', 'ENUM(\'explore\',\'attack\',\'recover\',\'use\')')
            table_sql = table_sql.replace('VARCHAR(11)', 'ENUM(\'achievement\',\'game\',\'system\')')
            table_sql = table_sql.replace('VARCHAR(1)', 'ENUM(\'m\',\'f\',\'o\')')
            
            # 添加字段注释
            for column in table.columns:
                if column.comment:
                    table_sql = table_sql.replace(
                        f"{column.name} {column.type}",
                        f"{column.name} {column.type} COMMENT '{column.comment}'"
                    )
            
            f.write(table_sql)
            f.write(";\n\n")
            
            # 生成索引SQL
            for index in table.indexes:
                index_sql = str(CreateIndex(index).compile(temp_engine))
                f.write(index_sql)
                f.write(";\n\n")
            
            # 添加外键约束
            if table.name == 'experience_logs':
                f.write("ALTER TABLE experience_logs ADD FOREIGN KEY (user_id) REFERENCES users(id);\n\n")
        
        # 生成插入示例数据的SQL语句(使用最新字段名)
        f.write("\n-- 示例数据\n")
        f.write("INSERT INTO users (id, username, password_hash, email, status, experience, energy) VALUES\n")
        f.write("('user001', 'player1', 'hash1', 'player1@test.com', 1, 100, 200),\n")
        f.write("('user002', 'player2', 'hash2', 'player2@test.com', 1, 50, 150),\n")
        f.write("('user003', 'player3', 'hash3', 'player3@test.com', 0, 0, 256);\n\n")

        f.write("INSERT INTO spaces (id, type, author_id, title, content, stability, creator_id) VALUES\n")
        f.write("('space001', 'temp', 'user001', '新手空间', '欢迎来到新手空间', 80, 'user001'),\n")
        f.write("('space002', 'stable', 'user002', '进阶空间', '这里是进阶玩家空间', 90, 'user002'),\n")
        f.write("('space003', 'fixed', 'user001', '高级空间', '高级玩家专属空间', 100, 'user001');\n\n")

        f.write("INSERT INTO replies (id, space_id, author_id, content, floor_num) VALUES\n")
        f.write("('reply001', 'space001', 'user002', '这个空间很棒', 1),\n")
        f.write("('reply002', 'space001', 'user003', '我也这么觉得', 2),\n")
        f.write("('reply003', 'space002', 'user001', '进阶内容很有帮助', 1);\n\n")

        f.write("INSERT INTO treasures (id, name, effect, strength, owner_id) VALUES\n")
        f.write("('card001', '火焰卡', '造成火焰伤害', 100, 'user001'),\n")
        f.write("('card002', '治疗卡', '恢复生命值', 80, 'user002'),\n")
        f.write("('card003', '防御卡', '提高防御力', 120, 'user001');\n\n")

        f.write("INSERT INTO energy_logs (user_id, change_value, current_value, action_type) VALUES\n")
        f.write("('user001', -50, 150, 'attack'),\n")
        f.write("('user002', 20, 170, 'recover'),\n")
        f.write("('user003', -100, 156, 'explore');\n\n")

        f.write("INSERT INTO experience_logs (id, user_id, experience_change, current_experience, source_type) VALUES\n")
        f.write("('exp001', 'user001', 20, 120, 'game'),\n")
        f.write("('exp002', 'user002', 10, 60, 'achievement'),\n")
        f.write("('exp003', 'user001', 5, 125, 'system');\n\n")

        f.write("INSERT INTO server_configs (config_key, config_value, data_type, description) VALUES\n")
        f.write("('space_stability_threshold', '80', 'int', '空间稳定转化线'),\n")
        f.write("('energy_recovery_rate', '10', 'int', '体力恢复时间(分钟)'),\n")
        f.write("('max_energy', '256', 'int', '最大体力值');\n")
    
    print(f"SQL file generated: {file_path}")

if __name__ == "__main__":
    to_init_sql()
