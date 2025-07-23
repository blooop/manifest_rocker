from typing import Dict
from core import DaggerRockerExtension


class NetworkExtension(DaggerRockerExtension):
    """Extension to configure container network settings"""
    
    def get_name(self) -> str:
        return "network"
    
    def validate_environment(self, args: Dict) -> None:
        """Validate network configuration"""
        network = args.get('network')
        if network and network not in ['bridge', 'none', 'host']:
            raise RuntimeError(f"Invalid network mode: {network}. Must be one of: bridge, none, host")
    
    async def setup_container(self, container, args: Dict):
        """Configure container network settings"""
        network = args.get('network')
        if not network:
            return container
            
        # Note: Dagger handles networking differently than Docker
        # This is a simplified implementation
        if network == 'host':
            # In Dagger, host networking might not be directly supported
            # This would need to be handled at the Dagger engine level
            pass
        elif network == 'none':
            # Disable networking - also engine level
            pass
        # bridge is the default
        
        return container
    
    def register_arguments(self, parser) -> None:
        """Register CLI arguments"""
        parser.add_argument('--network', choices=['bridge', 'none', 'host'],
                          help='What network configuration to use.')
    
    def get_dependencies(self):
        """Network extension has no dependencies"""
        return set()
    
    def get_load_order_hints(self):
        """Network extension should load early"""
        return set()
