import pytest
from app.utils import admin_required, init_admin_user

def test_admin_required_decorator():
    """Test the admin_required decorator."""
    @admin_required
    def dummy_function(*args, **kwargs):
        return "Access granted"

    # Initialize admin user
    admin_user = init_admin_user()

    # Test with valid admin token
    with pytest.raises(Exception) as e:
        response = dummy_function(admin_user)
        assert response == "Access granted"
