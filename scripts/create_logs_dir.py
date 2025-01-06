import os
from pathlib import Path

def create_logs_directory():
    """Create the required logs directory structure"""
    try:
        # Create main logs directory
        logs_dir = Path('logs')
        logs_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (logs_dir / 'app').mkdir(exist_ok=True)
        (logs_dir / 'tests').mkdir(exist_ok=True)
        (logs_dir / 'bots').mkdir(exist_ok=True)
        
        print("Logs directory structure created successfully")
        return True
    except Exception as e:
        print(f"Error creating logs directory: {str(e)}")
        return False

if __name__ == "__main__":
    create_logs_directory()
