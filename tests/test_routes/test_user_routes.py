import pytest

def test_user_index(client):
    response = client.get('/user/index')
    assert response.status_code == 200
    assert b'"message": "User index page"' in response.data

def test_user_profile(client):
    user_id = 1
    response = client.get(f'/user/profile/{user_id}')
    assert response.status_code == 200
    assert f'Profile for user {user_id}'.encode() in response.data
