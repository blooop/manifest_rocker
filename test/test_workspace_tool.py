#!/usr/bin/env python3
"""
Test script for the workspace management tool.
"""

import subprocess
import sys
import tempfile
import shutil
from pathlib import Path


def run_command(cmd, cwd=None):
    """Run a command and return the result."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.stdout:
        print(f"stdout: {result.stdout}")
    if result.stderr:
        print(f"stderr: {result.stderr}")
    return result


def test_workspace_tool():
    """Test the workspace tool functionality."""
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        test_repo = Path(temp_dir) / "test_repo"
        test_repo.mkdir()
        
        print(f"Testing in: {test_repo}")
        
        # Initialize a git repository
        run_command(["git", "init"], cwd=test_repo)
        run_command(["git", "config", "user.name", "Test User"], cwd=test_repo)
        run_command(["git", "config", "user.email", "test@example.com"], cwd=test_repo)
        
        # Create initial commit
        (test_repo / "README.md").write_text("# Test Repository")
        run_command(["git", "add", "README.md"], cwd=test_repo)
        run_command(["git", "commit", "-m", "Initial commit"], cwd=test_repo)
        
        # Copy workspace tool to test directory
        workspace_tool = Path(__file__).parent.parent / "scripts" / "workspace.py"
        shutil.copy(workspace_tool, test_repo / "workspace.py")
        
        # Test list command (should show no workspaces)
        result = run_command(["python3", "workspace.py", "list"], cwd=test_repo)
        assert "No workspaces found" in result.stdout
        
        print("✓ List command works correctly")
        
        # Test help command
        result = run_command(["python3", "workspace.py", "--help"], cwd=test_repo)
        assert result.returncode == 0
        assert "Workspace management tool" in result.stdout
        
        print("✓ Help command works correctly")
        
        print("All tests passed!")


if __name__ == "__main__":
    try:
        test_workspace_tool()
        print("✓ Workspace tool test completed successfully")
    except Exception as e:
        print(f"✗ Test failed: {e}")
        sys.exit(1)
