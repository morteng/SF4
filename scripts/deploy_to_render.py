import os
import subprocess

def deploy_to_render():
    """Deploy the application to render.com"""
    try:
        # Ensure we are on the correct branch
        subprocess.run(["git", "checkout", "main"], check=True)
        
        # Pull the latest changes
        subprocess.run(["git", "pull", "origin", "main"], check=True)
        
        # Push to render.com
        subprocess.run(["git", "push", "render", "main"], check=True)
        
        print("Deployment to render.com completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error during deployment: {e}")
        print(f"Error details: {e.stderr.decode()}")
        return False

if __name__ == "__main__":
    deploy_to_render()
