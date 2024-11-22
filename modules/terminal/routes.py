from flask import Blueprint, jsonify

# Make sure this uses 'terminal' as the name
bp = Blueprint('terminal', __name__)

@bp.route('/')
def index():
    return jsonify({'status': 'Terminal Operational'})