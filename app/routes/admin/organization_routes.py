# app/routes/admin/organization_routes.py

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required
from app.models.organization import Organization
from app.forms.admin_forms import OrganizationForm
from app.extensions import db
from app.utils import admin_required

admin_org_bp = Blueprint('admin_org', __name__, url_prefix='/admin/organizations')

@admin_org_bp.route('/')
@admin_required
def index():
    organizations = Organization.query.all()
    return render_template('admin/organizations/index.html', organizations=organizations)

@admin_org_bp.route('/create', methods=['GET', 'POST'])
@admin_required
def create():
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
    return render_template('admin/organizations/create.html', form=form)

@admin_org_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit(id):
    organization = Organization.query.get_or_404(id)
    form = OrganizationForm(obj=organization)
    if form.validate_on_submit():
        form.populate_obj(organization)
        db.session.commit()
        flash('Organization updated successfully.', 'success')
        return redirect(url_for('admin_org.index'))
    return render_template('admin/organizations/edit.html', form=form, organization=organization)

@admin_org_bp.route('/delete/<int:id>', methods=['POST'])
@admin_required
def delete(id):
    organization = Organization.query.get_or_404(id)
    db.session.delete(organization)
    db.session.commit()
    flash('Organization deleted successfully.', 'success')
    return redirect(url_for('admin_org.index'))
