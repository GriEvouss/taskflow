from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.stats_service import StatsService

stats_bp = Blueprint('stats', __name__)


@stats_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    user_id = int(get_jwt_identity())
    data = StatsService.get_dashboard_stats(user_id)
    return jsonify(data), 200
