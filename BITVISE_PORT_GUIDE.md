# Bitvise SSH Server 端口修改指南

## 问题
22 端口被占用，需要修改 Bitvise 使用其他端口（如 2222）

## 手动修改步骤

### 方法1：通过 Bitvise Control Panel（推荐）

1. **打开 Bitvise SSH Server Control Panel**
   - 在开始菜单中找到 "Bitvise SSH Server"
   - 或者运行：`C:\Program Files\Bitvise SSH Server\BvSshServer.exe`

2. **停止服务**
   - 点击 "Stop Server" 按钮

3. **修改端口**
   - 点击 "Open advanced settings"
   - 在左侧导航栏选择 **Server**
   - 找到 **Listen port** 设置
   - 将 `22` 改为 `2222`
   - 点击 "Apply" 或 "OK"

4. **启动服务**
   - 点击 "Start Server"

### 方法2：通过注册表修改

以管理员身份运行 PowerShell：

```powershell
# 停止服务
Stop-Service BvSshServer

# 修改注册表
Set-ItemProperty -Path "HKLM:\SOFTWARE\Bitvise\Bitvise SSH Server" -Name "ListenPort" -Value 2222

# 启动服务
Start-Service BvSshServer
```

### 方法3：使用命令行工具

```powershell
# 进入 Bitvise 目录
cd "C:\Program Files\Bitvise SSH Server"

# 导出配置
.\BvSshServer.exe /exportSettings=config.txt

# 编辑 config.txt，将端口 22 改为 2222
# 然后导入配置
.\BvSshServer.exe /importSettings=config.txt
```

## 连接测试

修改完成后，使用以下命令连接：

```bash
ssh -p 2222 23242@100.73.151.49
```

## 防火墙设置

确保 Windows 防火墙允许 2222 端口：

```powershell
# 添加防火墙规则
New-NetFirewallRule -Name "Bitvise SSH 2222" -DisplayName "Bitvise SSH Server (2222)" -Direction Inbound -Protocol TCP -LocalPort 2222 -Action Allow
```

---

**推荐使用方法1（图形界面），最简单直观！**
