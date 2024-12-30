from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, session
from werkzeug.routing import BuildError
from flask_login import login_user, current_user, logout_user, login_required
from app.forms.user_forms import LoginForm, RegisterForm
from app.models.user import User
from app.models.audit_log import AuditLog
from app import db

public_bp = Blueprint('public', __name__)

@public_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        # Redirect based on user role
        if current_user.is_admin:
            try:
                return redirect(url_for('admin.dashboard.dashboard'))
            except BuildError:
                current_app.logger.error("Admin dashboard route not found")
                return redirect(url_for('public.index'))
        return redirect(url_for('user.profile'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            # Ensure user is active before logging in
            if not user.is_active:
                flash('Your account is inactive.', 'danger')
                return redirect(url_for('public.login'))
                
            login_user(user)
            session['_user_id'] = str(user.id)
            session['is_admin'] = user.is_admin
            session['_fresh'] = True  # Mark session as fresh
            
            # Create audit log
            try:
                AuditLog.create(
                    user_id=user.id,
                    action='login',
                    details='User logged in',
                    ip_address=request.remote_addr,
                    http_method=request.method,
                    endpoint=request.endpoint
                )
            except Exception as e:
                current_app.logger.error(f"Error creating login audit log: {str(e)}")
            
            flash('Login successful.', 'success')
            
            # Handle redirect after login
            try:
                if user.is_admin:
                    return redirect(url_for('admin.dashboard.dashboard'))
                return redirect(url_for('user.profile'))
            except BuildError:
                current_app.logger.error("Dashboard route not found")
                return redirect(url_for('public.index'))
                
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
@login_required
def logout():
    # Clear session data
    session.pop('_user_id', None)
    session.pop('is_admin', None)
    session.pop('_fresh', None)
    
    # Logout user
    logout_user()
    
    # Create audit log
    try:
        AuditLog.create(
            user_id=current_user.id,
            action='logout',
            details='User logged out',
            ip_address=request.remote_addr,
            http_method=request.method,
            endpoint=request.endpoint
        )
    except Exception as e:
        current_app.logger.error(f"Error creating logout audit log: {str(e)}")
    
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
