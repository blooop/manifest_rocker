import os
import tempfile
import subprocess
from typing import Dict
from core import DaggerRockerExtension


class X11Extension(DaggerRockerExtension):
    """Extension to enable X11 forwarding for GUI applications"""
    
    def get_name(self) -> str:
        return "x11"
    
    def validate_environment(self, args: Dict) -> None:
        """Validate that X11 is available"""
        display = os.getenv('DISPLAY')
        if not display:
            raise RuntimeError("DISPLAY environment variable not set. X11 forwarding requires a running X server.")
        
        # Check if xauth is available
        try:
            subprocess.run(['which', 'xauth'], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            raise RuntimeError("xauth command not found. Please install xauth for X11 forwarding.")
    
    async def setup_container(self, container, args: Dict):
        """Setup X11 forwarding in the container"""
        display = os.getenv('DISPLAY', ':0')
        
        # Create temporary xauth file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xauth', delete=False) as xauth_file:
            xauth_path = xauth_file.name
        
        # Extract X11 authentication info
        try:
            cmd = f'xauth nlist {display} | sed -e "s/^..../ffff/" | xauth -f {xauth_path} nmerge -'
            subprocess.run(cmd, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to setup X11 authentication: {e}")
        
        # Set environment variables
        container = container.with_env_variable("DISPLAY", display)
        container = container.with_env_variable("XAUTHORITY", "/tmp/.docker.xauth")
        container = container.with_env_variable("QT_X11_NO_MITSHM", "1")
        
        # Mount X11 socket and xauth file
        x11_socket = container.host().directory("/tmp/.X11-unix")
        container = container.with_mounted_directory("/tmp/.X11-unix", x11_socket)
        
        xauth_host_file = container.host().file(xauth_path)
        container = container.with_mounted_file("/tmp/.docker.xauth", xauth_host_file)
        
        return container
    
    def register_arguments(self, parser) -> None:
        """Register CLI arguments"""
        parser.add_argument('--x11', action='store_true',
                          help='Enable X11 forwarding for GUI applications')
    
    def get_dependencies(self):
        """X11 extension has no dependencies"""
        return set()
    
    def get_load_order_hints(self):
        """X11 extension should load after user extension if present"""
        return {"user"}
