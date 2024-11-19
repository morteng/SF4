# app/routes/public_user_routes.py

from flask import Blueprint, render_template, request
from app.models.stipend import Stipend
from app.models.tag import Tag

public_user_bp = Blueprint('public_user', __name__)

@public_user_bp.route('/')
def index():
    # Fetch popular stipends or any default display
    stipends = Stipend.query.limit(10).all()
    tags = Tag.query.all()
    return render_template('user/index.html', stipends=stipends, tags=tags)

@public_user_bp.route('/search')
def search():
    query = request.args.get('query', '')
    selected_tags = request.args.getlist('tags')
    stipends = Stipend.query.filter(
        Stipend.name.contains(query)
    ).join(Stipend.tags).filter(
        Tag.name.in_(selected_tags)
    ).all()
    return render_template('user/search_results.html', stipends=stipends)

@public_user_bp.route('/stipend/<int:id>')
def stipend_detail(id):
    stipend = Stipend.query.get_or_404(id)
    return render_template('user/stipend_detail.html', stipend=stipend)
