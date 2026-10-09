#!/usr/bin/env bash
# Build and run the reference Apache Atlas 2.4.0 with Atlas's own Docker set-up
# (dev-support/atlas-docker in the Atlas source tree). See README.md.
set -euo pipefail

ATLAS_TAG="${ATLAS_TAG:-release-2.4.0}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="${HERE}/.atlas-src"
DOCKER_DIR="${SRC}/dev-support/atlas-docker"
COMPOSE=(docker compose -f docker-compose.atlas-base.yml -f docker-compose.atlas.yml
    -f docker-compose.atlas-hadoop.yml -f docker-compose.atlas-hbase.yml -f docker-compose.atlas-kafka.yml)

prepare() {
    if [ ! -d "${SRC}/.git" ]; then
        git clone --depth 1 --branch "${ATLAS_TAG}" https://github.com/apache/atlas.git "${SRC}"
    fi
    cd "${DOCKER_DIR}"
    # Build the tagged release, not the branch named in Atlas's own .env.
    sed -i.bak -e "s|^BRANCH=.*|BRANCH=${ATLAS_TAG}|" .env
    chmod +x download-archives.sh
    ./download-archives.sh
}

build() {
    cd "${DOCKER_DIR}"
    export DOCKER_BUILDKIT=1 COMPOSE_DOCKER_CLI_BUILD=1
    docker compose -f docker-compose.atlas-base.yml -f docker-compose.atlas-build.yml up --abort-on-container-exit
}

up() {
    cd "${DOCKER_DIR}"
    "${COMPOSE[@]}" up -d
    echo "Waiting for Atlas on http://localhost:21000 (first start takes several minutes)..."
    for _ in $(seq 1 120); do
        if curl -fs -u admin:atlasR0cks! http://localhost:21000/api/atlas/admin/version > /dev/null; then
            echo "Atlas is up."
            return 0
        fi
        sleep 10
    done
    echo "Atlas did not answer within 20 minutes; see: docker logs atlas" >&2
    return 1
}

down() {
    cd "${DOCKER_DIR}"
    "${COMPOSE[@]}" down
}

case "${1:-}" in
    prepare | build | up | down) "$1" ;;
    *)
        echo "usage: $0 prepare|build|up|down" >&2
        exit 2
        ;;
esac
