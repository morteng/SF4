import subprocess

def update_requirements():
    """Update requirements.txt with current environment packages"""
    try:
        with open('requirements.txt', 'w') as f:
            subprocess.run(['pip', 'freeze'], stdout=f, check=True)
        print("Requirements updated successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to update requirements: {str(e)}")
        return False

if __name__ == "__main__":
    update_requirements()
