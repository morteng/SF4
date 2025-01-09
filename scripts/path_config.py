import sys
import os
from pathlib import Path

def configure_paths():
    """Configure Python paths for the project"""
    try:
        # Get project root (two levels up from this script)
        project_root = str(Path(__file__).parent.parent)
        
        # Add paths in order of priority
        paths_to_add = [
            project_root,
            str(Path(project_root) / 'app'),
            str(Path(project_root) / 'scripts'),
            str(Path(project_root) / 'tests'),
            str(Path(__file__).parent)  # Add scripts directory itself
        ]
        
        # Add venv site-packages
        venv_path = os.getenv('VIRTUAL_ENV')
        if venv_path:
            site_packages = str(Path(venv_path) / 'Lib' / 'site-packages')
            paths_to_add.append(site_packages)
        
        # Add venv site-packages if exists
        venv_path = os.getenv('VIRTUAL_ENV')
        if venv_path:
            site_packages = str(Path(venv_path) / 'Lib' / 'site-packages')
            paths_to_add.append(site_packages)
            
        # Add paths to sys.path if not already present
        for path in paths_to_add:
            if path not in sys.path:
                sys.path.insert(0, path)
                print(f"Added to Python path: {path}")
                
        # Verify app can be imported
        try:
            import app
            print("Successfully imported app module")
            return True
        except ImportError as e:
            print(f"Failed to import app module: {str(e)}")
            return False
            
    except Exception as e:
        print(f"Path configuration failed: {str(e)}")
        return False

def verify_path_config():
    """Verify path configuration is correct"""
    try:
        # Check if app can be imported
        import app
        # Check if scripts can be imported
        import scripts
        return True
    except ImportError as e:
        print(f"Path verification failed: {str(e)}")
        return False

if __name__ == "__main__":
    if configure_paths():
        print("Path configuration successful")
        exit(0)
    else:
        print("Path configuration failed")
        exit(1)
