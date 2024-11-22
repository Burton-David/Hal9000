# File: hal9000/modules/api_hub/dev_controller.py

import os
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional

class DevController:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.allowed_extensions = {'.py', '.html', '.css', '.js', '.json', '.md'}
        
    def get_project_structure(self) -> Dict:
        """Get the current project structure"""
        def build_tree(path: Path) -> Dict:
            if path.name.startswith('.') or path.name == '__pycache__':
                return None
                
            if path.is_file():
                if path.suffix in self.allowed_extensions:
                    return {
                        'type': 'file',
                        'name': path.name,
                        'path': str(path.relative_to(self.project_root))
                    }
                return None
                
            items = {}
            for item in path.iterdir():
                result = build_tree(item)
                if result:
                    items[item.name] = result
                    
            return {
                'type': 'directory',
                'name': path.name,
                'contents': items
            }
            
        return build_tree(self.project_root)
        
    def read_file(self, filepath: str) -> Optional[str]:
        """Read contents of a project file"""
        full_path = self.project_root / filepath
        
        # Security checks
        if not full_path.exists():
            raise ValueError(f"File does not exist: {filepath}")
        if full_path.suffix not in self.allowed_extensions:
            raise ValueError(f"File type not allowed: {filepath}")
        if not str(full_path).startswith(str(self.project_root)):
            raise ValueError("Access denied: File outside project directory")
            
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise ValueError(f"Error reading file: {str(e)}")

    def write_file(self, filepath: str, content: str) -> Dict:
        """Write content to a project file"""
        full_path = self.project_root / filepath
        
        # Security checks
        if full_path.suffix not in self.allowed_extensions:
            raise ValueError(f"File type not allowed: {filepath}")
        if not str(full_path).startswith(str(self.project_root)):
            raise ValueError("Access denied: File outside project directory")
            
        # Create directories if they don't exist
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return {
                'status': 'success',
                'message': f"File written successfully: {filepath}"
            }
        except Exception as e:
            raise ValueError(f"Error writing file: {str(e)}")

    def pip_install(self, package: str) -> Dict:
        """Install a Python package using pip"""
        # Security check - basic package name validation
        if not package.replace('-', '').replace('_', '').isalnum():
            raise ValueError("Invalid package name")
            
        try:
            result = subprocess.run(
                ['pip', 'install', package],
                capture_output=True,
                text=True,
                check=True
            )
            return {
                'status': 'success',
                'message': f"Package installed successfully: {package}",
                'output': result.stdout
            }
        except subprocess.CalledProcessError as e:
            raise ValueError(f"Error installing package: {e.stderr}")

    def flask_command(self, command: str) -> Dict:
        """Execute Flask CLI commands"""
        allowed_commands = {'routes', 'db upgrade', 'db migrate'}
        
        if command not in allowed_commands:
            raise ValueError(f"Command not allowed: {command}")
            
        try:
            result = subprocess.run(
                f"flask {command}",
                shell=True,
                capture_output=True,
                text=True,
                check=True
            )
            return {
                'status': 'success',
                'message': f"Command executed successfully: flask {command}",
                'output': result.stdout
            }
        except subprocess.CalledProcessError as e:
            raise ValueError(f"Error executing command: {e.stderr}")