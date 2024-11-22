from flask import Blueprint, jsonify

# Make sure this uses 'dashboard' as the name
bp = Blueprint('dashboard', __name__)

@bp.route('/')
def index():
    return jsonify({'status': 'Dashboard Operational'})