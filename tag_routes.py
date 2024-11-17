from flask import Blueprint, request, jsonify
from app.models.tag import Tag
from app.extensions import db

tag_bp = Blueprint('tag', __name__, url_prefix='/admin/tags')

@tag_bp.route('', methods=['POST'])
def create_tag():
    """
    Creates a new tag.
    
    Expects a JSON payload with tag details.
    
    Returns:
        jsonify: A message indicating success and the created tag's ID.
    """
    data = request.get_json()
    tag = Tag(
        name=data['name'],
        category=data['category']
    )
    db.session.add(tag)
    db.session.commit()

    return jsonify({
        'message': 'Tag created successfully',
        'tag_id': tag.id
    }), 201

@tag_bp.route('/<int:tag_id>', methods=['PUT'])
def update_tag(tag_id):
    """
    Updates an existing tag.
    
    Expects a JSON payload with updated tag details.
    
    Args:
        tag_id (int): The ID of the tag to be updated.
        
    Returns:
        jsonify: A message indicating success and the updated tag's ID.
    """
    data = request.get_json()
    tag = Tag.query.get_or_404(tag_id)

    tag.name = data['name']
    tag.category = data['category']

    db.session.commit()

    return jsonify({
        'message': 'Tag updated successfully',
        'tag_id': tag.id
    }), 200

@tag_bp.route('/<int:tag_id>', methods=['DELETE'])
def delete_tag(tag_id):
    """
    Deletes a tag.
    
    Args:
        tag_id (int): The ID of the tag to be deleted.
        
    Returns:
        jsonify: A message indicating success and the deleted tag's ID.
    """
    tag = Tag.query.get_or_404(tag_id)
    db.session.delete(tag)
    db.session.commit()

    return jsonify({
        'message': 'Tag deleted successfully',
        'tag_id': tag.id
    }), 200
