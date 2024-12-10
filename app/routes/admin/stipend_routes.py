from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.forms.admin_forms import StipendEditForm, StipendForm
from app.models.stipend import Stipend
from app.services.stipend_service import create_stipend, get_stipend_by_id, update_stipend, delete_stipend, get_all_stipends
from app.extensions import db  # Import the db object

admin_stipend_bp = Blueprint('admin_stipend', __name__, url_prefix='/stipends')

@admin_stipend_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = StipendForm()
    
    if request.method == 'POST' and form.validate_on_submit():
        stipend = Stipend()
        form.populate_obj(stipend)  # Automatically maps form data
        
        if create_stipend(stipend):
            flash('Stipend created successfully!', 'success')
            return redirect(url_for('admin_stipend.index'))
        else:
            flash('Stipend with this name already exists.', 'danger')
    else:
        print(f"Form errors: {form.errors}")  # Debugging statement
    
    return render_template('admin/stipend_form.html', form=form)

@admin_stipend_bp.route('/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update(id):
    stipend = db.session.get(Stipend, id)  # Use session.get instead of get
    if not stipend:
        flash('Stipend not found!', 'danger')
        return redirect(url_for('admin_stipend.index'))
    
    form = StipendEditForm(obj=stipend)
    
    if request.method == 'POST' and form.validate_on_submit():
        form.populate_obj(stipend)
        update_stipend(stipend)
        
        flash('Stipend updated successfully!', 'success')
        return redirect(url_for('admin_stipend.index'))
    
    return render_template('admin/stipend_form.html', form=form)

@admin_stipend_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    stipend = db.session.get(Stipend, id)  # Use session.get instead of get
    if not stipend:
        flash('Stipend not found!', 'danger')
        return redirect(url_for('admin_stipend.index'))
    
    delete_stipend(stipend)
    
    flash('Stipend deleted successfully!', 'success')
    return redirect(url_for('admin_stipend.index'))

@admin_stipend_bp.route('/', methods=['GET'])
@login_required
def index():
    stipends = get_all_stipends()
    return render_template('admin/stipends/index.html', stipends=stipends)
