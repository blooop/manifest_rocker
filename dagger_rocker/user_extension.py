import os
import pwd
import grp
from typing import Dict
from core import DaggerRockerExtension


class UserExtension(DaggerRockerExtension):
    """Extension to create a user inside the container with matching UID/GID"""
    
    def get_name(self) -> str:
        return "user"
    
    def validate_environment(self, args: Dict) -> None:
        """Validate that we can get user information"""
        try:
            pwd.getpwuid(os.getuid())
            grp.getgrgid(os.getgid())
        except KeyError as e:
            raise RuntimeError(f"Cannot get user/group information: {e}")
    
    async def setup_container(self, container, args: Dict):
        """Setup user in the container"""
        # Get current user info
        user_info = pwd.getpwuid(os.getuid())
        group_info = grp.getgrgid(os.getgid())
        
        username = user_info.pw_name
        uid = user_info.pw_uid
        gid = user_info.pw_gid
        home_dir = user_info.pw_dir
        shell = user_info.pw_shell
        group_name = group_info.gr_name
        
        # Create user and group in container
        container = container.with_exec([
            "bash", "-c", f"""
            set -e
            # Create group if it doesn't exist
            if ! getent group {group_name} > /dev/null 2>&1; then
                groupadd -g {gid} {group_name}
            fi
            
            # Create user if it doesn't exist
            if ! getent passwd {username} > /dev/null 2>&1; then
                useradd -u {uid} -g {gid} -d {home_dir} -s {shell} -m {username}
            fi
            
            # Add user to sudo group if it exists
            if getent group sudo > /dev/null 2>&1; then
                usermod -aG sudo {username}
            fi
            
            # Set up sudo without password for convenience
            if command -v sudo > /dev/null 2>&1; then
                echo "{username} ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/{username}
            fi
            """
        ])
        
        # Set the user for subsequent commands
        container = container.with_user(f"{uid}:{gid}")
        
        # Set working directory to user's home
        container = container.with_workdir(home_dir)
        
        return container
    
    def register_arguments(self, parser) -> None:
        """Register CLI arguments"""
        parser.add_argument('--user', action='store_true',
                          help='Create a user inside the container matching the host user')
    
    def get_dependencies(self):
        """User extension has no dependencies"""
        return set()
    
    def get_load_order_hints(self):
        """User extension should load early"""
        return set()
