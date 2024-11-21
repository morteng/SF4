import os
from .extensions import db  # Import db here

def init_db(app):
    db_path = app.config['SQLALCHEMY_DATABASE_URI'].split('///')[-1]
    
    # Ensure the directory exists
    if not os.path.exists(os.path.dirname(db_path)):
        os.makedirs(os.path.dirname(db_path))
    
    print(f"Database path: {db_path}")  # Debugging line
    
    # Create the database file if it doesn't exist
    with app.app_context():
        db.create_all()
