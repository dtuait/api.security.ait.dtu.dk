#!/bin/bash

# Ensure the script exits if any command fails
set -e

# Set default UID and GID to 65000 if not provided
DEFAULT_UID=65000
DEFAULT_GID=65000
HOST_UID=${HOST_UID:-$DEFAULT_UID}
HOST_GID=${HOST_GID:-$DEFAULT_GID}

# Create the dockeruser with the specified UID and GID
# Create a group with the HOST_GID if it does not already exist
if ! getent group $HOST_GID > /dev/null 2>&1; then
    groupadd -g $HOST_GID dockeruser
fi

# Create a user with the HOST_UID and HOST_GID
if ! id -u $HOST_UID > /dev/null 2>&1; then
    useradd -u $HOST_UID -g $HOST_GID -m dockeruser
fi

# Change ownership of the mounted directories (optional, if needed)
chown -R $HOST_UID:$HOST_GID /usr/src/project
chown -R $HOST_UID:$HOST_GID /mnt/shared-project-data

# Default to a simple shell if no command is passed
if [ "$#" -eq 0 ]; then
    set -- bash
fi

# Run the specified command as dockeruser
exec gosu dockeruser "$@"