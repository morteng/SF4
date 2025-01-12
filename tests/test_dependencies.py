import pytest
import importlib
import subprocess
from typing import List

def get_requirements() -> List[str]:
    """Get a list of package names from requirements.txt."""
    try:
        with open("requirements.txt") as f:
            return [line.strip().split("==")[0] for line in f if line.strip() and not line.startswith("#")]
    except FileNotFoundError:
        pytest.fail("requirements.txt file not found")
    except PermissionError:
        pytest.fail("No permission to read requirements.txt")


def test_requirements_file_exists_and_readable():
    """Ensure requirements.txt exists and is readable."""
    try:
        with open("requirements.txt") as f:
            assert f.readable(), "requirements.txt is not readable"
    except FileNotFoundError:
        pytest.fail("requirements.txt file not found")
    except PermissionError:
        pytest.fail("No permission to read requirements.txt")


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


def test_package_versions():
    """Verify installed packages meet version requirements in requirements.txt."""
    import pkg_resources

    try:
        pkg_resources.require(get_requirements())
    except pkg_resources.ResolutionError as e:
        pytest.fail(f"Dependency issue: {str(e)}")


def test_critical_packages():
    """Verify critical packages are installed."""
    critical_packages = ["Flask", "freezegun", "pytest"]
    missing = []
    for package in critical_packages:
        try:
            importlib.import_module(package)
        except ImportError:
            missing.append(package)

    assert not missing, f"Critical missing packages: {', '.join(missing)}. Install them via pip."


def test_virtual_environment():
    """Check if running in a virtual environment."""
    import sys
    assert 'venv' in sys.prefix or '.venv' in sys.prefix, (
        "Not running in a virtual environment. Please activate one."
    )


def test_pip_installed():
    """Ensure pip is installed and usable."""
    try:
        subprocess.check_call(["pip", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        pytest.fail("pip is not installed or not available in PATH")


def test_install_dependencies():
    """Test installing dependencies from requirements.txt."""
    try:
        subprocess.check_call(["pip", "install", "-r", "requirements.txt"], stdout=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        pytest.fail("Failed to install dependencies from requirements.txt")
