import os
import shutil
from pathlib import Path
from datetime import datetime

def ensure_dir(path):
    Path(path).mkdir(parents=True, exist_ok=True)

def get_timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def save_file(content, filename, directory="."):
    ensure_dir(directory)
    filepath = Path(directory) / filename
    with open(filepath, 'w') as f:
        f.write(content)
    return filepath

def move_file(src, dst):
    shutil.move(src, dst)

def delete_file(path):
    if Path(path).exists():
        os.remove(path)