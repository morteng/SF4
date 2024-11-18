from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.services.stipend_service import get_stipend_by_id, update_stipend

stipend_bp = Blueprint('admin_stipend', __name__)

@stipend_bp.route('/stipends')
@login_required
def list_stipends():
    # Your code here
    pass

@stipend_bp.route('/stipends/<int:stipend_id>')
@login_required
def stipend_details(stipend_id):
    stipend = get_stipend_by_id(stipend_id)
    if not stipend:
        flash('Stipend not found', 'danger')
        return redirect(url_for('admin_stipend.list_stipends'))
    return render_template('admin/stipend_details.html', stipend=stipend)

@stipend_bp.route('/stipends/<int:stipend_id>/update', methods=['POST'])
@login_required
def update_stipend_route(stipend_id):
    name = request.form.get('name')
    summary = request.form.get('summary')
    description = request.form.get('description')
    homepage_url = request.form.get('homepage_url')
    application_procedure = request.form.get('application_procedure')
    eligibility_criteria = request.form.get('eligibility_criteria')
    application_deadline = request.form.get('application_deadline')
    open_for_applications = request.form.get('open_for_applications') == 'on'
    if update_stipend(stipend_id, name, summary, description, homepage_url, application_procedure, eligibility_criteria, application_deadline, open_for_applications):
        flash('Stipend updated successfully', 'success')
    else:
        flash('Failed to update stipend', 'danger')
    return redirect(url_for('admin_stipend.stipend_details', stipend_id=stipend_id))

# Add other routes as needed
