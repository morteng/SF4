from flask import Blueprint

blueprint = Blueprint('main', __name__)

@blueprint.route('/')
def index():
    return "Welcome to the Stipend Discovery Website!"
