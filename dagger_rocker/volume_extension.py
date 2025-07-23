import os
from typing import Dict
from core import DaggerRockerExtension


class VolumeExtension(DaggerRockerExtension):
    """Extension to mount volumes into the container"""
    
    def get_name(self) -> str:
        return "volume"
    
    def validate_environment(self, args: Dict) -> None:
        """Validate that specified volumes exist"""
        volumes = args.get('volume', [])
        if not volumes:
            return
            
        for volume_spec in volumes:
            # Parse volume specification (host_path[:container_path[:options]])
            parts = volume_spec.split(':')
            host_path = parts[0]
            
            # Expand user home directory
            host_path = os.path.expanduser(host_path)
            
            if not os.path.exists(host_path):
                raise RuntimeError(f"Volume source path does not exist: {host_path}")
    
    async def setup_container(self, container, args: Dict):
        """Mount volumes into the container"""
        volumes = args.get('volume', [])
        if not volumes:
            return container
            
        for volume_spec in volumes:
            # Parse volume specification
            parts = volume_spec.split(':')
            host_path = os.path.expanduser(parts[0])
            
            # Determine container path
            if len(parts) > 1 and parts[1]:
                container_path = parts[1]
            else:
                container_path = host_path
            
            # Mount the volume
            if os.path.isfile(host_path):
                # Mount file
                host_file = container.host().file(host_path)
                container = container.with_mounted_file(container_path, host_file)
            else:
                # Mount directory
                host_dir = container.host().directory(host_path)
                container = container.with_mounted_directory(container_path, host_dir)
        
        return container
    
    def register_arguments(self, parser) -> None:
        """Register CLI arguments"""
        parser.add_argument('--volume', action='append', default=[],
                          help='Mount a volume (host_path[:container_path]). Can be used multiple times.')
    
    def get_dependencies(self):
        """Volume extension has no dependencies"""
        return set()
    
    def get_load_order_hints(self):
        """Volume extension should load after user extension if present"""
        return {"user"}
