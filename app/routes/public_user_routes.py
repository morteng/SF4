from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models.user import User
from app.forms.user_forms import ProfileForm
from app.services.user_service import get_user_by_id
from app.models.stipend import Stipend
from app.services.stipend_service import get_stipend_by_id

public_user_bp = Blueprint('public_user', __name__, url_prefix='/user')

@public_user_bp.route('/profile')
@login_required
def profile():
    user = current_user
    return render_template('user/profile.html', user=user)

@public_user_bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = ProfileForm(original_username=current_user.username, original_email=current_user.email)
    if form.validate_on_submit():
        if form.username.data != current_user.username and User.query.filter_by(username=form.username.data).first():
            flash('Username already exists!', 'danger')
            return redirect(url_for('public_user.edit_profile'))
        
        if form.email.data != current_user.email and User.query.filter_by(email=form.email.data).first():
            flash('Email already exists!', 'danger')
            return redirect(url_for('public_user.edit_profile'))
        
        current_user.username = form.username.data
        current_user.email = form.email.data
        
        if form.password.data:
            current_user.set_password(form.password.data)
        
        from app import db
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('public_user.profile'))
    return render_template('user/edit_profile.html', form=form, title='Edit Profile')

# Homepage route
@public_user_bp.route('/')
def homepage():
    # Fetch popular stipends or any other data you want to display on the homepage
    stipends = Stipend.query.all()  # Example: fetch all stipends
    return render_template('user/homepage.html', stipends=stipends, title='Home')

# Stipend search route
@public_user_bp.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    if query:
        stipends = Stipend.query.filter(Stipend.name.contains(query) | Stipend.summary.contains(query)).all()
    else:
        stipends = []
    return render_template('user/search.html', stipends=stipends, query=query, title='Search Results')

# Stipend details route
@public_user_bp.route('/stipend/<int:id>')
def stipend_details(id):
    stipend = get_stipend_by_id(id)
    if stipend is None:
        flash('Stipend not found!', 'danger')
        return redirect(url_for('public_user.homepage'))
    return render_template('user/stipend_detail.html', stipend=stipend, title=stipend.name)
