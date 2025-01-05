# Semantic versioning for the project
__version__ = "0.1.0"  # Initial version

def get_version():
    """Get the current project version"""
    return __version__

def bump_version(version_type="patch"):
    """Bump the version number
    Args:
        version_type (str): Type of version bump - 'major', 'minor', or 'patch'
    Returns:
        str: New version string
    """
    major, minor, patch = map(int, __version__.split('.'))
    if version_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif version_type == "minor":
        minor += 1
        patch = 0
    else:
        patch += 1
    return f"{major}.{minor}.{patch}"
