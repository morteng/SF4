from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request, current_app
from app.constants import FLASH_CATEGORY_INFO
from flask_login import login_required
from app.constants import FLASH_MESSAGES, FLASH_CATEGORY_SUCCESS, FLASH_CATEGORY_ERROR
from app.forms.admin_forms import StipendForm, OrganizationForm
from app.services.organization_service import get_organization_by_id
from app.models.stipend import Stipend
from app.services.stipend_service import get_stipend_by_id, delete_stipend, get_all_stipends, create_stipend, update_stipend
from app.extensions import db
from app.models.organization import Organization
from app.models.stipend import Stipend
from app.services.stipend_service import get_stipend_by_id, delete_stipend, get_all_stipends, create_stipend, update_stipend
import logging
from app.utils import admin_required, flash_message
 
admin_stipend_bp = Blueprint('stipend', __name__, url_prefix='/stipends')
 
@admin_stipend_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    print("\n[DEBUG] Starting stipend create route")
    form = StipendForm()
    
    if form.validate_on_submit():
        try:
            print("[DEBUG] Form validated successfully")
            # Create a copy of form data and remove unnecessary fields
            stipend_data = {k: v for k, v in form.data.items() if k not in ('submit', 'csrf_token')}
            print(f"[DEBUG] Prepared stipend_data: {stipend_data}")
            
            # Handle empty application deadline
            if 'application_deadline' in stipend_data:
                print(f"[DEBUG] Processing application_deadline: {stipend_data['application_deadline']}")
                if stipend_data['application_deadline'] == '':
                    print("[DEBUG] Empty application_deadline, setting to None")
                    stipend_data['application_deadline'] = None
                
            # Create the stipend
            print("[DEBUG] Creating stipend")
            stipend = create_stipend(stipend_data)
            if not stipend:
                print("[DEBUG] Stipend creation failed")
                flash_message(FLASH_MESSAGES["CREATE_STIPEND_ERROR"], FLASH_CATEGORY_ERROR)
                return render_template('admin/stipends/form.html', form=form), 200
            
            print(f"[DEBUG] Stipend created successfully: {stipend}")
            flash_message(FLASH_MESSAGES["CREATE_STIPEND_SUCCESS"], FLASH_CATEGORY_SUCCESS)
            return redirect(url_for('admin.stipend.index'))
            
        except Exception as e:
            print(f"[DEBUG] Exception occurred: {str(e)}")
            db.session.rollback()
            logging.error(f"Failed to create stipend: {e}")
            if "date format" in str(e).lower() or "deadline cannot be" in str(e).lower():
                flash_message(str(e), FLASH_CATEGORY_ERROR)
            else:
                flash_message(FLASH_MESSAGES["CREATE_STIPEND_ERROR"], FLASH_CATEGORY_ERROR)
            return render_template('admin/stipends/form.html', form=form), 200
    
    print("[DEBUG] Rendering form")
    return render_template('admin/stipends/form.html', form=form), 200
 
 
@admin_stipend_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(id):
    stipend = get_stipend_by_id(id)
    if not stipend:
        flash_message(FLASH_MESSAGES["STIPEND_NOT_FOUND"], FLASH_CATEGORY_ERROR)
        return '', 200

    form = StipendForm(obj=stipend)
    
    if request.method == 'POST' and form.validate_on_submit():
        try:
            # Prepare update data
            stipend_data = {k: v for k, v in form.data.items() if k not in ('submit', 'csrf_token')}
            
            # Handle organization_id
            if 'organization_id' in stipend_data:
                organization = get_organization_by_id(stipend_data['organization_id'])
                if not organization:
                    flash_message(FLASH_MESSAGES["INVALID_ORGANIZATION"], FLASH_CATEGORY_ERROR)
                    return render_template('admin/stipends/form.html', form=form, stipend=stipend), 200
            
            # Update the stipend
            if update_stipend(stipend, stipend_data, session=db.session):
                flash_message(FLASH_MESSAGES["UPDATE_STIPEND_SUCCESS"], FLASH_CATEGORY_SUCCESS)
                return redirect(url_for('admin.stipend.index'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Failed to update stipend: {e}")
            flash_message(str(e) if str(e) else FLASH_MESSAGES["UPDATE_STIPEND_ERROR"], FLASH_CATEGORY_ERROR)
    
    return render_template('admin/stipends/form.html', form=form, stipend=stipend), 200
 
 
 
@admin_stipend_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(id):
    stipend = get_stipend_by_id(id)
    if not stipend:
        flash_message(FLASH_MESSAGES["STIPEND_NOT_FOUND"], FLASH_CATEGORY_ERROR)
        if request.headers.get('HX-Request'):
            return render_template('_flash_messages.html'), 404
        return redirect(url_for('admin.stipend.index'))
    
    try:
        delete_stipend(stipend.id)
        flash_message(FLASH_MESSAGES["DELETE_STIPEND_SUCCESS"], FLASH_CATEGORY_SUCCESS)
        if request.headers.get('HX-Request'):
            return render_template('_flash_messages.html'), 200
        return redirect(url_for('admin.stipend.index'))
    except Exception as e:
        db.session.rollback()
        logging.error(f"Failed to delete stipend: {e}")
        flash_message(FLASH_MESSAGES["DELETE_STIPEND_ERROR"], FLASH_CATEGORY_ERROR)
        if request.headers.get('HX-Request'):
            return render_template('_flash_messages.html'), 500
        return redirect(url_for('admin.stipend.index'))
 
 
@admin_stipend_bp.route('/', methods=['GET'])
@login_required
@admin_required
def index():
    page = request.args.get('page', 1, type=int)
    stipends = get_all_stipends().paginate(page=page, per_page=10, error_out=False)
    logging.info(f"Stipends fetched: {stipends.items}")  # Debug: Log the fetched stipends
    return render_template('admin/stipends/index.html', stipends=stipends)
 
@admin_stipend_bp.route('/paginate/<int:page>', methods=['GET'])
@login_required
@admin_required
def paginate(page):
    stipends = get_all_stipends().paginate(page=page, per_page=10, error_out=False)
    return render_template('admin/stipends/_stipends_table.html', stipends=stipends)
