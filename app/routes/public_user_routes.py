from flask import Blueprint, render_template, redirect, url_for, flash, request

public_bp = Blueprint('public', __name__)

# Public routes
@public_bp.route('/')
def index():
    # Logic for the homepage
    return render_template('index.html')

@public_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Logic for user login
    pass

@public_bp.route('/search')
def search_stipends():
    # Logic to search stipends
    return render_template('search.html')

@public_bp.route('/stipend/<int:id>')
def view_stipend(id):
    from app.services.stipend_service import get_stipend_by_id
    stipend = get_stipend_by_id(id)
    if stipend is None:
        flash('Stipend not found', 'danger')
        return redirect(url_for('public.index'))
    return render_template('stipend_detail.html', stipend=stipend)
