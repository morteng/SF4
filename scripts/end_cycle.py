from datetime import datetime
from pathlib import Path

def calculate_cycle_time(log: bool = False):
    """Calculate time since cycle start and print/log result"""
    try:
        scripts_dir = Path(__file__).parent
        cycle_file = scripts_dir / 'cycle_start.txt'
        
        if not cycle_file.exists():
            print("Cycle start file not found")
            return False
            
        with cycle_file.open('r') as f:
            start_time = datetime.strptime(f.read().strip(), '%Y-%m-%d %H:%M:%S')
            
        duration = datetime.now() - start_time
        result = f"Cycle ends, time to complete: {str(duration)}"
        
        if log:
            log_file = scripts_dir / 'cycle_logs.txt'
            with log_file.open('a') as f:
                f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {result}\n")
                
        print(result)
        return True
    except Exception as e:
        print(f"Error calculating cycle time: {str(e)}")
        return False

if __name__ == "__main__":
    calculate_cycle_time()
