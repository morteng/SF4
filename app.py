from flask import Flask
from app.config import get_config
from app.routes import init_routes

def create_app(config_name='default'):
    app = Flask(__name__)
    config = get_config(config_name)
    app.config.from_object(config)

    # Initialize routes
    init_routes(app)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
