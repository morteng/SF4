from flask import Flask
from app.factory import create_app

app = Flask(__name__)

# Initialize the app
app = create_app()

if __name__ == '__main__':
    app.run()
