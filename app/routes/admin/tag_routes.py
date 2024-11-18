from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.services.tag_service import get_tag_by_id, update_tag

tag_bp = Blueprint('admin_tag', __name__)

@tag_bp.route('/tags')
@login_required
def list_tags():
    # Your code here
    pass

@tag_bp.route('/tags/<int:tag_id>')
@login_required
def tag_details(tag_id):
    # Your code here
    pass

# Add other routes as needed
