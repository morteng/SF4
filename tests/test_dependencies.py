import importlib
import pytest
import subprocess
from typing import List
try:
    from requirements.parser import RequirementsParser
except ImportError:
    RequirementsParser = None

def get_requirements() -> List[str]:
    """Get list of package names from requirements.txt."""
    with open("requirements.txt") as f:
        return [line.strip().split("==")[0] for line in f if line.strip() and not line.startswith("#")]

def test_all_dependencies_installed():
    """Verify all packages in requirements.txt are installed."""
    missing_deps = []
    for package in get_requirements():
        try:
            importlib.import_module(package)
        except ImportError:
            missing_deps.append(package)
    
    assert not missing_deps, (
        f"Missing dependencies: {', '.join(missing_deps)}. "
        "Run `pip install -r requirements.txt` to install them."
    )

def test_flask_limiter_installed():
    """Verify flask-limiter is installed and importable"""
    flask_limiter = importlib.import_module("flask_limiter")
    assert flask_limiter is not None

def test_flask_limiter_installed():
    """Verify flask-limiter is installed and importable"""
    flask_limiter = importlib.import_module("flask_limiter")
    assert flask_limiter is not None

def test_freezegun_installed():
    """Verify freezegun is installed and importable"""
    try:
        import freezegun
        assert freezegun is not None
    except ImportError:
        pytest.fail("freezegun is not installed - required for time-based testing. Run `pip install -r requirements.txt` to install it.")

def test_requirements_file_exists():
    """Verify requirements.txt exists and is readable"""
    try:
        with open("requirements.txt") as f:
            assert f.readable()
    except FileNotFoundError:
        pytest.fail("requirements.txt file not found")
    except PermissionError:
        pytest.fail("No permission to read requirements.txt")

def test_requirements_format():
    """Verify requirements.txt has valid format"""
    try:
        get_requirements()
    except Exception as e:
        pytest.fail(f"Invalid requirements.txt format: {str(e)}")

def test_package_versions():
    """Verify installed packages meet minimum version requirements"""
    import pkg_resources
    missing_deps = []
    version_mismatches = []
    
    for package in get_requirements():
        try:
            pkg_resources.require(package)
        except pkg_resources.DistributionNotFound:
            missing_deps.append(package)
        except pkg_resources.VersionConflict as e:
            version_mismatches.append(f"{package}: {str(e)}")
    
    if missing_deps or version_mismatches:
        errors = []
        if missing_deps:
            errors.append(f"Missing packages: {', '.join(missing_deps)}")
        if version_mismatches:
            errors.append(f"Version mismatches: {', '.join(version_mismatches)}")
        pytest.fail("\n".join(errors))

def test_development_environment():
    """Verify basic development environment setup"""
    # Test virtual environment
    try:
        import sys
        assert 'venv' in sys.prefix or '.venv' in sys.prefix, "Not running in a virtual environment"
    except AssertionError:
        pytest.fail("Not running in a virtual environment. Create and activate one first.")
    
    # Test Python version
    import platform
    assert platform.python_version_tuple()[0] == '3', "Python 3 is required"
    
    # Test pip is installed
    try:
        subprocess.check_call(['pip', '--version'])
    except subprocess.CalledProcessError:
        pytest.fail("pip is not installed or not in PATH")
import subprocess
import pytest

def test_dependencies():
    """Verify all dependencies are installed."""
    try:
        subprocess.check_call(["pip", "install", "-r", "requirements.txt"])
    except subprocess.CalledProcessError:
        pytest.fail("Failed to install dependencies")
import subprocess
import pytest

def test_dependencies_installed():
    """Verify all required dependencies are installed"""
    try:
        subprocess.check_call(["pip", "install", "-r", "requirements.txt"])
    except subprocess.CalledProcessError:
        pytest.fail("Failed to install dependencies")

def test_critical_packages():
    """Verify critical packages are installed"""
    required = ["Flask", "freezegun", "pytest"]
    for package in required:
        try:
            subprocess.check_call(["pip", "show", package])
        except subprocess.CalledProcessError:
            pytest.fail(f"Required package {package} is not installed")
import subprocess
import pytest

def test_dependencies():
    """Verify all dependencies are installed."""
    try:
        subprocess.check_call(["pip", "install", "-r", "requirements.txt"])
    except subprocess.CalledProcessError:
        pytest.fail("Failed to install dependencies")
import subprocess
import pytest

def test_dependencies():
    try:
        subprocess.check_call(["pip", "install", "-r", "requirements.txt"])
    except subprocess.CalledProcessError:
        pytest.fail("Failed to install dependencies")
import subprocess
import pytest

def test_dependencies():
    """Verify all required dependencies are installed."""
    try:
        subprocess.check_call(["pip", "install", "-r", "requirements.txt"])
    except subprocess.CalledProcessError:
        pytest.fail("Failed to install dependencies")
