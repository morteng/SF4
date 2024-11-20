from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models.user import User
from app.forms.user_forms import ProfileForm
from app.services.user_service import get_user_by_id
from app.models.stipend import Stipend
from app.services.stipend_service import get_stipend_by_id

public_user_bp = Blueprint('public_user', __name__)

# Public routes
@public_user_bp.route('/')
def index():
    # Logic for the homepage
    return render_template('index.html')

@public_user_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Logic for user login
    pass

@public_user_bp.route('/logout')
@login_required
def logout():
    # Logic for user logout
    pass

@public_user_bp.route('/search')
def search_stipends():
    # Logic to search stipends
    return render_template('search.html')

@public_user_bp.route('/stipend/<int:id>')
def view_stipend(id):
    stipend = get_stipend_by_id(id)
    if stipend is None:
        flash('Stipend not found', 'danger')
        return redirect(url_for('public_user.index'))
    return render_template('stipend_detail.html', stipend=stipend)

# User-specific routes
@public_user_bp.route('/profile')
@login_required
def profile():
    user = get_user_by_id(current_user.id)
    if user is None:
        flash('User not found', 'danger')
        return redirect(url_for('public_user.index'))
    return render_template('user/profile.html', user=user)

@public_user_bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    user = get_user_by_id(current_user.id)
    if user is None:
        flash('User not found', 'danger')
        return redirect(url_for('public_user.index'))
    
    form = ProfileForm(original_username=user.username, original_email=user.email)
    if form.validate_on_submit():
        # Logic to update user profile
        pass
    
    return render_template('user/edit_profile.html', form=form, user=user)
