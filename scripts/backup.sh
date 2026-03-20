#!/bin/bash
# Volume Backup Script for Docker Containers

set -e  # Exit on error

# Configuration
BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=7

# Directories to backup
BACKUP_DIRS=(
    "data"
    "output"
    "videos"
    ".auth"
    "logs"
)

# Functions
log_info() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] INFO: $1"
}

log_error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1" >&2
}

# Create backup
create_backup() {
    log_info "Starting backup process..."

    # Create backup directory
    mkdir -p "$BACKUP_DIR"

    # Create backup filename
    BACKUP_FILE="${BACKUP_DIR}/demo_backup_${TIMESTAMP}.tar.gz"

    # Stop containers to ensure consistency (optional)
    read -p "Stop containers during backup? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Stopping containers..."
        docker-compose stop
        CONTAINERS_STOPPED=true
    fi

    # Create backup archive
    log_info "Creating backup archive: $BACKUP_FILE"
    tar -czf "$BACKUP_FILE" "${BACKUP_DIRS[@]}" 2>/dev/null || true

    # Restart containers if they were stopped
    if [ "${CONTAINERS_STOPPED:-false}" == "true" ]; then
        log_info "Restarting containers..."
        docker-compose start
    fi

    # Get backup size
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    log_info "Backup created: $BACKUP_FILE (Size: $BACKUP_SIZE)"
}

# Clean old backups
clean_old_backups() {
    log_info "Cleaning old backups (older than $RETENTION_DAYS days)..."

    if [ -d "$BACKUP_DIR" ]; then
        find "$BACKUP_DIR" -name "demo_backup_*.tar.gz" -type f -mtime +$RETENTION_DAYS -delete
        log_info "Old backups cleaned"
    fi
}

# Restore backup
restore_backup() {
    local BACKUP_FILE=$1

    if [ -z "$BACKUP_FILE" ]; then
        # List available backups
        log_info "Available backups:"
        ls -lh "$BACKUP_DIR"/demo_backup_*.tar.gz 2>/dev/null || {
            log_error "No backups found"
            exit 1
        }
        echo
        read -p "Enter backup filename to restore: " BACKUP_FILE
    fi

    if [ ! -f "$BACKUP_FILE" ]; then
        log_error "Backup file not found: $BACKUP_FILE"
        exit 1
    fi

    read -p "This will overwrite existing data. Continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Restore cancelled"
        exit 0
    fi

    log_info "Stopping containers..."
    docker-compose stop

    log_info "Restoring from: $BACKUP_FILE"
    tar -xzf "$BACKUP_FILE"

    log_info "Restarting containers..."
    docker-compose start

    log_info "Restore complete"
}

# Main script
main() {
    case "${1:-backup}" in
        backup)
            create_backup
            clean_old_backups
            ;;
        restore)
            restore_backup "$2"
            ;;
        list)
            ls -lh "$BACKUP_DIR"/demo_backup_*.tar.gz 2>/dev/null || echo "No backups found"
            ;;
        *)
            echo "Usage: $0 {backup|restore|list} [backup_file]"
            exit 1
            ;;
    esac
}

main "$@"