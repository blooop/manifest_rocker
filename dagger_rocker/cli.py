#!/usr/bin/env python3

"""
Dagger Rocker CLI - A modern container orchestration tool
"""

import argparse
import asyncio
import sys
import importlib.util
from pathlib import Path

# Check if dagger is available
if not importlib.util.find_spec("dagger"):
    print("dagger-io package not installed. Please install it with: pip install dagger-io")
    sys.exit(1)

# Add the current directory to the path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from core import DaggerRockerCore, BasicExtension
from user_extension import UserExtension
from volume_extension import VolumeExtension
from home_extension import HomeExtension
from x11_extension import X11Extension
from env_extension import EnvExtension
from network_extension import NetworkExtension
from detach_extension import DetachExtension


def create_parser():
    """Create the argument parser with all extensions"""
    parser = argparse.ArgumentParser(
        description='Dagger Rocker: Modern container orchestration inspired by the original rocker',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Base arguments
    parser.add_argument('image', help='Container image to run')
    parser.add_argument('command', nargs='*', help='Command to execute in container')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be done without executing')
    parser.add_argument('--interactive', action='store_true', 
                       help='Run in interactive mode (not yet implemented)')
    parser.add_argument('--version', action='version', version='dagger-rocker 0.1.0')
    
    return parser


async def main():
    """Main entry point for dagger-rocker"""
    parser = create_parser()
    
    # Initialize core and register all available extensions
    core = DaggerRockerCore()
    
    # Register built-in extensions
    extensions = [
        BasicExtension(),
        UserExtension(),
        VolumeExtension(),
        HomeExtension(),
        X11Extension(),
        EnvExtension(),
        NetworkExtension(),
        DetachExtension(),
    ]
    
    for ext in extensions:
        core.register_extension(ext)
    
    # Register extension arguments
    for ext in core.extensions.values():
        try:
            ext.register_arguments(parser)
        except Exception as e:
            print(f"Warning: Failed to register arguments for extension {ext.get_name()}: {e}")
    
    # Parse arguments
    args = parser.parse_args()
    args_dict = vars(args)
    
    # Get active extensions
    try:
        core.active_extensions = core.get_active_extensions(args_dict)
        print(f"Active extensions: {[ext.get_name() for ext in core.active_extensions]}")
    except Exception as e:
        print(f"Error determining active extensions: {e}")
        return 1
    
    # Validate environment for all active extensions
    for ext in core.active_extensions:
        try:
            ext.validate_environment(args_dict)
        except Exception as e:
            print(f"Error validating extension {ext.get_name()}: {e}")
            return 1
    
    # Handle dry run mode
    if args_dict.get('dry_run'):
        print("Dry run mode - would execute container with configured extensions")
        print(f"Image: {args_dict['image']}")
        if args_dict.get('command'):
            print(f"Command: {' '.join(args_dict['command'])}")
        print("Extensions would be applied in this order:")
        for i, ext in enumerate(core.active_extensions, 1):
            print(f"  {i}. {ext.get_name()}")
        return 0
    
    # Build and run container
    try:
        result = await core.run(args_dict)
        print(result)
        return 0
    except Exception as e:
        print(f"Error running container: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
