from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from sqlalchemy.orm import scoped_session, sessionmaker

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()  # Initialize CSRF protection
migrate = Migrate()

# Define db_session as a scoped session if needed
Session = sessionmaker(bind=db.engine)
db_session = scoped_session(Session)
