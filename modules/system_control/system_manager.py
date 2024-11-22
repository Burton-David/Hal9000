# File: hal9000/modules/system_control/system_manager.py

import psutil
import platform
import os
import subprocess
import json
from datetime import datetime

class SystemManager:
    def __init__(self):
        self.platform = platform.system().lower()
        
    def get_system_info(self):
        """Get basic system information"""
        try:
            return {
                'platform': platform.platform(),
                'processor': platform.processor(),
                'cpu_cores': psutil.cpu_count(),
                'memory_total': psutil.virtual_memory().total,
                'python_version': platform.python_version(),
                'hostname': platform.node()
            }
        except Exception as e:
            return {'error': str(e)}

    def get_system_status(self):
        """Get current system status"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Get network info
            network = psutil.net_io_counters()
            
            # Get top processes
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    pinfo = proc.info
                    processes.append({
                        'pid': pinfo['pid'],
                        'name': pinfo['name'],
                        'cpu_percent': pinfo['cpu_percent'],
                        'memory_percent': pinfo['memory_percent']
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
                    
            # Sort processes by CPU usage
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            
            return {
                'timestamp': datetime.now().isoformat(),
                'cpu': {
                    'percent': cpu_percent,
                    'frequency': psutil.cpu_freq().current if psutil.cpu_freq() else None,
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent,
                    'used': memory.used,
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': disk.percent,
                },
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                },
                'top_processes': processes[:5]  # Top 5 CPU-consuming processes
            }
        except Exception as e:
            return {'error': str(e)}

    def execute_command(self, command, args=None):
        """
        Safely execute system commands
        command: predefined command name
        args: optional arguments
        """
        # Define allowed commands and their implementations
        ALLOWED_COMMANDS = {
            'shutdown': self._shutdown,
            'restart': self._restart,
            'sleep': self._sleep,
            'lock': self._lock,
            'launch_app': self._launch_app
        }
        
        if command not in ALLOWED_COMMANDS:
            raise ValueError(f"Command not allowed: {command}")
            
        return ALLOWED_COMMANDS[command](args)

    def _shutdown(self, args=None):
        """Shutdown the system"""
        if self.platform == 'windows':
            os.system('shutdown /s /t 60')  # 60 second delay
            return {'message': 'System will shutdown in 60 seconds'}
        elif self.platform in ['linux', 'darwin']:
            os.system('sudo shutdown -h +1')  # 1 minute delay
            return {'message': 'System will shutdown in 60 seconds'}
        return {'error': 'Unsupported platform'}

    def _restart(self, args=None):
        """Restart the system"""
        if self.platform == 'windows':
            os.system('shutdown /r /t 60')
            return {'message': 'System will restart in 60 seconds'}
        elif self.platform in ['linux', 'darwin']:
            os.system('sudo shutdown -r +1')
            return {'message': 'System will restart in 60 seconds'}
        return {'error': 'Unsupported platform'}

    def _sleep(self, args=None):
        """Put system to sleep"""
        if self.platform == 'windows':
            os.system('rundll32.exe powrprof.dll,SetSuspendState 0,1,0')
        elif self.platform == 'darwin':
            os.system('pmset sleepnow')
        elif self.platform == 'linux':
            os.system('systemctl suspend')
        return {'message': 'System sleep command initiated'}

    def _lock(self, args=None):
        """Lock the system"""
        if self.platform == 'windows':
            os.system('rundll32.exe user32.dll,LockWorkStation')
        elif self.platform == 'darwin':
            os.system('pmset displaysleepnow')
        elif self.platform == 'linux':
            os.system('gnome-screensaver-command -l')
        return {'message': 'System lock command initiated'}

    def _launch_app(self, args):
        """
        Safely launch an application
        args: dictionary containing 'app_name' and optional 'parameters'
        """
        if not args or 'app_name' not in args:
            return {'error': 'No application specified'}
            
        # Define allowed applications and their paths
        ALLOWED_APPS = {
            'calculator': {
                'windows': 'calc.exe',
                'darwin': 'open -a Calculator',
                'linux': 'gnome-calculator'
            },
            'notepad': {
                'windows': 'notepad.exe',
                'darwin': 'open -a TextEdit',
                'linux': 'gedit'
            }
            # Add more applications as needed
        }
        
        app_name = args['app_name'].lower()
        if app_name not in ALLOWED_APPS:
            return {'error': f'Application not allowed: {app_name}'}
            
        try:
            if self.platform in ALLOWED_APPS[app_name]:
                command = ALLOWED_APPS[app_name][self.platform]
                subprocess.Popen(command.split())
                return {'message': f'Launched {app_name}'}
            else:
                return {'error': f'Application not supported on {self.platform}'}
        except Exception as e:
            return {'error': f'Failed to launch {app_name}: {str(e)}'}