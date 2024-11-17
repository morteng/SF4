import pytest
from app.models.user import User
from app.models.bot import Bot

@pytest.fixture
def admin_user(app, session):
    """Create test admin user"""
    user = User(
        username='admin_test',
        email='admin@test.com',
        is_admin=True
    )
    user.set_password('test_password')
    session.add(user)
    session.commit()
    return user

@pytest.fixture
def admin_token(admin_user):
    """Generate admin authentication token"""
    return admin_user.generate_auth_token()

@pytest.fixture
def test_bot(session):
    """Create test bot"""
    bot = Bot(
        name='Test Bot',
        description='Test Description',
        status='active'
    )
    session.add(bot)
    session.commit()
    return bot
