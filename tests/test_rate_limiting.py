import pytest
from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

def test_rate_limiting_setup(app):
    assert 'limiter' in app.extensions
    limiter = app.extensions['limiter']
    assert limiter.enabled is True
    assert limiter._storage is not None

@pytest.mark.parametrize('endpoint,limit', [
    ('create', '10 per minute'),
    ('update', '10 per minute'),
    ('delete', '5 per minute')
])
def test_rate_limits(app, endpoint, limit):
    service = app.extensions['services']['stipend']
    assert service.rate_limits[endpoint] == limit
