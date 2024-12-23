from flask import Blueprint, render_template, redirect, url_for, request, current_app
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
from app.extensions import db
import logging
from app.utils import admin_required, flash_message

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
            
            # Add the stipend to the session and commit
            db.session.add(stipend)
            db.session.commit()
            
            flash_message(FLASH_MESSAGES["CREATE_STIPEND_SUCCESS"], FLASH_CATEGORY_SUCCESS)
            
            if request.headers.get('HX-Request'):
                stipends = get_all_stipends()
                return render_template('admin/stipends/_stipend_list.html', stipends=stipends, form=form), 200
            
            return redirect(url_for('admin.stipend.index'))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Failed to create stipend: {e}")
            flash_message(FLASH_MESSAGES["CREATE_STIPEND_ERROR"], FLASH_CATEGORY_ERROR)
            if request.headers.get('HX-Request'):
                return render_template('_flash_messages.html'), 200
            else:
                return render_template('admin/stipends/form.html', form=form), 200
    
    for field, errors in form.errors.items():
        for error in errors:
            logging.error(f"Flashing error: {error}")
            if "date format" in error.lower():
                flash_message(FLASH_MESSAGES["INVALID_DATE_FORMAT"], FLASH_CATEGORY_ERROR)
            else:
                flash_message(error, FLASH_CATEGORY_ERROR)  # Flash each specific validation error
    
    if request.headers.get('HX-Request'):
        return render_template('_flash_messages.html'), 200
    else:
        return render_template('admin/stipends/form.html', form=form), 200


@admin_stipend_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(id):
    stipend = get_stipend_by_id(id)
    if not stipend:
        flash_message(FLASH_MESSAGES["STIPEND_NOT_FOUND"], FLASH_CATEGORY_ERROR)
        return redirect(url_for('admin.stipend.index'))
    
    if request.method == 'POST':
        form = StipendForm(request.form)
        if form.validate_on_submit():
            try:
                # Exclude 'submit' and 'csrf_token' from form data
                stipend_data = {k: v for k, v in form.data.items() if k not in ('submit', 'csrf_token')}
                update_stipend(stipend, stipend_data, session=db.session)
                
                flash_message(FLASH_MESSAGES["UPDATE_STIPEND_SUCCESS"], FLASH_CATEGORY_SUCCESS)
                return redirect(url_for('admin.stipend.index'))
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"Failed to update stipend: {e}")
                flash_message(FLASH_MESSAGES["UPDATE_STIPEND_ERROR"], FLASH_CATEGORY_ERROR)
                if request.headers.get('HX-Request'):
                    return render_template('_flash_messages.html'), 200
                else:
                    return render_template('admin/stipends/form.html', form=form, stipend=stipend), 200
    else:
        form = StipendForm(obj=stipend)
    
    if form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                logging.error(f"Flashing error: {error}")
                if "date format" in error.lower():
                    flash_message(FLASH_MESSAGES["INVALID_DATE_FORMAT"], FLASH_CATEGORY_ERROR)
                else:
                    flash_message(error, FLASH_CATEGORY_ERROR)  # Flash each specific validation error
    
    return render_template('admin/stipends/form.html', form=form, stipend=stipend), 200



@admin_stipend_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(id):
    stipend = get_stipend_by_id(id)
    if not stipend:
        flash_message(FLASH_MESSAGES["STIPEND_NOT_FOUND"], FLASH_CATEGORY_ERROR)
        return redirect(url_for('admin.stipend.index'))
    
    try:
        delete_stipend(stipend.id)
        db.session.commit()
        
        flash_message(FLASH_MESSAGES["DELETE_STIPEND_SUCCESS"], FLASH_CATEGORY_SUCCESS)
        return redirect(url_for('admin.stipend.index'))
    except Exception as e:
        db.session.rollback()
        logging.error(f"Failed to delete stipend: {e}")
        flash_message(FLASH_MESSAGES["DELETE_STIPEND_ERROR"], FLASH_CATEGORY_ERROR)
        return redirect(url_for('admin.stipend.index'))


@admin_stipend_bp.route('/', methods=['GET'])
@login_required
@admin_required
def index():
    stipends = get_all_stipends()
    return render_template('admin/stipends/index.html', stipends=stipends)
