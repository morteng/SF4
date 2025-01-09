import sys
import os
from pathlib import Path

def configure_paths():
    """Enhanced path configuration with proper error handling"""
    try:
        # Get project root (three levels up from this script)
        project_root = str(Path(__file__).parent.parent.parent)
        
        # Add project directories in correct order
        paths_to_add = [
            project_root,
            str(Path(project_root) / 'app'),
            str(Path(project_root) / 'scripts'),
            str(Path(project_root) / 'tests'),
            str(Path(__file__).parent)
        ]
        
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
        
        # Add project root to sys.path
        import sys
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
            
        # Configure logging
        import logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        
        # Add project root to sys.path if not present
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
            
        # Add scripts directory
        scripts_dir = str(Path(__file__).parent)
        if scripts_dir not in sys.path:
            sys.path.insert(0, scripts_dir)
        
        # Add venv site-packages explicitly
        venv_path = os.getenv('VIRTUAL_ENV')
        if venv_path:
            site_packages = str(Path(venv_path) / 'Lib' / 'site-packages')
            if site_packages not in sys.path:
                sys.path.insert(0, site_packages)
        
        # Add project directories in correct order
        paths_to_add = [
            project_root,
            str(Path(project_root) / 'app'),
            str(Path(project_root) / 'scripts'),
            str(Path(project_root) / 'tests'),
            str(Path(__file__).parent)
        ]
        
        # Add paths to sys.path if not already present
        for path in paths_to_add:
            if path not in sys.path:
                sys.path.insert(0, path)
                print(f"Added to Python path: {path}")
                
        # Add project directories
        paths_to_add = [
            project_root,
            str(Path(project_root) / 'app'),
            str(Path(project_root) / 'scripts'),
            str(Path(project_root) / 'tests'),
            str(Path(__file__).parent)
        ]
        
        # Add paths in order of priority
        paths_to_add = [
            project_root,
            str(Path(project_root) / 'app'),
            str(Path(project_root) / 'scripts'),
            str(Path(project_root) / 'tests'),
            str(Path(__file__).parent),  # Add scripts directory itself
            str(Path(project_root) / '.venv' / 'Lib' / 'site-packages')
        ]
        
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
