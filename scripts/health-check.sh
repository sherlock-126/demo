#!/bin/bash
# Service Health Check and Monitoring Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SERVICES=("nginx" "streamlit" "backend" "frontend")
ALERT_WEBHOOK="${ALERT_WEBHOOK:-}"  # Optional webhook for alerts
LOG_FILE="./logs/health-check.log"
MAX_RETRIES=3
RETRY_DELAY=30

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1" | tee -a "$LOG_FILE"
}

# Send alert (webhook or email)
send_alert() {
    local message="$1"
    local severity="${2:-warning}"

    if [ -n "$ALERT_WEBHOOK" ]; then
        curl -X POST "$ALERT_WEBHOOK" \
            -H "Content-Type: application/json" \
            -d "{\"severity\":\"$severity\",\"message\":\"$message\",\"timestamp\":\"$(date -Iseconds)\"}" \
            2>/dev/null || log_warn "Failed to send alert"
    fi

    # Log alert
    echo "[ALERT] [$severity] $message" >> "$LOG_FILE"
}

# Check if service is running
check_service_status() {
    local service="$1"
    local container_name="demo-$service"

    if [ "$service" = "nginx" ]; then
        container_name="demo-nginx"
    fi

    # Check if container exists and is running
    if docker ps --format '{{.Names}}' | grep -q "^$container_name$"; then
        return 0
    else
        return 1
    fi
}

# Check service health endpoint
check_service_health() {
    local service="$1"
    local health_url=""
    local expected_status="200"

    case "$service" in
        nginx)
            health_url="http://localhost/health"
            ;;
        streamlit)
            health_url="http://localhost:8501/_stcore/health"
            ;;
        backend)
            health_url="http://localhost:8000/health"
            ;;
        frontend)
            health_url="http://localhost:3001/api/health"
            ;;
        *)
            return 1
            ;;
    esac

    # Check health endpoint
    local status=$(curl -s -o /dev/null -w "%{http_code}" "$health_url" 2>/dev/null || echo "000")

    if [ "$status" = "$expected_status" ]; then
        return 0
    else
        log_warn "$service health check returned status: $status"
        return 1
    fi
}

# Restart unhealthy service
restart_service() {
    local service="$1"
    local retries=0

    log_warn "Attempting to restart $service..."

    while [ $retries -lt $MAX_RETRIES ]; do
        docker-compose restart "$service" 2>&1 | tee -a "$LOG_FILE"

        sleep $RETRY_DELAY

        if check_service_health "$service"; then
            log_success "$service restarted successfully"
            send_alert "$service was restarted successfully after health check failure" "info"
            return 0
        fi

        retries=$((retries + 1))
        log_warn "Restart attempt $retries/$MAX_RETRIES failed for $service"
    done

    log_error "Failed to restart $service after $MAX_RETRIES attempts"
    send_alert "$service is down and could not be restarted" "critical"
    return 1
}

# Check Docker daemon
check_docker_daemon() {
    if ! docker info &>/dev/null; then
        log_error "Docker daemon is not running"
        send_alert "Docker daemon is not running" "critical"
        exit 1
    fi
}

# Check disk space
check_disk_space() {
    local threshold=90
    local usage=$(df -h / | awk 'NR==2 {print int($5)}')

    if [ "$usage" -gt "$threshold" ]; then
        log_warn "Disk usage is at ${usage}% (threshold: ${threshold}%)"
        send_alert "High disk usage: ${usage}%" "warning"

        # Try to clean up
        log_info "Attempting to clean up Docker resources..."
        docker system prune -f --volumes 2>&1 | tee -a "$LOG_FILE"
    fi
}

# Check memory usage
check_memory() {
    local threshold=90
    local usage=$(free | grep Mem | awk '{print int($3/$2 * 100)}')

    if [ "$usage" -gt "$threshold" ]; then
        log_warn "Memory usage is at ${usage}% (threshold: ${threshold}%)"
        send_alert "High memory usage: ${usage}%" "warning"
    fi
}

# Check container resource usage
check_container_resources() {
    log_info "Container resource usage:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" | tee -a "$LOG_FILE"

    # Check for high CPU usage
    docker stats --no-stream --format "{{.Container}}:{{.CPUPerc}}" | while IFS=: read -r container cpu; do
        cpu_value=${cpu%\%}
        if (( $(echo "$cpu_value > 80" | bc -l) )); then
            log_warn "High CPU usage for $container: $cpu"
        fi
    done
}

# Check logs for errors
check_logs_for_errors() {
    local service="$1"
    local container_name="demo-$service"

    if [ "$service" = "nginx" ]; then
        container_name="demo-nginx"
    fi

    # Check last 100 lines for errors
    local errors=$(docker logs --tail 100 "$container_name" 2>&1 | grep -iE "error|critical|fatal" | wc -l)

    if [ "$errors" -gt 0 ]; then
        log_warn "$service has $errors error messages in recent logs"
        docker logs --tail 20 "$container_name" 2>&1 | grep -iE "error|critical|fatal" | head -5 >> "$LOG_FILE"
    fi
}

# Monitor service
monitor_service() {
    local service="$1"

    echo -n "Checking $service... "

    # Check if container is running
    if ! check_service_status "$service"; then
        log_error "$service container is not running"
        restart_service "$service"
        return
    fi

    # Check health endpoint
    if ! check_service_health "$service"; then
        log_warn "$service health check failed"
        restart_service "$service"
        return
    fi

    # Check logs for errors
    check_logs_for_errors "$service"

    log_success "$service is healthy"
}

# Main monitoring loop
monitor_all_services() {
    log_info "Starting health check at $(date)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # System checks
    check_docker_daemon
    check_disk_space
    check_memory

    echo ""

    # Service checks
    for service in "${SERVICES[@]}"; do
        # Skip if service is not in current profile
        if docker-compose ps "$service" 2>/dev/null | grep -q "No such service"; then
            continue
        fi

        monitor_service "$service"
    done

    echo ""

    # Resource usage
    check_container_resources

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log_info "Health check completed at $(date)"
}

# Continuous monitoring mode
continuous_monitoring() {
    local interval="${1:-60}"  # Default 60 seconds

    log_info "Starting continuous monitoring (interval: ${interval}s)"
    log_info "Press Ctrl+C to stop"

    while true; do
        clear
        monitor_all_services
        sleep "$interval"
    done
}

# Main execution
main() {
    # Create log directory
    mkdir -p "$(dirname "$LOG_FILE")"

    # Parse arguments
    case "${1:-once}" in
        once)
            monitor_all_services
            ;;
        continuous)
            continuous_monitoring "${2:-60}"
            ;;
        --help|-h)
            echo "Usage: $0 [mode] [interval]"
            echo ""
            echo "Modes:"
            echo "  once       - Run health check once (default)"
            echo "  continuous - Run continuously with interval"
            echo ""
            echo "Arguments:"
            echo "  interval   - Seconds between checks in continuous mode (default: 60)"
            echo ""
            echo "Examples:"
            echo "  $0                    # Run once"
            echo "  $0 continuous         # Run every 60 seconds"
            echo "  $0 continuous 30      # Run every 30 seconds"
            echo ""
            echo "Environment Variables:"
            echo "  ALERT_WEBHOOK - Webhook URL for sending alerts"
            exit 0
            ;;
        *)
            log_error "Unknown mode: $1"
            exit 1
            ;;
    esac
}

main "$@"