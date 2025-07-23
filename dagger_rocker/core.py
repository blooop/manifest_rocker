import argparse
import asyncio
import sys
from typing import Dict, List, Set
from abc import ABC, abstractmethod

try:
    import dagger
except ImportError:
    print("dagger-io package not installed. Please install it with: pip install dagger-io")
    sys.exit(1)


class DaggerRockerExtension(ABC):
    """Base class for Dagger Rocker extensions"""
    
    @abstractmethod
    async def setup_container(self, container: dagger.Container, args: Dict) -> dagger.Container:
        """Configure the container with this extension's requirements"""
        pass
    
    @abstractmethod
    def validate_environment(self, args: Dict) -> None:
        """Validate that the local environment supports this extension"""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Return the name of this extension"""
        pass
    
    @abstractmethod
    def register_arguments(self, parser: argparse.ArgumentParser) -> None:
        """Register CLI arguments for this extension"""
        pass
    
    def check_args_for_activation(self, args: Dict) -> bool:
        """Check if this extension should be activated based on CLI args"""
        return bool(args.get(self.get_name()))
    
    def get_dependencies(self) -> Set[str]:
        """Return set of extension names this extension depends on"""
        return set()
    
    def get_load_order_hints(self) -> Set[str]:
        """Return set of extension names that should load before this one"""
        return set()


class DaggerRockerCore:
    """Core class for managing Dagger-based container execution"""
    
    def __init__(self):
        self.extensions: Dict[str, DaggerRockerExtension] = {}
        self.active_extensions: List[DaggerRockerExtension] = []
    
    def register_extension(self, extension: DaggerRockerExtension) -> None:
        """Register an extension"""
        self.extensions[extension.get_name()] = extension
    
    def get_active_extensions(self, args: Dict) -> List[DaggerRockerExtension]:
        """Get list of active extensions based on CLI arguments"""
        active = {}
        
        # Find initially requested extensions
        for name, ext in self.extensions.items():
            if ext.check_args_for_activation(args):
                active[name] = ext
        
        # Add dependencies
        changed = True
        while changed:
            changed = False
            for name, ext in list(active.items()):
                for dep_name in ext.get_dependencies():
                    if dep_name not in active and dep_name in self.extensions:
                        active[dep_name] = self.extensions[dep_name]
                        changed = True
        
        # Sort by load order
        return self._sort_extensions(active, args)
    
    def _sort_extensions(self, extensions: Dict[str, DaggerRockerExtension], args: Dict) -> List[DaggerRockerExtension]:
        """Sort extensions based on load order hints"""
        def topological_sort(items):
            # Simple topological sort implementation
            visited = set()
            temp_visited = set()
            result = []
            
            def visit(name):
                if name in temp_visited:
                    raise ValueError(f"Circular dependency detected involving {name}")
                if name in visited:
                    return
                    
                temp_visited.add(name)
                if name in items:
                    ext = items[name]
                    for dep in ext.get_load_order_hints():
                        if dep in items:
                            visit(dep)
                
                temp_visited.remove(name)
                visited.add(name)
                if name in items:
                    result.append(items[name])
            
            for name in items:
                visit(name)
                
            return result
        
        return topological_sort(extensions)
    
    async def build_and_run(self, args: Dict) -> None:
        """Build and run a container with active extensions"""
        async with dagger.Connection(dagger.Config(log_output=sys.stderr)) as client:
            # Get base container
            container = client.container().from_(args['image'])
            
            # Apply each extension
            for ext in self.active_extensions:
                container = await ext.setup_container(container, args)
            
            # Execute command or run interactive shell
            if args.get('command'):
                result = await container.with_exec(args['command']).sync()
            else:
                # For interactive mode, we'll need to handle this differently
                # For now, just run a shell
                result = await container.with_exec(["/bin/bash"]).sync()
            
            return result
    
    async def run(self, args: Dict) -> str:
        """Run a container with active extensions and return output"""
        # Get active extensions
        self.active_extensions = self.get_active_extensions(args)
        
        # Validate environment
        for ext in self.active_extensions:
            ext.validate_environment(args)
        
        async with dagger.Connection(dagger.Config(log_output=sys.stderr)) as client:
            # Get base container
            container = client.container().from_(args['image'])
            
            # Apply each extension
            for ext in self.active_extensions:
                container = await ext.setup_container(container, args)
            
            # Execute command
            if args.get('command'):
                result = await container.with_exec(args['command']).stdout()
                return result
            else:
                # Default to bash if no command specified
                result = await container.with_exec(["/bin/bash", "-c", "echo 'No command specified'"]).stdout()
                return result


class BasicExtension(DaggerRockerExtension):
    """Basic extension that provides fundamental container setup"""
    
    def get_name(self) -> str:
        return "basic"
    
    async def setup_container(self, container: dagger.Container, args: Dict) -> dagger.Container:
        """Basic container setup"""
        return container
    
    def validate_environment(self, args: Dict) -> None:
        """No special validation needed for basic extension"""
        pass
    
    def register_arguments(self, parser: argparse.ArgumentParser) -> None:
        """No additional arguments for basic extension"""
        pass
    
    def check_args_for_activation(self, args: Dict) -> bool:
        """Basic extension is always active"""
        return True


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Dagger-based rocker: Modern container orchestration',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument('image', help='Container image to run')
    parser.add_argument('command', nargs='*', help='Command to execute in container')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without executing')
    
    # Initialize core and register basic extensions
    core = DaggerRockerCore()
    core.register_extension(BasicExtension())
    
    # Register extension arguments
    for ext in core.extensions.values():
        ext.register_arguments(parser)
    
    args = parser.parse_args()
    args_dict = vars(args)
    
    # Get active extensions
    core.active_extensions = core.get_active_extensions(args_dict)
    print(f"Active extensions: {[ext.get_name() for ext in core.active_extensions]}")
    
    # Validate environment
    for ext in core.active_extensions:
        ext.validate_environment(args_dict)
    
    if args_dict.get('dry_run'):
        print("Dry run mode - would execute container with configured extensions")
        return
    
    # Build and run container
    await core.build_and_run(args_dict)


if __name__ == "__main__":
    asyncio.run(main())
