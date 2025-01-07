import os
import subprocess

def deploy_to_render():
    """Deploy the application to render.com"""
    try:
        # Verify git remote exists
        remotes = subprocess.run(["git", "remote"], capture_output=True).stdout.decode()
        if "render" not in remotes:
            # Add render remote
            subprocess.run(["git", "remote", "add", "render", "https://github.com/morteng/SF4"], check=True)
        
        # Ensure we are on the correct branch
        subprocess.run(["git", "checkout", "main"], check=True)
        
        # Pull the latest changes
        subprocess.run(["git", "pull", "origin", "main"], check=True)
        
        # Push to render.com
        result = subprocess.run(["git", "push", "render", "main"], capture_output=True)
        if result.retcode != 0:
            print(f"Push failed: {result.stderr.decode()}")
            return False
        
        print("Deployment to render.com completed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error during deployment: {e}")
        if e.stderr:
            print(f"Error details: {e.stderr.decode()}")
        return False

if __name__ == "__main__":
    deploy_to_render()
