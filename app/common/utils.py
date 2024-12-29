from datetime import datetime
import pytz
from app.constants import FlashMessages
from wtforms.validators import ValidationError

def validate_application_deadline(field):
    """Validate that the application deadline is a future date."""
    if field.errors:
        return

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

def init_admin_user():
    """Initialize the admin user with default credentials."""
    # Implementation goes here
    pass

def shared_function():
    """Shared functionality to avoid circular imports."""
    pass
