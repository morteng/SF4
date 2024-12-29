from datetime import datetime
from app import constants

class CustomDateTimeField:
    """Custom field for validating date/time strings."""
    
    def __init__(self, format="%Y-%m-%d %H:%M:%S"):
        self.format = format

    def validate(self, value):
        """Validate the date/time string."""
        try:
            dt = datetime.strptime(value, self.format)
            # Check for invalid leap year dates
            if dt.month == 2 and dt.day == 29 and not self.is_leap_year(dt.year):
                raise ValueError(constants.INVALID_LEAP_YEAR)
        except ValueError:
            raise ValueError(constants.INVALID_DATETIME_FORMAT)

    def is_leap_year(self, year):
        """Check if a year is a leap year."""
        return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
