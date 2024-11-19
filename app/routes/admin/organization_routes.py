from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.services.organization_service import get_organization_by_id, update_organization, create_organization, delete_organization

organization_bp = Blueprint('admin_organization', __name__)

@organization_bp.route('/organizations', methods=['GET'])
@login_required
def list_organizations():
    from app.services.organization_service import list_all_applied for the `list_all_stipends` function.
2. **Filtering Logic**: Implement filtering logic in the `search_stipends` route based on the query parameter.

Let's update these files accordingly.

### Updated `app/routes/public_user_routes.py`

```python
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
    stipends = list_all_stipends(query=query)  # Pass the query to filter stipends
    return jsonify(stipends=[stipend.to_dict() for stipend in stipends])

@public_user_bp.route('/stipend/<int:stipend_id>')
def stipend_details(stipend_id):
    stipend = get_stipend_by_id(stipend_id)
    if stipend is None:
        return render_template('errors/404.html'), 404
    return render_template('user/stipend_detail.html', stipend=stipend)

print("Public user blueprint initialized successfully.")
