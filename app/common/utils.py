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
