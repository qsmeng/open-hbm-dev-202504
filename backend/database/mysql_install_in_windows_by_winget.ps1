# 检查是否以管理员身份运行
function Test-Admin {
    $currentUser = New-Object Security.Principal.WindowsPrincipal $([Security.Principal.WindowsIdentity]::GetCurrent())
    $currentUser.IsInRole([Security.Principal.WindowsBuiltinRole]::Administrator)
}

if (-not (Test-Admin)) {
    Write-Host "请以管理员身份运行此脚本。"
    exit 1
}

# 检查 winget 是否可用
if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    Write-Host "winget 未安装，请先安装 winget。"
    exit 1
}

# 升级 winget 并添加源
Write-Host "升级 winget 并添加源..."
try {
    winget upgrade -r -u --force
    winget source add zkd https://mirrors.ustc.edu.cn/winget-source --no-proxy
    winget source add qh https://mirrors.tuna.tsinghua.edu.cn/winget --no-proxy
    winget source add al https://mirrors.aliyun.com/winget --no-proxy
    winget source add wy https://mirrors.163.com/winget --no-proxy
    winget source add hw https://mirrors.huaweicloud.com/winget --no-proxy
    winget source add tx https://mirrors.cloud.tencent.com/winget --no-proxy
    winget source add bd https://mirrors.baidubce.com/winget --no-proxy
    winget source add Contoso https://www.contoso.com/cache --no-proxy
    winget source add winget https://winget.azureedge.net/cache --no-proxy
} catch {
    Write-Host "尝试更新源失败： $_"
}

# 使用 winget 安装 MySQL 8
Write-Host "开始使用 winget 安装 MySQL 8..."
try {
    winget install MySQL.MySQLServer.8.0
} catch {
    Write-Host "安装 MySQL 失败： $_"
    exit 1
}

# 配置 MySQL 环境变量
Write-Host "配置 MySQL 环境变量..."
$mysqlPath = "C:\Program Files\MySQL\MySQL Server 8.0\bin"
if (-not (Test-Path $mysqlPath)) {
    Write-Host "未找到 MySQL 安装路径，请确认 MySQL 是否安装成功。"
    exit 1
}
$env:Path = "$env:Path;$mysqlPath"
[Environment]::SetEnvironmentVariable("Path", $env:Path, [EnvironmentVariableTarget]::Machine)

# 等待用户设置 MySQL root 密码
Write-Host "请手动设置 MySQL root 用户的密码，设置完成后按任意键继续..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# 创建项目所需的数据库和用户
Write-Host "创建项目所需的数据库和用户..."
$rootPassword = Read-Host -Prompt "请输入 MySQL root 用户的密码"
$mysqlCommand = "mysql -u root -p$rootPassword -e "
$createDatabase = "CREATE DATABASE hbm_db;"
$createUser = "CREATE USER 'hbm_user'@'%' IDENTIFIED BY 'hbm_password';"
$grantPrivileges = "GRANT ALL PRIVILEGES ON hbm_db.* TO 'hbm_user'@'%';"
$flushPrivileges = "FLUSH PRIVILEGES;"
Invoke-Expression ($mysqlCommand + "`"$createDatabase`"")
Invoke-Expression ($mysqlCommand + "`"$createUser`"")
Invoke-Expression ($mysqlCommand + "`"$grantPrivileges`"")
Invoke-Expression ($mysqlCommand + "`"$flushPrivileges`"")

# 初始化数据库表和数据
Write-Host "初始化数据库表和数据..."
$initSqlPath = "F:\workspace\open-hbm-dev-202504\database\mysql\hbm_mysql_init.sql"
if (-not (Test-Path $initSqlPath)) {
    Write-Host "未找到初始化 SQL 文件，请确认文件路径是否正确。"
    exit 1
}
Invoke-Expression ($mysqlCommand + "`"SOURCE $initSqlPath`" -D hbm_db")

# 配置项目环境变量
Write-Host "配置项目环境变量..."
[Environment]::SetEnvironmentVariable("MYSQL_HOST", "localhost", [EnvironmentVariableTarget]::User)
[Environment]::SetEnvironmentVariable("MYSQL_PORT", "3306", [EnvironmentVariableTarget]::User)
[Environment]::SetEnvironmentVariable("MYSQL_USER", "hbm_user", [EnvironmentVariableTarget]::User)
[Environment]::SetEnvironmentVariable("MYSQL_PASSWORD", "hbm_password", [EnvironmentVariableTarget]::User)
[Environment]::SetEnvironmentVariable("MYSQL_DATABASE", "hbm_db", [EnvironmentVariableTarget]::User)

Write-Host "MySQL 安装和配置完成！"