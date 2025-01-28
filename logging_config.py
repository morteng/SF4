from configs.config import Configuration

def configure_logging(app):
    """Configure logging for the application"""
    config = Configuration(app.env)
    config.configure_logging(app)
