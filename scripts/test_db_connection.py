import logging
from scripts.version import validate_db_connection

def test_db_connection():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    test_cases = [
        ('instance/stipend.db', True),
        ('nonexistent.db', False),
        ('', False),
        (None, False)
    ]
    
    for db_path, expected in test_cases:
        result = validate_db_connection(db_path)
        assert result == expected, f"Test failed for {db_path}"
        logging.info(f"Test passed for {db_path}")

if __name__ == "__main__":
    test_db_connection()
