import logging
from app.extensions import db

logging.basicConfig(level=logging.ERROR)

def update_stipend(stipend, data):
    try:
        for key, value in data.items():
            if hasattr(stipend, key):
                setattr(stipend, key, value)
        db.session.commit()
        return stipend
    except Exception as e:
        logging.error(f"Failed to update stipend: {e}")
        db.session.rollback()
        return None
