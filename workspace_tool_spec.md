make a tool that supports these commands

workspace add [repo_name:branch:folder_in_repo] name of branch
workspace open name_of_branch

The development workflow is to select a third party repo branch, and optionally a folder in that repo. Using the add command clones the selected code into a new branchname provided by the user and then creates a worktree folder with the same name and opens that worktree. 

workspace open takes the branchname and opens that worktree. 