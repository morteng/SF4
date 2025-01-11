import sys
import os
from pathlib import Path

def get_project_root():
    """Centralized project root calculation"""
    return str(Path(__file__).resolve().parent.parent.parent)

def configure_paths(production=False):
    """Enhanced path configuration with proper error handling"""
    try:
        # Use centralized project root
        project_root = get_project_root()
        
        # Clear existing paths to avoid duplicates
        sys.path = [p for p in sys.path if not p.startswith(project_root)]
        
        # Add project root and scripts directory first
        sys.path.insert(0, project_root)
        sys.path.insert(0, str(Path(project_root) / 'scripts'))
        
        # Verify imports work
        import app
        import scripts
        
        # Add production-specific paths if needed
        if production:
            sys.path.insert(0, str(Path(project_root) / 'logs'))
            sys.path.insert(0, str(Path(project_root) / 'backups'))
            
        return True
        
        # Add project directories in correct order
        paths_to_add = [
            project_root,
            str(Path(project_root) / 'app'),
            str(Path(project_root) / 'scripts'),
            str(Path(__file__).parent),
            str(Path(project_root) / 'scripts/verification'),
            str(Path(project_root) / 'scripts/testing')
        ]
        
        # Add virtual environment site-packages
        venv_path = os.getenv('VIRTUAL_ENV')
        if venv_path:
            site_packages = str(Path(venv_path) / 'Lib' / 'site-packages')
            paths_to_add.append(site_packages)
            
        # Add paths to sys.path if not already present
        for path in paths_to_add:
            if path not in sys.path:
                sys.path.insert(0, path)
                print(f"Added to Python path: {path}")
                
        # Verify critical imports
        try:
            import app
            import scripts
            print("Successfully imported app and scripts modules")
            return True
        except ImportError as e:
            print(f"Import verification failed: {str(e)}")
            print(f"Current sys.path: {sys.path}")
            return False
        
        # Add production-specific paths if needed
        if production:
            paths_to_add.append(str(Path(project_root) / 'logs'))
            paths_to_add.append(str(Path(project_root) / 'backups'))
            
        # Add paths in reverse order to ensure correct precedence
        for path in reversed(paths_to_add):
            if path not in sys.path:
                sys.path.insert(0, path)
                
        # Verify critical imports
        try:
            import app
            import scripts
            print("Successfully imported app and scripts modules")
            return True
        except ImportError as e:
            print(f"Import verification failed: {str(e)}")
            print(f"Current sys.path: {sys.path}")
            return False
        
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
                
        # Verify critical imports
        try:
            import app
            import scripts
            print("Successfully imported app and scripts modules")
            return True
        except ImportError as e:
            print(f"Import verification failed: {str(e)}")
            print(f"Current sys.path: {sys.path}")
            return False
        
    except Exception as e:
        print(f"Path configuration failed: {str(e)}")
        return False

def verify_path_config():
    """Verify path configuration is correct"""
    try:
        # Check critical imports
        import app
        import scripts
        from scripts.verification import verify_db_connection
        from scripts.verification import verify_security
        
        # Verify paths are in correct order
        project_root = str(Path(__file__).parent.parent.parent)
        if sys.path[0] != project_root:
            print(f"Project root not first in sys.path: {sys.path[0]}")
            return False
            
        # Verify venv path if exists
        venv_path = os.getenv('VIRTUAL_ENV')
        if venv_path:
            site_packages = str(Path(venv_path) / 'Lib' / 'site-packages')
            if site_packages not in sys.path:
                print(f"Missing site-packages: {site_packages}")
                return False
                
        return True
    except ImportError as e:
        print(f"Path verification failed: {str(e)}")
        print(f"Current sys.path: {sys.path}")
        return False

if __name__ == "__main__":
    if configure_paths():
        print("Path configuration successful")
        exit(0)
    else:
        print("Path configuration failed")
        exit(1)
