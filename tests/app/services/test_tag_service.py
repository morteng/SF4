import pytest
from app.models.tag import Tag
from app.services.tag_service import get_all_tags, delete_tag, create_tag, get_tag_by_id, update_tag
from sqlalchemy.exc import SQLAlchemyError
from wtforms.validators import ValidationError

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
    db_session.rollback()  # Ensure a clean session
    tag = Tag(
        name=tag_data['name'],
        category=tag_data['category']
    )
    db_session.add(tag)
    db_session.commit()
    yield tag

    # Teardown: Attempt to delete the tag and rollback if an error occurs
    try:
        db_session.delete(tag)
        db_session.commit()
    except SQLAlchemyError as e:
        print(f"Failed to delete test tag during teardown: {e}")
        db_session.rollback()

def test_get_all_tags(db_session, test_tag):
    tags = get_all_tags()
    assert len(tags) >= 1
    assert test_tag in tags

def test_delete_tag(db_session, test_tag):
    delete_tag(test_tag)
    db_session.expire_all()
    tag = db_session.get(Tag, test_tag.id)
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
    tag = db_session.get(Tag, test_tag.id)
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

# Additional tests for edge cases

def test_create_tag_duplicate_name(db_session, test_tag, tag_data):
    db_session.rollback()  # Ensure a clean session
    duplicate_tag_data = {
        'name': test_tag.name,
        'category': 'AnotherCategory'
    }
    with pytest.raises(SQLAlchemyError) as excinfo:
        create_tag(duplicate_tag_data)
    assert "UNIQUE constraint failed" in str(excinfo.value)

def test_update_tag_duplicate_name(db_session, test_tag, another_test_tag):
    db_session.rollback()  # Ensure a clean session
    updated_data = {
        'name': another_test_tag.name,
        'category': 'UpdatedCategory'
    }
    with pytest.raises(SQLAlchemyError) as excinfo:
        update_tag(test_tag, updated_data)
    assert "UNIQUE constraint failed" in str(excinfo.value)

@pytest.fixture(scope='function')
def another_test_tag(db_session, tag_data):
    """Provide another test tag for use in tests."""
    db_session.rollback()  # Ensure a clean session
    another_tag = Tag(
        name='Another Test Tag',
        category=tag_data['category']
    )
    db_session.add(another_tag)
    db_session.commit()
    yield another_tag

    # Teardown: Attempt to delete the tag and rollback if an error occurs
    try:
        db_session.delete(another_tag)
        db_session.commit()
    except SQLAlchemyError as e:
        print(f"Failed to delete test tag during teardown: {e}")
        db_session.rollback()

# New tests for edge cases

def test_update_tag_with_empty_name(db_session, test_tag):
    updated_data = {
        'name': '',
        'category': 'UpdatedCategory'
    }
    with pytest.raises(ValidationError) as excinfo:
        update_tag(test_tag, updated_data)
    assert "Name cannot be empty." in str(excinfo.value)

def test_update_tag_with_empty_category(db_session, test_tag):
    updated_data = {
        'name': 'Updated Tag Name',
        'category': ''
    }
    with pytest.raises(ValidationError) as excinfo:
        update_tag(test_tag, updated_data)
    assert "Category cannot be empty." in str(excinfo.value)

def test_create_tag_with_empty_name(db_session):
    invalid_tag_data = {
        'name': '',
        'category': 'TestCategory'
    }
    with pytest.raises(ValidationError) as excinfo:
        create_tag(invalid_tag_data)
    assert "Name cannot be empty." in str(excinfo.value)

def test_create_tag_with_empty_category(db_session):
    invalid_tag_data = {
        'name': 'Test Tag',
        'category': ''
    }
    with pytest.raises(ValidationError) as excinfo:
        create_tag(invalid_tag_data)
    assert "Category cannot be empty." in str(excinfo.value)
