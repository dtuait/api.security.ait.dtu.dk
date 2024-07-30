#!/bin/bash

# Ensure the script exits if any command fails
set -e

# Read environment variables for user configuration
DOCKERUSER_UID=${DOCKERUSER_UID:-65000}
DOCKERUSER_GID=${DOCKERUSER_GID:-65000}
DOCKERUSER_NAME=${DOCKERUSER_NAME:-dockeruser}
DOCKERUSER_PASSWORD=${DOCKERUSER_PASSWORD:-dockeruser}
DOCKERUSER_HOME=${DOCKERUSER_HOME:-/home/dockeruser}
DOCKERUSER_SHELL=${DOCKERUSER_SHELL:-/bin/bash}

# Function to setup or update home directory
setup_home_directory () {
    mkdir -p $1
    chown $DOCKERUSER_UID:$DOCKERUSER_GID $1
    if [ ! -f "$1/.bashrc" ]; then
        touch "$1/.bashrc"
        chown $DOCKERUSER_UID:$DOCKERUSER_GID "$1/.bashrc"
    fi
}

# Ensure root operations
if [ "$(id -u)" -eq 0 ]; then
    # Create group if it does not exist
    if ! getent group $DOCKERUSER_GID &>/dev/null; then
        groupadd -g $DOCKERUSER_GID $DOCKERUSER_NAME
    fi

    # Create or modify the user
    if ! id -u $DOCKERUSER_UID &>/dev/null; then
        useradd -u $DOCKERUSER_UID -g $DOCKERUSER_GID -m -d $DOCKERUSER_HOME -s $DOCKERUSER_SHELL $DOCKERUSER_NAME > /dev/null 2>&1
        setup_home_directory $DOCKERUSER_HOME
    else
        usermod -u $DOCKERUSER_UID -g $DOCKERUSER_GID -d $DOCKERUSER_HOME -s $DOCKERUSER_SHELL $DOCKERUSER_NAME
        if [ "$(grep $DOCKERUSER_NAME /etc/passwd | cut -d: -f6)" != "$DOCKERUSER_HOME" ]; then
            user_home_old=$(grep $DOCKERUSER_NAME /etc/passwd | cut -d: -f6)
            mv $user_home_old/* $DOCKERUSER_HOME/ 2>/dev/null || true
            mv $user_home_old/.* $DOCKERUSER_HOME/ 2>/dev/null || true
            rmdir $user_home_old || true
        fi
        setup_home_directory $DOCKERUSER_HOME
    fi

    # Ensure /usr/src/project directory exists and has the correct permissions
    mkdir -p /usr/src/project
    chown $DOCKERUSER_UID:$DOCKERUSER_GID /usr/src/project

    # Set ownership to the user's home directory and create .bashrc if not exists
    chown $DOCKERUSER_UID:$DOCKERUSER_GID $DOCKERUSER_HOME
    touch $DOCKERUSER_HOME/.bashrc
    chown $DOCKERUSER_UID:$DOCKERUSER_GID $DOCKERUSER_HOME/.bashrc

    # Add dockeruser and grant sudo privileges
    echo "$DOCKERUSER_NAME:$DOCKERUSER_PASSWORD" | chpasswd
    usermod -aG sudo $DOCKERUSER_NAME
    echo "$DOCKERUSER_NAME ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/$DOCKERUSER_NAME

    # Execute the script again as dockeruser
    exec gosu $DOCKERUSER_NAME "$0" "$@"
else
    # If already running as dockeruser, execute the provided command
    exec "$@"
fi