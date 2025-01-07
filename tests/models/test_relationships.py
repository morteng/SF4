import pytest
from app.models import Stipend, Tag, Organization
from app.extensions import db

@pytest.fixture
def init_db():
    """Initialize test database with relationships"""
    db.create_all()
    yield
    db.drop_all()

def test_stipend_tag_relationship(init_db):
    """Test Stipend-Tag many-to-many relationship"""
    # Create test data
    org = Organization(name="Test Org")
    stipend = Stipend(name="Test Stipend", organization=org)
    tag1 = Tag(name="Test Tag 1")
    tag2 = Tag(name="Test Tag 2")
    
    # Add relationships
    stipend.tags.append(tag1)
    stipend.tags.append(tag2)
    
    db.session.add_all([org, stipend, tag1, tag2])
    db.session.commit()
    
    # Verify relationships
    assert len(stipend.tags) == 2
    assert tag1 in stipend.tags
    assert tag2 in stipend.tags
    assert stipend in tag1.stipends
    assert stipend in tag2.stipends
    assert stipend.organization == org

def test_tag_stipend_relationship(init_db):
    """Test Tag-Stipend many-to-many relationship"""
    # Create test data
    tag = Tag(name="Test Tag")
    stipend1 = Stipend(name="Test Stipend 1")
    stipend2 = Stipend(name="Test Stipend 2")
    
    # Add relationships
    tag.stipends.append(stipend1)
    tag.stipends.append(stipend2)
    
    db.session.add(tag)
    db.session.commit()
    
    # Verify relationships
    assert len(tag.stipends) == 2
    assert stipend1 in tag.stipends
    assert stipend2 in tag.stipends
    assert tag in stipend1.tags
    assert tag in stipend2.tags
