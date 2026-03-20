#!/bin/bash
# Docker Compose Deployment Script

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.yml"
COMPOSE_PROD_FILE="docker-compose.prod.yml"
ENV_FILE=".env"
ENV_TEMPLATE=".env.docker"

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi

    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi

    # Check environment file
    if [ ! -f "$ENV_FILE" ]; then
        if [ -f "$ENV_TEMPLATE" ]; then
            log_warn "Environment file not found. Copying template..."
            cp "$ENV_TEMPLATE" "$ENV_FILE"
            log_error "Please configure $ENV_FILE before running deployment"
            exit 1
        else
            log_error "Environment file and template not found"
            exit 1
        fi
    fi

    log_info "Prerequisites check passed"
}

# Create necessary directories
create_directories() {
    log_info "Creating necessary directories..."
    mkdir -p data output videos audio assets logs cache .auth
    mkdir -p nginx/ssl logs/nginx
    log_info "Directories created"
}

# Deploy services
deploy() {
    local MODE=${1:-dev}

    log_info "Deploying in $MODE mode..."

    if [ "$MODE" == "prod" ]; then
        log_info "Using production configuration..."
        docker-compose -f "$COMPOSE_FILE" -f "$COMPOSE_PROD_FILE" up -d --build
    else
        log_info "Using development configuration..."
        docker-compose -f "$COMPOSE_FILE" up -d --build streamlit
    fi

    # Wait for services to be healthy
    log_info "Waiting for services to be healthy..."
    sleep 5

    # Check service health
    if [ "$MODE" == "prod" ]; then
        docker-compose -f "$COMPOSE_FILE" -f "$COMPOSE_PROD_FILE" ps
    else
        docker-compose -f "$COMPOSE_FILE" ps
    fi
}

# Stop services
stop() {
    log_info "Stopping services..."
    docker-compose down
}

# View logs
logs() {
    local SERVICE=${1:-}
    if [ -z "$SERVICE" ]; then
        docker-compose logs -f
    else
        docker-compose logs -f "$SERVICE"
    fi
}

# Main script
main() {
    case "${1:-deploy}" in
        deploy)
            check_prerequisites
            create_directories
            deploy "${2:-dev}"
            log_info "Deployment complete!"
            ;;
        stop)
            stop
            log_info "Services stopped"
            ;;
        restart)
            stop
            deploy "${2:-dev}"
            ;;
        logs)
            logs "${2:-}"
            ;;
        *)
            echo "Usage: $0 {deploy|stop|restart|logs} [dev|prod] [service]"
            exit 1
            ;;
    esac
}

main "$@"