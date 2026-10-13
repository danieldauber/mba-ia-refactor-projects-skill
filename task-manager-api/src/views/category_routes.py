from flask import Blueprint, request, jsonify
from src.controllers import category_controller

category_bp = Blueprint('categories', __name__)


@category_bp.route('/categories', methods=['GET'])
def get_categories():
    return jsonify(category_controller.get_all_categories()), 200


@category_bp.route('/categories', methods=['POST'])
def create_category():
    body = request.get_json()
    if not body:
        return jsonify({'error': 'Invalid data'}), 400
    data, error = category_controller.create_category(body)
    if error:
        return jsonify({'error': error}), 400
    return jsonify(data), 201


@category_bp.route('/categories/<int:cat_id>', methods=['PUT'])
def update_category(cat_id):
    body = request.get_json()
    if not body:
        return jsonify({'error': 'Invalid data'}), 400
    data, error = category_controller.update_category(cat_id, body)
    if error:
        return jsonify({'error': error}), 404
    return jsonify(data), 200


@category_bp.route('/categories/<int:cat_id>', methods=['DELETE'])
def delete_category(cat_id):
    ok, error = category_controller.delete_category(cat_id)
    if error:
        return jsonify({'error': error}), 404
    return jsonify({'message': 'Category deleted'}), 200
