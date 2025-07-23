from typing import Dict
from core import DaggerRockerExtension


class DetachExtension(DaggerRockerExtension):
    """Extension to run container in detached mode"""
    
    def get_name(self) -> str:
        return "detach"
    
    def validate_environment(self, args: Dict) -> None:
        """Validate detach configuration"""
        if args.get('detach') and args.get('interactive'):
            raise RuntimeError("Cannot use both --detach and --interactive modes")
    
    async def setup_container(self, container, args: Dict):
        """Configure container for detached execution"""
        # Note: Dagger containers run differently than Docker
        # This extension mainly affects how the container is executed
        # rather than how it's configured
        return container
    
    def register_arguments(self, parser) -> None:
        """Register CLI arguments"""
        parser.add_argument('-d', '--detach', action='store_true',
                          help='Run the container in the background.')
    
    def get_dependencies(self):
        """Detach extension has no dependencies"""
        return set()
    
    def get_load_order_hints(self):
        """Detach extension should load late"""
        return set()
