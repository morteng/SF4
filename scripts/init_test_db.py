from app import create_app
from app.models import db

def init_test_db():
    app = create_app('testing')
    with app.app_context():
        db.create_all()

if __name__ == "__main__":
    init_test_db()
