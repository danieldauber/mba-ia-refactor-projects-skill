from flask import Blueprint, request, jsonify
from src.controllers import user_controller

user_bp = Blueprint('users', __name__)


@user_bp.route('/users', methods=['GET'])
def get_users():
    return jsonify(user_controller.get_all_users()), 200


@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    data, error = user_controller.get_user(user_id)
    if error:
        return jsonify({'error': error}), 404
    return jsonify(data), 200


@user_bp.route('/users', methods=['POST'])
def create_user():
    body = request.get_json()
    if not body:
        return jsonify({'error': 'Invalid data'}), 400
    data, error = user_controller.create_user(body)
    if error:
        status = 409 if 'already registered' in error.lower() else 400
        return jsonify({'error': error}), status
    return jsonify(data), 201


@user_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    body = request.get_json()
    if not body:
        return jsonify({'error': 'Invalid data'}), 400
    data, error = user_controller.update_user(user_id, body)
    if error:
        if 'not found' in error.lower():
            return jsonify({'error': error}), 404
        if 'already registered' in error.lower():
            return jsonify({'error': error}), 409
        return jsonify({'error': error}), 400
    return jsonify(data), 200


@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    ok, error = user_controller.delete_user(user_id)
    if error:
        return jsonify({'error': error}), 404
    return jsonify({'message': 'User deleted successfully'}), 200


@user_bp.route('/users/<int:user_id>/tasks', methods=['GET'])
def get_user_tasks(user_id):
    data, error = user_controller.get_user_tasks(user_id)
    if error:
        return jsonify({'error': error}), 404
    return jsonify(data), 200


@user_bp.route('/login', methods=['POST'])
def login():
    body = request.get_json()
    if not body:
        return jsonify({'error': 'Invalid data'}), 400
    data, error = user_controller.login(body)
    if error:
        status = 403 if 'inactive' in error.lower() else 401
        return jsonify({'error': error}), status
    return jsonify(data), 200
