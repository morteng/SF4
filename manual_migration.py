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
        
        # Check if column already exists
        inspector = db.inspect(db.engine)
        columns = inspector.get_columns('user')
        column_names = [col['name'] for col in columns]
        
        if 'confirmed_at' not in column_names:
            # Use connection object for SQL execution
            with db.engine.connect() as connection:
                # Add the column manually
                connection.execute(db.text("""
                    ALTER TABLE user 
                    ADD COLUMN confirmed_at DATETIME
                """))
                print("Added confirmed_at column")
        else:
            print("confirmed_at column already exists")
            
        # Update existing users
        with db.engine.connect() as connection:
            connection.execute(db.text("""
                UPDATE user 
                SET confirmed_at = CURRENT_TIMESTAMP 
                WHERE confirmed_at IS NULL
            """))
            print("Updated existing users")
            
            # Commit the changes
            connection.commit()
        
        # Verify migration
        test_user = User.query.first()
        print(f"Test user confirmed_at: {test_user.confirmed_at}")

if __name__ == "__main__":
    apply_migration()
    print("Migration applied successfully")
