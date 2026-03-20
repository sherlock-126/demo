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
COMPOSE_MONITORING_FILE="docker-compose.monitoring.yml"
ENV_FILE=".env"
ENV_TEMPLATE=".env.docker"
ENV_PROD_TEMPLATE=".env.production"

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

    # Check for OpenSSL (for SSL setup)
    if ! command -v openssl &> /dev/null; then
        log_warn "OpenSSL not found - SSL setup may not work"
    fi

    # Check environment file
    if [ ! -f "$ENV_FILE" ]; then
        local TEMPLATE="$ENV_TEMPLATE"
        if [ "$1" == "prod" ]; then
            TEMPLATE="$ENV_PROD_TEMPLATE"
        fi

        if [ -f "$TEMPLATE" ]; then
            log_warn "Environment file not found. Copying template..."
            cp "$TEMPLATE" "$ENV_FILE"
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
    mkdir -p nginx/ssl nginx/ssl/.well-known/acme-challenge
    mkdir -p logs/nginx cache/nginx
    mkdir -p monitoring/prometheus monitoring/grafana/dashboards monitoring/loki
    mkdir -p security-reports

    # Set permissions for nginx directories
    chmod 755 nginx/ssl
    chmod 755 logs/nginx

    log_info "Directories created"
}

# Setup SSL certificates
setup_ssl() {
    local DOMAIN="${1:-demo.yourdomain.com}"
    local EMAIL="${2:-admin@yourdomain.com}"

    log_info "Setting up SSL for $DOMAIN..."

    if [ -f "scripts/ssl-setup.sh" ]; then
        bash scripts/ssl-setup.sh "$DOMAIN" "$EMAIL"
    else
        log_warn "SSL setup script not found, skipping SSL configuration"
    fi
}

# Deploy services
deploy() {
    local MODE=${1:-dev}
    local WITH_MONITORING=${2:-false}

    log_info "Deploying in $MODE mode..."

    if [ "$MODE" == "prod" ]; then
        log_info "Using production configuration..."

        # Build custom Nginx image
        log_info "Building Nginx image with security enhancements..."
        docker build -f nginx/Dockerfile.nginx -t demo-nginx:latest .

        if [ "$WITH_MONITORING" == "true" ]; then
            log_info "Deploying with monitoring stack..."
            docker-compose -f "$COMPOSE_FILE" -f "$COMPOSE_PROD_FILE" -f "$COMPOSE_MONITORING_FILE" up -d --build
        else
            docker-compose -f "$COMPOSE_FILE" -f "$COMPOSE_PROD_FILE" up -d --build
        fi
    else
        log_info "Using development configuration..."
        docker-compose -f "$COMPOSE_FILE" up -d --build streamlit
    fi

    # Wait for services to be healthy
    log_info "Waiting for services to be healthy..."
    sleep 10

    # Check service health
    if [ "$MODE" == "prod" ]; then
        docker-compose -f "$COMPOSE_FILE" -f "$COMPOSE_PROD_FILE" ps

        # Run health check
        if [ -f "scripts/health-check.sh" ]; then
            log_info "Running health check..."
            bash scripts/health-check.sh once
        fi
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

# Security scan
security_scan() {
    log_info "Running security scan..."

    if [ -f "scripts/security-scan.sh" ]; then
        bash scripts/security-scan.sh
    else
        log_warn "Security scan script not found"
    fi
}

# Main script
main() {
    case "${1:-deploy}" in
        deploy)
            local MODE="${2:-dev}"
            check_prerequisites "$MODE"
            create_directories

            if [ "$MODE" == "prod" ]; then
                # Production deployment
                log_info "Production deployment initiated"

                # Setup SSL if not exists
                if [ ! -f "nginx/ssl/cert.pem" ]; then
                    read -p "Enter your domain (or press Enter for demo.yourdomain.com): " DOMAIN
                    read -p "Enter your email for SSL (or press Enter for admin@yourdomain.com): " EMAIL
                    setup_ssl "${DOMAIN:-demo.yourdomain.com}" "${EMAIL:-admin@yourdomain.com}"
                fi

                # Deploy with optional monitoring
                read -p "Deploy with monitoring stack? (y/n): " WITH_MON
                if [ "$WITH_MON" == "y" ]; then
                    deploy "$MODE" true
                else
                    deploy "$MODE" false
                fi

                log_info "Production deployment complete!"
                log_info "Access the application at https://your-domain.com"
                log_info "Run 'docker-compose logs -f nginx' to monitor Nginx logs"
            else
                # Development deployment
                deploy "$MODE"
                log_info "Development deployment complete!"
                log_info "Access Streamlit at http://localhost:8501"
            fi
            ;;
        stop)
            stop
            log_info "Services stopped"
            ;;
        restart)
            stop
            deploy "${2:-dev}" "${3:-false}"
            ;;
        logs)
            logs "${2:-}"
            ;;
        ssl-setup)
            setup_ssl "${2:-demo.yourdomain.com}" "${3:-admin@yourdomain.com}"
            ;;
        security-scan)
            security_scan
            ;;
        health-check)
            if [ -f "scripts/health-check.sh" ]; then
                bash scripts/health-check.sh "${2:-once}"
            else
                log_error "Health check script not found"
            fi
            ;;
        *)
            echo "Usage: $0 {deploy|stop|restart|logs|ssl-setup|security-scan|health-check} [options]"
            echo ""
            echo "Commands:"
            echo "  deploy [dev|prod]        - Deploy services"
            echo "  stop                     - Stop all services"
            echo "  restart [dev|prod]       - Restart services"
            echo "  logs [service]           - View logs"
            echo "  ssl-setup [domain] [email] - Setup SSL certificates"
            echo "  security-scan            - Run security audit"
            echo "  health-check [once|continuous] - Check service health"
            exit 1
            ;;
    esac
}

main "$@"