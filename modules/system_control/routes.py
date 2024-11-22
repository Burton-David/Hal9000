# File: hal9000/modules/system_control/routes.py

from flask import Blueprint, jsonify, request, render_template
from .system_manager import SystemManager
import traceback

bp = Blueprint('system', __name__)
system_manager = SystemManager()

@bp.route('/')
def index():
    return render_template('pages/system_control.html')

@bp.route('/info')
def system_info():
    try:
        info = system_manager.get_system_info()
        return jsonify(info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/status')
def system_status():
    try:
        status = system_manager.get_system_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/execute', methods=['POST'])
def execute_command():
    try:
        data = request.json
        command = data.get('command')
        args = data.get('args')
        
        if not command:
            return jsonify({'error': 'No command specified'}), 400
            
        result = system_manager.execute_command(command, args)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500