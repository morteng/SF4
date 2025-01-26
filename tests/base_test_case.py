import pytest
from app.models import User, Stipend, Tag, Organization
import uuid
from datetime import datetime, timedelta, timezone

class BaseTestCase:
    @pytest.fixture(autouse=True)
    def setup(self, client, db_session):
        """Base test setup using fixtures"""
        self.client = client
        self.db = db_session
        
        # Create test data
        self.org = Organization(name='Test Org', description='Test Description')
        self.db.add(self.org)
        
        # Create admin user
        self.admin = User(
            username='testadmin',
            email='admin@test.com',
            is_admin=True
        )
        self.admin.set_password('testpassword')
        self.db.add(self.admin)
        
        self.db.commit()
