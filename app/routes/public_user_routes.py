from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models.user import User
from app.forms.user_forms import ProfileForm
from app.services.user_service import get_user_by_id
from app.models.stipend import Stipend
from app.services.stipend_service import get_stipend_by_id

public_user_bp = Blueprint('public_user', __name__)

# Remove user-specific routes from here
