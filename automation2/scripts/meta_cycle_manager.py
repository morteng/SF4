import json
from pathlib import Path
from datetime import datetime

META_CYCLE_FILE = Path("automation2/cycles/meta_cycle.json")
CURRENT_CYCLE_FILE = Path("automation2/cycles/current_cycle.json")
METRICS_LOG = Path("automation2/logs/cycle_metrics.log")

def load_meta_cycle():
    with open(META_CYCLE_FILE, 'r') as file:
        return json.load(file)

def save_current_cycle(cycle_data):
    with open(CURRENT_CYCLE_FILE, 'w') as file:
        json.dump(cycle_data, file, indent=4)

def select_next_cycle(cycles):
    # Sort by descending priority
    sorted_cycles = sorted(cycles, key=lambda c: c["priority"], reverse=True)
    for c in sorted_cycles:
        if not c.get("completed"):
            return c
    return None

def log_meta_cycle_selection(cycle_name):
    with open(METRICS_LOG, 'a') as log_file:
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": "SELECT_CYCLE",
            "cycle_selected": cycle_name
        }
        log_file.write(json.dumps(log_entry) + "\n")

def main():
    meta_cycle = load_meta_cycle()
    cycles = meta_cycle.get("cycles", [])

    next_cycle = select_next_cycle(cycles)
    if next_cycle:
        save_current_cycle(next_cycle)
        log_meta_cycle_selection(next_cycle["name"])
        print(f"Next cycle selected: {next_cycle['name']}")
    else:
        print("All cycles are marked completed. Nice job, you overachiever!")

if __name__ == "__main__":
    main()
