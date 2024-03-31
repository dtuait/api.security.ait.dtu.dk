# cd ./app and remove venv if it exits, then rebuild venv, activate it, and install requirements
# cd ./app-main && rm -rf venv && \
#     python3 -m venv venv && \
#     source venv/bin/activate && \
#     pip install --upgrade pip && \
#     pip install -r requirements.txt

echo "Starting postCreateCommand.sh"

cd /usr/src/project/app-main && source /usr/src/venvs/app-main/bin/activate

git config --global user.email "vicre@dtu.dk"
git config --global user.name "Victor Reipur"
git config --global --add safe.directory /usr/src/project
git config --global --add safe.directory /mnt/project
git config --global --add safe.directory /usr/src/project/.devcontainer/.docker-migrate
git config --global --add safe.directory /usr/src/project/.devcontainer/.docker-image-builder
git config pull.rebase true
# git submodule update --remote # gets the latest commit from the submodule

# show current pip freeze
echo "Show current pip freeze into requirements.txt"
/usr/src/venvs/app-main/bin/pip freeze > /usr/src/project/app-main/requirements.txt

echo "Getting git submodules"
git submodule init && git submodule update

echo "Ending postCreateCommand.sh"