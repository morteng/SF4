from flask import Blueprint, redirect, url_for, flash, render_template, request
from flask_login import login_required
from app.models.organization import Organization
from app.services.organization_service import get_organization_by_id, delete_organization
from app.extensions import db  # Import db here

admin_org_bp = Blueprint('admin_org', __name__, url_prefix='/organizations')

@admin_org_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    organization = get_organization_by_id(id)
    if organization:
        delete_organization(organization)
        flash('Organization deleted successfully.', 'success')
    else:
        flash('Organization not found.', 'danger')
    return redirect(url_for('admin_org.index'))

@admin_org_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    from app.forms.admin_forms import OrganizationForm
    form = OrganizationForm()
    if form.validate_on_submit():
        organization = Organization(
            name=form.name.data,
            description=form.description.data,
            homepage_url=form.homepage_url.data
        )
        db.session.add(organization)
        db.session.commit()
        flash('Organization created successfully.', 'success')
        return redirect(url_for('admin_org.index'))
    return render_template('admin/organization_form.html', form=form)

@admin_org_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    organization = get_organization_by_id(id)
    if not organization:
        flash('Organization not found.', 'danger')
        return redirect(url_for('admin_org.index'))
    
    from app.forms.admin_forms import OrganizationForm
    form = OrganizationForm(obj=organization)
    if form.validate_on_submit():
        organization.name = form.name.data
        organization.description = form.description.data
        organization.homepage_url = form.homepage_url.data
        db.session.commit()
        flash('Organization updated successfully.', 'success')
        return redirect(url_for('admin_org.index'))
    return render_template('admin/organization_form.html', form=form)
