import os
import subprocess
import sys


def run_command(command):
    """Run a shell command with error handling."""
    try:
        subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {command}")
        print(e.stderr)
        sys.exit(1)


def check_file_exists(filename):
    """Check if a file exists."""
    return os.path.exists(filename)
