import sys
import os
from pathlib import Path

def get_project_root():
    """Centralized project root calculation"""
    current_path = Path(__file__).resolve()

    # Traverse up to find the project root (SF4 directory)
    while current_path.name != 'SF4' and current_path.parent != current_path:
        current_path = current_path.parent

    if current_path.name != 'SF4':
        raise RuntimeError("Could not find project root directory (SF4)")

    return str(current_path)

def configure_paths(production=False):
    # Add scripts directory explicitly
    scripts_dir = str(Path(__file__).parent)
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    """Enhanced path configuration with proper error handling"""
    try:
        project_root = get_project_root()

        # Clear existing project paths from sys.path to avoid duplicates
        sys.path = [p for p in sys.path if not p.startswith(project_root)]

        # Define paths to add
        paths_to_add = [
            project_root,
            str(Path(project_root) / 'app'),
            str(Path(project_root) / 'scripts'),
            str(Path(__file__).parent),
            str(Path(project_root) / 'scripts/verification'),
            str(Path(project_root) / 'scripts/testing'),
            str(Path(project_root) / 'scripts/startup')
        ]

        # Add production-specific paths
        if production:
            paths_to_add.extend([
                str(Path(project_root) / 'logs'),
                str(Path(project_root) / 'backups')
            ])

        # Add virtual environment site-packages if available
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
        except ImportError as e:
            print(f"Import verification failed: {str(e)}")
            print(f"Current sys.path: {sys.path}")
            return False

        return True

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

        # Verify project root is first in sys.path
        project_root = get_project_root()
        if sys.path[0] != project_root:
            print(f"Project root not first in sys.path: {sys.path[0]}")
            return False

        # Verify virtual environment path
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
