import subprocess

def run_tests():
    try:
        subprocess.run(['pytest', 'tests/'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Tests failed with error: {e}")
        return False
    return True
