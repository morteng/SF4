import pytest
from app.models.bot import Bot

def test_create_bot_unauthorized(client):
    """Test creating bot without authentication fails"""
    response = client.post('/admin/bots', json={
        'name': 'Test Bot',
        'description': 'Test Description',
        'status': 'active'
    })
    assert response.status_code == 401

def test_create_bot_authorized(client, admin_token):
    """Test creating bot with admin authentication succeeds"""
    response = client.post('/admin/bots', 
        json={
            'name': 'Test Bot',
            'description': 'Test Description',
            'status': 'active'
        },
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert response.status_code == 201
    assert 'bot_id' in response.json

def test_update_bot_authorized(client, admin_token, test_bot):
    """Test updating bot with admin authentication"""
    response = client.put(f'/admin/bots/{test_bot.id}',
        json={
            'name': 'Updated Bot',
            'description': 'Updated Description',
            'status': 'inactive'
        },
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert response.status_code == 200
    assert Bot.query.get(test_bot.id).name == 'Updated Bot'

def test_delete_bot_authorized(client, admin_token, test_bot):
    """Test deleting bot with admin authentication"""
    response = client.delete(f'/admin/bots/{test_bot.id}',
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert response.status_code == 200
    assert Bot.query.get(test_bot.id) is None

def test_create_bot_missing_fields(client, admin_token):
    """Test creating bot with missing fields fails"""
    response = client.post('/admin/bots', 
        json={
            'name': 'Test Bot',
            'status': 'active'
        },
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert response.status_code == 400

def test_create_bot_invalid_name(client, admin_token):
    """Test creating bot with invalid name fails"""
    response = client.post('/admin/bots', 
        json={
            'name': '',
            'description': 'Test Description',
            'status': 'active'
        },
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert response.status_code == 400
