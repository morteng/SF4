import pytest
from app import create_app
from app.extensions import db
from app.models import Stipend, AuditLog

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

def test_create_stipend(app):
    with app.test_client() as client:
        response = client.post('/admin/stipends/create', data={
            'name': 'Test Stipend',
            'summary': 'Test Summary',
            'description': 'Test Description',
            'application_deadline': '2025-01-01'
        })
        assert response.status_code == 302
        
        # Verify database
        stipend = Stipend.query.first()
        assert stipend.name == 'Test Stipend'
        
        # Verify audit log
        audit = AuditLog.query.first()
        assert audit.action_type == 'create'
