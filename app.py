import os
from flask import Flask, render_template
from app.config import get_config
from app.extensions import init_extensions
from app.routes import init_routes

def create_app(config_name='default'):
    # Create and configure the app
    app = Flask(__name__)
    config = get_config(config_name)
    app.config.from_object(config)

    # Initialize extensions
    init_extensions(app)

    # Register routes
    init_routes(app)

    @app.route('/')
    def index():
        return render_template('index.html')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
