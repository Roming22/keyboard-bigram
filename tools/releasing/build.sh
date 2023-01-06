#!/bin/bash -e
#
# Build the image
#
set -o pipefail
SCRIPT_DIR="$(dirname "$(realpath "$0")")"
PROJECT_DIR="$(realpath "${SCRIPT_DIR}/../..")"

# Generate a new version
if [[ -n "${IMAGE_REPOSITORY_USER}" ]]; then
    python tools/releasing/version.py
    VERSION="$(python "${PROJECT_DIR}/src/myapp/__version__.py")"
else
    VERSION="latest"
fi
# Build the image
echo "Release: ${VERSION}"
DOCKERFILE="${PROJECT_DIR}/tools/tooling/container/Dockerfile"
TAG="myapp:latest"
TARGET="release"
docker build --file "${DOCKERFILE}" --tag "${TAG}" --target "${TARGET}" "${PROJECT_DIR}"

if [[ -n "${IMAGE_REPOSITORY_USER}" ]]; then
    docker tag "${TAG}" "${IMAGE_REPOSITORY_USER}/myapp:${VERSION}"
    echo "${IMAGE_REPOSITORY_USER}/myapp:${VERSION}"
else
    IMAGE_REPOSITORY_USER="k3d-registry.localhost"
    if ping -c1 -q "$IMAGE_REPOSITORY_USER" >/dev/null 2>&1; then
        IMAGE_REPOSITORY_USER="${IMAGE_REPOSITORY_USER}/skwr/web"
        docker tag "${TAG}" "${IMAGE_REPOSITORY_USER}/myapp:${VERSION}"
    else
        echo "[WARNING] IMAGE_REPOSITORY_USER is not set, image can't be pushed without being retagged";
    fi
    echo "$TAG"
fi
