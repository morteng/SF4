import pytest
from app.models import Tag
from app.services.tag_service import TagService
from app import db
from app.forms.admin_forms import TagForm

@pytest.fixture
def tag_service():
    return TagService()

@pytest.fixture
def test_data():
    return {
        'name': 'Test Tag',
        'category': 'Academic'
    }

def test_create_tag(tag_service, test_data, db_session):
    # Test valid tag creation
    tag = tag_service.create(test_data)
    db_session.commit()
    assert tag.id is not None
    assert tag.name == test_data['name']
    assert tag.category == test_data['category']

def test_update_tag(tag_service, test_data, db_session):
    # Test tag update
    tag = tag_service.create(test_data)
    db_session.commit()
    updated_data = {
        'name': 'Updated Tag',
        'category': 'Professional'
    }
    updated_tag = tag_service.update(tag, updated_data)
    db_session.commit()
    assert updated_tag.name == updated_data['name']
    assert updated_tag.category == updated_data['category']

def test_delete_tag(tag_service, test_data, db_session):
    # Test tag deletion
    tag = tag_service.create(test_data)
    db_session.commit()
    tag_service.delete(tag)
    db_session.commit()
    assert tag_service.get(tag.id) is None
