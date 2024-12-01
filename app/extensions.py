# tests/test_example.py
from app.extensions import db  # Ensure db is imported from app.extensions

def test_example(client):
    response = client.get('/')
    assert response.status_code == 200
