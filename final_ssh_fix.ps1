# Windows SSH 免密登录最终修复
# 在 cao 上以管理员 PowerShell 运行

# 1. 修改 sshd_config 使用绝对路径
$configPath = "$env:ProgramData\ssh\sshd_config"

# 读取当前配置
$config = Get-Content $configPath -Raw

# 替换 AuthorizedKeysFile 为绝对路径
$config = $config -replace "AuthorizedKeysFile .ssh/authorized_keys", "AuthorizedKeysFile C:/Users/openclaw/.ssh/authorized_keys"

# 写回配置
Set-Content $configPath $config -Force

Write-Host "✓ 已修改 AuthorizedKeysFile 为绝对路径" -ForegroundColor Green

# 2. 确保 StrictModes 禁用
if ($config -notmatch "StrictModes no") {
    Add-Content $configPath -Value "`nStrictModes no"
    Write-Host "✓ 已添加 StrictModes no" -ForegroundColor Green
}

# 3. 重启 SSH 服务
Restart-Service sshd
Write-Host "✓ SSH 服务已重启" -ForegroundColor Green

# 4. 验证配置
Write-Host "`n当前配置:" -ForegroundColor Yellow
Get-Content $configPath | Select-String "AuthorizedKeysFile|StrictModes|PubkeyAuthentication"

Write-Host "`n✓ 配置完成，请测试免密登录" -ForegroundColor Green
Write-Host "  ssh openclaw@100.90.189.121" -ForegroundColor Cyan
