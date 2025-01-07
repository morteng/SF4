import logging
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.version import validate_db_connection

def test_db_connection():
    """Test database connection with various scenarios"""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    test_cases = [
        ('instance/stipend.db', True),
        ('nonexistent.db', False),
        ('', False),
        (None, False),
        ('invalid/path.db', False)
    ]
    
    # Ensure test database exists and is initialized
    from scripts.init_test_db import init_test_db
    from app.factory import create_app
    app = create_app('testing')
    with app.app_context():
        init_test_db()
    
    for db_path, expected in test_cases:
        try:
            result = validate_db_connection(db_path)
            assert result == expected, f"Test failed for {db_path}"
            logger.info(f"Test passed for {db_path}")
        except Exception as e:
            logger.error(f"Test error for {db_path}: {str(e)}")
            return False

    return True

if __name__ == "__main__":
    test_db_connection()
