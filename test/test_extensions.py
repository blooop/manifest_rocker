import pytest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add the dagger_rocker directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "dagger_rocker"))

try:
    from user_extension import UserExtension
    from volume_extension import VolumeExtension
    from home_extension import HomeExtension
except ImportError as e:
    pytest.skip(f"Extensions not available: {e}", allow_module_level=True)


class TestUserExtension:
    """Test the UserExtension"""
    
    def test_extension_name(self):
        """Test extension name"""
        ext = UserExtension()
        assert ext.get_name() == "user"
    
    def test_validation_success(self):
        """Test successful validation"""
        ext = UserExtension()
        # Should not raise exception with normal user
        ext.validate_environment({})
    
    def test_dependencies(self):
        """Test extension dependencies"""
        ext = UserExtension()
        assert ext.get_dependencies() == set()
        assert ext.get_load_order_hints() == set()
    
    def test_argument_registration(self):
        """Test CLI argument registration"""
        ext = UserExtension()
        parser = Mock()
        ext.register_arguments(parser)
        
        parser.add_argument.assert_called_once_with(
            '--user', action='store_true',
            help='Create a user inside the container matching the host user'
        )
    
    @pytest.mark.asyncio
    async def test_container_setup(self):
        """Test container setup"""
        ext = UserExtension()
        mock_container = Mock()
        mock_container.with_exec.return_value = mock_container
        mock_container.with_user.return_value = mock_container
        mock_container.with_workdir.return_value = mock_container
        
        result = await ext.setup_container(mock_container, {})
        
        # Should call with_exec to create user
        mock_container.with_exec.assert_called_once()
        # Should set user
        mock_container.with_user.assert_called_once()
        # Should set working directory
        mock_container.with_workdir.assert_called_once()


class TestVolumeExtension:
    """Test the VolumeExtension"""
    
    def test_extension_name(self):
        """Test extension name"""
        ext = VolumeExtension()
        assert ext.get_name() == "volume"
    
    def test_validation_no_volumes(self):
        """Test validation with no volumes"""
        ext = VolumeExtension()
        ext.validate_environment({})  # Should not raise
    
    def test_validation_existing_path(self):
        """Test validation with existing path"""
        ext = VolumeExtension()
        with patch('os.path.exists', return_value=True):
            ext.validate_environment({'volume': ['/tmp']})
    
    def test_validation_missing_path(self):
        """Test validation with missing path"""
        ext = VolumeExtension()
        with patch('os.path.exists', return_value=False):
            with pytest.raises(RuntimeError, match="does not exist"):
                ext.validate_environment({'volume': ['/nonexistent']})
    
    def test_dependencies(self):
        """Test extension dependencies"""
        ext = VolumeExtension()
        assert ext.get_dependencies() == set()
        assert ext.get_load_order_hints() == {"user"}
    
    def test_argument_registration(self):
        """Test CLI argument registration"""
        ext = VolumeExtension()
        parser = Mock()
        ext.register_arguments(parser)
        
        parser.add_argument.assert_called_once_with(
            '--volume', action='append', default=[],
            help='Mount a volume (host_path[:container_path]). Can be used multiple times.'
        )
    
    @pytest.mark.asyncio
    async def test_container_setup_no_volumes(self):
        """Test container setup with no volumes"""
        ext = VolumeExtension()
        mock_container = Mock()
        
        result = await ext.setup_container(mock_container, {})
        
        assert result == mock_container
    
    @pytest.mark.asyncio
    async def test_container_setup_with_file(self):
        """Test container setup with file volume"""
        ext = VolumeExtension()
        mock_container = Mock()
        mock_host = Mock()
        mock_file = Mock()
        
        mock_container.host.return_value = mock_host
        mock_host.file.return_value = mock_file
        mock_container.with_mounted_file.return_value = mock_container
        
        with patch('os.path.expanduser', return_value='/home/user/file.txt'):
            with patch('os.path.isfile', return_value=True):
                result = await ext.setup_container(
                    mock_container, 
                    {'volume': ['~/file.txt']}
                )
        
        mock_host.file.assert_called_once_with('/home/user/file.txt')
        mock_container.with_mounted_file.assert_called_once_with('/home/user/file.txt', mock_file)
    
    @pytest.mark.asyncio
    async def test_container_setup_with_directory(self):
        """Test container setup with directory volume"""
        ext = VolumeExtension()
        mock_container = Mock()
        mock_host = Mock()
        mock_dir = Mock()
        
        mock_container.host.return_value = mock_host
        mock_host.directory.return_value = mock_dir
        mock_container.with_mounted_directory.return_value = mock_container
        
        with patch('os.path.expanduser', return_value='/home/user/dir'):
            with patch('os.path.isfile', return_value=False):
                result = await ext.setup_container(
                    mock_container, 
                    {'volume': ['~/dir:/container/dir']}
                )
        
        mock_host.directory.assert_called_once_with('/home/user/dir')
        mock_container.with_mounted_directory.assert_called_once_with('/container/dir', mock_dir)


class TestHomeExtension:
    """Test the HomeExtension"""
    
    def test_extension_name(self):
        """Test extension name"""
        ext = HomeExtension()
        assert ext.get_name() == "home"
    
    def test_validation_success(self):
        """Test successful validation"""
        ext = HomeExtension()
        with patch('os.path.exists', return_value=True):
            ext.validate_environment({})
    
    def test_validation_missing_home(self):
        """Test validation with missing home directory"""
        ext = HomeExtension()
        with patch('os.path.exists', return_value=False):
            with pytest.raises(RuntimeError, match="Home directory does not exist"):
                ext.validate_environment({})
    
    def test_dependencies(self):
        """Test extension dependencies"""
        ext = HomeExtension()
        assert ext.get_dependencies() == {"user"}
        assert ext.get_load_order_hints() == {"user"}
    
    def test_argument_registration(self):
        """Test CLI argument registration"""
        ext = HomeExtension()
        parser = Mock()
        ext.register_arguments(parser)
        
        parser.add_argument.assert_called_once_with(
            '--home', action='store_true',
            help='Mount the user home directory into the container'
        )
    
    @pytest.mark.asyncio
    async def test_container_setup(self):
        """Test container setup"""
        ext = HomeExtension()
        mock_container = Mock()
        mock_host = Mock()
        mock_dir = Mock()
        
        mock_container.host.return_value = mock_host
        mock_host.directory.return_value = mock_dir
        mock_container.with_mounted_directory.return_value = mock_container
        
        with patch('os.path.expanduser', return_value='/home/testuser'):
            result = await ext.setup_container(mock_container, {})
        
        mock_host.directory.assert_called_once_with('/home/testuser')
        mock_container.with_mounted_directory.assert_called_once_with('/home/testuser', mock_dir)


if __name__ == "__main__":
    pytest.main([__file__])
