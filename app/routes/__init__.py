from flask import Blueprint

def init_routes(app):
    from .admin.bot_routes import admin_bot_bp
    from .admin.organization_routes import admin_org_bp
    from .admin.stipend_routes import admin_stipend_bp
    from .admin.tag_routes import admin_tag_bp
    from .admin.user_routes import admin_user_bp

    app.register_blueprint(admin_bot_bp)
    app.register_blueprint(admin_org_bp)
    app.register_blueprint(admin_stipend_bp)
    app.register_blueprint(admin_tag_bp)
    app.register_blueprint(admin_user_bp)
