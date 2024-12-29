import sys
import subprocess

def check_virtualenv():
    try:
        import flask
    except ImportError:
        print("Virtual environment is not activated or dependencies are not installed.")
        print("Run the following commands to set up the environment:")
        print("  python -m venv .venv")
        print("  source .venv/bin/activate  # macOS/Linux")
        print("  .venv\\Scripts\\activate  # Windows")
        print("  pip install -r requirements.txt")
        sys.exit(1)

def check_dependencies():
    try:
        subprocess.check_call(["pip", "install", "-r", "requirements.txt"])
    except subprocess.CalledProcessError:
        print("Failed to install dependencies. Check your internet connection and try again.")
        sys.exit(1)

if __name__ == "__main__":
    check_virtualenv()
    check_dependencies()
    print("Environment is ready!")
