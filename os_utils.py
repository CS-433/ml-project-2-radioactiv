import os
import subprocess

def run_command(command):
    """Run a shell command with error handling."""
    try:
        subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        return

def check_file_exists(filename):
    """Check if a file exists."""
    return os.path.exists(filename)

def create_folder(folder_name):
    """Create a folder if it doesn't exist."""
    os.makedirs(folder_name, exist_ok=True)

def get_subfolders(folder):
    """Get the subfolders of a folder."""
    if not os.path.exists(folder):
        raise FileNotFoundError(f"The folder '{folder}' does not exist.")
    
    subfolders = next(os.walk(folder), (None, [], []))[1]
    return subfolders
