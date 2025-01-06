# Key Management

import os
from dotenv import load_dotenv

load_dotenv()

def validate_secret_key():
    secret_key = os.getenv('SECRET_KEY')
    if not secret_key or len(secret_key) < 64:
        raise ValueError("SECRET_KEY is too short (minimum 64 characters)")
    return secret_key

if __name__ == "__main__":
    try:
        validate_secret_key()
        print("SECRET_KEY is valid.")
    except ValueError as e:
        print(e)
