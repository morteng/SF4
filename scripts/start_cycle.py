import os
from datetime import datetime
from pathlib import Path

def write_cycle_start():
    """Write current datetime to cycle_start.txt"""
    try:
        cycle_file = Path('cycle_start.txt')
        with cycle_file.open('w') as f:
            f.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        return True
    except Exception as e:
        print(f"Error writing cycle start time: {str(e)}")
        return False

if __name__ == "__main__":
    write_cycle_start()
