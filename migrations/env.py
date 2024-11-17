from app import create_app
from app.extensions import db

# Create an application context to use the app's configuration
app = create_app('default')
app.app_context().push()

target_metadata = db.metadata
