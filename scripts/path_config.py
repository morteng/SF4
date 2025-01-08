import sys
from pathlib import Path

def configure_paths():
    """Configure Python paths for the project"""
    try:
        # Add project root to Python path
        project_root = str(Path(__file__).parent.parent)
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
            
        # Add app directory to Python path
        app_dir = str(Path(__file__).parent.parent / 'app')
        if app_dir not in sys.path:
            sys.path.insert(0, app_dir)
            
        return True
    except Exception as e:
        print(f"Path configuration failed: {str(e)}")
        return False

if __name__ == "__main__":
    if configure_paths():
        print("Path configuration successful")
        exit(0)
    else:
        print("Path configuration failed")
        exit(1)
