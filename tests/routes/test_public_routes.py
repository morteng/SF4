import pytest
from flask import url_for

def test_index_route(client):
    """Test the public index route"""
    response = client.get(url_for('public.index'))
    assert response.status_code == 200
    assert b"Welcome" in response.data

def test_login_route_accessible(client):
    """Test login route is accessible"""
    response = client.get(url_for('public.login'))
    assert response.status_code == 200
    assert b"Login" in response.data

def test_register_route_accessible(client):
    """Test registration route is accessible"""
    response = client.get(url_for('public.register'))
    assert response.status_code == 200
    assert b"Register" in response.data
```
```python
tests\routes\test_public_routes_integration.py
<<<<<<< SEARCH
