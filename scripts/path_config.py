import sys
import os
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
            
        # Add scripts directory to Python path
        scripts_dir = str(Path(__file__).parent)
        if scripts_dir not in sys.path:
            sys.path.insert(0, scripts_dir)
            
        # Add venv site-packages if exists
        venv_path = os.getenv('VIRTUAL_ENV')
        if venv_path:
            site_packages = str(Path(venv_path) / 'Lib' / 'site-packages')
            if site_packages not in sys.path:
                sys.path.insert(0, site_packages)
                
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
