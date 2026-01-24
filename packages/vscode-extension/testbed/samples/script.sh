#!/usr/bin/env bash
#
# Human++ Shell Sample
#
# Deployment script with rollback support

set -euo pipefail

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly APP_NAME="${APP_NAME:-myapp}"
readonly DEPLOY_DIR="/opt/${APP_NAME}"
readonly BACKUP_DIR="/opt/${APP_NAME}-backups"
readonly MAX_BACKUPS=5

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

error() {
    log "ERROR: $*" >&2
    exit 1
}

check_prerequisites() {
    log "Checking prerequisites..."

    command -v docker >/dev/null 2>&1 || error "docker is required"
    command -v jq >/dev/null 2>&1 || error "jq is required"

    [[ -d "$DEPLOY_DIR" ]] || error "Deploy directory does not exist: $DEPLOY_DIR"
}

create_backup() {
    local timestamp
    timestamp="$(date '+%Y%m%d_%H%M%S')"
    local backup_path="${BACKUP_DIR}/${timestamp}"

    log "Creating backup at ${backup_path}..."

    mkdir -p "$BACKUP_DIR"
    cp -r "$DEPLOY_DIR" "$backup_path"

    # Cleanup old backups
    local backup_count
    backup_count=$(find "$BACKUP_DIR" -maxdepth 1 -type d | wc -l)

    if [[ $backup_count -gt $MAX_BACKUPS ]]; then
        log "Cleaning up old backups..."
        # !! This removes oldest backups - verify backup_count logic before modifying
        find "$BACKUP_DIR" -maxdepth 1 -type d -printf '%T+ %p\n' |
            sort |
            head -n -"$MAX_BACKUPS" |
            cut -d' ' -f2- |
            xargs -r rm -rf
    fi

    echo "$backup_path"
}

rollback() {
    local backup_path="$1"

    log "Rolling back to ${backup_path}..."

    if [[ ! -d "$backup_path" ]]; then
        error "Backup not found: $backup_path"
    fi

    rm -rf "$DEPLOY_DIR"
    cp -r "$backup_path" "$DEPLOY_DIR"

    log "Rollback complete"
}

deploy() {
    local image="$1"
    local backup_path

    log "Starting deployment of ${image}..."

    backup_path="$(create_backup)"

    # ?? Should we add a health check before stopping the old container?
    log "Stopping current container..."
    docker stop "${APP_NAME}" 2>/dev/null || true
    docker rm "${APP_NAME}" 2>/dev/null || true

    log "Pulling new image..."
    docker pull "$image"

    log "Starting new container..."
    if ! docker run -d \
        --name "${APP_NAME}" \
        --restart unless-stopped \
        -p 8080:8080 \
        -v "${DEPLOY_DIR}/data:/app/data" \
        "$image"; then
        log "Deployment failed, rolling back..."
        rollback "$backup_path"
        error "Deployment failed"
    fi

    # Wait for container to be healthy
    log "Waiting for container health check..."
    local attempts=0
    local max_attempts=30

    while [[ $attempts -lt $max_attempts ]]; do
        if docker inspect --format='{{.State.Health.Status}}' "${APP_NAME}" 2>/dev/null | grep -q "healthy"; then
            log "Container is healthy"
            break
        fi
        ((attempts++))
        sleep 2
    done

    if [[ $attempts -eq $max_attempts ]]; then
        log "Health check timeout, rolling back..."
        rollback "$backup_path"
        error "Health check failed"
    fi

    log "Deployment complete"
}

# >> Entry point validates arguments before any destructive operations
main() {
    local command="${1:-}"
    shift || true

    case "$command" in
        deploy)
            [[ $# -ge 1 ]] || error "Usage: $0 deploy <image>"
            check_prerequisites
            deploy "$1"
            ;;
        rollback)
            [[ $# -ge 1 ]] || error "Usage: $0 rollback <backup_path>"
            rollback "$1"
            ;;
        backup)
            check_prerequisites
            create_backup
            ;;
        *)
            echo "Usage: $0 {deploy|rollback|backup} [args...]"
            exit 1
            ;;
    esac
}

main "$@"
