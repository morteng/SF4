from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required
from app.controllers.base_crud_controller import BaseCrudController

class AdminBaseController(BaseCrudController):
    def __init__(self, service, entity_name, form_class, template_dir):
        super().__init__(service, entity_name, form_class, template_dir)
        self.admin_bp = Blueprint(f'{entity_name}_admin', __name__, 
                                template_folder=f'templates/admin/{self.template_dir}')
        
    def _register_routes(self):
        self.admin_bp.add_url_rule('/', view_func=self.index, methods=['GET'])
        self.admin_bp.add_url_rule('/create', view_func=self.create, methods=['GET', 'POST'])
        # Add other common routes here
        
    def index(self):
        items = self.service.get_all()
        return render_template(f'{self.template_dir}/index.html', items=items)
