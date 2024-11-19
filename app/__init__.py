import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from app.config import get_config
from app.extensions import init_extensions
from app.routes import init_routes

# Define the db object here
db = SQLAlchemy()

def create_app(config_name='default'):
    # Ensure instance directory exists
    instance_path = os.path.join(os.getcwd(), 'instance')
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)

    app = Flask(__name__, instance_relative_config=True)
    config = get_config(config_name)
    app.config.from_object(config)

    db.init_app(app)  # Initialize the database with the app
    init_extensions(app)
    init_routes(app)

    @app.route('/')
    def index():
        return render_template('index.html')

    return app

if __name__ == '__main__':
    app = create_app('development')
    app.run(debug=True)
