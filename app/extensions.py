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
        
        # Apply rate limits to admin endpoints
        limiter.limit("100/hour")(app.blueprints['admin'])
        limiter.limit("10/minute")(app.blueprints['admin'].decorators)
        
        # Apply rate limits to sensitive endpoints
        limiter.limit("100/hour")(app.blueprints['admin'])
        limiter.limit("10/minute")(app.blueprints['admin'].decorators)
        
        # Enable CSRF protection
        csrf.init_app(app)
        
        # Apply rate limits to admin routes
        limiter.limit("100/hour")(app.blueprints['admin'])

def init_extensions(app):
    global Session, db_session
    with app.app_context():
        Session = sessionmaker(bind=db.engine)
        db_session = scoped_session(Session)
        
        # Initialize rate limiting
        limiter.init_app(app)
        
        # Apply rate limits to admin endpoints
        limiter.limit("100/hour")(app.blueprints['admin'])
        limiter.limit("10/minute")(app.blueprints['admin'].decorators)
        
        # Enable CSRF protection
        csrf.init_app(app)
