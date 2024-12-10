from flask import Blueprint, render_template, redirect, url_for, flash, current_app
from flask_login import login_required
from app.forms.admin_forms import UserForm
from app.services.user_service import get_user_by_id, delete_user, get_all_users, create_user, update_user
from sqlalchemy.orm import Session
from app.models.user import User

user_bp = Blueprint('admin_user', __name__, url_prefix='/users')

@user_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = UserForm()
    if form.validate_on_submit():
        try:
            new_user = create_user(form.data)
            flash('User created successfully.', 'success')
            return redirect(url_for('admin_user.index'))
        except ValueError as e:
            flash(str(e), 'danger')
    return render_template('admin/user/create.html', form=form)

@user_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    with current_app.app_context():
        session = Session(current_app.extensions['sqlalchemy'].db.engine)
        user = session.get(User, id)
        if user:
            delete_user(user)
            flash(f'User {user.username} deleted.', 'success')
        else:
            flash('User not found.', 'danger')
    return redirect(url_for('admin_user.index'))

@user_bp.route('/', methods=['GET'])
@login_required
def index():
    with current_app.app_context():
        session = Session(current_app.extensions['sqlalchemy'].db.engine)
        users = session.query(User).all()
    return render_template('admin/user/index.html', users=users)

@user_bp.route('/update/<int:id>', methods=['GET'])
@login_required
def update(id):
    user = get_user_by_id(id)  # Fetch user data
    form = UserForm(obj=user)
    return render_template('admin/user/_edit_row.html', form=form, user=user)

@user_bp.route('/update/<int:id>', methods=['POST'])
@login_required
def update_post(id):
    form = UserForm()
    if form.validate_on_submit():
        user = get_user_by_id(id)
        if user:
            update_user(user, form.data)
            flash('User updated successfully.', 'success')
        else:
            flash('User not found.', 'danger')
    return redirect(url_for('admin_user.index'))
