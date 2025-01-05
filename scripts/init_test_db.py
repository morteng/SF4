import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import db

def init_test_db():
    app = create_app('testing')
    with app.app_context():
        db.drop_all()
        db.create_all()

if __name__ == "__main__":
    init_test_db()
