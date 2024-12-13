from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required
from app.forms.admin_forms import StipendForm
from app.services.stipend_service import (
    get_stipend_by_id,
    delete_stipend,
    get_all_stipends,
    create_stipend,
    update_stipend
)
from app.models.stipend import Stipend
from app.extensions import db  # Import db
import logging  # Import logging

admin_stipend_bp = Blueprint('stipend', __name__, url_prefix='/stipends')

@admin_stipend_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = StipendForm()
    
    if form.validate_on_submit():
        try:
            stipend_data = {k: v for k, v in form.data.items() if k != 'submit'}
            stipend = Stipend(**stipend_data)
            result = create_stipend(stipend)
            if not result:
                raise ValueError("Stipend creation failed due to invalid input.")
            
            if request.headers.get('HX-Request'):
                stipends = get_all_stipends()
                return render_template('admin/stipends/_stipend_list.html', stipends=stipends, form=form), 200
            
            return redirect(url_for('admin.stipend.index'))
        except ValueError as ve:
            flash(str(ve), 'danger')
            if request.headers.get('HX-Request'):
                return render_template('admin/stipends/_stipend_form.html', form=form), 200
            else:
                return render_template('admin/stipends/form.html', form=form), 200
        except Exception as e:
            db.session.rollback()  # Explicitly rollback session on failure
            logging.error(f"Failed to create stipend: {e}")
            flash('Failed to create stipend. Please try again.', 'danger')
            if request.headers.get('HX-Request'):
                return render_template('admin/stipends/_stipend_form.html', form=form), 200
            else:
                return render_template('admin/stipends/form.html', form=form), 200
    
    # Handle form validation failure
    if request.headers.get('HX-Request'):
        # Return only the targeted container for HTMX
        return render_template('admin/stipends/_stipend_form.html', form=form), 200
    else:
        # Render the full page with form and errors for non-HTMX requests
        return render_template('admin/stipends/form.html', form=form), 200


@admin_stipend_bp.route('/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update(id):
    stipend = get_stipend_by_id(id)  # Use session.get instead of get
    if not stipend:
        flash('Stipend not found!', 'danger')
        return redirect(url_for('admin.stipend.index'))
    
    form = StipendForm(obj=stipend, original_name=stipend.name)  # Set original_name to the current stipend's name
    
    if form.validate_on_submit():
        try:
            
            # Populate other fields from the form
            form.populate_obj(stipend)
            stipend.open_for_applications = 'open_for_applications' in request.form
            
            update_stipend(stipend, stipend.__dict__)
            db.session.commit()
            flash('Stipend updated successfully!', 'success')
            return redirect(url_for('admin.stipend.index'))
        except Exception as e:
            db.session.rollback()  # Explicitly rollback session on failure
            current_app.logger.error(f"Failed to update stipend: {e}")
            flash('Failed to update stipend', 'danger')
            return render_template('admin/stipends/form.html', form=form, stipend=stipend), 200
    
    # Ensure the form is re-rendered with errors and a 200 status code
    return render_template('admin/stipends/form.html', form=form, stipend=stipend), 200


@admin_stipend_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    stipend = get_stipend_by_id(id)  # Use session.get instead of get
    if not stipend:
        flash('Stipend not found!', 'danger')
        return redirect(url_for('admin.stipend.index'))
    
    try:
        delete_stipend(stipend.id)
        db.session.commit()
        
        flash('Stipend deleted successfully!', 'success')
        return redirect(url_for('admin.stipend.index'))
    except Exception as e:
        db.session.rollback()  # Explicitly rollback session on failure
        logging.error(f"Failed to delete stipend: {e}")
        flash('An error occurred while deleting the stipend.', 'danger')
        return redirect(url_for('admin.stipend.index'))


@admin_stipend_bp.route('/', methods=['GET'])
@login_required
def index():
    stipends = get_all_stipends()
    return render_template('admin/stipends/index.html', stipends=stipends)
