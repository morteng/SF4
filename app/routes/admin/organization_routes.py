from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required
from app.forms.admin_forms import OrganizationForm
from app.services.organization_service import get_organization_by_id, delete_organization, get_all_organizations, create_organization
from werkzeug.exceptions import abort

org_bp = Blueprint('admin_org', __name__, url_prefix='/admin/organizations')

@org_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        data = request.get_json()
        if not data:
            abort(400, description='No input data provided.')
        
        # Validate required fields
        name = data.get('name')
        description = data.get('description')
        homepage_url = data.get('homepage_url')
        
        if not name or not homepage_url:
            abort(400, description='Name and Homepage URL are required.')
        
        # Create the organization
        new_org = create_organization({
            'name': name,
            'description': description,
            'homepage_url': homepage_url
        })
        
        return jsonify(new_org.to_dict()), 201
    else:
        form = OrganizationForm()
        return render_template('admin/organization/create.html', form=form)

@org_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    organization = get_organization_by_id(id)
    if organization:
        delete_organization(organization)
        flash(f'Organization {organization.name} deleted.', 'success')
    else:
        flash('Organization not found.', 'danger')
    return redirect(url_for('admin_org.index'))

@org_bp.route('/', methods=['GET'])
@login_required
def index():
    organizations = get_all_organizations()
    return render_template('admin/organization/index.html', organizations=organizations)
