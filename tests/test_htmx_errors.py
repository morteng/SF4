from flask import get_flashed_messages
from tests.base_test_case import BaseTestCase

class TestHtmxErrors(BaseTestCase):
    def test_htmx_partial_recovery(self):
        headers = {'HX-Request': 'true'}
        response = self.client.post('/admin/stipends/create', 
                                  data={'name': ''},
                                  headers=headers)
        self.assertIn(b'form-error', response.data)
        self.assertEqual(response.status_code, 422)
