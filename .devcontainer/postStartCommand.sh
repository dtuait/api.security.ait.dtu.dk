#!/bin/bash

# Ensure venv is active and dependencies are up to date
cd /usr/src/project/app-main && source /usr/src/venvs/app-main/bin/activate

# Keep the development venv aligned with requirements
pip install -r /usr/src/project/app-main/requirements.txt >/dev/null 2>&1 || true

# Optionally run entrypoint tasks manually in dev if needed
# bash /entrypoint.sh
