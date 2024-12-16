from flask import redirect, url_for, flash, render_template
from flask_login import login_user, current_user
from .forms import LoginForm
from ..models import User

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Logged in successfully.', 'success')
            # Check if the user is an admin
            if current_user.is_admin:
                return redirect(url_for('admin.dashboard.dashboard'))
            else:
                return redirect(url_for('public.index'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html', form=form)
