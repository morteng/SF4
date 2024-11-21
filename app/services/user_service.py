from app.models.user import User
from werkzeug.security import generate_password_hash
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def get_user_by_id(user_id):
    return User.query.get(user_id)

def delete_user(user):
    db.session.delete(user)
    db.session.commit()

def get_all_users():
    return User.query.all()

def create_admin_user():
    from app.config import DevelopmentConfig, TestingConfig, ProductionConfig
    config = {
        'development': DevelopmentConfig,
        'testing': TestingConfig,
        'production': ProductionConfig
    }
    
    admin_username = os.environ.get('ADMIN_USERNAME', config[os.getenv('FLASK_CONFIG')].ADMIN_USERNAME)
    admin_password = os.environ.get('ADMIN_PASSWORD', config[os.getenv('FLASK_CONFIG')].ADMIN_PASSWORD)
    admin_email = os.environ.get('ADMIN_EMAIL', config[os.getenv('FLASK_CONFIG')].ADMIN_EMAIL)

    if not User.query.filter_by(username=admin_username).first():
        admin_user = User(
            username=admin_username,
            email=admin_email,
            is_admin=True
        )
        admin_user.set_password(admin_password)
        db.session.add(admin_user)
        db.session.commit()
