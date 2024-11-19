# app/routes/user/user_routes.py

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app.forms.user_forms import ProfileForm
from app.extensions import db

user_bp = Blueprint('user', __name__, url_prefix='/user')

@user_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        form.populate_obj(current_user)
        if form.password.data:
            current_user.set_password(form.password.data)
        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('user.profile'))
    return render_template('user/profile.html', form=form)
