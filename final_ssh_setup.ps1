# Windows SSH 免密登录最终配置
# 在 cao 上以管理员 PowerShell 运行

Write-Host "=== 最终 SSH 配置修复 ===" -ForegroundColor Green

# 1. 确保 authorized_keys 文件存在且内容正确
$authKeys = "C:\Users\openclaw\.ssh\authorized_keys"
$sshDir = "C:\Users\openclaw\.ssh"
$pubKey = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIFDXZqKPkoiTdWmi7/VOPVmxUuow2O9UnPAivZ1efcZe lingyungou@tongji.edu.cn"

# 创建目录
if (!(Test-Path $sshDir)) {
    New-Item -ItemType Directory -Path $sshDir -Force
    Write-Host "✓ 创建 .ssh 目录" -ForegroundColor Green
}

# 创建/更新文件
Set-Content -Path $authKeys -Value $pubKey -Force
Write-Host "✓ 更新 authorized_keys" -ForegroundColor Green

# 2. 设置权限
icacls $authKeys /inheritance:r 2>$null
icacls $authKeys /grant "openclaw:F" 2>$null
Write-Host "✓ 设置文件权限" -ForegroundColor Green

# 3. 修改 sshd_config - 添加 AllowUsers
$configPath = "$env:ProgramData\ssh\sshd_config"
$config = @"
Port 22
ListenAddress 0.0.0.0
ListenAddress ::

# 允许 openclaw 用户访问
AllowUsers openclaw

# 认证配置
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys
PasswordAuthentication yes

# 禁用严格模式检查
StrictModes no

# SFTP 子系统
Subsystem sftp sftp-server.exe
"@

Set-Content -Path $configPath -Value $config -Force
Write-Host "✓ 更新 sshd_config（添加 AllowUsers openclaw）" -ForegroundColor Green

# 4. 重启 SSH 服务
Restart-Service sshd
Write-Host "✓ SSH 服务已重启" -ForegroundColor Green

# 5. 验证
Write-Host "`n=== 验证配置 ===" -ForegroundColor Yellow
Write-Host "authorized_keys 内容:"
Get-Content $authKeys
Write-Host "`n文件权限:"
icacls $authKeys
Write-Host "`nSSH 配置:"
Get-Content $configPath | Select-String "AllowUsers|Pubkey|AuthorizedKeysFile"

Write-Host "`n✓ 配置完成！请测试免密登录" -ForegroundColor Green
Write-Host "  ssh openclaw@100.90.189.121" -ForegroundColor Cyan
