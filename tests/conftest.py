import tempfile
import shutil
import pytest
from app import create_app, db as _db

@pytest.fixture(scope='module')
def app():
    db_fd, db_fname = tempfile.mkstemp()
    config = {
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_fname}",
        "TESTING": True
    }
    
    app = create_app(config)
    with app.app_context():
        _db.create_all()
        
    yield app
    
    _db.session.remove()
    os.close(db_fd)
    os.unlink(db_fname)
