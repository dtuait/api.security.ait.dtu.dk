#!/bin/bash

# this script runs first time when container is created
echo "running postCreateCommand.sh"

# store current pwd into a variable
current_pwd=$(pwd)
cd /usr/src/project

# Check if /usr/src/project/.git is a valid git repository
if [ -d "/usr/src/project/.git" ]; then
    # Set git to ignore file mode (permissions) changes in this repository
    git --git-dir=/usr/src/project/.git config core.fileMode false
else
    echo "Error: /usr/src/project/.git is not a valid git repository."
fi

# Set git to ignore file mode (permissions) changes globally for all repositories
git config --global core.fileMode false

# Try to get name and email from .env.local
if [ -f "/usr/src/project/app-main/.env.local" ]; then
  GIT_USER_NAME=$(grep -oP '^DEVCONTAINER_GITHUB_NAME=\K.*' /usr/src/project/.devcontainer/.env)
  GIT_USER_EMAIL=$(grep -oP '^DEVCONTAINER_GITHUB_EMAIL=\K.*' /usr/src/project/.devcontainer/.env)
fi

# If name or email is empty, prompt the user
if [ -z "$GIT_USER_NAME" ]; then
  echo "Enter your name:"
  read GIT_USER_NAME
fi

if [ -z "$GIT_USER_EMAIL" ]; then
  echo "Enter your email:"
  read GIT_USER_EMAIL
fi

git config --global --add safe.directory /usr/src/project
# git config --global --add safe.directory /mnt/project
# git config --global --add safe.directory /usr/src/project/.devcontainer/.docker-migrate
# git config --global --add safe.directory /usr/src/project/.devcontainer/.docker-image-builder
git config pull.rebase true

# show current pip freeze
echo "Show current pip freeze into requirements.txt"
/usr/src/venvs/app-main/bin/pip freeze > /usr/src/project/app-main/requirements.txt

echo "Getting git submodules"
git submodule init && git submodule update

echo "Ending postCreateCommand.sh"

# restore the pwd
cd $current_pwd
