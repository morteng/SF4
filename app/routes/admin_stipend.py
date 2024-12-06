from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required
from app.forms.admin_forms import StipendForm
from app.services.stipend_service import create_stipend, get_stipend_by_id, get_all_stipends, update_stipend, delete_stipend
from app.extensions import db

admin_stipend_bp = Blueprint('admin_stipend', __name__)

@admin_stipend_bp.route('/stipends/create', methods=['GET', 'POST'])
@login_required
def create():
    """Handle creation of a new stipend."""
    form = StipendForm()
    if form.validate_on_submit():
        stipend = create_stipend(form.data)
        return redirect(url_for('admin_stipend.index'))
    return render_template('admin/stipend_form.html', form=form)

@admin_stipend_bp.route('/stipends/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    """Handle deletion of a stipend by ID."""
    stipend = get_stipend_by_id(id)
    if stipend:
        db.session.delete(stipend)
        db.session.commit()
        return redirect(url_for('admin_stipend.index'))
    return "Stipend not found", 404

@admin_stipend_bp.route('/stipends/', methods=['GET'])
@login_required
def index():
    """Display the dashboard for stipends."""
    stipends = get_all_stipends()
    return render_template('admin/stipend_dashboard.html', stipends=stipends)

@admin_stipend_bp.route('/stipends/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    """Handle updating a stipend by ID."""
    stipend = get_stipend_by_id(id)
    if not stipend:
        return "Stipend not found", 404
    form = StipendForm(obj=stipend)
    if form.validate_on_submit():
        update_stipend(stipend, form.data)
        return redirect(url_for('admin_stipend.index'))
    return render_template('admin/stipend_form.html', form=form)
