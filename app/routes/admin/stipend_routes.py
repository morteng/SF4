from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required
from app.constants import FLASH_MESSAGES, FLASH_CATEGORY_SUCCESS, FLASH_CATEGORY_ERROR
from app.forms.admin_forms import StipendForm
from app.services.stipend_service import (
    get_stipend_by_id,
    delete_stipend,
    get_all_stipends,
    create_stipend,
    update_stipend
)
from app.models.stipend import Stipend
from app.extensions import db, db_session  # Ensure this matches how db_session is defined or imported
import logging
from app.utils import admin_required  # Import the admin_required decorator

admin_stipend_bp = Blueprint('stipend', __name__, url_prefix='/stipends')

@admin_stipend_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    form = StipendForm()
    
    if form.validate_on_submit():
        try:
            stipend_data = {k: v for k, v in form.data.items() if k != 'submit' and k != 'csrf_token'}
            logging.info(f"Stipend data to be created: {stipend_data}")
            stipend = Stipend(**stipend_data)
            result = create_stipend(stipend)
            
            if not result:
                flash(FLASH_MESSAGES["CREATE_STIPEND_ERROR"], FLASH_CATEGORY_ERROR)
                if request.headers.get('HX-Request'):
                    return render_template('admin/stipends/_stipend_form.html', form=form), 200
                else:
                    return render_template('admin/stipends/form.html', form=form), 200
            
            flash(FLASH_MESSAGES["CREATE_STIPEND_SUCCESS"], FLASH_CATEGORY_SUCCESS)
            
            if request.headers.get('HX-Request'):
                stipends = get_all_stipends()
                return render_template('admin/stipends/_stipend_list.html', stipends=stipends, form=form), 200
            
            return redirect(url_for('admin.stipend.index'))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Failed to create stipend: {e}")
            flash(FLASH_MESSAGES["CREATE_STIPEND_ERROR"], FLASH_CATEGORY_ERROR)
            if request.headers.get('HX-Request'):
                return render_template('admin/stipends/_stipend_form.html', form=form), 200
            else:
                return render_template('admin/stipends/form.html', form=form), 200
    
    for field, errors in form.errors.items():
        for error in errors:
            logging.error(f"Flashing error: {error}")
    
    if request.headers.get('HX-Request'):
        return render_template('admin/stipends/_stipend_form.html', form=form), 200
    else:
        return render_template('admin/stipends/form.html', form=form), 200


@admin_stipend_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(id):
    stipend = get_stipend_by_id(id)
    if not stipend:
        flash(FLASH_MESSAGES["STIPEND_NOT_FOUND"], FLASH_CATEGORY_ERROR)
        return redirect(url_for('admin.stipend.index'))
    
    form = StipendForm(obj=stipend, original_name=stipend.name)
    
    if form.validate_on_submit():
        try:
            form.populate_obj(stipend)
            
            db.session.commit()
            flash(FLASH_MESSAGES["UPDATE_STIPEND_SUCCESS"], FLASH_CATEGORY_SUCCESS)
            return redirect(url_for('admin.stipend.index'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Failed to update stipend: {e}")
            flash(FLASH_MESSAGES["UPDATE_STIPEND_ERROR"], FLASH_CATEGORY_ERROR)
            return render_template('admin/stipends/form.html', form=form, stipend=stipend), 200
    
    if form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                flash(FLASH_MESSAGES["UPDATE_STIPEND_FORM_ERROR"], FLASH_CATEGORY_ERROR)
    
    return render_template('admin/stipends/form.html', form=form, stipend=stipend), 200


@admin_stipend_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(id):
    stipend = get_stipend_by_id(id)
    if not stipend:
        flash(FLASH_MESSAGES["GENERIC_ERROR"], FLASH_CATEGORY_ERROR)
        return redirect(url_for('admin.stipend.index'))
    
    try:
        delete_stipend(stipend.id)
        db.session.commit()
        
        flash(FLASH_MESSAGES["DELETE_STIPEND_SUCCESS"], FLASH_CATEGORY_SUCCESS)
        return redirect(url_for('admin.stipend.index'))
    except Exception as e:
        db.session.rollback()
        logging.error(f"Failed to delete stipend: {e}")
        flash(FLASH_MESSAGES["DELETE_STIPEND_ERROR"], FLASH_CATEGORY_ERROR)
        return redirect(url_for('admin.stipend.index'))


@admin_stipend_bp.route('/', methods=['GET'])
@login_required
@admin_required
def index():
    stipends = get_all_stipends()
    return render_template('admin/stipends/index.html', stipends=stipends)
