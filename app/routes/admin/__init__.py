from flask import Blueprint, render_template
from app.services.stipend_service import get_stipend_count
from app.services.bot_service import get_recent_logs

# Import sub-blueprints
from .bot_routes import admin_bot_bp
from .organization_routes import org_bp
from .stipend_routes import stipend_bp
from .tag_routes import tag_bp
from .user_routes import user_bp

admin_dashboard_bp = Blueprint('admin_dashboard', __name__)

@admin_dashboard_bp.route('/data')
def data():
    stipend_count = get_stipend_count()
    bot_logs = get_recent_logs()
    return render_template('_dashboard_data.html', stipend_count=stipend_count, bot_logs=bot_logs)

# Register sub-blueprints
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
admin_bp.register_blueprint(admin_dashboard_bp)
admin_bp.register_blueprint(admin_bot_bp)  # Ensure this line is correct
admin_bp.register_blueprint(org_bp)  # Corrected import name
admin_bp.register_blueprint(stipend_bp)
admin_bp.register_blueprint(tag_bp)
admin_bp.register_blueprint(user_bp)

def register_admin_blueprints(app):
    app.register_blueprint(admin_bp)
