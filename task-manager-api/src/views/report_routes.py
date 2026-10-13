from flask import Blueprint, request, jsonify
from src.controllers import report_controller

report_bp = Blueprint('reports', __name__)


@report_bp.route('/reports/summary', methods=['GET'])
def summary_report():
    return jsonify(report_controller.get_summary_report()), 200


@report_bp.route('/reports/user/<int:user_id>', methods=['GET'])
def user_report(user_id):
    data, error = report_controller.get_user_report(user_id)
    if error:
        return jsonify({'error': error}), 404
    return jsonify(data), 200
