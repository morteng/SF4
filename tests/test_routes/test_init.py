def test_create_app_default():
    from app import create_app
    app = create_app()
    assert app is not None
    assert app.config['DEBUG'] is False  # Assuming default config has DEBUG=False

def test_create_app_testing():
    from app import create_app
    app = create_app('testing')
    assert app.config['TESTING'] is True
    assert app.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:///:memory:'

def test_create_app_development():
    from app import create_app
    app = create_app('development')
    assert app.config['DEBUG'] is True  # Assuming development config has DEBUG=True

def test_create_app_production():
    from app import create_app
    app = create_app('production')
    assert app.config['DEBUG'] is False  # Assuming production config has DEBUG=False
