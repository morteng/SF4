import json
import os

COMMAND_CONFIG = "automation2/cycles/current_cycle.json"

def read_commands():
    with open(COMMAND_CONFIG, 'r') as file:
        cycle = json.load(file)
    return cycle.get("dynamic_commands", [])

def execute_commands(commands):
    for cmd in commands:
        # You might write these commands to a .txt file for your existing system to run.
        # We'll just print them here because we respect the "no direct runs in console" rule.
        print(f"/run {cmd['script']} {cmd.get('args', '')}")

if __name__ == "__main__":
    commands = read_commands()
    if commands:
        execute_commands(commands)
    else:
        print("No dynamic commands to execute.")
