from datetime import datetime
from wtforms import ValidationError
from app import constants

class CustomDateTimeField:
    def __init__(self, format="%Y-%m-%d %H:%M:%S"):
        self.format = format

    def validate(self, value):
        try:
            datetime.strptime(value, self.format)
        except ValueError:
            raise ValidationError(constants.INVALID_DATETIME_FORMAT)
