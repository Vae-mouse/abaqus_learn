# -*- coding: utf-8 -*-
"""
Remote test runner for 3DPC model on cao device.
Handles SSH connection and Abaqus execution.
"""

import subprocess
import os
import sys


# CAO device connection info
CAO_HOST = "100.73.151.49"
CAO_PORT = 2222
CAO_USER = "23242"

# Remote paths (on cao device)
REMOTE_WORK_DIR = "D:\\Abaqus3DPC_Test"
REMOTE_ABAQUS_CMD = "abq2021.bat"


def test_ssh_connection():
    """Test SSH connection to cao device."""
    print("Testing SSH connection to cao device...")
    
    try:
        result = subprocess.run(
            ["ssh", "-p", str(CAO_PORT), 
             "%s@%s" % (CAO_USER, CAO_HOST),
             "echo", "Connection successful"],
            capture_output=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("✓ SSH connection successful")
            return True
        else:
            print("✗ SSH connection failed")
            print("Error: %s" % result.stderr.decode('utf-8', errors='replace'))
            return False
            
    except Exception as e:
        print("✗ SSH connection error: %s" % str(e))
        return False


def copy_files_to_remote(local_dir, remote_dir):
    """Copy project files to remote device."""
    print("\nCopying files to cao device...")
    
    # Create remote directory
    subprocess.run(
        ["ssh", "-p", str(CAO_PORT),
         "%s@%s" % (CAO_USER, CAO_HOST),
         "mkdir", "-p", remote_dir],
        capture_output=True
    )
    
    # Copy files using scp
    result = subprocess.run(
        ["scp", "-P", str(CAO_PORT), "-r",
         local_dir + "/*",
         "%s@%s:%s" % (CAO_USER, CAO_HOST, remote_dir)],
        capture_output=True
    )
    
    if result.returncode == 0:
        print("✓ Files copied successfully")
        return True
    else:
        print("✗ File copy failed")
        print("Error: %s" % result.stderr.decode('utf-8', errors='replace'))
        return False


def run_abaqus_on_remote(script_name="main.py"):
    """Run Abaqus script on cao device."""
    print("\nRunning Abaqus on cao device...")
    
    # Build remote command
    remote_cmd = 'cd /d %s && %s cae noGUI=%s' % (
        REMOTE_WORK_DIR, REMOTE_ABAQUS_CMD, script_name
    )
    
    result = subprocess.run(
        ["ssh", "-p", str(CAO_PORT),
         "%s@%s" % (CAO_USER, CAO_HOST),
         remote_cmd],
        capture_output=True,
        timeout=300  # 5 minute timeout
    )
    
    stdout = result.stdout.decode('utf-8', errors='replace')
    stderr = result.stderr.decode('utf-8', errors='replace')
    
    print("\n--- Abaqus Output ---")
    print(stdout)
    
    if stderr:
        print("\n--- Errors ---")
        print(stderr)
    
    if result.returncode == 0:
        print("\n✓ Abaqus execution successful")
    else:
        print("\n✗ Abaqus execution failed (return code: %d)" % result.returncode)
    
    return result.returncode == 0, stdout, stderr


def check_remote_results():
    """Check if results were generated on remote device."""
    print("\nChecking for results...")
    
    result = subprocess.run(
        ["ssh", "-p", str(CAO_PORT),
         "%s@%s" % (CAO_USER, CAO_HOST),
         "ls", "-la", REMOTE_WORK_DIR],
        capture_output=True
    )
    
    if result.returncode == 0:
        output = result.stdout.decode('utf-8', errors='replace')
        print("Remote directory contents:")
        print(output)
        
        # Check for .cae file
        if "3DPC_Beam.cae" in output:
            print("✓ Model file (3DPC_Beam.cae) created successfully")
            return True
        else:
            print("✗ Model file not found")
            return False
    else:
        print("✗ Failed to list remote directory")
        return False


def main():
    """Main test function."""
    print("=" * 70)
    print("3DPC Model Remote Test on cao Device")
    print("=" * 70)
    print("Target: %s:%d" % (CAO_HOST, CAO_PORT))
    print("Work dir: %s" % REMOTE_WORK_DIR)
    print("=" * 70)
    
    # Step 1: Test SSH connection
    if not test_ssh_connection():
        print("\n✗ Cannot proceed without SSH connection")
        return False
    
    # Step 2: Copy files
    local_project_dir = os.path.dirname(os.path.abspath(__file__))
    if not copy_files_to_remote(local_project_dir, REMOTE_WORK_DIR):
        print("\n✗ Cannot proceed without file copy")
        return False
    
    # Step 3: Run Abaqus
    success, stdout, stderr = run_abaqus_on_remote("main.py")
    
    # Step 4: Check results
    if success:
        check_remote_results()
    
    print("\n" + "=" * 70)
    if success:
        print("Test completed successfully!")
    else:
        print("Test failed. Check output above for details.")
    print("=" * 70)
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
