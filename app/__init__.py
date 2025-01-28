from flask import Flask
from app.configs.base_config import BaseConfig

app = Flask(__name__)

# Initialize the app
app.config = BaseConfig(str(app.root_path))

if __name__ == '__main__':
    app.run()
