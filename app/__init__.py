import logging
from flask import Flask
from app.models.user import User
from app.extensions import db, login_manager

def create_app(config_name='default'):
    """Create and configure the Flask application."""
    from app.config import config_by_name
    
    # Initialize Flask app
    app = Flask(__name__)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    # Load configuration
    try:
        app.config.from_object(config_by_name[config_name])
        logger.info(f"Loaded {config_name} configuration successfully")
    except KeyError:
        logger.error(f"Invalid configuration name: {config_name}")
        raise ValueError(f"Invalid configuration name: {config_name}")

    init_extensions(app)
    init_models(app)
    init_routes(app)

    # Initialize the user loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app

def init_extensions(app):
    """Initialize Flask extensions with proper error handling."""
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize database
        db.init_app(app)
        logger.info("Database extension initialized successfully")
        
        # Initialize login manager
        login_manager.init_app(app)
        login_manager.login_view = 'auth.login'
        logger.info("Login manager initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize extensions: {str(e)}")
        raise

def init_models(app):
    """Initialize database models with proper context."""
    logger = logging.getLogger(__name__)
    
    with app.app_context():
        try:
            from app.models import association_tables
            from app.models.bot import Bot
            from app.models.notification import Notification
            from app.models.organization import Organization
            from app.models.stipend import Stipend
            from app.models.tag import Tag
            from app.models.user import User
            
            # Create database tables if they don't exist
            db.create_all()
            logger.info("Database models initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize models: {str(e)}")
            raise

def init_routes(app):
    from app.routes import routes_bp
    app.register_blueprint(routes_bp)
