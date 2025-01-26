import pytest
from app.models.stipend import Stipend
from app import db

def test_stipend_tags_default_to_empty_list():
    stipend = Stipend(name="Test Stipend")
    db.session.add(stipend)
    db.session.commit()
    assert stipend.tags == []

def test_stipend_tags_can_be_updated():
    stipend = Stipend(name="Test Stipend", tags=["education", "scholarship"])
    db.session.add(stipend)
    db.session.commit()
    
    # Update tags
    stipend.tags = ["grant", "funding"]
    db.session.commit()
    
    assert stipend.tags == ["grant", "funding"]

def test_stipend_tags_validate_to_list():
    stipend = Stipend(name="Test Stipend", tags="not a list")
    with pytest.raises(TypeError):
        db.session.add(stipend)
        db.session.commit()
