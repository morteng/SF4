from flask import url_for
import pytest

def test_dashboard_data(client, app):
    response = client.get(url_for('admin_dashboard.data'))
    assert response.status_code == 200
    assert b'Stipend Count:' in response.data
    assert b'Recent Bot Logs:' in response.data
