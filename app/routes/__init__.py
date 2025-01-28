from flask import Blueprint

def register_blueprints(app):
    from app.routes.admin import register_admin_blueprints
    register_admin_blueprints(app)
