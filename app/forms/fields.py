from wtforms import Field
from wtforms.widgets import TextInput
from datetime import datetime

class NullableDateTimeField(Field):
    widget = TextInput()

    def process_formdata(self, valuelist):
        if valuelist:
            date_str = valuelist[0]
            try:
                self.data = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                self.data = None
        else:
            self.data = None

    def _value(self):
        if self.data is not None:
            return self.data.strftime('%Y-%m-%d %H:%M:%S')
        return ''
