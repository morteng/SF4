import logging
from flask import Blueprint
from app.common.base_blueprint import BaseBlueprint

logger = logging.getLogger(__name__)

_admin_blueprints_registered = False

def register_admin_blueprints(app):
    global _admin_blueprints_registered
    
    if _admin_blueprints_registered:
        logger.debug("Admin blueprints already registered. Skipping.")
        return
    
    try:
        # Register stipend routes
        from .stipend_routes import admin_stipend_bp
        app.register_blueprint(
            admin_stipend_bp,
            url_prefix='/stipends',
            endpoint='admin_stipend'
        )
        logger.debug("Registered stipend routes")
        
        # Register other admin blueprints here
        
        _admin_blueprints_registered = True
    except Exception as e:
        logger.error(f"Failed to register admin blueprints: {str(e)}")
        raise
