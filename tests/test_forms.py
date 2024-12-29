from .base_test_case import BaseTestCase
from datetime import datetime
from app.forms.fields import CustomDateTimeField

class TestCustomDateTimeField(BaseTestCase):
    
    def test_empty_date(self):
        field = CustomDateTimeField()
        self.assertFormInvalid(
            field, {'': ''},
            {'': ['Date is required']}
        )

    def test_vague_date_conversion(self):
        field = CustomDateTimeField()
        field.process_formdata(['in August'])
        self.assertTrue(field.validate(None))
        self.assertEqual(field.data, datetime(2023, 8, 1))

    def test_case_insensitive_month(self):
        field = CustomDateTimeField()
        field.process_formdata(['august 2023'])
        self.assertTrue(field.validate(None))
        self.assertEqual(field.data, datetime(2023, 8, 1))

    def test_short_month_name(self):
        field = CustomDateTimeField()
        field.process_formdata(['Aug 2023'])
        self.assertTrue(field.validate(None))
        self.assertEqual(field.data, datetime(2023, 8, 1))

    def test_invalid_vague_date(self):
        field = CustomDateTimeField()
        self.assertFormInvalid(
            field, {'': 'in NotAMonth'},
            {'': ['Invalid date values']}
        )

    def test_year_only_format(self):
        field = CustomDateTimeField()
        field.process_formdata(['2023'])
        self.assertTrue(field.validate(None))
        self.assertEqual(field.data, datetime(2023, 1, 1))

    def test_full_datetime_format(self):
        field = CustomDateTimeField()
        field.process_formdata(['2023-08-15 23:59:59'])
        self.assertTrue(field.validate(None))
        self.assertEqual(field.data, datetime(2023, 8, 15, 23, 59, 59))

    def test_invalid_month(self):
        field = CustomDateTimeField()
        self.assertFormInvalid(
            field, {'': 'Month 2023'},
            {'': ['Invalid date values']}
        )

    def test_invalid_year(self):
        field = CustomDateTimeField()
        self.assertFormInvalid(
            field, {'': 'August 999'},
            {'': ['Invalid date values']}
        )

    def test_past_date(self):
        field = CustomDateTimeField()
        self.assertFormInvalid(
            field, {'': '2020-01-01 00:00:00'},
            {'': ['Application deadline must be a future date']}
        )

