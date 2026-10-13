from flask import Blueprint, request, jsonify
from src.controllers import task_controller

task_bp = Blueprint('tasks', __name__)


@task_bp.route('/tasks', methods=['GET'])
def get_tasks():
    return jsonify(task_controller.get_all_tasks()), 200


@task_bp.route('/tasks/search', methods=['GET'])
def search_tasks():
    results = task_controller.search_tasks(
        query=request.args.get('q', ''),
        status=request.args.get('status', ''),
        priority=request.args.get('priority', ''),
        user_id=request.args.get('user_id', ''),
    )
    return jsonify(results), 200


@task_bp.route('/tasks/stats', methods=['GET'])
def task_stats():
    return jsonify(task_controller.get_task_stats()), 200


@task_bp.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    data, error = task_controller.get_task(task_id)
    if error:
        return jsonify({'error': error}), 404
    return jsonify(data), 200


@task_bp.route('/tasks', methods=['POST'])
def create_task():
    body = request.get_json()
    if not body:
        return jsonify({'error': 'Invalid data'}), 400
    data, error = task_controller.create_task(body)
    if error:
        status = 404 if 'not found' in error.lower() else 400
        return jsonify({'error': error}), status
    return jsonify(data), 201


@task_bp.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    body = request.get_json()
    if not body:
        return jsonify({'error': 'Invalid data'}), 400
    data, error = task_controller.update_task(task_id, body)
    if error:
        status = 404 if 'not found' in error.lower() else 400
        return jsonify({'error': error}), status
    return jsonify(data), 200


@task_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    ok, error = task_controller.delete_task(task_id)
    if error:
        return jsonify({'error': error}), 404
    return jsonify({'message': 'Task deleted successfully'}), 200
