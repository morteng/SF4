from app import create_app
from app.extensions import db
from app.models.user import User

def apply_migration():
    # Create app instance
    app = create_app('testing')
    
    # Push application context
    with app.app_context():
        # Verify database connection
        print("Database URL:", app.config['SQLALCHEMY_DATABASE_URI'])
        
        # Add the column manually
        db.engine.execute("""
            ALTER TABLE user 
            ADD COLUMN confirmed_at DATETIME
        """)
        
        # Update existing users
        db.engine.execute("""
            UPDATE user 
            SET confirmed_at = CURRENT_TIMESTAMP 
            WHERE confirmed_at IS NULL
        """)
        
        # Verify migration
        test_user = User.query.first()
        print(f"Test user confirmed_at: {test_user.confirmed_at}")

if __name__ == "__main__":
    apply_migration()
    print("Migration applied successfully")
