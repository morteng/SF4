import json
import logging
from flask import Blueprint, redirect, url_for, request, current_app
from app.common.base_blueprint import BaseBlueprint
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.models.notification import Notification, NotificationType
from flask_wtf.csrf import validate_csrf
from functools import wraps
from flask_login import current_user
from app.models.notification import Notification
from app.models.audit_log import AuditLog
from app.extensions import db
from app.utils import flash_message
from app.constants import FlashMessages, FlashCategory

logger = logging.getLogger(__name__)
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

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

# Export the admin blueprint
admin_bp = create_admin_blueprint()

from flask import abort
from functools import wraps
from flask_login import current_user
from app.common.utils import validate_blueprint_routes

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function
