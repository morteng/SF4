from flask import Flask
from app.factory import create_app

app = Flask(__name__)
app.config.from_object(BaseConfig())
app.config['ROOT_PATH'] = app.root_path

# Initialize extensions and other setup
