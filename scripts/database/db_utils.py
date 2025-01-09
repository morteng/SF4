import time
import logging
from app.extensions import db

def init_db_with_retry(app, max_retries=3):
    """Initialize database with retry logic"""
    retry_delay = 1  # seconds
    for attempt in range(max_retries):
        try:
            db.init_app(app)
            return True
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(retry_delay)
            logging.warning(f"Database init attempt {attempt + 1} failed, retrying...")
