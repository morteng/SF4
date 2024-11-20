from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required

user_bp = Blueprint('user', __name__)

@user_bp.route('/profile')
@login_required
def profile():
    # Logic to display user profile
    pass

@user_bp.route('/edit')
@login_required
def edit_profile():
    # Logic to edit user profile
    pass
