def test_create_app_testing():
    from app import create_app
    app = create_app('testing')
    assert app.config['TESTING'] is True

def test_create_app_development():
    from app import create_app
    app = create_app('development')
    assert app.config['DEBUG'] is True

def test_create_app_production():
    from app import create_app
    app = create_app('production')
    assert app.config['DEBUG'] is False

# If you want to test the default configuration, ensure it has a valid config name
def test_create_app_default():
    from app import create_app
    app = create_app('default')  # Ensure 'default' is a valid config name in your config.py
    assert app.config['DEBUG'] is False
