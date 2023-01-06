#!/bin/bash -e
SCRIPT_DIR="$(cd "$(dirname "$0")"; pwd)"
poetry run "$SCRIPT_DIR/../myapp/main.py" "$@"