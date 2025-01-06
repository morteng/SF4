import logging
from pathlib import Path

def validate_version_file():
    """Validate version file integrity"""
    try:
        version_file = Path('scripts/version.py')
        if not version_file.exists():
            logging.error("Version file not found")
            return False
            
        with version_file.open('r') as f:
            content = f.read()
            return ('__version__' in content and 
                    'validate_version' in content and
                    'bump_version' in content)
    except Exception as e:
        logging.error(f"Version file validation error: {str(e)}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if validate_version_file():
        print("Version file validation passed")
        exit(0)
    else:
        print("Version file validation failed")
        exit(1)
