# File: hal9000/modules/api_hub/claude_client.py

import os
from anthropic import Anthropic
from dotenv import load_dotenv
from .dev_controller import DevController

class ClaudeClient:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("No API key found. Make sure ANTHROPIC_API_KEY is set in your .env file")
        self.client = Anthropic(api_key=api_key)
        self.dev_controller = DevController()
    
    def handle_development_task(self, message: str):
        """Handle development-related tasks with proper context"""
        try:
            # Get current project structure
            project_structure = self.dev_controller.get_project_structure()
            
            # Create context about the development environment
            context = f"""You are integrated with a Flask application development environment. 
            You can read and modify files, install packages, and execute Flask commands.
            
            Current project structure:
            {json.dumps(project_structure, indent=2)}
            
            You can perform the following actions:
            1. Read files using: self.dev_controller.read_file(filepath)
            2. Write files using: self.dev_controller.write_file(filepath, content)
            3. Install packages using: self.dev_controller.pip_install(package)
            4. Execute Flask commands using: self.dev_controller.flask_command(command)
            
            User request: {message}
            """
            
            # Get Claude's response with development context
            response = self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=2048,
                messages=[{
                    "role": "user",
                    "content": context
                }]
            )
            
            # Parse and execute Claude's suggested actions
            actions = self._parse_development_actions(response.content[0].text)
            results = self._execute_development_actions(actions)
            
            return {
                'status': 'success',
                'message': response.content[0].text,
                'actions': results
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

    def _parse_development_actions(self, response: str) -> list[dict]:
        """Parse Claude's response for development actions"""
        # This is a basic implementation - we can make it more sophisticated
        actions = []
        
        if 'read_file(' in response:
            # Extract file read requests
            pass
            
        if 'write_file(' in response:
            # Extract file write requests
            pass
            
        if 'pip_install(' in response:
            # Extract package installation requests
            pass
            
        if 'flask_command(' in response:
            # Extract Flask commands
            pass
            
        return actions

    def _execute_development_actions(self, actions: list[dict]) -> list[dict]:
        """Execute the parsed development actions"""
        results = []
        
        for action in actions:
            try:
                if action['type'] == 'read_file':
                    content = self.dev_controller.read_file(action['filepath'])
                    results.append({
                        'action': action,
                        'status': 'success',
                        'result': content
                    })
                elif action['type'] == 'write_file':
                    result = self.dev_controller.write_file(
                        action['filepath'],
                        action['content']
                    )
                    results.append({
                        'action': action,
                        'status': 'success',
                        'result': result
                    })
                # Add other action types as needed
                
            except Exception as e:
                results.append({
                    'action': action,
                    'status': 'error',
                    'error': str(e)
                })
                
        return results