from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, current_user, logout_user, login_required
from app.forms.user_forms import LoginForm, RegisterForm
from app.models.user import User
from app.models.audit_log import AuditLog
from app import db

public_bp = Blueprint('public', __name__)

@public_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        # Redirect to admin dashboard if user is an admin, else redirect to user profile
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard.dashboard'))  
        else:
            return redirect(url_for('user.profile'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        password = form.password.data
        if user and user.check_password(password):
            print(f"Login success for: {user.username}")
            login_user(user)
            
            # Create audit log for successful login
            try:
                AuditLog.create(
                    user_id=user.id,
                    action='login',
                    object_type='user',
                    object_id=user.id,
                    ip_address=request.remote_addr,
                    http_method=request.method,
                    endpoint=request.endpoint
                )
            except Exception as e:
                current_app.logger.error(f"Error creating login audit log: {str(e)}")
            
            flash('Login successful.', 'success')
            # Redirect to admin dashboard if user is an admin, else redirect to user profile
            if current_user.is_admin:
                flash('Admin logged in.', 'success')
                return redirect(url_for('admin.dashboard.dashboard'))  
            else:
                return redirect(url_for('user.profile'))
        else:
            print("Login failed.")
            flash('Invalid username or password.', 'danger')
    return render_template('login.html', form=form)

from app.models.tag import Tag
from app.models.stipend import Stipend

@public_bp.route('/')
def index():
    tags = Tag.query.order_by(Tag.name).all()
    stipends = Stipend.query.filter_by(open_for_applications=True).order_by(Stipend.application_deadline).limit(10).all()
    return render_template('index.html', stipends=stipends, tags=tags)

@public_bp.route('/filter', methods=['POST'])
def filter_stipends():
    tag_ids = request.form.getlist('tags[]')
    search_term = request.form.get('search', '').strip()
    
    query = Stipend.query.filter_by(open_for_applications=True)
    
    if tag_ids:
        query = query.filter(Stipend.tags.any(Tag.id.in_(tag_ids)))
    
    if search_term:
        query = query.filter(
            Stipend.name.ilike(f'%{search_term}%') |
            Stipend.description.ilike(f'%{search_term}%')
        )
    
    stipends = query.order_by(Stipend.application_deadline).all()
    
    return render_template('_stipend_list.html', stipends=stipends)

@public_bp.route('/logout')
@login_required  # Ensure the user is logged in to log out
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('public.index'))

# Add register route
@public_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('user.profile'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('public.login'))
    return render_template('register.html', form=form)
