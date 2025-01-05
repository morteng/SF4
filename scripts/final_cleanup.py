import os
import shutil
from pathlib import Path

def cleanup():
    """Perform final cleanup tasks before deployment"""
    # Remove temporary files
    temp_dirs = [
        'tmp',
        'build',
        'dist',
        '__pycache__'
    ]
    
    for temp_dir in temp_dirs:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            print(f"Removed {temp_dir} directory")

    # Remove .pyc files
    for pyc_file in Path('.').rglob('*.pyc'):
        pyc_file.unlink()
        print(f"Removed {pyc_file}")

    # Remove empty directories
    for root, dirs, files in os.walk('.', topdown=False):
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            try:
                if not os.listdir(dir_path):
                    os.rmdir(dir_path)
                    print(f"Removed empty directory: {dir_path}")
            except OSError:
                pass

    print("Cleanup completed successfully")

if __name__ == '__main__':
    cleanup()
