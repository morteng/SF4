import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(os.getenv('INSTANCE_PATH', '/home/morten/sf4/instance'), 'site.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    def __init__(self):
        print(f"Configured Database URI: {self.SQLALCHEMY_DATABASE_URI}")  # Debugging line
