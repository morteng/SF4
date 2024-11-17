from flask import Blueprint, request, jsonify
from app.models.stipend import Stipend
from app.extensions import db
from app.utils import admin_required

stipend_bp = Blueprint('stipend', __name__, url_prefix='/admin/stipends')

@stipend_bp.route('', methods=['POST'])
@admin_required
def create_stipend():
    """
    Creates a new stipend.
    
    Expects a JSON payload with stipend details.
    
    Returns:
        jsonify: A message indicating success and the created stipend's ID.
    """
    data = request.get_json()
    stipend = Stipend(
        name=data['name'],
        summary=data['summary'],
        description=data['description'],
        homepage_url=data['homepage_url'],
        application_procedure=data['application_procedure'],
        eligibility_criteria=data['eligibility_criteria'],
        application_deadline=data['application_deadline'],
        open_for_applications=data['open_for_applications']
    )
    db.session.add(stipend)
    db.session.commit()

    return jsonify({
        'message': 'Stipend created successfully',
        'stipend_id': stipend.id
    }), 201

@stipend_bp.route('/<int:stipend_id>', methods=['PUT'])
@admin_required
def update_stipend(stipend_id):
    """
    Updates an existing stipend.
    
    Expects a JSON payload with updated stipend details.
    
    Args:
        stipend_id (int): The ID of the stipend to be updated.
        
    Returns:
        jsonify: A message indicating success and the updated stipend's ID.
    """
    data = request.get_json()
    stipend = Stipend.query.get_or_404(stipend_id)

    stipend.name = data['name']
    stipend.summary = data['summary']
    stipend.description = data['description']
    stipend.homepage_url = data['homepage_url']
    stipend.application_procedure = data['application_procedure']
    stipend.eligibility_criteria = data['eligibility_criteria']
    stipend.application_deadline = data['application_deadline']
    stipend.open_for_applications = data['open_for_applications']

    db.session.commit()

    return jsonify({
        'message': 'Stipend updated successfully',
        'stipend_id': stipend.id
    }), 200

@stipend_bp.route('/<int:stipend_id>', methods=['DELETE'])
@admin_required
def delete_stipend(stipend_id):
    """
    Deletes a stipend.
    
    Args:
        stipend_id (int): The ID of the stipend to be deleted.
        
    Returns:
        jsonify: A message indicating success and the deleted stipend's ID.
    """
    stipend = Stipend.query.get_or_404(stipend_id)
    db.session.delete(stipend)
    db.session.commit()

    return jsonify({
        'message': 'Stipend deleted successfully',
        'stipend_id': stipend.id
    }), 200
