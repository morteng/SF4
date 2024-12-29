from datetime import datetime
import pytz
from app.constants import FlashMessages
from wtforms.validators import ValidationError

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

