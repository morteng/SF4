from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

class CustomSQLAlchemy(SQLAlchemy):
    def init_app(self, app):
        print(f"Initializing SQLAlchemy with app: {app}")
        # Check if already initialized
        if not hasattr(self, 'app'):
            super().init_app(app)
        else:
            print("SQLAlchemy already initialized")

db = CustomSQLAlchemy()
migrate = Migrate()
