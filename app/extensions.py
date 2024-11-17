from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Use a custom SQLAlchemy class to help with debugging
class CustomSQLAlchemy(SQLAlchemy):
    def init_app(self, app):
        print(f"Initializing SQLAlchemy with app: {app}")
        super().init_app(app)

db = CustomSQLAlchemy()
migrate = Migrate()
