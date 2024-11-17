from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

print("Creating SQLAlchemy and Migrate instances")
db = SQLAlchemy()
migrate = Migrate()
