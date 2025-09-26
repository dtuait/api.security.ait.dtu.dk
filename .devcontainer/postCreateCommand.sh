#!/bin/bash

# this script runs first time when container is created
echo "running postCreateCommand.sh"

# Resolve workspace path provided by the devcontainer runtime (falls back to /app)
workspace_dir=${REMOTE_CONTAINERS_WORKSPACE_FOLDER:-/app}
venv_pip="/usr/src/venvs/app-main/bin/pip"
requirements_target="$workspace_dir/app-main/requirements.txt"

if [ ! -d "$workspace_dir" ]; then
    echo "Error: workspace directory '$workspace_dir' does not exist."
    exit 1
fi

# store current pwd into a variable
current_pwd=$(pwd)
cd "$workspace_dir"

# Check if the workspace is a valid git repository
if [ -d ".git" ]; then
    # Set git to ignore file mode (permissions) changes in this repository
    git config core.fileMode false
else
    echo "Error: $workspace_dir/.git is not a valid git repository."
fi

# Set git to ignore file mode (permissions) changes globally for all repositories
git config --global core.fileMode false

echo "Enter your username:"
read username
case $username in
    afos)
        git config --global user.email "afos@dtu.dk"
        git config --global user.name "Anders Fosgerau"
        ;;
    jaholm)
        git config --global user.email "jaholm@dtu.dk"
        git config --global user.name "Jakob Holm"
        ;;
    vicre)
        git config --global user.email "vicre@dtu.dk"
        git config --global user.name "Victor Reipur"
        ;;
    *)
        echo "Enter your email:"
        read email
        git config --global user.email "$email"
        echo "Enter your name:"
        read name
        git config --global user.name "$name"
        ;;
esac

git config --global --add safe.directory "$workspace_dir"
# git config --global --add safe.directory /mnt/project
# git config --global --add safe.directory "$workspace_dir/.devcontainer/.docker-migrate"
# git config --global --add safe.directory "$workspace_dir/.devcontainer/.docker-image-builder"

if [ -d ".git" ]; then
    git config pull.rebase true
fi

# show current pip freeze
echo "Show current pip freeze into requirements.txt"
if [ -x "$venv_pip" ]; then
    "$venv_pip" freeze > "$requirements_target"
else
    echo "Warning: pip executable '$venv_pip' not found; skipping freeze."
fi

if [ -d ".git" ]; then
    echo "Getting git submodules"
    git submodule init && git submodule update
fi


echo "Ending postCreateCommand.sh"

# restore the pwd
cd "$current_pwd"
