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
        
        # Use connection object for SQL execution
        with db.engine.connect() as connection:
            # Add the column manually
            connection.execute(db.text("""
                ALTER TABLE user 
                ADD COLUMN confirmed_at DATETIME
            """))
            
            # Update existing users
            connection.execute(db.text("""
                UPDATE user 
                SET confirmed_at = CURRENT_TIMESTAMP 
                WHERE confirmed_at IS NULL
            """))
            
            # Commit the changes
            connection.commit()
        
        # Verify migration
        test_user = User.query.first()
        print(f"Test user confirmed_at: {test_user.confirmed_at}")

if __name__ == "__main__":
    apply_migration()
    print("Migration applied successfully")
