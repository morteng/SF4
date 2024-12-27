import importlib
import pytest
from requirements.parser import RequirementsParser

def test_flask_limiter_installed():
    """Verify flask-limiter is installed and importable"""
    flask_limiter = importlib.import_module("flask_limiter")
    assert flask_limiter is not None

def test_all_requirements_installed():
    """Verify all packages in requirements.txt are installed"""
    with open("requirements.txt") as f:
        parser = RequirementsParser()
        requirements = parser.parse(f)
    
    for req in requirements:
        try:
            importlib.import_module(req.name)
        except ImportError:
            pytest.fail(f"Required package {req.name} is not installed")
