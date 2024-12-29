from .base_test_case import BaseTestCase
from datetime import datetime
from app.forms.fields import CustomDateTimeField

class TestCustomDateTimeField(BaseTestCase):
    
    def test_empty_date(self):
        field = CustomDateTimeField()
        field.process_formdata([''])
        self.assertFalse(field.validate(None))
        self.assertIn('Date is required', field.errors[0])

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
        field.process_formdata(['in NotAMonth'])
        self.assertFalse(field.validate(None))
        self.assertIn('Invalid date values', field.errors[0])

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
        field.process_formdata(['Month 2023'])
        self.assertFalse(field.validate(None))
        self.assertIn('Invalid date values', field.errors[0])

    def test_invalid_year(self):
        field = CustomDateTimeField()
        field.process_formdata(['August 999'])
        self.assertFalse(field.validate(None))
        self.assertIn('Invalid date values', field.errors[0])

    def test_past_date(self):
        field = CustomDateTimeField()
        field.process_formdata(['2020-01-01 00:00:00'])
        self.assertFalse(field.validate(None))
        self.assertIn('Application deadline must be a future date', field.errors[0])

