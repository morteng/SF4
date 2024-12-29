import importlib
import pytest
import subprocess
try:
    from requirements.parser import RequirementsParser
except ImportError:
    RequirementsParser = None

def test_all_dependencies_installed():
    """Verify all packages in requirements.txt are installed"""
    if RequirementsParser is None:
        pytest.skip("requirements-parser not installed")
        
    with open("requirements.txt") as f:
        parser = RequirementsParser()
        requirements = parser.parse(f)
    
    missing_deps = []
    for req in requirements:
        try:
            importlib.import_module(req.name)
        except ImportError:
            missing_deps.append(req.name)
    
    if missing_deps:
        pytest.fail(f"Missing dependencies: {', '.join(missing_deps)}. Run `pip install -r requirements.txt` to install them.")

def test_flask_limiter_installed():
    """Verify flask-limiter is installed and importable"""
    flask_limiter = importlib.import_module("flask_limiter")
    assert flask_limiter is not None

def test_freezegun_installed():
    """Verify freezegun is installed and importable"""
    try:
        freezegun = importlib.import_module("freezegun")
        assert freezegun is not None
    except ImportError:
        pytest.fail("freezegun is not installed - required for time-based testing")
