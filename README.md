# Dagger Rocker

A modern container orchestration tool built on [Dagger](https://dagger.io), inspired by the original [rocker](https://github.com/osrf/rocker) project.

## Overview

Dagger Rocker reimagines the rocker concept using Dagger's modern container orchestration capabilities. It provides a plugin-based system for customizing container environments with features like user management, volume mounting, X11 forwarding, and more.

## Key Features

- **Modern Architecture**: Built on Dagger for better performance and reliability
- **Extension System**: Modular plugin architecture for adding functionality
- **User Management**: Automatically create matching users inside containers
- **Volume Mounting**: Easy file and directory mounting with host path resolution
- **X11 Support**: GUI application support with proper X11 forwarding
- **Test-Driven**: Comprehensive test suite ensuring reliability

## Installation

### Prerequisites

- Python 3.8 or higher
- Docker installed and running
- Dagger CLI (optional, but recommended)

### Install from source

```bash
git clone <repository-url>
cd dagger-rocker
pip install -e .
```

### Install dependencies only

```bash
pip install -r requirements.txt
```

## Quick Start

### Basic Usage

Run a simple container:
```bash
dagger-rocker ubuntu:20.04 echo "Hello World"
```

### User Management

Create a user inside the container matching your host user:
```bash
dagger-rocker --user ubuntu:20.04 whoami
```

### Volume Mounting

Mount files and directories:
```bash
dagger-rocker --user --volume ~/workspace:/workspace ubuntu:20.04 ls -la /workspace
```

### Home Directory

Mount your entire home directory:
```bash
dagger-rocker --user --home ubuntu:20.04 bash
```

### X11 GUI Support

Run GUI applications (requires X11):
```bash
dagger-rocker --user --x11 ubuntu:20.04 xterm
```

### Dry Run

See what would be executed without running:
```bash
dagger-rocker --dry-run --user --volume ~/data:/data ubuntu:20.04 ls /data
```

## Available Extensions

### Built-in Extensions

- **user**: Creates a user in the container matching the host user's UID/GID
- **volume**: Mounts files and directories from host to container
- **home**: Mounts the user's home directory
- **x11**: Enables X11 forwarding for GUI applications

### Extension System

Dagger Rocker uses a plugin-based extension system. Each extension can:

- Add CLI arguments
- Validate the environment
- Configure the container
- Specify dependencies and load order

## Development

### Running Tests

```bash
# Install development dependencies
pip install -e .[dev]

# Run all tests
pytest

# Run specific test files
pytest test/test_dagger_rocker_core.py
pytest test/test_extensions.py
pytest test/test_integration_complete.py
```

### Code Quality

```bash
# Format code
black dagger_rocker/

# Lint code
ruff check dagger_rocker/
```

### Creating Extensions

To create a new extension, inherit from `DaggerRockerExtension`:

```python
from dagger_rocker.core import DaggerRockerExtension
from typing import Dict

class MyExtension(DaggerRockerExtension):
    def get_name(self) -> str:
        return "my_extension"
    
    async def setup_container(self, container, args: Dict):
        # Modify the container here
        return container
    
    def validate_environment(self, args: Dict) -> None:
        # Validate prerequisites
        pass
    
    def register_arguments(self, parser) -> None:
        parser.add_argument('--my-extension', action='store_true',
                          help='Enable my extension')
```

## Comparison with Original Rocker

| Feature | Original Rocker | Dagger Rocker |
|---------|----------------|---------------|
| Container Engine | Docker only | Dagger (multi-engine support) |
| Configuration | Dockerfile generation | Native container operations |
| Caching | Docker layer caching | Dagger's advanced caching |
| Extension System | Python entry points | Class-based plugins |
| Testing | Limited | Comprehensive test suite |
| Performance | Good | Better (Dagger optimizations) |

## Architecture

Dagger Rocker is built around several key components:

1. **Core**: `DaggerRockerCore` manages extension lifecycle and container execution
2. **Extensions**: Modular plugins that add specific functionality
3. **CLI**: Command-line interface that ties everything together

### Extension Lifecycle

1. **Registration**: Extensions register with the core
2. **Argument Parsing**: CLI arguments are processed
3. **Activation**: Extensions are activated based on arguments
4. **Dependency Resolution**: Dependencies are automatically resolved
5. **Ordering**: Extensions are sorted based on load order hints
6. **Validation**: Environment validation occurs
7. **Container Setup**: Extensions configure the container
8. **Execution**: Container is built and executed

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

Licensed under the Apache License, Version 2.0. See LICENSE file for details.
- expensive: expensive dependencies (cuda, torch etc)
- main: most installation should happen here
- post-main: any setup after everything is installed
- build
- lint
- test

run with:

```
rocker --deps ubuntu:22.04
```


## limitations/TODO

The order of the layers relies on convention.  If different projects use a different convention then combining them may break in weird ways



## Continuous Integration Status

[![Ci](https://github.com/blooop/python_template/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/blooop/python_template/actions/workflows/ci.yml?query=branch%3Amain)
[![Codecov](https://codecov.io/gh/blooop/python_template/branch/main/graph/badge.svg?token=Y212GW1PG6)](https://codecov.io/gh/blooop/python_template)
[![GitHub issues](https://img.shields.io/github/issues/blooop/python_template.svg)](https://GitHub.com/blooop/python_template/issues/)
[![GitHub pull-requests merged](https://badgen.net/github/merged-prs/blooop/python_template)](https://github.com/blooop/python_template/pulls?q=is%3Amerged)
[![GitHub release](https://img.shields.io/github/release/blooop/python_template.svg)](https://GitHub.com/blooop/python_template/releases/)
[![License](https://img.shields.io/pypi/l/bencher)](https://opensource.org/license/mit/)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11-blue)](https://www.python.org/downloads/release/python-310/)


To set up your project run the vscode task "pull updates from template repo" and then task "rename project template name"
