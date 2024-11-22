from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.forms.user_forms import ProfileForm
from app.services.user_service import update_user
from app import user_bp

@user_bp.route('/profile', methods=['GET'])
@login_required
def profile():
    return render_template('user/profile.html', user=current_user)

@user_bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = ProfileForm(original_username=current_user.username, original_email=current_user.email)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        update_user(current_user)
        flash('Your changes have been saved.')
        return redirect(url_for('routes.user.profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('user/edit_profile.html', form=form)
