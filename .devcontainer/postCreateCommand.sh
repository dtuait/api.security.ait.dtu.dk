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

allow_prompt=${DEVCONTAINER_ALLOW_INTERACTIVE_PROMPT:-0}
username=${DEVCONTAINER_GIT_USERNAME:-}
email=${DEVCONTAINER_GIT_EMAIL:-}
name=${DEVCONTAINER_GIT_NAME:-}

if [ "$allow_prompt" = "1" ] && [ -t 0 ]; then
    echo "Enter your username:"
    read -r username
    case "$username" in
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
            read -r email
            git config --global user.email "$email"
            echo "Enter your name:"
            read -r name
            git config --global user.name "$name"
            ;;
    esac
fi

if [ -z "$email" ] || [ -z "$name" ]; then
    case "$username" in
        afos)
            email="afos@dtu.dk"
            name="Anders Fosgerau"
            ;;
        jaholm)
            email="jaholm@dtu.dk"
            name="Jakob Holm"
            ;;
        vicre)
            email="vicre@dtu.dk"
            name="Victor Reipur"
            ;;
        "")
            echo "Skipping git identity setup (no username/email provided)."
            ;;
        *)
            if [ -z "$email" ] || [ -z "$name" ]; then
                echo "Skipping git identity setup: no email/name provided for username '$username'."
            fi
            ;;
    esac
fi

if [ -n "$email" ] && [ -n "$name" ]; then
    git config --global user.email "$email"
    git config --global user.name "$name"
fi

git config --global --add safe.directory "$workspace_dir"
# git config --global --add safe.directory /mnt/project
# git config --global --add safe.directory "$workspace_dir/.devcontainer/.docker-migrate"
# git config --global --add safe.directory "$workspace_dir/.devcontainer/.docker-image-builder"

if [ -d ".git" ]; then
    git config pull.rebase true
fi

# ensure required Python dependencies are installed
pip_candidates=()
if [ -x "$venv_pip" ]; then
    pip_candidates+=("$venv_pip")
fi
if command -v python3 >/dev/null 2>&1; then
    pip_candidates+=("python3 -m pip")
fi
if command -v pip3 >/dev/null 2>&1; then
    pip_candidates+=("pip3")
fi

if [ ${#pip_candidates[@]} -eq 0 ]; then
    echo "Warning: no pip executable found; skipping Python dependency install."
elif [ ! -f "$requirements_target" ]; then
    echo "Warning: requirements file '$requirements_target' not found; skipping Python dependency install."
else
    freeze_written=0
    for pip_cmd in "${pip_candidates[@]}"; do
        if ! eval "$pip_cmd --version" >/dev/null 2>&1; then
            echo "Skipping pip command '$pip_cmd'; not available."
            continue
        fi

        echo "Installing Python dependencies with '$pip_cmd'"
        eval "$pip_cmd install --upgrade pip setuptools wheel"
        eval "$pip_cmd install -r '$requirements_target'"

        if [ $freeze_written -eq 0 ] && [ "$pip_cmd" = "$venv_pip" ]; then
            echo "Updating requirements.txt with current venv environment"
            "$venv_pip" freeze > "$requirements_target"
            freeze_written=1
        fi
    done

    if [ $freeze_written -eq 0 ] && [ -x "$venv_pip" ]; then
        echo "Updating requirements.txt with current venv environment"
        "$venv_pip" freeze > "$requirements_target"
    fi
fi

if [ -d ".git" ]; then
    echo "Getting git submodules"
    git submodule init && git submodule update
fi


echo "Ending postCreateCommand.sh"

# restore the pwd
cd "$current_pwd"
