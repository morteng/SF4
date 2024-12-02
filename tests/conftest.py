from flask import Blueprint, jsonify

greeting_bp = Blueprint('greeting', __name__)

@greeting_bp.route('/greet', methods=['GET'])
def greet():
    return jsonify({"message": "Hey there!"})
