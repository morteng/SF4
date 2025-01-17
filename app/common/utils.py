from datetime import datetime
import pytz
import logging
from app.constants import FlashMessages
from wtforms.validators import ValidationError

from flask import Blueprint, current_app

logger = logging.getLogger(__name__)

class BaseBlueprint(Blueprint):
    """Base blueprint class with built-in validation."""
    def __init__(self, name, import_name, **kwargs):
        self.validate_name(name)
        super().__init__(name, import_name, **kwargs)
        self.validate_endpoints()

    def validate_name(self, name):
        """Validate blueprint name."""
        if not name:
            raise ValueError("Blueprint must have a name")
        if '.' in name:
            raise ValueError("Blueprint name cannot contain dots")
        if not name.islower():
            raise ValueError("Blueprint name must be lowercase")

    def validate_endpoints(self):
        """Validate endpoint names."""
        for endpoint in self.view_functions.keys():
            if not isinstance(endpoint, str):
                raise ValueError(f"Invalid endpoint name: {endpoint}")
            if not endpoint.startswith(self.name + '.'):
                raise ValueError(f"Endpoint {endpoint} must start with blueprint name {self.name}")

def validate_blueprint_routes(app, required_routes):
    """Validate that all required routes are registered."""
    with app.app_context():
        registered_routes = [rule.endpoint for rule in app.url_map.iter_rules()]
        missing_routes = [route for route in required_routes if route not in registered_routes]

        logger.debug(f"Registered routes: {registered_routes}")
        logger.debug(f"Required routes: {required_routes}")

        if missing_routes:
            # Get detailed blueprint info
            blueprint_info = []
            for name, bp in app.blueprints.items():
                blueprint_info.append(f"{name}: {list(bp.view_functions.keys())}")

            app.logger.error("Route Validation Error:")
            app.logger.error(f"Registered routes: {registered_routes}")
            app.logger.error(f"Missing routes: {missing_routes}")
            app.logger.error(f"Current blueprints: {blueprint_info}")

            # Provide more detailed error message
            error_msg = (
                f"Missing routes: {', '.join(missing_routes)}.\n"
                "Possible causes:\n"
                "1. Blueprint not registered\n"
                "2. Route endpoint name mismatch\n"
                "3. URL prefix incorrect\n"
                f"Registered blueprints: {blueprint_info}\n"
                f"Registered routes: {registered_routes}"
            )
            raise RuntimeError(error_msg)

import os
import re
from app.models.user import User
from werkzeug.security import generate_password_hash
from app.models.audit_log import AuditLog

def init_admin_user():
    """Initialize admin user from environment variables with validation."""
    # Check required environment variables
    required_vars = ['ADMIN_USERNAME', 'ADMIN_EMAIL', 'ADMIN_PASSWORD']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        return
        
    # Validate email format
    if not re.match(r"[^@]+@[^@]+\.[^@]+", os.environ.get('ADMIN_EMAIL')):
        logger.error("Invalid admin email format")
        return
        
    # Check if admin user already exists
    if User.query.filter_by(is_admin=True).first():
        logger.info("Admin user already exists")
        return
        
    # Create admin user
    try:
        admin = User(
            username=os.environ.get('ADMIN_USERNAME'),
            email=os.environ.get('ADMIN_EMAIL'),
            password_hash=generate_password_hash(os.environ.get('ADMIN_PASSWORD')),
            is_admin=True
        )
        
        db.session.add(admin)
        db.session.commit()
        
        logger.info("Admin user created successfully")
        
        # Create audit log entry
        AuditLog.create(
            user_id=admin.id,
            action='admin_user_created',
            details='Initial admin user created from environment variables',
            object_type='User',
            object_id=admin.id
        )
        
    except Exception as e:
        logger.error(f"Failed to create admin user: {str(e)}")
        db.session.rollback()

def validate_application_deadline(field):
    """Validate that the application deadline is a future date."""
    if not isinstance(field.data, (str, datetime)):
        raise ValidationError(FlashMessages.INVALID_DATE_FORMAT)

    if not field.data:
        raise ValidationError(FlashMessages.MISSING_FIELD_ERROR)

    if isinstance(field.data, str):
        try:
            field.data = datetime.strptime(field.data, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            raise ValidationError(FlashMessages.INVALID_DATE_FORMAT)

    if field.data.tzinfo is None:
        field.data = pytz.UTC.localize(field.data)

    now = datetime.now(pytz.UTC)
    if field.data < now:
        raise ValidationError(FlashMessages.FUTURE_DATE_REQUIRED)

    # Check for leap year
    if field.data.month == 2 and field.data.day == 29:
        year = field.data.year
        if not (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)):
            raise ValidationError(FlashMessages.INVALID_LEAP_YEAR_DATE)

    # Validate time components
    if not (0 <= field.data.hour <= 23 and 
            0 <= field.data.minute <= 59 and 
            0 <= field.data.second <= 59):
        raise ValidationError(FlashMessages.INVALID_TIME_COMPONENTS)

