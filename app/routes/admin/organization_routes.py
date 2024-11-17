from flask import Blueprint, request, jsonify
from app.models.organization import Organization
from app.extensions import db
from app.utils import admin_required

org_bp = Blueprint('organization', __name__, url_prefix='/admin/organizations')

@org_bp.route('', methods=['POST'])
@admin_required
def create_organization():
    """
    Creates a new organization.
    
    Expects a JSON payload with organization details.
    
    Returns:
        jsonify: A message indicating success and the created organization's ID.
    """
    data = request.get_json()
    organization = Organization(
        name=data['name'],
        description=data['description'],
        homepage_url=data['homepage_url']
    )
    db.session.add(organization)
    db.session.commit()

    return jsonify({
        'message': 'Organization created successfully',
        'organization_id': organization.id
    }), 201

@org_bp.route('/<int:organization_id>', methods=['PUT'])
@admin_required
def update_organization(organization_id):
    """
    Updates an existing organization.
    
    Expects a JSON payload with updated organization details.
    
    Args:
        organization_id (int): The ID of the organization to be updated.
        
    Returns:
        jsonify: A message indicating success and the updated organization's ID.
    """
    data = request.get_json()
    organization = Organization.query.get_or_404(organization_id)

    organization.name = data['name']
    organization.description = data['description']
    organization.homepage_url = data['homepage_url']

    db.session.commit()

    return jsonify({
        'message': 'Organization updated successfully',
        'organization_id': organization.id
    }), 200

@org_bp.route('/<int:organization_id>', methods=['DELETE'])
@admin_required
def delete_organization(organization_id):
    """
    Deletes an organization.
    
    Args:
        organization_id (int): The ID of the organization to be deleted.
        
    Returns:
        jsonify: A message indicating success and the deleted organization's ID.
    """
    organization = Organization.query.get_or_404(organization_id)
    db.session.delete(organization)
    db.session.commit()

    return jsonify({
        'message': 'Organization deleted successfully',
        'organization_id': organization.id
    }), 200
