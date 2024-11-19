from .admin import admin_bp
from .user import user_bp  
from .public_bot_routes import public_bot_bp  
from .public_user_routes import public_user_bp  

def init_routes(app):
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(user_bp)  
    app.register_blueprint(public_bot_bp, url_prefix='/bots')  
    app.register_blueprint(public_user_bp)  
