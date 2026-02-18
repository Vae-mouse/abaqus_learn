"""
Abaqus 自动化控制模块
通过 PowerShell 在 WSL 中控制 Windows Abaqus
"""
import subprocess
import time
from pathlib import Path

# Windows 本地工作目录（避免 WSL 权限问题）
WINDOWS_WORK_DIR = "C:\\Users\\23242\\Documents\\AbaqusWorkspace"
ABAQUS_COMMAND = "D:\\Program Files\\SIMULIA\\Commands\\abq2026.bat"


def run_powershell_command(command: str, timeout: int = 60) -> tuple:
    """
    在 PowerShell 中执行命令
    
    Returns:
        (returncode, stdout, stderr)
    """
    ps_path = "/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"
    
    result = subprocess.run(
        [ps_path, "-Command", command],
        capture_output=True,
        timeout=timeout
    )
    
    try:
        stdout = result.stdout.decode('utf-8', errors='replace')
        stderr = result.stderr.decode('utf-8', errors='replace')
    except:
        stdout = str(result.stdout)
        stderr = str(result.stderr)
    
    return result.returncode, stdout, stderr


def ensure_workspace():
    """确保 Windows 工作目录存在"""
    cmd = f'''
    $dir = "{WINDOWS_WORK_DIR}"
    if (!(Test-Path $dir)) {{
        New-Item -ItemType Directory -Force -Path $dir | Out-Null
        Write-Host "Created: $dir"
    }} else {{
        Write-Host "Exists: $dir"
    }}
    '''
    return run_powershell_command(cmd)


def copy_to_workspace(source_file: str, filename: str = None) -> str:
    """
    将文件复制到 Windows 工作目录
    
    Args:
        source_file: WSL 路径
        filename: 目标文件名（可选）
    
    Returns:
        Windows 目标路径
    """
    if filename is None:
        filename = Path(source_file).name
    
    dest_path = f"{WINDOWS_WORK_DIR}\\{filename}"
    
    cmd = f'Copy-Item -Path "{source_file}" -Destination "{dest_path}" -Force'
    run_powershell_command(cmd)
    
    return dest_path


def open_cae_file(cae_path: str = None) -> bool:
    """
    用 Abaqus CAE GUI 打开 .cae 文件
    
    Args:
        cae_path: CAE 文件的 Windows 路径或 WSL 路径，如果为 None 则只启动 CAE
    """
    ensure_workspace()
    
    if cae_path:
        # 检查是否是 WSL 路径 (/mnt/d/...)
        if cae_path.startswith("/mnt/"):
            # 从 WSL 路径复制
            dest = copy_to_workspace(cae_path)
            cae_path = dest
        elif not cae_path.startswith(WINDOWS_WORK_DIR):
            # 其他 Windows 路径，复制到工作目录
            dest = f"{WINDOWS_WORK_DIR}\\{Path(cae_path).name}"
            cmd = f'Copy-Item -Path "{cae_path}" -Destination "{dest}" -Force'
            run_powershell_command(cmd)
            cae_path = dest
        
        args = f'cae "{cae_path}"'
    else:
        args = "cae"
    
    cmd = f'''
    $abq = "{ABAQUS_COMMAND}"
    Set-Location -Path "{WINDOWS_WORK_DIR}"
    Start-Process -FilePath $abq -ArgumentList "{args}"
    Write-Host "Abaqus CAE started"
    '''
    
    returncode, stdout, stderr = run_powershell_command(cmd, timeout=10)
    
    if returncode == 0:
        print(f"✓ Abaqus CAE 已启动")
        if cae_path:
            print(f"  文件: {cae_path}")
        return True
    else:
        print(f"✗ 启动失败: {stderr}")
        return False


def run_script(script_path: str, no_gui: bool = True) -> tuple:
    """
    在 Abaqus 中运行 Python 脚本
    
    Args:
        script_path: Python 脚本的 WSL 路径
        no_gui: 是否使用无 GUI 模式
    
    Returns:
        (success, stdout, stderr)
    """
    ensure_workspace()
    
    # 复制脚本到 Windows 目录
    dest_path = copy_to_workspace(script_path)
    
    mode = "noGUI" if no_gui else "script"
    
    cmd = f'''
    $abq = "{ABAQUS_COMMAND}"
    $script = "{dest_path}"
    Set-Location -Path "{WINDOWS_WORK_DIR}"
    & $abq cae {mode}=$script 2>&1
    '''
    
    print(f"运行脚本: {Path(script_path).name}")
    returncode, stdout, stderr = run_powershell_command(cmd, timeout=300)
    
    success = returncode == 0 or "成功" in stdout
    return success, stdout, stderr


def check_abaqus_status():
    """检查 Abaqus 进程状态"""
    cmd = '''
    $processes = Get-Process | Where-Object { 
        $_.ProcessName -match "ABQ|abaqus|SMALauncher|CAE" 
    } | Select-Object ProcessName, Id, MainWindowTitle, StartTime
    
    if ($processes) {
        Write-Host "=== Abaqus 进程 ==="
        $processes | Format-Table -AutoSize
    } else {
        Write-Host "没有 Abaqus 进程在运行"
    }
    '''
    return run_powershell_command(cmd)


def kill_abaqus():
    """强制关闭所有 Abaqus 进程"""
    cmd = '''
    Get-Process | Where-Object { 
        $_.ProcessName -match "ABQ|abaqus|SMALauncher|CAE" 
    } | Stop-Process -Force
    Write-Host "所有 Abaqus 进程已终止"
    '''
    return run_powershell_command(cmd)


if __name__ == "__main__":
    # 测试
    print("Abaqus 自动化控制模块")
    print("=" * 50)
    
    # 检查状态
    print("\n检查 Abaqus 状态...")
    check_abaqus_status()
    
    # 打开测试模型
    print("\n打开测试模型...")
    open_cae_file()
