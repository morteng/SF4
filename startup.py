import os
from flask_migrate import Migrate, upgrade
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from app import create_app, db

app = create_app(os.getenv('FLASK_CONFIG', 'default'))

migrate = Migrate(app, db)

def init_db():
    with app.app_context():
        # Create the database tables
        db.create_all()
        
        # Run migrations
        upgrade()

if __name__ == '__main__':
    init_db()
    
    # Run tests here if needed
    
    # Start the application
    app.run(host='0.0.0.0', port=5000)
