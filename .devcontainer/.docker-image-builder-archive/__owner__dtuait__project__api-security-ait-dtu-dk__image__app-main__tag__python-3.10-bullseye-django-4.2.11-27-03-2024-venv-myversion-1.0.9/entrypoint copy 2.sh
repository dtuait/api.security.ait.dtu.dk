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

source /usr/src/project/.bashrc

# # Question: what is @ in this context exec gosu dockeruser "$@"
# # Answer: In the context of the shell script, "$@" represents all the positional parameters passed to the script, starting from the first one. When used with exec gosu dockeruser "$@", it means to execute the command gosu with dockeruser as the first argument, followed by all the arguments originally passed to the script. This allows the script to pass through any command-line arguments to the command being executed under gosu, effectively running that command as the dockeruser user with those arguments. If no arguments are passed to the script, the condition above it (if [ "$#" -eq 0 ]; then) will catch that case and default to running /bin/bash as dockeruser.
# if [ "$#" -eq 0 ]; then
#     exec gosu dockeruser /bin/bash
# else
#     exec gosu dockeruser "$@"
# fi

chsh -s /bin/bash dockeruser

# Always run /bin/bash with gosu as dockeruser, ignoring any passed command
exec gosu dockeruser /bin/bash