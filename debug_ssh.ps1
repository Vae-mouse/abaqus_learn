# Windows SSH 免密登录最终排查脚本
# 在 cao 上以管理员 PowerShell 运行

Write-Host "=== SSH 免密登录排查 ===" -ForegroundColor Green

# 1. 检查 authorized_keys 文件详细权限
Write-Host "`n1. 文件详细信息:" -ForegroundColor Yellow
$authKeys = "C:\Users\openclaw\.ssh\authorized_keys"
Get-Item $authKeys | Select-Object FullName, Length, Mode, LastWriteTime | Format-List

# 2. 检查 ACL 详细信息
Write-Host "`n2. 详细权限列表:" -ForegroundColor Yellow
$acl = Get-Acl $authKeys
$acl.Access | Format-Table IdentityReference, FileSystemRights, AccessControlType, IsInherited -AutoSize

# 3. 检查父目录权限
Write-Host "`n3. .ssh 目录权限:" -ForegroundColor Yellow
$sshDir = "C:\Users\openclaw\.ssh"
Get-Acl $sshDir | Select-Object -ExpandProperty Access | Format-Table IdentityReference, FileSystemRights -AutoSize

# 4. 检查 SSH 服务日志
Write-Host "`n4. SSH 服务日志:" -ForegroundColor Yellow
$logPath = "$env:ProgramData\ssh\logs"
if (Test-Path $logPath) {
    Get-ChildItem $logPath -Filter "*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 1 | Get-Content -Tail 20
} else {
    Write-Host "日志目录不存在"
}

# 5. 检查 sshd_config 完整内容
Write-Host "`n5. SSH 配置:" -ForegroundColor Yellow
Get-Content "$env:ProgramData\ssh\sshd_config" | Where-Object { $_ -notmatch "^#" -and $_ -notmatch "^$" }

# 6. 测试从本地使用密钥登录
Write-Host "`n6. 本地测试:" -ForegroundColor Yellow
$privateKey = "C:\Users\openclaw\.ssh\id_ed25519"
if (Test-Path $privateKey) {
    Write-Host "本地私钥存在"
} else {
    Write-Host "本地私钥不存在（这是正常的，私钥在 MOSS 上）"
}

# 7. 检查是否有其他安全软件阻止
Write-Host "`n7. Windows Defender 状态:" -ForegroundColor Yellow
Get-MpComputerStatus | Select-Object RealTimeProtectionEnabled, AntivirusEnabled | Format-List

Write-Host "`n=== 排查完成 ===" -ForegroundColor Green
Write-Host "如果以上都正确但仍需密码，尝试:" -ForegroundColor Red
Write-Host "1. 重启 SSH 服务: Restart-Service sshd"
Write-Host "2. 检查 Windows 防火墙"
Write-Host "3. 检查是否有其他安全软件"
