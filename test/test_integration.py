import pytest
import asyncio
import tempfile
import os
from unittest.mock import Mock, AsyncMock, patch
import sys
from pathlib import Path

# Add the dagger_rocker directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "dagger_rocker"))

try:
    from core import DaggerRockerCore
    from user_extension import UserExtension
    from volume_extension import VolumeExtension
    from home_extension import HomeExtension
    from main import main as dagger_main
except ImportError as e:
    pytest.skip(f"Integration test dependencies not available: {e}", allow_module_level=True)


class TestIntegration:
    """Integration tests for dagger-rocker"""
    
    def test_extension_integration(self):
        """Test that all extensions work together"""
        core = DaggerRockerCore()
        
        # Register all extensions
        user_ext = UserExtension()
        volume_ext = VolumeExtension()
        home_ext = HomeExtension()
        
        core.register_extension(user_ext)
        core.register_extension(volume_ext)
        core.register_extension(home_ext)
        
        # Test with home extension (which requires user)
        args = {'image': 'ubuntu:20.04', 'home': True}
        active = core.get_active_extensions(args)
        
        names = [ext.get_name() for ext in active]
        assert "basic" in names
        assert "user" in names  # Should be automatically included
        assert "home" in names
        
        # Check load order: user should come before home
        user_idx = names.index("user")
        home_idx = names.index("home")
        assert user_idx < home_idx
    
    def test_volume_and_user_integration(self):
        """Test volume and user extensions together"""
        core = DaggerRockerCore()
        
        user_ext = UserExtension()
        volume_ext = VolumeExtension()
        
        core.register_extension(user_ext)
        core.register_extension(volume_ext)
        
        # Create a temporary file for testing
        with tempfile.NamedTemporaryFile(delete=False) as tf:
            temp_file = tf.name
            tf.write(b"test content")
        
        try:
            args = {
                'image': 'ubuntu:20.04', 
                'user': True, 
                'volume': [f'{temp_file}:/container/file']
            }
            active = core.get_active_extensions(args)
            
            names = [ext.get_name() for ext in active]
            assert "user" in names
            assert "volume" in names
            
            # Check load order: user should come before volume
            user_idx = names.index("user")
            volume_idx = names.index("volume")
            assert user_idx < volume_idx
            
        finally:
            os.unlink(temp_file)
    
    @pytest.mark.asyncio
    async def test_dry_run_integration(self):
        """Test dry run mode works end-to-end"""
        # Mock sys.argv to simulate command line
        test_args = [
            'dagger-rocker',
            '--dry-run',
            '--user',
            '--volume', '/tmp:/tmp',
            'ubuntu:20.04',
            'echo', 'hello'
        ]
        
        with patch('sys.argv', test_args):
            with patch('sys.exit') as mock_exit:
                # Mock the importlib check
                with patch('importlib.util.find_spec', return_value=True):
                    result = await dagger_main()
                    assert result == 0
    
    def test_all_extensions_load_order(self):
        """Test that all extensions load in correct order"""
        core = DaggerRockerCore()
        
        # Register all extensions
        from core import BasicExtension
        extensions = [
            BasicExtension(),
            UserExtension(),
            VolumeExtension(),
            HomeExtension(),
        ]
        
        for ext in extensions:
            core.register_extension(ext)
        
        # Activate all extensions
        args = {
            'image': 'ubuntu:20.04',
            'user': True,
            'volume': ['/tmp:/tmp'],
            'home': True
        }
        
        active = core.get_active_extensions(args)
        names = [ext.get_name() for ext in active]
        
        # Check all are present
        assert "basic" in names
        assert "user" in names
        assert "volume" in names
        assert "home" in names
        
        # Check user comes before home and volume
        user_idx = names.index("user")
        if "home" in names:
            home_idx = names.index("home")
            assert user_idx < home_idx
        if "volume" in names:
            volume_idx = names.index("volume")
            assert user_idx < volume_idx


class TestArgumentParsing:
    """Test argument parsing integration"""
    
    def test_all_arguments_registered(self):
        """Test that all extension arguments are properly registered"""
        import argparse
        
        parser = argparse.ArgumentParser()
        
        # Add base arguments
        parser.add_argument('image')
        parser.add_argument('command', nargs='*')
        parser.add_argument('--dry-run', action='store_true')
        
        # Register extension arguments
        extensions = [
            UserExtension(),
            VolumeExtension(),
            HomeExtension(),
        ]
        
        for ext in extensions:
            ext.register_arguments(parser)
        
        # Parse test arguments
        args = parser.parse_args([
            '--user',
            '--volume', '/tmp:/tmp',
            '--home',
            'ubuntu:20.04',
            'bash'
        ])
        
        assert args.user is True
        assert args.volume == ['/tmp:/tmp']
        assert args.home is True
        assert args.image == 'ubuntu:20.04'
        assert args.command == ['bash']


if __name__ == "__main__":
    pytest.main([__file__])
