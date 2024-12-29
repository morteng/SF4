import pytest
from datetime import datetime
from app.models.stipend import Stipend
from app.models.organization import Organization
from app.models.tag import Tag
from app.extensions import db

def test_stipend_create_operation(app, form_data, test_db):
    """Test CRUD create operation"""
    with app.test_request_context():
        form = StipendForm()
        csrf_token = form.csrf_token.current_token
        form_data['csrf_token'] = csrf_token
        
        tag_choices = [(tag.id, tag.name) for tag in Tag.query.all()]
        
        # Test valid creation
        form = StipendForm(data=form_data, meta={'csrf': False})
        form.tags.choices = tag_choices
        
        if not form.validate():
            print("Validation errors:", form.errors)
        assert form.validate() is True
        
        # Test missing required fields
        for field in ['name', 'summary', 'description']:
            invalid_data = form_data.copy()
            del invalid_data[field]
            form = StipendForm(data=invalid_data)
            form.tags.choices = tag_choices
            assert form.validate() is False
            assert field in form.errors

def test_stipend_update_operation(app, form_data, test_db):
    """Test CRUD update operation"""
    with app.test_request_context():
        form = StipendForm()
        csrf_token = form.csrf_token.current_token
        form_data['csrf_token'] = csrf_token
        
        tag_choices = [(tag.id, tag.name) for tag in Tag.query.all()]
        
        # Create initial stipend
        form = StipendForm(data=form_data, meta={'csrf': False})
        form.tags.choices = tag_choices
        
        deadline = datetime.strptime(form.application_deadline.data, '%Y-%m-%d %H:%M:%S')
            
        stipend = Stipend.create({
            'name': form.name.data,
            'summary': form.summary.data,
            'description': form.description.data,
            'homepage_url': form.homepage_url.data,
            'application_procedure': form.application_procedure.data,
            'eligibility_criteria': form.eligibility_criteria.data,
            'application_deadline': deadline,
            'organization_id': form.organization_id.data,
            'open_for_applications': form.open_for_applications.data,
            'tags': [Tag.query.get(tag_id) for tag_id in form.tags.data]
        }, user_id=1)
        
        # Update stipend
        updated_data = form_data.copy()
        updated_data['name'] = 'Updated Stipend Name'
        updated_data['tags'] = [tag_choices[0][0]]
        
        update_form = StipendForm(data=updated_data, meta={'csrf': False})
        update_form.tags.choices = tag_choices
        
        if not update_form.validate():
            print("Validation errors:", update_form.errors)
        assert update_form.validate() is True
        
        stipend.update({
            'name': update_form.name.data,
            'summary': update_form.summary.data,
            'description': update_form.description.data,
            'tags': [Tag.query.get(tag_id) for tag_id in update_form.tags.data]
        }, user_id=1)
