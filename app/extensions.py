from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect, generate_csrf
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from sqlalchemy.orm import scoped_session, sessionmaker

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
csrf_token = generate_csrf  # Use the correct function
migrate = Migrate()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

Session = None
db_session = None

def init_extensions(app):
    global Session, db_session
    with app.app_context():
        Session = sessionmaker(bind=db.engine)
        db_session = scoped_session(Session)
        
        # Initialize rate limiting
        limiter.init_app(app)
        
        # Enable CSRF protection
        csrf.init_app(app)
