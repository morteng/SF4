from flask import Blueprint, render_template, redirect, url_for, flash, request
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
            stipend = Stipend(
                name=form.name.data,
                summary=form.summary.data,
                description=form.description.data,
                homepage_url=form.homepage_url.data,
                application_procedure=form.application_procedure.data,
                eligibility_criteria=form.eligibility_criteria.data,
                application_deadline=form.application_deadline.data,
                open_for_applications=form.open_for_applications.data
            )
            create_stipend(stipend)
            db.session.commit()
            flash('Stipend created successfully.', 'success')
            
            if request.headers.get('HX-Request'):
                # Render only the stipend list or a fragment for HTMX
                stipends = get_all_stipends()
                return render_template('admin/stipends/_stipend_list.html', stipends=stipends, form=form), 200
            
            return redirect(url_for('admin.stipend.index'))
        except Exception as e:
            db.session.rollback()  # Explicitly rollback session on failure
            logging.error(f"Failed to create stipend: {e}")
    
    # Handle form validation failure
    if request.headers.get('HX-Request'):
        # Return only the targeted container for HTMX
        return render_template('admin/stipends/_stipend_form.html', form=form), 200
    else:
        # Render the full page with form and errors for non-HTMX requests
        return render_template('admin/stipends/create.html', form=form), 200


@admin_stipend_bp.route('/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update(id):
    stipend = get_stipend_by_id(id)  # Use session.get instead of get
    if not stipend:
        flash('Stipend not found!', 'danger')
        return redirect(url_for('admin.stipend.index'))
    
    form = StipendForm(obj=stipend, original_name=stipend.name)  # Set original_name to the current stipend's name
    
    if form.validate_on_submit():
        form.populate_obj(stipend)  # Use this to populate the stipend object
        try:
            update_stipend(stipend, stipend.__dict__)
            
            flash('Stipend updated successfully!', 'success')
            return redirect(url_for('admin.stipend.index'))
        except Exception as e:
            db.session.rollback()  # Explicitly rollback session on failure
            logging.error(f"Failed to update stipend: {e}")
    
    return render_template('admin/stipends/form.html', form=form)

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
