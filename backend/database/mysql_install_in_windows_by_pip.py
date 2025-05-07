import subprocess
import os
import getpass
import time


def install_mysql_server():
    try:
        print("开始使用 winget 安装 MySQL 8 Server...")
        subprocess.run(["winget", "install", "MySQL.MySQLServer.8.0"], check=True)
        print("MySQL 8 Server 安装成功。")
    except subprocess.CalledProcessError as e:
        print(f"安装 MySQL 8 Server 失败: {e}")


def wait_for_mysql_service():
    print("等待 MySQL 服务启动...")
    time.sleep(30)  # 等待 30 秒，确保服务启动
    print("MySQL 服务已启动。")


def create_database_and_user(root_password):
    try:
        print("创建项目所需的数据库和用户...")
        commands = [
            f'mysql -u root -p{root_password} -e "CREATE DATABASE IF NOT EXISTS hbm_db;"',
            f'mysql -u root -p{root_password} -e "CREATE USER IF NOT EXISTS \'hbm_user\'@\'%\' IDENTIFIED BY \'hbm_password\';"',
            f'mysql -u root -p{root_password} -e "GRANT ALL PRIVILEGES ON hbm_db.* TO \'hbm_user\'@\'%\';"',
            f'mysql -u root -p{root_password} -e "FLUSH PRIVILEGES;"'
        ]
        for command in commands:
            subprocess.run(command, shell=True, check=True)
        print("数据库和用户创建成功。")
    except subprocess.CalledProcessError as e:
        print(f"创建数据库和用户失败: {e}")


def initialize_database():
    try:
        print("初始化数据库表和数据...")
        init_sql_path = r"F:\workspace\open-hbm-dev-202504\database\mysql\hbm_mysql_init.sql"
        if not os.path.exists(init_sql_path):
            print("未找到初始化 SQL 文件，请确认文件路径是否正确。")
            return
        command = f'mysql -u hbm_user -phbm_password hbm_db < {init_sql_path}'
        subprocess.run(command, shell=True, check=True)
        print("数据库表和数据初始化成功。")
    except subprocess.CalledProcessError as e:
        print(f"初始化数据库表和数据失败: {e}")


def set_environment_variables():
    print("配置项目环境变量...")
    os.environ["MYSQL_HOST"] = "localhost"
    os.environ["MYSQL_PORT"] = "3306"
    os.environ["MYSQL_USER"] = "hbm_user"
    os.environ["MYSQL_PASSWORD"] = "hbm_password"
    os.environ["MYSQL_DATABASE"] = "hbm_db"
    print("项目环境变量配置成功。")


if __name__ == "__main__":
    # 安装 MySQL 8 Server
    install_mysql_server()

    # 等待用户设置 MySQL root 密码
    input("请手动设置 MySQL root 用户的密码，设置完成后按回车键继续...")

    # 等待 MySQL 服务启动
    wait_for_mysql_service()

    # 获取 MySQL root 用户密码
    root_password = getpass.getpass("请输入 MySQL root 用户的密码: ")

    # 创建数据库和用户
    create_database_and_user(root_password)

    # 初始化数据库表和数据
    initialize_database()

    # 设置项目环境变量
    set_environment_variables()

    print("MySQL 安装和配置完成！")