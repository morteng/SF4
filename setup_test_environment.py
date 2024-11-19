import os

def setup():
    instance_dir = 'instance'
    if not os.path.exists(instance_dir):
        os.makedirs(instance_dir)
        print(f"Created {instance_dir} directory.")
    else:
        print(f"{instance_dir} directory already exists.")

if __name__ == '__main__':
    setup()
