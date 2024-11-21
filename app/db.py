import os
from .extensions import db  # Import db here

def init_db(app):
    db_path = app.config['SQLALCHEMY_DATABASE_URI'].split('///')[-1]

    print(f"Database path: {db_path}")  # Debugging line

    # Ensure the directory exists
    if not os.path.exists(os.path.dirname(db_path)):
        print(f"Creating directory: {os.path.dirname(db_path)}")  # Debugging line
        os.makedirs(os.path.dirname(db_path))

    # Ensure the database file exists
    if not os.path.isfile(db_path):
        print(f"Creating database file: {db_path}")  # Debugging line
        open(db_path, 'a').close()  # Create an empty file

    # Create the database tables if they don't exist
    with app.app_context():
        db.create_all()