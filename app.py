from flask import Flask
from app.configs import ProductionConfig
from app.models.base import Base
from app.extensions import db, migrate

app = Flask(__name__)
config = ProductionConfig(app.root_path)
app.config.from_object(config)

# Initialize extensions
db.init_app(app)
migrate.init_app(app, db)

with app.app_context():
    # Initialize any required data or services here
    pass

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=config.DEBUG)
