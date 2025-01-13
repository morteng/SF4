import json
from datetime import datetime
from pathlib import Path

METRICS_FILE = Path("automation2/logs/cycle_metrics.log")

def log_cycle_metrics(cycle_name, metrics):
    """
    Example metrics: 
        {
            "time_taken": "10 minutes",
            "tests_passed": 27,
            "tests_failed": 2,
            "coverage": 88
        }
    """
    with open(METRICS_FILE, 'a') as file:
        entry = {
            "timestamp": datetime.now().isoformat(),
            "cycle_name": cycle_name,
            "metrics": metrics
        }
        file.write(json.dumps(entry) + "\n")

if __name__ == "__main__":
    test_metrics = {
        "time_taken": "25m",
        "tests_passed": 45,
        "tests_failed": 3,
        "coverage": 89
    }
    log_cycle_metrics("Bug Fixing Cycle", test_metrics)
    print("Cycle metrics logged.")
