#!/bin/bash
echo "Format"; echo
set -e
set -o pipefail
SCRIPT_DIR="$(dirname "$(realpath "$0")")"
PROJECT_DIR="$(realpath "${SCRIPT_DIR}/../..")"

OPTIONS=()
PATHS=()
while [[ "$#" -gt "0" ]]; do
    case $1 in
        --check)
            OPTIONS+=( "$1" )
            ;;
        *)
            [[ -e "$1" ]] || { echo "[ERROR] Path not found: $1"; exit 1; };
            PATHS+=( "$(realpath --relative-to="${PROJECT_DIR}" "$1")" )
            ;;
    esac
    shift
done
[[ -n "${PATHS[*]}" ]] || PATHS+=( "$PROJECT_DIR" )

cd "${PROJECT_DIR}"
echo "PWD"
set -x
poetry run isort --profile=black "${OPTIONS[@]}" "${PATHS[@]}"
poetry run black "${OPTIONS[@]}" "${PATHS[@]}"

echo [OK]