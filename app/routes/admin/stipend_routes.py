from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.forms.admin_forms import StipendForm
from app.services.stipend_service import get_stipend_by_id, delete_stipend, get_all_stipends, create_stipend, update_stipend
from app.models.stipend import Stipend

admin_stipend_bp = Blueprint('stipend', __name__, url_prefix='/stipends')

@admin_stipend_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = StipendForm()
    if form.validate_on_submit():
        valid_fields = {key: value for key, value in form.data.items() if hasattr(Stipend, key)}
        stipend = Stipend(**valid_fields)
        new_stipend = create_stipend(stipend)
        flash('Stipend created successfully.', 'success')

        if request.headers.get('HX-Request'):
            # Render only the stipend list or a fragment for HTMX
            stipends = get_all_stipends()
            return render_template('admin/stipends/_stipend_list.html', stipends=stipends), 200
        
        return redirect(url_for('admin.stipend.index'))
    
    print(f"Form errors: {form.errors}")
    return render_template('admin/stipend_form.html', form=form)

@admin_stipend_bp.route('/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update(id):
    stipend = get_stipend_by_id(id)  # Use session.get instead of get
    if not stipend:
        flash('Stipend not found!', 'danger')
        return redirect(url_for('admin.stipend.index'))
    
    form = StipendForm(obj=stipend)
    
    if request.method == 'POST' and form.validate_on_submit():
        form.populate_obj(stipend)
        update_stipend(stipend)
        
        flash('Stipend updated successfully!', 'success')
        return redirect(url_for('admin.stipend.index'))
    
    return render_template('admin/stipend_form.html', form=form)

@admin_stipend_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    stipend = get_stipend_by_id(id)  # Use session.get instead of get
    if not stipend:
        flash('Stipend not found!', 'danger')
        return redirect(url_for('admin.stipend.index'))
    
    delete_stipend(stipend)
    
    flash('Stipend deleted successfully!', 'success')
    return redirect(url_for('admin.stipend.index'))

@admin_stipend_bp.route('/', methods=['GET'])
@login_required
def index():
    stipends = get_all_stipends()
    return render_template('admin/stipends/index.html', stipends=stipends)
