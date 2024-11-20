from flask import Blueprint, render_template, redirect, url_for, flash, request
from ..forms.user_forms import RegistrationForm, LoginForm
from ..models.user import User
from flask_login import login_user

visitor_bp = Blueprint('visitor', __name__)

@visitor_bp.route('/')
def index():
    # Logic for the homepage
    return render_template('index.html')

@visitor_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('user.profile'))
        else:
            flash('Invalid username or password')
    return render_template('login.html', form=form)

@visitor_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            flash('Username already exists')
            return redirect(url_for('visitor.register'))
        new_user = User(username=form.username.data, email=form.email.data)
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('user.profile'))
    return render_template('register.html', form=form)

@visitor_bp.route('/search')
def search_stipends():
    query = request.args.get('query', '')
    if query:
        stipends = Stipend.query.filter(Stipend.name.contains(query) | Stipend.summary.contains(query)).all()
    else:
        stipends = []
    return render_template('search.html', stipends=stipends, query=query, title='Search Results')

@visitor_bp.route('/stipend/<int:id>')
def view_stipend(id):
    from app.services.stipend_service import get_stipend_by_id
    stipend = get_stipend_by_id(id)
    if stipend is None:
        flash('Stipend not found', 'danger')
        return redirect(url_for('visitor.index'))
    return render_template('stipend_detail.html', stipend=stipend, title=stipend.name)