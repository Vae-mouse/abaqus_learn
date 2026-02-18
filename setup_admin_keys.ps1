# 使用默认 administrators_authorized_keys 路径配置免密登录
# 在 cao 上以管理员 PowerShell 运行

Write-Host "=== 配置 administrators_authorized_keys ===" -ForegroundColor Green

# 1. 创建 ProgramData\ssh 目录（如果不存在）
$sshDir = "$env:ProgramData\ssh"
if (!(Test-Path $sshDir)) {
    New-Item -ItemType Directory -Path $sshDir -Force
}

# 2. 创建 administrators_authorized_keys 文件
$adminKeys = "$sshDir\administrators_authorized_keys"
$pubKey = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIFDXZqKPkoiTdWmi7/VOPVmxUuow2O9UnPAivZ1efcZe lingyungou@tongji.edu.cn"
Set-Content -Path $adminKeys -Value $pubKey -Force
Write-Host "✓ 已创建 administrators_authorized_keys" -ForegroundColor Green

# 3. 设置严格的权限（只有 SYSTEM 和 Administrators 可以访问）
icacls $adminKeys /inheritance:r
icacls $adminKeys /grant "SYSTEM:F"
icacls $adminKeys /grant "Administrators:F"
# 移除其他所有权限
icacls $adminKeys /remove "NT AUTHORITY\Authenticated Users" 2>$null
icacls $adminKeys /remove "BUILTIN\Users" 2>$null
icacls $adminKeys /remove "$env:USERNAME" 2>$null
Write-Host "✓ 已设置权限" -ForegroundColor Green

# 4. 确保 sshd_config 使用默认配置（移除自定义的 AuthorizedKeysFile）
$configPath = "$env:ProgramData\ssh\sshd_config"
$config = Get-Content $configPath -Raw

# 如果之前修改过，恢复默认（注释掉或删除自定义的 AuthorizedKeysFile）
if ($config -match "AuthorizedKeysFile \.ssh/authorized_keys") {
    $config = $config -replace "AuthorizedKeysFile \.ssh/authorized_keys", "# AuthorizedKeysFile .ssh/authorized_keys (using default for admins)"
    Set-Content $configPath $config -Force
    Write-Host "✓ 已恢复默认配置" -ForegroundColor Green
}

# 5. 重启 SSH 服务
Restart-Service sshd
Write-Host "✓ SSH 服务已重启" -ForegroundColor Green

# 6. 验证
Write-Host "`n=== 验证 ===" -ForegroundColor Yellow
Write-Host "文件位置: $adminKeys"
Write-Host "文件内容:"
Get-Content $adminKeys
Write-Host "`n文件权限:"
icacls $adminKeys

Write-Host "`n✓ 配置完成！请测试免密登录" -ForegroundColor Green
Write-Host "  ssh openclaw@100.90.189.121" -ForegroundColor Cyan
