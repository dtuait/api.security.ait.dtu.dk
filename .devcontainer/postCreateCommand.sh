# cd ./app and remove venv if it exits, then rebuild venv, activate it, and install requirements
# cd ./app-main && rm -rf venv && \
#     python3 -m venv venv && \
#     source venv/bin/activate && \
#     pip install --upgrade pip && \
#     pip install -r requirements.txt

cd ./app-main && source venv/bin/activate

git config --global user.email "vicre@dtu.dk"
git config --global user.name "Victor Reipur"
git config --global --add safe.directory /usr/src/project
git config --global --add safe.directory /mnt/project
git config --global --add safe.directory /usr/src/project/.docker-migrate
git config pull.rebase true
