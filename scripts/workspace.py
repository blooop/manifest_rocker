#!/usr/bin/env python3
"""
Workspace management tool for manifest repositories.
"""

import argparse
import subprocess
import sys
from pathlib import Path


class WorkspaceManager:
    """Manages git worktrees for different codebases."""
    
    def __init__(self, repo_root=None):
        if repo_root is None:
            repo_root = Path.cwd()
        
        self.repo_root = Path(repo_root).resolve()
        self.worktrees_dir = self.repo_root / "worktrees"
        
        # Ensure we're in a git repository
        if not (self.repo_root / ".git").exists():
            raise RuntimeError(f"Not a git repository: {self.repo_root}")
    
    def _run_git_command(self, cmd, cwd=None):
        """Run a git command and return the result."""
        if cwd is None:
            cwd = self.repo_root
            
        full_cmd = ["git"] + cmd
        print(f"Running: {' '.join(full_cmd)} (in {cwd})")
        
        try:
            result = subprocess.run(
                full_cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                check=True
            )
            return result
        except subprocess.CalledProcessError as e:
            print(f"Git command failed: {e}")
            print(f"stdout: {e.stdout}")
            print(f"stderr: {e.stderr}")
            raise
    
    def _parse_repo_spec(self, repo_spec):
        """Parse repo specification in format: repo_name:branch[:folder_in_repo]"""
        parts = repo_spec.split(":")
        if len(parts) < 2:
            raise ValueError(f"Invalid repo spec: {repo_spec}. Expected format: repo_name:branch[:folder_in_repo]")
        
        repo_name = parts[0]
        branch = parts[1]
        folder_in_repo = parts[2] if len(parts) > 2 else None
        
        return repo_name, branch, folder_in_repo
    
    def _get_existing_branches(self):
        """Get list of existing local branches."""
        result = self._run_git_command(["branch", "--format=%(refname:short)"])
        return [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
    
    def _get_existing_worktrees(self):
        """Get list of existing worktrees."""
        try:
            result = self._run_git_command(["worktree", "list", "--porcelain"])
            worktrees = []
            for line in result.stdout.strip().split('\n'):
                if line.startswith('worktree '):
                    worktree_path = line.replace('worktree ', '')
                    worktree_name = Path(worktree_path).name
                    if worktree_name != self.repo_root.name:  # Skip main worktree
                        worktrees.append(worktree_name)
            return worktrees
        except subprocess.CalledProcessError:
            return []
    
    def add_workspace(self, repo_spec, branch_name):
        """Add a new workspace by cloning a repo/branch and creating a worktree."""
        repo_name, remote_branch, folder_in_repo = self._parse_repo_spec(repo_spec)
        
        # Check if branch already exists
        existing_branches = self._get_existing_branches()
        if branch_name in existing_branches:
            print(f"Branch '{branch_name}' already exists. Use 'workspace open {branch_name}' to open it.")
            return
        
        # Ensure worktrees directory exists
        self.worktrees_dir.mkdir(exist_ok=True)
        
        worktree_path = self.worktrees_dir / branch_name
        
        # Check if worktree directory already exists
        if worktree_path.exists():
            print(f"Worktree directory '{worktree_path}' already exists.")
            return
        
        try:
            # Add remote if it doesn't exist
            try:
                self._run_git_command(["remote", "get-url", repo_name])
                print(f"Remote '{repo_name}' already exists")
            except subprocess.CalledProcessError:
                # Assume repo_name is a URL if it contains :// or @
                if "://" in repo_name or "@" in repo_name:
                    remote_url = repo_name
                else:
                    # Try common git hosting patterns
                    if "/" in repo_name:
                        remote_url = f"https://github.com/{repo_name}.git"
                    else:
                        raise ValueError(f"Cannot determine remote URL for: {repo_name}")
                
                print(f"Adding remote '{repo_name}' -> '{remote_url}'")
                self._run_git_command(["remote", "add", repo_name, remote_url])
            
            # Fetch from the remote
            print(f"Fetching from remote '{repo_name}'")
            self._run_git_command(["fetch", repo_name])
            
            # Create new branch tracking the remote branch
            remote_ref = f"{repo_name}/{remote_branch}"
            print(f"Creating branch '{branch_name}' from '{remote_ref}'")
            self._run_git_command(["branch", branch_name, remote_ref])
            
            # Create worktree
            print(f"Creating worktree at '{worktree_path}'")
            self._run_git_command(["worktree", "add", str(worktree_path), branch_name])
            
            # If folder_in_repo is specified, we need to handle it
            if folder_in_repo:
                print(f"Note: Folder filtering for '{folder_in_repo}' is not yet implemented.")
                print("You can manually navigate to the desired folder in the worktree.")
            
            print(f"Workspace '{branch_name}' created successfully at: {worktree_path}")
            print(f"To open in VS Code, run: code {worktree_path}")
            
        except subprocess.CalledProcessError as e:
            print(f"Failed to create workspace: {e}")
            # Clean up on failure
            if worktree_path.exists():
                self._run_git_command(["worktree", "remove", str(worktree_path)])
            try:
                self._run_git_command(["branch", "-D", branch_name])
            except subprocess.CalledProcessError:
                pass  # Branch might not have been created
            raise
    
    def open_workspace(self, branch_name):
        """Open an existing workspace worktree."""
        worktree_path = self.worktrees_dir / branch_name
        
        # Check if worktree exists
        if not worktree_path.exists():
            existing_worktrees = self._get_existing_worktrees()
            print(f"Worktree '{branch_name}' not found.")
            if existing_worktrees:
                print("Available worktrees:")
                for wt in existing_worktrees:
                    print(f"  - {wt}")
            else:
                print("No worktrees found. Use 'workspace add' to create one.")
            return
        
        # Open in VS Code
        print(f"Opening workspace '{branch_name}' in VS Code...")
        try:
            subprocess.run(["code", str(worktree_path)], check=True)
        except subprocess.CalledProcessError:
            print(f"Failed to open VS Code. You can manually navigate to: {worktree_path}")
        except FileNotFoundError:
            print(f"VS Code not found in PATH. You can manually navigate to: {worktree_path}")
    
    def list_workspaces(self):
        """List all available workspaces."""
        existing_worktrees = self._get_existing_worktrees()
        
        if not existing_worktrees:
            print("No workspaces found.")
            return
        
        print("Available workspaces:")
        for wt in existing_worktrees:
            worktree_path = self.worktrees_dir / wt
            print(f"  - {wt} ({worktree_path})")
    
    def remove_workspace(self, branch_name):
        """Remove a workspace and its associated branch."""
        worktree_path = self.worktrees_dir / branch_name
        
        if not worktree_path.exists():
            print(f"Worktree '{branch_name}' not found.")
            return
        
        # Confirm removal
        response = input(f"Are you sure you want to remove workspace '{branch_name}'? [y/N]: ")
        if response.lower() != 'y':
            print("Cancelled.")
            return
        
        try:
            # Remove worktree
            print(f"Removing worktree '{branch_name}'...")
            self._run_git_command(["worktree", "remove", str(worktree_path)])
            
            # Remove branch
            print(f"Removing branch '{branch_name}'...")
            self._run_git_command(["branch", "-D", branch_name])
            
            print(f"Workspace '{branch_name}' removed successfully.")
            
        except subprocess.CalledProcessError as e:
            print(f"Failed to remove workspace: {e}")


def main():
    """Main entry point for the workspace tool."""
    parser = argparse.ArgumentParser(
        description="Workspace management tool for manifest repositories",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  workspace add https://github.com/user/repo.git:main my-workspace
  workspace add user/repo:develop:src/package my-dev-workspace
  workspace open my-workspace
  workspace list
  workspace remove my-workspace
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new workspace")
    add_parser.add_argument(
        "repo_spec",
        help="Repository specification: repo_name:branch[:folder_in_repo]"
    )
    add_parser.add_argument("branch_name", help="Name for the new local branch and worktree")
    
    # Open command
    open_parser = subparsers.add_parser("open", help="Open an existing workspace")
    open_parser.add_argument("branch_name", help="Name of the branch/worktree to open")
    
    # List command
    subparsers.add_parser("list", help="List all available workspaces")
    
    # Remove command
    remove_parser = subparsers.add_parser("remove", help="Remove a workspace")
    remove_parser.add_argument("branch_name", help="Name of the branch/worktree to remove")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        manager = WorkspaceManager()
        
        if args.command == "add":
            manager.add_workspace(args.repo_spec, args.branch_name)
        elif args.command == "open":
            manager.open_workspace(args.branch_name)
        elif args.command == "list":
            manager.list_workspaces()
        elif args.command == "remove":
            manager.remove_workspace(args.branch_name)
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
