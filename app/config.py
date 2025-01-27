from dotenv import load_dotenv
import os

load_dotenv()

class BaseConfig:
    DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', 'on', '1')
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
