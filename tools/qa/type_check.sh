#!/bin/bash
echo "Type check"; echo
set -e
set -o pipefail
SCRIPT_DIR="$(dirname "$(realpath "$0")")"
PROJECT_DIR="$(realpath "${SCRIPT_DIR}/../..")"

run_mypy(){
    echo "=> mypy ${PROJECT_DIR}/src"
    poetry run mypy "${PROJECT_DIR}/src"
    echo

}

run_mypy
echo [OK]