# Windows SSH 免密登录配置脚本
# 在 cao 设备上以管理员身份运行

Write-Host "=== Windows SSH 免密登录修复 ===" -ForegroundColor Green

# 1. 停止 SSH 服务
Stop-Service sshd -Force
Write-Host "✓ SSH 服务已停止"

# 2. 创建 .ssh 目录并设置权限
$sshDir = "$env:USERPROFILE\.ssh"
if (!(Test-Path $sshDir)) {
    New-Item -ItemType Directory -Path $sshDir -Force | Out-Null
}

# 3. 创建 authorized_keys 文件
$authKeys = "$sshDir\authorized_keys"
$pubKey = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIFDXZqKPkoiTdWmi7/VOPVmxUuow2O9UnPAivZ1efcZe lingyungou@tongji.edu.cn"
Set-Content -Path $authKeys -Value $pubKey -Force
Write-Host "✓ authorized_keys 已创建"

# 4. 设置关键权限（这是 Windows OpenSSH 最严格的要求）
# 只有当前用户有完全控制权限
$acl = New-Object System.Security.AccessControl.FileSecurity
$currentUser = New-Object System.Security.Principal.NTAccount($env:USERNAME)
$acl.SetOwner($currentUser)
$acl.AddAccessRule((New-Object System.Security.AccessControl.FileSystemAccessRule(
    $currentUser, "FullControl", "Allow"
)))
Set-Acl $authKeys $acl
Set-Acl $sshDir $acl
Write-Host "✓ 权限已设置"

# 5. 修改 sshd_config 配置
$configPath = "$env:ProgramData\ssh\sshd_config"
$config = @"
# This is the sshd server system-wide configuration file.
Port 22
ListenAddress 0.0.0.0
ListenAddress ::

# 启用公钥认证
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys

# 允许密码认证（作为备用）
PasswordAuthentication yes

# 禁用 strict modes 检查（Windows 权限模型不同）
StrictModes no

# 其他安全设置
PermitRootLogin no
Subsystem sftp sftp-server.exe
"@

Set-Content -Path $configPath -Value $config -Force
Write-Host "✓ sshd_config 已更新"

# 6. 启动 SSH 服务
Start-Service sshd
Write-Host "✓ SSH 服务已启动"

# 7. 验证
Write-Host ""
Write-Host "=== 验证 ===" -ForegroundColor Yellow
Get-Service sshd | Select-Object Name, Status
Write-Host ""
Write-Host "authorized_keys 内容:"
Get-Content $authKeys
Write-Host ""
Write-Host "✓ 配置完成！现在可以从 MOSS 免密登录了"
Write-Host "  命令: ssh openclaw@100.90.189.121"
