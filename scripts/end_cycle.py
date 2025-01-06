from datetime import datetime
from pathlib import Path

def calculate_cycle_time():
    """Calculate time since cycle start and print result"""
    try:
        scripts_dir = Path(__file__).parent
        cycle_file = scripts_dir / 'cycle_start.txt'
        
        if not cycle_file.exists():
            print("Cycle start file not found")
            return False
            
        with cycle_file.open('r') as f:
            start_time = datetime.strptime(f.read().strip(), '%Y-%m-%d %H:%M:%S')
            
        duration = datetime.now() - start_time
        print(f"Cycle ends, time to complete: {str(duration)}")
        return True
    except Exception as e:
        print(f"Error calculating cycle time: {str(e)}")
        return False

if __name__ == "__main__":
    calculate_cycle_time()
