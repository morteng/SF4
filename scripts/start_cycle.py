import os
import sys
from datetime import datetime
from pathlib import Path

def write_cycle_start():
    """Write current datetime to cycle_start.txt"""
    try:
        # Get absolute path to INSTANCE directory
        base_dir = Path(__file__).resolve().parent.parent  # Go up one level
        instance_dir = base_dir / 'instance'
        
        # Create instance directory if it doesn't exist
        instance_dir.mkdir(exist_ok=True)
        
        cycle_file = instance_dir / 'cycle_start.txt'
        
        # Write timestamp with error handling
        try:
            with cycle_file.open('w') as f:
                f.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            print(f"Cycle started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            return True
        except IOError as e:
            print(f"Error writing to cycle file: {str(e)}")
            return False
            
    except Exception as e:
        print(f"Error in write_cycle_start: {str(e)}")
        return False

if __name__ == "__main__":
    if not write_cycle_start():
        sys.exit(1)
