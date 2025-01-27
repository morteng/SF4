from datetime import datetime
import pytz
import logging
from app.constants import FlashMessages
from wtforms.validators import ValidationError

from flask import Blueprint, current_app
from app.extensions import db

logger = logging.getLogger(__name__)

class BaseBlueprint(Blueprint):
    def __init__(self, name, import_name, **kwargs):
        super().__init__(name, import_name, **kwargs)

def validate_blueprint_routes(bp, required_routes=None):
    """Validate that all routes in the blueprint have proper permissions."""
    if required_routes:
        for route in required_routes:
            if not hasattr(bp, route):
                raise ValueError(f"Required route '{route}' not found in blueprint")
    for route in bp.routes:
        if not hasattr(route, 'is_admin_route'):
            raise ValueError(f"Route '{route.endpoint}' is missing required permissions")

def validate_application_deadline(form, field):
    """Validate that the application deadline is at least 24 hours in the future."""
    if not field.data:
        raise ValidationError("Application deadline is required.")
    
    # Get the current time in UTC
    now = datetime.utcnow()
    
    # Check if deadline is at least 24 hours in the future
    if field.data < now + datetime.timedelta(hours=24):
        raise ValidationError("Application deadline must be at least 24 hours in the future.")
