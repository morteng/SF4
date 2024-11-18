from app.models.user import User

def get_user_by_id(user_id):
    """Retrieve a user by their ID."""
    try:
        return User.query.get(user_id)
    except Exception as e:
        print(f"Failed to retrieve user with ID {user_id}: {e}")
        return None

def list_all_users():
    """List all users in the database."""
    try:
        return User.query.all()
    except Exception as e:
        print(f"Failed to list users: {e}")
        return []
