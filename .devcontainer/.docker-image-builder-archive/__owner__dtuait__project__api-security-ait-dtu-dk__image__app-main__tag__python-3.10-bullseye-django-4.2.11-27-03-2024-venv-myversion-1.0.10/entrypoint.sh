#!/bin/bash

# Ensure the script exits if any command fails
set -e

# Create the dockeruser with the specified UID and GID
if [ -n "$HOST_UID" ] && [ -n "$HOST_GID" ]; then
    # Create a group with the HOST_GID if it does not already exist
    if ! getent group $HOST_GID > /dev/null 2>&1; then
        groupadd -g $HOST_GID dockeruser
    fi
    
    # Ensure the home directory exists and create a .bashrc file
    mkdir -p /usr/src/project
    
    # Create a user with the HOST_UID and HOST_GID, and set the home directory
    if ! id -u $HOST_UID > /dev/null 2>&1; then
        useradd -u $HOST_UID -g $HOST_GID -m -d /usr/src/project dockeruser
        # Ensure the .bashrc file and home directory are owned by dockeruser
        chown $HOST_UID:$HOST_GID /usr/src/project/.bashrc
    fi
fi

# Change ownership of the mounted directories (optional, if needed)
chown -R $HOST_UID:$HOST_GID /usr/src/project
chown -R $HOST_UID:$HOST_GID /mnt/shared-project-data


# Add user and grant sudo privileges
useradd -m dockeruser && echo "dockeruser:dockeruser" | chpasswd && adduser dockeruser sudo
echo 'dockeruser ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/dockeruser


# Always run /bin/bash with gosu as dockeruser, ignoring any passed command
source /usr/src/project/.bashrc
chsh -s /bin/bash dockeruser
exec gosu dockeruser /bin/bash