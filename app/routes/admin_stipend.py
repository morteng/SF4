from flask import Blueprint, render_template, request, redirect, url_for
from app.forms.admin_forms import StipendForm
from app.services.stipend_service import create_stipend, get_stipend_by_id, get_all_stipends, update_stipend

admin_stipend_bp = Blueprint('stipend_bp', __name__)

@admin_stipend_bp.route('/stipends/create', methods=['GET', 'POST'])
def create():
    form = StipendForm()
    if form.validate_on_submit():
        stipend = create_stipend(form.data)
        return redirect(url_for('stipend_bp.index'))
    return render_template('admin/stipend_form.html', form=form)

@admin_stipend_bp.route('/stipends/delete/<int:id>', methods=['POST'])
def delete(id):
    stipend = get_stipend_by_id(id)
    if stipend:
        # Implement stipend deletion logic here
        return redirect(url_for('stipend_bp.index'))
    return "Stipend not found", 404

@admin_stipend_bp.route('/stipends/', methods=['GET'])
def index():
    stipends = get_all_stipends()
    return render_template('admin/stipend_dashboard.html', stipends=stipends)

@admin_stipend_bp.route('/stipends/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    stipend = get_stipend_by_id(id)
    if not stipend:
        return "Stipend not found", 404
    form = StipendForm(obj=stipend)
    if form.validate_on_submit():
        update_stipend(stipend, form.data)
        return redirect(url_for('stipend_bp.index'))
    return render_template('admin/stipend_form.html', form=form)
