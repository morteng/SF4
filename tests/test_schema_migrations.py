import pytest
from app.extensions import db
from app.models.stipend import Stipend
from sqlalchemy.dialects.postgresql import JSONB

def test_tags_column_type():
    """Verify tags column is JSONB type"""
    column = Stipend.__table__.c.tags
    assert isinstance(column.type, JSONB), "Tags column should be JSONB type"

def test_tags_data_migration():
    """Test that tags data was migrated correctly"""
    # Create test stipend with numeric tags
    with db.engine.connect() as connection:
        connection.execute("""
            INSERT INTO stipend (name, tags)
            VALUES ('Test Stipend', '[1, 2, 3]'::jsonb)
        """)
    
    # Verify data
    stipend = Stipend.query.filter_by(name='Test Stipend').first()
    assert stipend.tags == [1, 2, 3], "Tags should be properly converted to JSONB array"
    
    # Cleanup
    db.session.delete(stipend)
    db.session.commit()

def test_tags_null_handling():
    """Test NULL values are handled correctly"""
    stipend = Stipend(name='Null Tags Test')
    db.session.add(stipend)
    db.session.commit()
    
    assert stipend.tags is None, "NULL tags should be allowed"
    
    # Cleanup
    db.session.delete(stipend)
    db.session.commit()
