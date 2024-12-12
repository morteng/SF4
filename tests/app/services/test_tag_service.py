import pytest
from app.models.tag import Tag
from app.services.tag_service import get_all_tags, delete_tag, create_tag, get_tag_by_id, update_tag
from sqlalchemy.exc import SQLAlchemyError

@pytest.fixture(scope='function')
def tag_data():
    """Provide test data for tags."""
    return {
        'name': 'Test Tag',
        'category': 'TestCategory'
    }

@pytest.fixture(scope='function')
def test_tag(db_session, tag_data):
    """Provide a test tag for use in tests."""
    tag = Tag(
        name=tag_data['name'],
        category=tag_data['category']
    )
    db_session.add(tag)
    db_session.commit()
    yield tag
    db_session.delete(tag)
    db_session.commit()

def test_get_all_tags(db_session, test_tag):
    tags = get_all_tags()
    assert len(tags) >= 1
    assert test_tag in tags

def test_delete_tag(db_session, test_tag):
    delete_tag(test_tag)
    db_session.expire_all()
    tag = db_session.query(Tag).get(test_tag.id)
    assert tag is None

def test_create_tag(db_session, tag_data):
    new_tag = create_tag(tag_data)
    assert new_tag.name == tag_data['name']
    assert new_tag.category == tag_data['category']

    db_session.expire_all()
    saved_tag = db_session.query(Tag).filter_by(name=tag_data['name']).first()
    assert saved_tag is not None
    assert saved_tag.name == tag_data['name']
    assert saved_tag.category == tag_data['category']

def test_get_tag_by_id(db_session, test_tag):
    tag = get_tag_by_id(test_tag.id)
    assert tag is not None
    assert tag.name == test_tag.name
    assert tag.category == test_tag.category

def test_update_tag(db_session, test_tag, tag_data):
    updated_data = {
        'name': 'Updated Tag',
        'category': 'UpdatedCategory'
    }
    update_tag(test_tag, updated_data)
    
    db_session.expire_all()
    tag = db_session.query(Tag).get(test_tag.id)
    assert tag.name == updated_data['name']
    assert tag.category == updated_data['category']

def test_get_tag_by_id_not_found(db_session):
    non_existent_tag_id = 9999
    tag = get_tag_by_id(non_existent_tag_id)
    assert tag is None

def test_create_tag_with_error(monkeypatch, db_session, tag_data):
    def mock_add(*args, **kwargs):
        raise SQLAlchemyError("Database error")

    monkeypatch.setattr(db_session, 'add', mock_add)

    with pytest.raises(SQLAlchemyError) as excinfo:
        create_tag(tag_data)
    assert "Database error" in str(excinfo.value)

def test_delete_tag_with_error(monkeypatch, db_session, test_tag):
    def mock_delete(*args, **kwargs):
        raise SQLAlchemyError("Database error")

    monkeypatch.setattr(db_session, 'delete', mock_delete)

    with pytest.raises(SQLAlchemyError) as excinfo:
        delete_tag(test_tag)
    assert "Database error" in str(excinfo.value)

def test_update_tag_with_error(monkeypatch, db_session, test_tag, tag_data):
    def mock_commit(*args, **kwargs):
        raise SQLAlchemyError("Database error")

    monkeypatch.setattr(db_session, 'commit', mock_commit)

    with pytest.raises(SQLAlchemyError) as excinfo:
        update_tag(test_tag, tag_data)
    assert "Database error" in str(excinfo.value)
