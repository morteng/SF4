from .tag import Tag
from .stipend import Stipend
from .user import User
from .bot import Bot
from .notification import Notification
from .organization import Organization
from .audit_log import AuditLog

def init_models(app):
    """Initialize models with proper relationship mapping"""
    from app.extensions import db
    
    # Ensure all models are imported before creating tables
    with app.app_context():
        # Configure mapper relationships
        Tag.stipends = db.relationship(
            'Stipend',
            secondary='stipend_tag_association',
            back_populates='tags'
        )
        
        Stipend.tags = db.relationship(
            'Tag',
            secondary='stipend_tag_association',
            back_populates='stipends'
        )
        
        db.create_all()
