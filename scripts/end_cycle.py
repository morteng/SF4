import os
import sys
from datetime import datetime
from pathlib import Path

def calculate_cycle_time(log: bool = False):
    """Calculate time since cycle start and print/log result"""
    try:
        # Get absolute path to scripts directory
        scripts_dir = Path(__file__).resolve().parent
        cycle_file = scripts_dir / 'cycle_start.txt'
        
        # Generate cycle summary
        summary = f"""
        Cycle Summary:
        - Version: 1.2.7
        - Tests Run: 10
        - Tests Passed: 8
        - Tests Failed: 2
        - Coverage: 42%
        - Issues Resolved: 6
        - New Features: 3
        """
        
        if not cycle_file.exists():
            print("Error: cycle_start.txt not found. Did you start a cycle?")
            return False
            
        # Read timestamp with error handling
        try:
            with cycle_file.open('r') as f:
                start_time_str = f.read().strip()
                start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')
        except (IOError, ValueError) as e:
            print(f"Error reading cycle file: {str(e)}")
            return False
            
        duration = datetime.now() - start_time
        result = f"Cycle ends, time to complete: {str(duration)}"
        
        # Log if requested
        if log:
            log_file = scripts_dir / 'cycle_logs.txt'
            try:
                with log_file.open('a') as f:
                    f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {result}\n")
            except IOError as e:
                print(f"Error writing to log file: {str(e)}")
                
        print(result)
        return True
        
    except Exception as e:
        print(f"Error in calculate_cycle_time: {str(e)}")
        return False

if __name__ == "__main__":
    if not calculate_cycle_time():
        sys.exit(1)
