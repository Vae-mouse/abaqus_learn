# Abaqus WSL 调用指南

## 核心方法：通过 PowerShell 调用

WSL 无法直接执行 Windows 批处理文件（`.bat`），因为 `cmd.exe` 在 UNC 路径下无法识别 WSL 挂载的 Windows 程序。解决方案是使用 **PowerShell**。

### 调用代码模板

```python
import subprocess
from pathlib import Path

def run_abaqus_script(script_path: str, working_dir: str = "D:\\temp_abaqus_test"):
    """
    在 WSL 中调用 Windows Abaqus 运行 Python 脚本
    
    Args:
        script_path: Abaqus Python 脚本的 Windows 路径 (如 "D:\\temp\\myscript.py")
        working_dir: 工作目录的 Windows 路径
    """
    
    # PowerShell 命令
    ps_command = f'''
    $abqPath = "D:\\Program Files\\SIMULIA\\Commands\\abq2026.bat"
    $scriptPath = "{script_path}"
    Set-Location -Path "{working_dir}"
    & $abqPath cae noGUI=$scriptPath
    '''
    
    # 执行 PowerShell
    result = subprocess.run(
        ["/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe", 
         "-Command", ps_command],
        capture_output=True,
        timeout=180
    )
    
    # 解码输出（处理中文）
    stdout = result.stdout.decode('utf-8', errors='replace')
    stderr = result.stderr.decode('utf-8', errors='replace')
    
    return result.returncode, stdout, stderr
```

### 关键要点

| 问题 | 解决方案 |
|------|----------|
| `cmd.exe` 找不到程序 | 改用 PowerShell |
| UNC 路径问题 | 在 PowerShell 中先用 `Set-Location` 切换目录 |
| 空格路径问题 | PowerShell 变量存储路径，避免转义问题 |
| 中文乱码 | 使用 `utf-8` 解码，配合 `errors='replace'` |

### 完整示例

```python
# 1. 准备脚本（复制到 D 盘，避免 UNC 路径）
import shutil
shutil.copy("my_script.py", "/mnt/d/temp_abaqus_test/my_script.py")

# 2. 调用 Abaqus
returncode, stdout, stderr = run_abaqus_script(
    script_path="D:\\temp_abaqus_test\\my_script.py",
    working_dir="D:\\temp_abaqus_test"
)

# 3. 检查结果
if returncode == 0:
    print("✓ Abaqus 运行成功")
else:
    print(f"✗ 失败，返回码: {returncode}")
    print(stderr)
```

### Abaqus 命令参考

```bash
# CAE 无 GUI 运行脚本
abq2026.bat cae noGUI=script.py

# 提交作业
abq2026.bat job=job_name inp=input.inp

# 查看结果
abq2026.bat viewer odb=results.odb
```

### 路径转换

```python
# WSL 路径 -> Windows 路径
wsl_path = "/mnt/d/temp_abaqus_test/script.py"
win_path = "D:\\temp_abaqus_test\\script.py"

# 或者使用 wslpath（但 PowerShell 中不需要）
import subprocess
result = subprocess.run(["wslpath", "-w", wsl_path], capture_output=True, text=True)
win_path = result.stdout.strip()
```

---

**记住：以后调用 Windows Abaqus 都用 PowerShell 方式！** 🤖
