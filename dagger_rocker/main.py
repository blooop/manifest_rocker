#!/usr/bin/env python3

import argparse
import asyncio
import sys
import importlib.util

# Check if dagger is available
if not importlib.util.find_spec("dagger"):
    print("dagger-io package not installed. Please install it with: pip install dagger-io")
    sys.exit(1)

from .core import DaggerRockerCore, BasicExtension
from .user_extension import UserExtension
from .volume_extension import VolumeExtension
from .home_extension import HomeExtension


async def main():
    """Main entry point for dagger-rocker"""
    parser = argparse.ArgumentParser(
        description='Dagger-based rocker: Modern container orchestration',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument('image', help='Container image to run')
    parser.add_argument('command', nargs='*', help='Command to execute in container')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without executing')
    parser.add_argument('--interactive', action='store_true', help='Run in interactive mode')
    
    # Initialize core and register extensions
    core = DaggerRockerCore()
    
    # Register all available extensions
    extensions = [
        BasicExtension(),
        UserExtension(),
        VolumeExtension(),
        HomeExtension(),
    ]
    
    for ext in extensions:
        core.register_extension(ext)
    
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
        try:
            ext.validate_environment(args_dict)
        except Exception as e:
            print(f"Error validating extension {ext.get_name()}: {e}")
            return 1
    
    if args_dict.get('dry_run'):
        print("Dry run mode - would execute container with configured extensions")
        print(f"Image: {args_dict['image']}")
        if args_dict.get('command'):
            print(f"Command: {' '.join(args_dict['command'])}")
        return 0
    
    # Build and run container
    try:
        await core.build_and_run(args_dict)
    except Exception as e:
        print(f"Error running container: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
