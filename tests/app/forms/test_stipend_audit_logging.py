import pytest
from datetime import datetime
from app.models.stipend import Stipend
from app.models.audit_log import AuditLog
from app.models.organization import Organization
from app.models.tag import Tag
from app.extensions import db
from app.forms.admin_forms import StipendForm

def test_audit_log_on_create(app, form_data, test_db):
    """Test audit log creation on stipend create"""
    with app.test_request_context():
        tag_choices = [(tag.id, tag.name) for tag in Tag.query.all()]
        
        form = StipendForm(data=form_data)
        form.tags.choices = tag_choices
        if form.validate():
            stipend = Stipend(**form.data)
            db.session.add(stipend)
            db.session.commit()
            
            update_data = {
                'name': 'Updated Stipend Name',
                'summary': 'Updated summary',
                'description': 'Updated description',
                'tags': [tag_choices[0][0]]
            }
            
            stipend.update(update_data)
            
            logs = AuditLog.query.filter_by(object_type='Stipend', object_id=stipend.id).order_by(AuditLog.timestamp.desc()).all()
            assert len(logs) >= 2
            
            update_log = logs[0]
            assert update_log is not None
            assert update_log.action == 'update_stipend'
            assert update_log.details_before is not None
            assert update_log.details_after is not None
            
            create_log = logs[1]
            assert create_log is not None
            assert create_log.action == 'create_stipend'
            assert create_log.details_after is not None
