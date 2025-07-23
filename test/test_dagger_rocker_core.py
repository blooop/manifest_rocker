import pytest
from unittest.mock import Mock
import sys
from pathlib import Path

# Add the dagger_rocker directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "dagger_rocker"))

try:
    from core import DaggerRockerCore, DaggerRockerExtension, BasicExtension
except ImportError as e:
    pytest.skip(f"Dagger not available: {e}", allow_module_level=True)


class MockExtension(DaggerRockerExtension):
    """Mock extension for testing"""
    
    def __init__(self, name: str, dependencies=None, load_order_hints=None):
        self._name = name
        self._dependencies = dependencies or set()
        self._load_order_hints = load_order_hints or set()
        self.setup_container_called = False
        self.validate_environment_called = False
    
    def get_name(self) -> str:
        return self._name
    
    async def setup_container(self, container, args):
        self.setup_container_called = True
        return container
    
    def validate_environment(self, args):
        self.validate_environment_called = True
    
    def register_arguments(self, parser):
        parser.add_argument(f'--{self._name}', action='store_true', 
                          help=f'Enable {self._name} extension')
    
    def get_dependencies(self):
        return self._dependencies
    
    def get_load_order_hints(self):
        return self._load_order_hints


class TestDaggerRockerCore:
    """Test the core functionality"""
    
    def test_extension_registration(self):
        """Test that extensions can be registered"""
        core = DaggerRockerCore()
        ext = MockExtension("test")
        
        core.register_extension(ext)
        
        assert "test" in core.extensions
        assert core.extensions["test"] == ext
    
    def test_basic_extension_activation(self):
        """Test that basic extension is always active"""
        core = DaggerRockerCore()
        basic_ext = BasicExtension()
        core.register_extension(basic_ext)
        
        args = {'image': 'ubuntu:20.04'}
        active = core.get_active_extensions(args)
        
        assert len(active) == 1
        assert active[0].get_name() == "basic"
    
    def test_extension_activation_by_argument(self):
        """Test that extensions are activated by CLI arguments"""
        core = DaggerRockerCore()
        
        basic_ext = BasicExtension()
        test_ext = MockExtension("test")
        
        core.register_extension(basic_ext)
        core.register_extension(test_ext)
        
        # Without test argument
        args = {'image': 'ubuntu:20.04'}
        active = core.get_active_extensions(args)
        names = [ext.get_name() for ext in active]
        assert "basic" in names
        assert "test" not in names
        
        # With test argument
        args = {'image': 'ubuntu:20.04', 'test': True}
        active = core.get_active_extensions(args)
        names = [ext.get_name() for ext in active]
        assert "basic" in names
        assert "test" in names
    
    def test_extension_dependencies(self):
        """Test that extension dependencies are automatically included"""
        core = DaggerRockerCore()
        
        basic_ext = BasicExtension()
        dep_ext = MockExtension("dependency")
        main_ext = MockExtension("main", dependencies={"dependency"})
        
        core.register_extension(basic_ext)
        core.register_extension(dep_ext)
        core.register_extension(main_ext)
        
        # Only activate main extension
        args = {'image': 'ubuntu:20.04', 'main': True}
        active = core.get_active_extensions(args)
        names = [ext.get_name() for ext in active]
        
        assert "basic" in names
        assert "main" in names
        assert "dependency" in names  # Should be automatically included
    
    def test_extension_load_order(self):
        """Test that extensions are loaded in the correct order"""
        core = DaggerRockerCore()
        
        basic_ext = BasicExtension()
        first_ext = MockExtension("first")
        second_ext = MockExtension("second", load_order_hints={"first"})
        
        core.register_extension(basic_ext)
        core.register_extension(second_ext)
        core.register_extension(first_ext)
        
        args = {'image': 'ubuntu:20.04', 'first': True, 'second': True}
        active = core.get_active_extensions(args)
        
        # Find the positions
        names = [ext.get_name() for ext in active]
        first_idx = names.index("first")
        second_idx = names.index("second")
        
        # First should come before second
        assert first_idx < second_idx
    
    def test_circular_dependency_detection(self):
        """Test that circular dependencies are detected"""
        core = DaggerRockerCore()
        
        ext_a = MockExtension("a", load_order_hints={"b"})
        ext_b = MockExtension("b", load_order_hints={"a"})
        
        core.register_extension(ext_a)
        core.register_extension(ext_b)
        
        args = {'image': 'ubuntu:20.04', 'a': True, 'b': True}
        
        with pytest.raises(ValueError, match="Circular dependency"):
            core.get_active_extensions(args)


class TestBasicExtension:
    """Test the BasicExtension"""
    
    def test_basic_extension_name(self):
        """Test basic extension name"""
        ext = BasicExtension()
        assert ext.get_name() == "basic"
    
    def test_basic_extension_always_active(self):
        """Test that basic extension is always active"""
        ext = BasicExtension()
        assert ext.check_args_for_activation({})
        assert ext.check_args_for_activation({'image': 'ubuntu'})
        assert ext.check_args_for_activation({'basic': False})
    
    def test_basic_extension_no_dependencies(self):
        """Test that basic extension has no dependencies"""
        ext = BasicExtension()
        assert ext.get_dependencies() == set()
        assert ext.get_load_order_hints() == set()
    
    def test_basic_extension_validation(self):
        """Test that basic extension validation passes"""
        ext = BasicExtension()
        # Should not raise any exception
        ext.validate_environment({})
    
    @pytest.mark.asyncio
    async def test_basic_extension_container_setup(self):
        """Test that basic extension doesn't modify container"""
        ext = BasicExtension()
        mock_container = Mock()
        
        result = await ext.setup_container(mock_container, {})
        
        # Should return the same container unchanged
        assert result == mock_container


if __name__ == "__main__":
    pytest.main([__file__])
