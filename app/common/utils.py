from datetime import datetime
import pytz
from app.constants import FlashMessages
from wtforms.validators import ValidationError

from flask import Blueprint, current_app

def validate_blueprint(bp):
    """Validate blueprint parameters with more detailed checks."""
    if not isinstance(bp, Blueprint):
        raise ValueError("Invalid blueprint instance")
    if not bp.name:
        raise ValueError("Blueprint must have a name")
    if '.' in bp.name:
        raise ValueError("Blueprint name cannot contain dots")
    if not bp.url_prefix:
        raise ValueError("Blueprint must have a URL prefix")
    if not bp.import_name:
        raise ValueError("Blueprint must have an import name")

def validate_blueprint_routes(app, required_routes):
    """Validate that all required routes are registered."""
    with app.app_context():
        registered_routes = [rule.endpoint for rule in app.url_map.iter_rules()]
        missing_routes = [route for route in required_routes if route not in registered_routes]
        
        if missing_routes:
            app.logger.error("Route Validation Error:")
            app.logger.error(f"Registered routes: {registered_routes}")
            app.logger.error(f"Missing routes: {missing_routes}")
            app.logger.error(f"Current blueprints: {list(app.blueprints.keys())}")
            
            # Provide more detailed error message
            error_msg = (
                f"Missing routes: {', '.join(missing_routes)}.\n"
                "Check blueprint names and route endpoints.\n"
                f"Registered blueprints: {list(app.blueprints.keys())}\n"
                f"Registered routes: {registered_routes}"
            )
            raise RuntimeError(error_msg)

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

