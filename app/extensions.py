from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Create the SQLAlchemy instance without binding to an app
db = SQLAlchemy()
migrate = Migrate()
