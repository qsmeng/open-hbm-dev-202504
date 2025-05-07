# 定义 MySQL 相关信息
$mysqlRootPassword = Read-Host -Prompt "请输入 MySQL root 用户的密码"
$mysqlUser = "hbm_user"
$mysqlPassword = "hbm_password"
$mysqlDatabase = "hbm_db"
$initSqlPath = "F:\workspace\open-hbm-dev-202504\database\mysql\hbm_mysql_init.sql"

# 检查 MySQL 命令是否可用
if (-not (Get-Command mysql -ErrorAction SilentlyContinue)) {
    Write-Host "未找到 mysql 命令，请确认 MySQL 是否安装成功或环境变量是否配置正确。"
    exit 1
}

# 创建数据库和用户
Write-Host "创建数据库和用户..."
$createDatabaseCommand = "mysql -u root -p$mysqlRootPassword -e `"CREATE DATABASE IF NOT EXISTS $mysqlDatabase;`""
$createUserCommand = "mysql -u root -p$mysqlRootPassword -e `"CREATE USER IF NOT EXISTS '$mysqlUser'@'%' IDENTIFIED BY '$mysqlPassword';`""
$grantPrivilegesCommand = "mysql -u root -p$mysqlRootPassword -e `"GRANT ALL PRIVILEGES ON $mysqlDatabase.* TO '$mysqlUser'@'%';`""
$flushPrivilegesCommand = "mysql -u root -p$mysqlRootPassword -e `"FLUSH PRIVILEGES;`""

try {
    Invoke-Expression $createDatabaseCommand
    Invoke-Expression $createUserCommand
    Invoke-Expression $grantPrivilegesCommand
    Invoke-Expression $flushPrivilegesCommand
    Write-Host "数据库和用户创建成功。"
} catch {
    Write-Host "创建数据库和用户时出错: $_"
    exit 1
}

# 初始化数据库表和数据
Write-Host "初始化数据库表和数据..."
if (-not (Test-Path $initSqlPath)) {
    Write-Host "未找到初始化 SQL 文件，请确认文件路径是否正确。"
    exit 1
}
$initDatabaseCommand = "mysql -u $mysqlUser -p$mysqlPassword $mysqlDatabase < $initSqlPath"
try {
    Invoke-Expression $initDatabaseCommand
    Write-Host "数据库表和数据初始化成功。"
} catch {
    Write-Host "初始化数据库表和数据时出错: $_"
    exit 1
}

# 配置项目环境变量
Write-Host "配置项目环境变量..."
[Environment]::SetEnvironmentVariable("MYSQL_HOST", "localhost", [EnvironmentVariableTarget]::User)
[Environment]::SetEnvironmentVariable("MYSQL_PORT", "3306", [EnvironmentVariableTarget]::User)
[Environment]::SetEnvironmentVariable("MYSQL_USER", $mysqlUser, [EnvironmentVariableTarget]::User)
[Environment]::SetEnvironmentVariable("MYSQL_PASSWORD", $mysqlPassword, [EnvironmentVariableTarget]::User)
[Environment]::SetEnvironmentVariable("MYSQL_DATABASE", $mysqlDatabase, [EnvironmentVariableTarget]::User)
Write-Host "项目环境变量配置成功。"

Write-Host "MySQL 设置完成！"