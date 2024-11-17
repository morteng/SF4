from flask import current_app as app
from werkzeug.security import generate_password_hash
from app.models.user import User
from app.extensions import db  # Import db here

def init_admin_user():
    with app.app_context():
        username = app.config['ADMIN_USERNAME']
        password = app.config['ADMIN_PASSWORD']
        email = app.config['ADMIN_EMAIL']

        admin_user = User.query.filter_by(username=username).first()
        if not admin_user:
            admin_user = User(
                username=username,
                password_hash=generate_password_hash(password),
                email=email,
                is_admin=True
            )
            db.session.add(admin_user)
            db.session.commit()
