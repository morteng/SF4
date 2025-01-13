import json

# Hardcoded path to your existing TODO file
TODO_FILE = "automation/TODO.txt"

def update_todo(test_results):
    with open(TODO_FILE, 'a') as file:
        for failure in test_results.get("failures", []):
            desc = failure.get("description")
            test_name = failure.get("test_name")
            file.write(f"- [ ] {desc} (Test failed: {test_name})\n")

if __name__ == "__main__":
    # In a real scenario, you'd parse actual test results from a JSON or something
    sample_test_results = {
        "failures": [
            {
                "test_name": "test_db_connection",
                "description": "Database connection timed out."
            },
            {
                "test_name": "test_security_headers",
                "description": "Security headers missing or incomplete."
            }
        ]
    }
    update_todo(sample_test_results)
    print("TODO file updated with new test failures.")
