import pytest
from flask import url_for
from app.models.stipend import Stipend
from datetime import datetime

@pytest.fixture
def htmx_headers():
    return {'HX-Request': 'true'}

def test_htmx_stipend_create(client, db_session, htmx_headers):
    # Test HTMX create form rendering
    response = client.get(url_for('admin.stipend.create'), headers=htmx_headers)
    assert response.status_code == 200
    assert b'<form' in response.data

def test_htmx_stipend_create_submission(client, db_session, htmx_headers):
    test_data = {
        'name': 'HTMX Test',
        'application_deadline': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
        'csrf_token': client.get(url_for('admin.stipend.create')).data.decode('utf-8').split('name="csrf_token" value="')[1].split('"')[0]
    }
    
    response = client.post(
        url_for('admin.stipend.create'),
        data=test_data,
        headers=htmx_headers
    )
    assert response.status_code == 200
    assert b'HTMX Test' in response.data

def test_htmx_stipend_edit(client, db_session, htmx_headers):
    # Create test stipend
    stipend = Stipend(name='Edit Test', application_deadline=datetime.utcnow())
    db_session.add(stipend)
    db_session.commit()
    
    # Test HTMX edit form
    response = client.get(
        url_for('admin.stipend.edit', id=stipend.id),
        headers=htmx_headers
    )
    assert response.status_code == 200
    assert b'Edit Test' in response.data

def test_htmx_stipend_delete(client, db_session, htmx_headers):
    # Create test stipend
    stipend = Stipend(name='Delete Test', application_deadline=datetime.utcnow())
    db_session.add(stipend)
    db_session.commit()
    
    # Test HTMX delete
    response = client.post(
        url_for('admin.stipend.delete', id=stipend.id),
        headers=htmx_headers
    )
    assert response.status_code == 200
    assert db_session.query(Stipend).count() == 0
