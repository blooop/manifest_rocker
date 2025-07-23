from typing import Dict
from core import DaggerRockerExtension


class EnvExtension(DaggerRockerExtension):
    """Extension to set environment variables in the container"""
    
    def get_name(self) -> str:
        return "env"
    
    def validate_environment(self, args: Dict) -> None:
        """No special validation needed for environment variables"""
        pass
    
    async def setup_container(self, container, args: Dict):
        """Set environment variables in the container"""
        env_vars = args.get('env', [])
        if not env_vars:
            return container
            
        for env_var in env_vars:
            if '=' in env_var:
                # Format: NAME=VALUE
                name, value = env_var.split('=', 1)
                container = container.with_env_variable(name, value)
            else:
                # Format: NAME (use value from host environment)
                import os
                value = os.getenv(env_var, '')
                container = container.with_env_variable(env_var, value)
        
        return container
    
    def register_arguments(self, parser) -> None:
        """Register CLI arguments"""
        parser.add_argument('--env', '-e', action='append', default=[],
                          help='Set environment variables (NAME=VALUE or NAME). Can be used multiple times.')
    
    def get_dependencies(self):
        """Env extension has no dependencies"""
        return set()
    
    def get_load_order_hints(self):
        """Env extension should load early"""
        return set()
