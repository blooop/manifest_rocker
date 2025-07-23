import os
from typing import Dict
from core import DaggerRockerExtension


class HomeExtension(DaggerRockerExtension):
    """Extension to mount the user's home directory into the container"""
    
    def get_name(self) -> str:
        return "home"
    
    def validate_environment(self, args: Dict) -> None:
        """Validate that home directory exists"""
        home_dir = os.path.expanduser("~")
        if not os.path.exists(home_dir):
            raise RuntimeError(f"Home directory does not exist: {home_dir}")
    
    async def setup_container(self, container, args: Dict):
        """Mount home directory into the container"""
        # Get home directory
        home_dir = os.path.expanduser("~")
        
        # Mount the home directory
        host_home = container.host().directory(home_dir)
        container = container.with_mounted_directory(home_dir, host_home)
        
        return container
    
    def register_arguments(self, parser) -> None:
        """Register CLI arguments"""
        parser.add_argument('--home', action='store_true',
                          help='Mount the user home directory into the container')
    
    def get_dependencies(self):
        """Home extension requires user extension"""
        return {"user"}
    
    def get_load_order_hints(self):
        """Home extension should load after user extension"""
        return {"user"}
