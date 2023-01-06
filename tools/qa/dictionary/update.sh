#!/bin/bash
echo "Update dictionary"
set -e
set -o pipefail
SCRIPT_DIR="$(dirname "$(realpath "$0")")"
PROJECT_DIR="$(realpath "${SCRIPT_DIR}/../../..")"

set -x
parse_args(){
    DICT="${SCRIPT_DIR}/words.txt"
    while [[ "$#" -gt "0" ]]; do
        case $1 in
            --check)
                ACTION="check"
                ;;
        esac
        shift
    done
    ACTION="${ACTION:-generate}"
}

generate(){
    DIR="src"
    find "${PROJECT_DIR}/${DIR}" -maxdepth 1 -mindepth 1 -type d -not -name \*.egg-info | while read -r SUBDIR; do
        echo "=> pylint ${PROJECT_DIR}/${DIR}"
        poetry run pylint --rcfile="${SCRIPT_DIR}/pylintrc.dictionary.ini" "${SUBDIR}"
    done
    DIR="tests"
    echo "=> pylint ${PROJECT_DIR}/${DIR}"
    poetry run pylint --rcfile="${SCRIPT_DIR}/pylintrc.dictionary.ini" "${PROJECT_DIR}/${DIR}"
    sort -o "${DICT}" "${DICT}"
}

check(){
    CURRENT="${DICT}.bak"
    NEW="${DICT}.new"
    mv "${DICT}" "${CURRENT}"
    generate
    mv "${DICT}" "${NEW}" 
    mv "${CURRENT}" "${DICT}"
    diff "${DICT}" "${NEW}"
    rm -f "${NEW}"
}

parse_args "$@"
$ACTION
echo "[OK]"