# 在 cao 设备上配置免密登录的完整步骤
# 当你已经通过 SSH 连接到 cao 后，依次运行以下命令：

# 步骤 1: 创建 .ssh 目录
mkdir "$env:USERPROFILE\.ssh" -Force

# 步骤 2: 写入公钥到 authorized_keys
$pubKey = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIFDXZqKPkoiTdWmi7/VOPVmxUuow2O9UnPAivZ1efcZe lingyungou@tongji.edu.cn"
$authKeys = "$env:USERPROFILE\.ssh\authorized_keys"
Set-Content -Path $authKeys -Value $pubKey -Force

# 步骤 3: 设置正确的权限（Windows OpenSSH 要求非常严格）
# 移除继承权限
icacls $authKeys /inheritance:r
# 只给当前用户完全控制权限
icacls $authKeys /grant "$env:USERNAME`:F"
# 移除其他所有用户的权限
icacls $authKeys /remove "NT AUTHORITY\Authenticated Users" 2>$null
icacls $authKeys /remove "BUILTIN\Users" 2>$null

# 步骤 4: 同样设置 .ssh 目录权限
$sshDir = "$env:USERPROFILE\.ssh"
icacls $sshDir /inheritance:r
icacls $sshDir /grant "$env:USERNAME`:F"

# 步骤 5: 验证文件内容
Write-Host "=== authorized_keys 内容 ===" -ForegroundColor Green
Get-Content $authKeys

Write-Host ""
Write-Host "=== 文件权限 ===" -ForegroundColor Green
icacls $authKeys

Write-Host ""
Write-Host "✓ 配置完成！" -ForegroundColor Green
Write-Host "现在可以从 MOSS 免密登录了："
Write-Host "  ssh openclaw@100.90.189.121"
