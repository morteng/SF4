from app import create_app
from app.extensions import db
from app.models.user import User

app = create_app()

with app.app_context():
    # Check if users table exists
    print("Tables in database:", db.engine.table_names())
    
    # Check if any users exist
    users = User.query.all()
    print("Existing users:", users)
    
    # Try to create admin user directly
    from scripts.ensure_admin_user import ensure_admin_user
    result = ensure_admin_user()
    print("Admin user creation result:", result)
