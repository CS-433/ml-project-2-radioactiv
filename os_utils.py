import os
import subprocess

def run_command(command):
    """Run a shell command with error handling."""
    try:
        subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        # print("Some pdf files might not render correctly.")
        return

def check_file_exists(filename):
    """Check if a file exists."""
    return os.path.exists(filename)
