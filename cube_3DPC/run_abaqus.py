# -*- coding: utf-8 -*-
"""
UV Runner for 3DPC Cube Compression Test
Allows running the workflow from UV terminal
Python 2.7 compatible for Abaqus 2021

Usage:
    uv run python run_abaqus.py [--submit]
"""

import os
import sys
import subprocess
import argparse


def get_abaqus_command():
    """
    Get Abaqus command path
    
    Returns:
        str: Path to abaqus executable
    """
    # Try common Abaqus installation paths
    possible_paths = [
        r"D:\abaqus2021\SIMULIA\Commands\abq2021.bat",
        r"C:\SIMULIA\Commands\abq2021.bat",
        r"C:\Program Files\SIMULIA\Commands\abq2021.bat",
        "abq2021",  # If in PATH
        "abaqus",   # Generic
    ]
    
    for path in possible_paths:
        if os.path.exists(path) or path in ["abq2021", "abaqus"]:
            return path
    
    # Default
    return "abq2021"


def run_in_abaqus_cae(script_path, no_gui=False):
    """
    Run script in Abaqus CAE
    
    Args:
        script_path: Path to Python script
        no_gui: Whether to run without GUI
        
    Returns:
        int: Return code
    """
    abaqus_cmd = get_abaqus_command()
    
    if no_gui:
        cmd = [abaqus_cmd, "cae", "noGUI=%s" % script_path]
    else:
        cmd = [abaqus_cmd, "cae", "script=%s" % script_path]
    
    print("Running: %s" % " ".join(cmd))
    
    try:
        result = subprocess.call(cmd, shell=True)
        return result
    except Exception as e:
        print("Error running Abaqus: %s" % str(e))
        return 1


def run_job(job_name, work_dir):
    """
    Submit Abaqus job from command line
    
    Args:
        job_name: Name of the job
        work_dir: Working directory
        
    Returns:
        int: Return code
    """
    abaqus_cmd = get_abaqus_command()
    
    cmd = [abaqus_cmd, "job=%s" % job_name]
    
    print("Submitting job: %s" % " ".join(cmd))
    print("Working directory: %s" % work_dir)
    
    try:
        # Change to work directory
        original_dir = os.getcwd()
        os.chdir(work_dir)
        
        result = subprocess.call(cmd, shell=True)
        
        # Return to original directory
        os.chdir(original_dir)
        
        return result
    except Exception as e:
        print("Error submitting job: %s" % str(e))
        return 1


def main():
    """
    Main entry point
    """
    parser = argparse.ArgumentParser(
        description='Run 3DPC cube compression test in Abaqus'
    )
    parser.add_argument(
        '--no-gui',
        action='store_true',
        help='Run without GUI (noGUI mode)'
    )
    parser.add_argument(
        '--submit',
        action='store_true',
        help='Submit job after creating model'
    )
    parser.add_argument(
        '--job-only',
        action='store_true',
        help='Only submit existing job, do not create model'
    )
    
    args = parser.parse_args()
    
    # Get script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    main_script = os.path.join(script_dir, "main.py")
    
    # Work directory from config
    work_dir = r"C:\Users\openclaw\cube_3DPC"
    job_name = "CubeCompression_Job"
    
    print("=" * 70)
    print("3DPC Cube Compression Test - UV Runner")
    print("=" * 70)
    print("Script: %s" % main_script)
    print("Work directory: %s" % work_dir)
    print("=" * 70)
    
    if args.job_only:
        # Only submit job
        print("\nSubmitting existing job...")
        ret = run_job(job_name, work_dir)
    else:
        # Create model in Abaqus
        print("\nCreating model in Abaqus CAE...")
        ret = run_in_abaqus_cae(main_script, no_gui=args.no_gui)
        
        if ret == 0 and args.submit:
            # Submit job if requested
            print("\nSubmitting analysis job...")
            ret = run_job(job_name, work_dir)
    
    print("\n" + "=" * 70)
    if ret == 0:
        print("Success!")
    else:
        print("Completed with errors (code: %d)" % ret)
    print("=" * 70)
    
    return ret


if __name__ == "__main__":
    sys.exit(main())
