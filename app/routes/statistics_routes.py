from flask import Blueprint, jsonify
from app.services.statistics_generator import StatisticsGenerator

stats_bp = Blueprint('stats', __name__)

@stats_bp.route('/global', methods=['GET'])
def global_stats():
    generator = StatisticsGenerator()
    return jsonify(generator.generate_global_stats())
