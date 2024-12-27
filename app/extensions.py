from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from sqlalchemy.orm import scoped_session, sessionmaker

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()  # Initialize CSRF protection
migrate = Migrate()
limiter = Limiter(key_func=get_remote_address)

Session = None
db_session = None

def init_extensions(app):
    global Session, db_session
    with app.app_context():
        Session = sessionmaker(bind=db.engine)
        db_session = scoped_session(Session)
        limiter.init_app(app)
