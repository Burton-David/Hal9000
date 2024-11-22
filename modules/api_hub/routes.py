from flask import Blueprint, jsonify, request, render_template, current_app
from .claude_client import ClaudeClient
import traceback
import sys
import os
from werkzeug.utils import secure_filename
import base64
from datetime import datetime

bp = Blueprint('api_hub', __name__)

# Configure upload settings
UPLOAD_FOLDER = 'hal9000/uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'csv', 'json', 'xml', 'md'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ensure_upload_folder():
    """Ensure upload folder exists and is properly configured"""
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    return UPLOAD_FOLDER

def save_file(file):
    """Save uploaded file and return secure path"""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Add timestamp to filename to prevent collisions
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(ensure_upload_folder(), filename)
        file.save(filepath)
        return filepath
    return None

def read_file_content(filepath):
    """Read and return file content based on file type"""
    _, ext = os.path.splitext(filepath)
    ext = ext.lower()
    
    try:
        if ext in {'.png', '.jpg', '.jpeg'}:
            with open(filepath, 'rb') as f:
                content = base64.b64encode(f.read()).decode('utf-8')
                return f"[Image file encoded in base64: {content[:100]}...]"
        else:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                # Truncate very large files
                if len(content) > 10000:
                    return content[:10000] + "\n... [Content truncated for length]"
                return content
    except Exception as e:
        return f"Error reading file: {str(e)}"

@bp.route('/')
def index():
    return render_template('pages/api_hub.html')

@bp.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'files[]' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('files[]')
        uploaded_files = []
        
        for file in files:
            if file.filename == '':
                continue
                
            if not allowed_file(file.filename):
                continue
                
            filepath = save_file(file)
            if filepath:
                uploaded_files.append({
                    'name': os.path.basename(filepath),
                    'path': filepath,
                    'size': os.path.getsize(filepath)
                })
        
        return jsonify({
            'status': 'success',
            'files': uploaded_files
        })
        
    except Exception as e:
        print("Error in /upload endpoint:", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@bp.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        message = data.get('message', '')
        file_paths = data.get('files', [])
        
        # Process any uploaded files
        file_contents = []
        for file_path in file_paths:
            if os.path.exists(file_path):
                content = read_file_content(file_path)
                file_contents.append(f"Content of {os.path.basename(file_path)}:\n{content}")
        
        # Combine message with file contents
        complete_message = message
        if file_contents:
            complete_message += "\n\nFile contents:\n" + "\n---\n".join(file_contents)
        
        if not complete_message:
            return jsonify({'error': 'No message or files provided'}), 400
        
        client = ClaudeClient()
        response = client.client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": complete_message
            }]
        )
        
        response_text = response.content[0].text if response.content else "No response received"
        
        return jsonify({
            'status': 'success',
            'response': response_text
        })
        
    except Exception as e:
        print("Error in /chat endpoint:", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

# Cleanup routine for old files (optional)
@bp.route('/cleanup', methods=['POST'])
def cleanup_old_files():
    """Remove files older than 24 hours"""
    try:
        cutoff = datetime.now().timestamp() - (24 * 60 * 60)  # 24 hours ago
        cleaned = 0
        
        for filename in os.listdir(UPLOAD_FOLDER):
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.getctime(filepath) < cutoff:
                os.remove(filepath)
                cleaned += 1
                
        return jsonify({
            'status': 'success',
            'files_cleaned': cleaned
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500