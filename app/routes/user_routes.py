from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from ..forms.user_forms import ProfileForm, RegistrationForm  # Add RegistrationForm import
from ..models.user import User
from ..services.user_service import get_user_by_id
from ..models.stipend import Stipend  # Import Stipend model
from ..services.stipend_service import get_stipend_by_id  # Import get_stipend_by_id function

user_bp = Blueprint('user', __name__, url_prefix='/user')

@user_bp.route('/register', methods=['GET', 'POST'])  # Add this route
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists')
            return redirect(url_for('user.register'))
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        from app import db
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('user.profile'))
    return render_template('register.html')

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('user.profile'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@user_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('public.index'))

@user_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm(original_username=current_user.username, original_email=current_user.email)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        from app import db
        db.session.commit()
        flash('Your changes have been saved.')
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('profile.html', form=form)

# Move user-specific routes here

@user_bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = ProfileForm(original_username=current_user.username, original_email=current_user.email)
    if form.validate_on_submit():
        if form.username.data != current_user.username and User.query.filter_by(username=form.username.data).first():
            flash('Username already exists!', 'danger')
            return redirect(url_for('user.edit_profile'))
        
        if form.email.data != current_user.email and User.query.filter_by(email=form.email.data).first():
            flash('Email already exists!', 'danger')
            return redirect(url_for('user.edit_profile'))
        
        current_user.username = form.username.data
        current_user.email = form.email.data
        
        if form.password.data:
            current_user.set_password(form.password.data)
        
        from app import db
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('user.profile'))
    return render_template('edit_profile.html', form=form, title='Edit Profile')

# Homepage route
@user_bp.route('/')
def homepage():
    # Fetch popular stipends or any other data you want to display on the homepage
    stipends = Stipend.query.all()  # Example: fetch all stipends
    return render_template('homepage.html', stipends=stipends, title='Home')

# Stipend search route
@user_bp.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    if query:
        stipends = Stipend.query.filter(Stipend.name.contains(query) | Stipend.summary.contains(query)).all()
    else:
        stipends = []
    return render_template('search.html', stipends=stipends, query=query, title='Search Results')

# Stipend details route
@user_bp.route('/stipend/<int:id>')
def stipend_details(id):
    stipend = get_stipend_by_id(id)
    if stipend is None:
        flash('Stipend not found!', 'danger')
        return redirect(url_for('user.homepage'))
    return render_template('stipend_detail.html', stipend=stipend, title=stipend.name)
