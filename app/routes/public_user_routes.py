from flask import Blueprint, render_template, request, jsonify
from app.services.stipend_service import list_all_stipends, get_stipend_by_id

public_user_bp = Blueprint('public_user', __name__)

@public_user_bp.route('/')
def homepage():
    # Fetch popular stipends and tags for filtering
    stipends = list_all_stipends()
    return render_template('user/index.html', stipends=stipends)

@public_user_bp.route('/search')
def search_stipends():
    query = request.args.get('query', '')
    stipends = list_all_stipends()  # This should be filtered based on the query
    return jsonify(stipends=[stipend.to_dict() for stipend in stipends])

@public_user_bp.route('/stipend/<int:stipend_id>')
def stipend_details(stipend_id):
    stipend = get_stipend_by_id(stipend_id)
    if stipend is None:
        return render_template('errors/404.html'), 404
    return render_template('user/stipend_detail.html', stipend=stipend)

print("Public user blueprint initialized successfully.")
