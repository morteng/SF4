import subprocess
import pytest

def pytest_sessionstart(session):
    """Run dependency verification before test session starts"""
    try:
        subprocess.check_call(["pip", "install", "-r", "requirements.txt"])
    except subprocess.CalledProcessError:
        pytest.exit("Failed to install dependencies - aborting test session")
