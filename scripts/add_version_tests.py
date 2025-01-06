import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from scripts.version import validate_db_connection, validate_version

class VersionManagementTests(unittest.TestCase):
    def test_validate_db_connection(self):
        self.assertTrue(validate_db_connection(':memory:'))
        
    def test_validate_version(self):
        self.assertTrue(validate_version('1.0.0'))
        self.assertTrue(validate_version('2.1.3-beta'))
        self.assertFalse(validate_version('invalid'))

if __name__ == "__main__":
    unittest.main()
