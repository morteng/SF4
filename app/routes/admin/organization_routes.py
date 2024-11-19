from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.models.organization import Organization
from app.forms.admin_forms import OrganizationForm
from app.services.organization_service import get_organization_by_id, delete_organization

admin_org_bp = Blueprint('admin_org', __name__, url_prefix='/admin/organizations')

@admin_org_bp.route('/')
@login_required
def index():
    from app import db  # Import db within the function to avoid circular imports
    organizations = Organization.query.all()
    return render_template('admin/organization_index.html', organizations=organizations)

@admin_org_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = OrganizationForm()
    if form.validate_on_submit():
        organization = Organization(
            name=form.name.data,
            description=form.description.data,
            homepage_url=form.homepage_url.data
        )
        from app import db  # Import db within the function to avoid circular imports
        db.session.add(organization)
        db.session.commit()
        flash('Organization created successfully!', 'success')
        return redirect(url_for('admin_org.index'))
    return render_template('admin/organization_form.html', form=form, title='Create Organization')

@admin_org_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    organization = get_organization_by_id(id)
    if not organization:
        flash('Organization not found!', 'danger')
        return redirect(url_for('admin_org.index'))
    
    form = OrganizationForm(obj=organization)
    if form.validate_on_submit():
        organization.name = form.name.data
        organization.description = form.description.data
        organization.homepage_url = form.homepage_url.data
        from app import db  # Import db within the function to avoid circular imports
        db.session.commit()
        flash('Organization updated successfully!', 'success')
        return redirect(url_for('admin_org.index'))
    return render_template('admin/organization_form.html', form=form, title='Edit Organization')

@admin_org_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    organization = get_organization_by_id(id)
    if not organization:
        flash('Organization not found!', 'danger')
        return redirect(url_for('admin_org.index'))
    
    try:
        delete_organization(organization)
        from app import db  # Import db within the function to avoid circular imports
        db.session.commit()
        flash('Organization deleted successfully!', 'success')
    except Exception as e:
        flash(f'Failed to delete organization: {str(e)}', 'danger')
    
    return redirect(url_for('admin_org.index'))
