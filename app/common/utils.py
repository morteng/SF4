import os
import logging
from flask import Blueprint

logger = logging.getLogger(__name__)

class BaseBlueprint:
    def __init__(self, name, import_name, url_prefix=None, template_folder=None):
        self.blueprint = Blueprint(
            name=name,
            import_name=import_name,
            url_prefix=url_prefix,
            template_folder=template_folder
        )
        
    def register_route(self, rule, endpoint=None, view_func=None, **options):
        self.blueprint.add_url_rule(rule, endpoint, view_func, **options)
        
    def get_blueprint(self):
        return self.blueprint

def configure_logging(app):
    """Configure logging for the application."""
    app.logger.setLevel(app.config['LOG_LEVEL'])
    
    # Rotating file handler
    file_handler = RotatingFileHandler(
        app.config['LOG_FILE'],
        maxBytes=app.config['LOG_FILE_SIZE'],
        backupCount=app.config['LOG_BACKUP_COUNT']
    )
    
    # Formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    
    # Add handler to logger
    app.logger.addHandler(file_handler)
