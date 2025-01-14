from app.extensions import db
from app.models.user import User

def apply_migration():
    with db.engine.connect() as connection:
        # Add the column manually
        connection.execute("""
            ALTER TABLE user 
            ADD COLUMN confirmed_at DATETIME
        """)
        
        # Update existing users
        connection.execute("""
            UPDATE user 
            SET confirmed_at = CURRENT_TIMESTAMP 
            WHERE confirmed_at IS NULL
        """)

if __name__ == "__main__":
    apply_migration()
    print("Migration applied successfully")
