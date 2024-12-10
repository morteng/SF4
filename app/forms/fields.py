from wtforms import FormField
from datetime import datetime

class NullableDateTimeField(FormField):
    def process_formdata(self, valuelist):
        if valuelist:
            date_str = valuelist[0]
            try:
                self.data = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                self.data = None
        else:
            self.data = None
