from flask import Blueprint, request, jsonify, abort
from sqlalchemy.exc import IntegrityError
from app.models.user import User
from app.extensions import db
import logging

user_bp = Blueprint('user', __name__)

@user_bp.route('/register', methods=['POST'])
def register_user():
    data = request.get_json()
    
    # Validate input
    if not data or not all(key in data for key in ['username', 'email', 'password']):
        return jsonify({
            'error': 'Missing required fields',
            'message': 'Username, email, and password are required'
        }), 400
    
    try:
        # Check if user already exists
        existing_user = User.query.filter(
            (User.username == data['username']) | (User.email == data['email'])
        ).first()
        
        if existing_user:
            return jsonify({
                'error': 'User already exists',
                'message': 'A user with this username or email already exists'
            }), 409
        
        # Create new user
        new_user = User(
            username=data['username'], 
            email=data['email']
        )
        new_user.set_password(data['password'])
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            'message': "Hey! You're all set!",
            'id': new_user.id,
            'username': new_user.username,
            'email': new_user.email
        }), 201
    
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            'error': 'Registration failed',
            'message': 'Unable to register user due to a database constraint'
        }), 400
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error registering user: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred'
        }), 500

@user_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'No data provided',
                'message': 'Request must contain update data'
            }), 400

        # Partial update
        if 'username' in data:
            user.username = data['username']
        if 'email' in data:
            user.email = data['email']
        if 'password' in data:
            user.set_password(data['password'])

        db.session.commit()
        
        return jsonify({
            'message': 'User updated successfully',
            'id': user.id,
            'username': user.username,
            'email': user.email
        }), 200
    
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            'error': 'Update failed',
            'message': 'Username or email already exists'
        }), 400
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating user: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred'
        }), 500
