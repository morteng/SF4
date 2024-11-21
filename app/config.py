import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    instance_path = os.path.abspath('/home/morten/sf4/instance')
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(instance_path, 'site.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    def __init__(self):
        print(f"Configured Database URI: {self.SQLALCHEMY_DATABASE_URI}")  # Debugging line
