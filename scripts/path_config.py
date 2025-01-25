import sys
import os
from pathlib import Path

def get_project_root():
    """Improved Windows-compatible root detection"""
    markers = ['SF4', 'requirements.txt', 'app', 'scripts']
    current_path = Path(__file__).resolve()
    
    for _ in range(5):  # Limit search depth
        if any((current_path / m).exists() for m in markers):
            return str(current_path)
        current_path = current_path.parent
    
    raise RuntimeError(f"Project root not found. Checked: {markers}")


def configure_paths(production=False, verify=False):
    """Enhanced path configuration with proper error handling."""
    try:
        import platform
        project_root = get_project_root()
        
        # Windows path normalization
        if platform.system() == 'Windows':
            project_root = project_root.replace('\\', '/')

        # Clear existing project paths from sys.path to avoid duplicates.
        sys.path = [p for p in sys.path if not p.startswith(project_root)]

        # Define base paths to add.
        paths_to_add = [
            project_root,
            str(Path(project_root) / 'app'),
            str(Path(project_root) / 'scripts'),
            str(Path(__file__).parent),
            str(Path(project_root) / 'scripts/verification'),
            str(Path(project_root) / 'scripts/testing'),
            str(Path(project_root) / 'scripts/startup'),
            str(Path(project_root) / 'instance'),
        ]

        # Add production-specific paths if needed.
        if production:
            paths_to_add.extend([
                str(Path(project_root) / 'logs'),
                str(Path(project_root) / 'backups'),
            ])

        # Add virtual environment paths with explicit site-packages
        venv_path = os.path.join(project_root, '.venv')
        site_packages = os.path.join(venv_path, 'Lib', 'site-packages')
        if os.path.exists(site_packages):
            paths_to_add.append(site_packages)
            print(f"Added virtualenv site-packages: {site_packages}")

        # Insert paths into sys.path if not already present.
        # Ensure project root is first
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
            print(f"Added to Python path: {project_root}")
        for path in paths_to_add:
            if path != project_root and path not in sys.path:
                sys.path.insert(1, path)
                print(f"Added to Python path: {path}")

        # Quick import verification.
        try:
            import app
            import scripts
            print("Successfully imported app and scripts modules.")
        except ImportError as e:
            print(f"Import verification failed: {str(e)}")
            print(f"Current sys.path: {sys.path}")
            return False
        
        if verify:
            if not verify_path_config():
                print("Path verification failed")
                return False

        return True

    except Exception as e:
        print(f"Path configuration failed: {str(e)}")
        return False


def verify_path_config():
    """Verify path configuration is correct."""
    try:
        # Check critical imports.
        import app
        import scripts
        from scripts.verification import verify_db_connection
        from scripts.verification import verify_security
        from scripts.verification import verify_test_coverage

        # Ensure project root is first in sys.path.
        project_root = get_project_root()
        if sys.path[0] != project_root:
            print(f"Project root not first in sys.path, fixing that. Current first: {sys.path[0]}")
            sys.path.insert(0, project_root)

        # Check that site-packages from virtualenv is present if applicable.
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
    # Configure paths, then verify
    if configure_paths():
        if verify_path_config():
            print("Path configuration and verification successful.")
            exit(0)
        else:
            print("Path verification failed.")
            exit(1)
    else:
        print("Path configuration failed.")
        exit(1)
