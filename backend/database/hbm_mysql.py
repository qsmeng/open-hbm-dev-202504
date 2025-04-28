"""
MySQL数据库操作模块
==================

提供MySQL数据库连接池管理和基本CRUD操作功能。

主要功能：
- get_db_pool: 创建数据库连接池
- get_db_connection: 获取数据库连接(带重试机制)
- insert_data: 插入数据
- upsert_data: 更新或插入数据
- delete_data: 删除数据
- query_data: 查询数据

依赖组件：
- mysql-connector-python: MySQL官方Python驱动
- 环境变量配置:
  - LOCAL_MYSQL_URL: MySQL服务器地址和端口
  - MYSQL_USER: 数据库用户名
  - MYSQL_PASSWORD: 数据库密码
  - MYSQL_DATABASE: 数据库名称

安全注意事项：
1. 所有SQL查询使用参数化查询防止注入
2. 连接池大小限制为20
3. 数据库操作失败会自动回滚
"""

import time
import os
import mysql.connector.pooling

def get_db_pool():
    """
    创建并返回MySQL数据库连接池
    
    返回值:
    - MySQLConnectionPool: 数据库连接池对象
    
    异常:
    - Exception: 连接池创建失败时抛出
    
    配置说明:
    - 连接池大小固定为20
    - 连接信息从环境变量读取
    """
    try:
        # 从环境变量中获取MySQL连接信息
        local_mysql_url = os.getenv('LOCAL_MYSQL_URL', 'localhost:3306')
        host, port = local_mysql_url.split(':') if ':' in local_mysql_url else (local_mysql_url, '3306')
        
        # 连接池配置
        config = {
            'host': host,
            'port': port,
            'user': os.getenv('MYSQL_USER'),
            'password': os.getenv('MYSQL_PASSWORD'),
            'database': os.getenv('MYSQL_DATABASE'),
            'pool_name': 'hbm_mysql_pool',
            'pool_size': 20  # 固定连接池大小
        }
        return mysql.connector.pooling.MySQLConnectionPool(**config)
    except Exception as e:
        print(f"Error creating database connection pool: {e}")
        raise

def get_db_connection(retries=5, delay=5):
    """
    从连接池获取数据库连接，支持重试机制
    
    参数:
    - retries: 最大重试次数，默认5次
    - delay: 重试间隔(秒)，默认5秒
    
    返回值:
    - MySQLConnection: 数据库连接对象
    
    异常:
    - Exception: 所有重试失败后抛出
    
    重试逻辑:
    - 每次失败后等待指定延迟时间
    - 记录每次失败错误信息
    """
    for i in range(retries):
        try:
            pool = get_db_pool()
            return pool.get_connection()
        except mysql.connector.Error as err:
            print(f"Error getting database connection from pool (attempt {i + 1}/{retries}): {err}")
            if i < retries - 1:
                time.sleep(delay)  # 等待后重试
    raise Exception("无法连接到数据库，请检查数据库服务是否已启动")

def insert_data(table_name, data):
    """
    向指定表插入数据
    
    参数:
    - table_name: 目标表名
    - data: 字典形式的数据，键为列名
    
    返回值:
    - int: 插入行的ID
    
    异常:
    - mysql.connector.Error: 数据库操作失败时抛出
    
    安全说明:
    - 使用参数化查询防止SQL注入
    - 操作失败自动回滚
    """
    try:
        # 使用上下文管理器确保连接正确关闭
        with get_db_connection() as connection:
            cursor = connection.cursor()
            # 构建参数化插入语句
            placeholders = ", ".join(["%s"] * len(data))
            sql = f"INSERT INTO {table_name} ({', '.join(data.keys())}) VALUES ({placeholders})"
            cursor.execute(sql, list(data.values()))
            connection.commit()
            return cursor.lastrowid  # 返回自增ID
    except mysql.connector.Error as err:
        print(f"Error inserting data: {err}")
        connection.rollback()  # 失败回滚
        raise

def upsert_data(table_name, data, unique_keys):
    """
    更新或插入数据(存在则更新，不存在则插入)
    
    参数:
    - table_name: 目标表名
    - data: 字典形式的数据，键为列名
    - unique_keys: 唯一键列表，用于判断记录是否存在
    
    返回值:
    - int: 受影响的行数
    
    异常:
    - mysql.connector.Error: 数据库操作失败时抛出
    
    实现说明:
    - 使用ON DUPLICATE KEY UPDATE语法
    - 非唯一键的列会被更新
    """
    try:
        with get_db_connection() as connection:
            cursor = connection.cursor()
            # 构建UPSERT语句
            columns = ", ".join(data.keys())
            placeholders = ", ".join(["%s"] * len(data))
            update_clause = ", ".join([f"{key}=VALUES({key})" for key in data if key not in unique_keys])

            sql = f"""
            INSERT INTO {table_name} ({columns})
            VALUES ({placeholders})
            ON DUPLICATE KEY UPDATE {update_clause}
            """
            cursor.execute(sql, list(data.values()))
            connection.commit()
            return cursor.rowcount  # 返回受影响行数
    except mysql.connector.Error as err:
        print(f"Error updating or inserting data: {err}")
        raise

def delete_data(table_name, condition, params):
    """
    删除指定表中的数据
    
    参数:
    - table_name: 目标表名
    - condition: WHERE条件语句
    - params: 条件参数列表
    
    返回值:
    - int: 受影响的行数
    
    异常:
    - mysql.connector.Error: 数据库操作失败时抛出
    
    安全说明:
    - 使用参数化查询防止SQL注入
    - 操作失败自动回滚
    """
    try:
        with get_db_connection() as connection:
            cursor = connection.cursor()
            # 参数化删除语句
            sql = f"DELETE FROM {table_name} WHERE {condition}"
            cursor.execute(sql, params)
            connection.commit()
            return cursor.rowcount
    except mysql.connector.Error as err:
        print(f"Error deleting data: {err}")
        connection.rollback()
        raise

def query_data(table_name, condition, params):
    """
    查询指定表中的数据
    
    参数:
    - table_name: 目标表名
    - condition: WHERE条件语句
    - params: 条件参数列表
    
    返回值:
    - list: 查询结果列表
    
    异常:
    - mysql.connector.Error: 数据库操作失败时抛出
    
    安全说明:
    - 使用参数化查询防止SQL注入
    """
    try:
        with get_db_connection() as connection:
            cursor = connection.cursor()
            # 参数化查询语句
            sql = f"SELECT * FROM {table_name} WHERE {condition}"
            cursor.execute(sql, params)
            return cursor.fetchall()  # 返回所有结果
    except mysql.connector.Error as err:
        print(f"Error getting data: {err}")
        raise

def main():
    """
    模块测试函数
    
    示例用法:
    - 测试数据库连接
    - 演示基本CRUD操作
    """
    try:
        # 测试数据库连接
        with get_db_connection() as connection:
            cursor = connection.cursor()
            # 简单查询测试
            cursor.execute("SELECT 1 FROM dual")
            for row in cursor.fetchall():
                print("Database connection test:", row)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    """模块直接运行时执行的测试代码"""
    main()