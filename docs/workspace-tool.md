# Workspace Management Tool

The workspace tool allows you to manage different codebases as separate git branches and worktrees without needing to commit anything. This is particularly useful for manifest repositories where each branch represents a completely different codebase.

## Installation

The tool is located at `scripts/workspace` and can be run directly:

```bash
./scripts/workspace [command] [arguments]
```

## Commands

### Add a new workspace

```bash
workspace add [repo_name:branch:folder_in_repo] name_of_branch
```

This command:
1. Adds the remote repository if it doesn't exist
2. Fetches the specified branch from the remote
3. Creates a new local branch tracking the remote branch
4. Creates a worktree in `worktrees/name_of_branch/`
5. Optionally opens the worktree in VS Code

**Examples:**

```bash
# Add a workspace from a GitHub repository
workspace add https://github.com/user/repo.git:main my-workspace

# Add a workspace using GitHub shorthand notation
workspace add user/repo:develop my-dev-workspace

# Add a workspace with a specific folder (note: folder filtering not yet implemented)
workspace add user/repo:main:src/package my-package-workspace
```

### Open an existing workspace

```bash
workspace open name_of_branch
```

This command opens the specified workspace worktree in VS Code.

**Example:**

```bash
workspace open my-workspace
```

### List all workspaces

```bash
workspace list
```

This command shows all available workspaces and their paths.

### Remove a workspace

```bash
workspace remove name_of_branch
```

This command removes both the worktree and the associated branch after confirmation.

**Example:**

```bash
workspace remove my-workspace
```

## How it works

### Git Worktrees

The tool uses git worktrees to manage multiple working directories. Each workspace is:

- A separate git branch
- A separate working directory under `worktrees/`
- Completely isolated from other workspaces

### Repository Structure

```
project-root/
├── .git/
├── main-project-files...
└── worktrees/
    ├── workspace1/
    │   └── files-from-branch1...
    ├── workspace2/
    │   └── files-from-branch2...
    └── workspace3/
        └── files-from-branch3...
```

### Benefits

1. **No need to commit**: Switch between codebases without committing changes
2. **Isolated environments**: Each workspace is completely separate
3. **Fast switching**: No need to clone repositories multiple times
4. **VS Code integration**: Automatically opens workspaces in VS Code

## Workflow Example

1. **Add a new workspace from a third-party repository:**
   ```bash
   workspace add https://github.com/ros/ros_tutorials.git:melodic ros-melodic-tutorials
   ```

2. **Work in the workspace:**
   ```bash
   workspace open ros-melodic-tutorials
   # VS Code opens with the ROS tutorials code
   ```

3. **Add another workspace for a different branch:**
   ```bash
   workspace add ros/ros_tutorials:noetic ros-noetic-tutorials
   ```

4. **Switch between workspaces as needed:**
   ```bash
   workspace open ros-noetic-tutorials
   workspace open ros-melodic-tutorials
   ```

5. **List all available workspaces:**
   ```bash
   workspace list
   ```

6. **Remove workspace when done:**
   ```bash
   workspace remove ros-melodic-tutorials
   ```

## Requirements

- Python 3.6+
- Git 2.5+ (for worktree support)
- VS Code (optional, for automatic opening)

## Limitations

- Folder filtering (`repo:branch:folder`) is not yet implemented
- Only supports Git repositories
- Requires manual setup of remotes for private repositories that need authentication

## Troubleshooting

### "Not a git repository" error
Make sure you're running the tool from within a git repository.

### "VS Code not found" error
The tool will still create the workspace, you can manually navigate to the worktree directory.

### Remote authentication issues
For private repositories, you may need to configure git credentials or SSH keys manually.
