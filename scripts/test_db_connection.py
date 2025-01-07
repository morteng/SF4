import logging
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.version import validate_db_connection

def test_db_connection():
    """Test database connection with various scenarios"""
    test_cases = [
        ('instance/stipend.db', True),
        ('nonexistent.db', False),
        ('', False),
        (None, False),
        ('invalid/path.db', False)
    ]
    
    for db_path, expected in test_cases:
        result = validate_db_connection(db_path)
        assert result == expected, f"Test failed for {db_path}"
        logging.info(f"Test passed for {db_path}")

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    test_db_connection()
