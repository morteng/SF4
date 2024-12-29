import unittest
from datetime import datetime
from app.models import Stipend

class TestStipendModel(unittest.TestCase):

    def test_year_only_format(self):
        data = {
            'name': 'Test Stipend', 
            'application_deadline': '2023'
        }
        stipend = Stipend.create(data)
        self.assertEqual(stipend.application_deadline, datetime(2023, 1, 1))

    def test_vague_date_format(self):
        data = {
            'name': 'Test Stipend',
            'application_deadline': 'in August'
        }
        stipend = Stipend.create(data)
        self.assertEqual(stipend.application_deadline, datetime(2023, 8, 1))

    def test_case_insensitive_month(self):
        data = {
            'name': 'Test Stipend',
            'application_deadline': 'august 2023'
        }
        stipend = Stipend.create(data)
        self.assertEqual(stipend.application_deadline, datetime(2023, 8, 1))

    def test_short_month_name(self):
        data = {
            'name': 'Test Stipend',
            'application_deadline': 'Aug 2023'
        }
        stipend = Stipend.create(data)
        self.assertEqual(stipend.application_deadline, datetime(2023, 8, 1))

    def test_full_datetime_format(self):
        data = {
            'name': 'Test Stipend',
            'application_deadline': '2023-08-15 23:59:59'
        }
        stipend = Stipend.create(data)
        self.assertEqual(stipend.application_deadline, datetime(2023, 8, 15, 23, 59, 59))

    def test_invalid_month(self):
        data = {
            'name': 'Test Stipend',
            'application_deadline': 'Month 2023'
        }
        with self.assertRaises(ValueError):
            Stipend.create(data)

    def test_invalid_year(self):
        data = {
            'name': 'Test Stipend',
            'application_deadline': 'August 999'
        }
        with self.assertRaises(ValueError):
            Stipend.create(data)

    def test_past_date(self):
        data = {
            'name': 'Test Stipend',
            'application_deadline': '2020-01-01 00:00:00'
        }
        with self.assertRaises(ValueError):
            Stipend.create(data)

if __name__ == '__main__':
    unittest.main()
