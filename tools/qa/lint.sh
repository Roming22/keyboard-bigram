#!/bin/bash
echo "Lint"; echo
set -e
set -o pipefail
SCRIPT_DIR="$(dirname "$(realpath "$0")")"
PROJECT_DIR="$(realpath "${SCRIPT_DIR}/../..")"
cd "${PROJECT_DIR}"

parse_args(){
    LINTERS=()
    while [[ "$#" -gt "0" ]]; do
        case $1 in
            --*)
                LINTERS+=( "$(echo "$1" | cut -c3-)" )
                ;;
        esac
        shift
    done

    if [[ -z "${LINTERS[*]}" ]]; then
        for LINTER in "pylint" "shellcheck"; do
            LINTERS+=( "${LINTER}" )
        done
    fi
}

run_pylint(){
    DIR="src"
    find "${PROJECT_DIR}/${DIR}" -maxdepth 1 -mindepth 1 -type d -not -name \*.egg-info | while read -r SUBDIR; do
        echo "=> pylint ${PROJECT_DIR}/${DIR}"
        poetry run pylint --rcfile="${SCRIPT_DIR}/pylintrc.${DIR}.ini" "${SUBDIR}"
    done
    DIR="tests"
    echo "=> pylint ${PROJECT_DIR}/${DIR}"
    poetry run pylint --rcfile="${SCRIPT_DIR}/pylintrc.${DIR}.ini" "${PROJECT_DIR}/${DIR}"

    echo

}

run_shellcheck(){
    echo "=> shellcheck"
    find "${PROJECT_DIR}" -name \*.sh -print0 | xargs --no-run-if-empty --null poetry run shellcheck
    echo
}

parse_args "$@"
for LINTER in "${LINTERS[@]}"; do
    "run_${LINTER}"
done
echo [OK]
