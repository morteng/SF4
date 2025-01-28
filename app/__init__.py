from flask import Flask
from app.configs.base_config import BaseConfig
from app.extensions import db

app = Flask(__name__)
config = BaseConfig(app.root_path)
app.config.from_object(config)

# Initialize extensions
db.init_app(app)

if __name__ == '__main__':
    app.run()
