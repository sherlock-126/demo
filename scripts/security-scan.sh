#!/bin/bash
# Security Scanning and Audit Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPORT_DIR="./security-reports"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
REPORT_FILE="$REPORT_DIR/security-audit_$TIMESTAMP.txt"

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1" | tee -a "$REPORT_FILE"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$REPORT_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$REPORT_FILE"
}

log_section() {
    echo -e "\n${BLUE}═══ $1 ═══${NC}" | tee -a "$REPORT_FILE"
}

# Initialize report
init_report() {
    mkdir -p "$REPORT_DIR"
    echo "Security Audit Report - $(date)" > "$REPORT_FILE"
    echo "======================================" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
}

# Check Docker security
check_docker_security() {
    log_section "Docker Security Check"

    # Check for running containers
    log_info "Checking running containers..."
    docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}" | tee -a "$REPORT_FILE"

    # Check for privileged containers
    log_info "Checking for privileged containers..."
    PRIV_CONTAINERS=$(docker ps -q | xargs -I {} docker inspect {} --format '{{.Name}}: Privileged={{.HostConfig.Privileged}}')
    echo "$PRIV_CONTAINERS" | tee -a "$REPORT_FILE"

    # Check for containers running as root
    log_info "Checking for containers running as root..."
    for container in $(docker ps -q); do
        USER=$(docker exec "$container" whoami 2>/dev/null || echo "N/A")
        NAME=$(docker inspect "$container" --format '{{.Name}}')
        echo "$NAME: User=$USER" | tee -a "$REPORT_FILE"
        if [ "$USER" = "root" ]; then
            log_warn "$NAME is running as root"
        fi
    done

    # Check Docker daemon configuration
    if [ -f /etc/docker/daemon.json ]; then
        log_info "Docker daemon configuration:"
        cat /etc/docker/daemon.json | tee -a "$REPORT_FILE"
    fi
}

# Scan container images for vulnerabilities
scan_container_images() {
    log_section "Container Image Vulnerability Scan"

    # Check if Trivy is available
    if command -v trivy &> /dev/null; then
        log_info "Scanning images with Trivy..."
        for image in $(docker images --format "{{.Repository}}:{{.Tag}}" | grep -v "<none>"); do
            log_info "Scanning $image..."
            trivy image --severity HIGH,CRITICAL "$image" >> "$REPORT_FILE" 2>&1 || true
        done
    else
        log_warn "Trivy not installed. Install with: wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add - && sudo apt-get update && sudo apt-get install trivy"
    fi
}

# Check Nginx configuration
check_nginx_config() {
    log_section "Nginx Configuration Security"

    # Test Nginx configuration
    log_info "Testing Nginx configuration..."
    docker exec demo-nginx nginx -t 2>&1 | tee -a "$REPORT_FILE" || log_warn "Nginx config test failed"

    # Check SSL configuration
    log_info "Checking SSL/TLS configuration..."
    if [ -f nginx/ssl/cert.pem ]; then
        openssl x509 -in nginx/ssl/cert.pem -text -noout | grep -E "(Signature Algorithm|Not After)" | tee -a "$REPORT_FILE"
    else
        log_warn "SSL certificate not found"
    fi

    # Check for security headers in Nginx config
    log_info "Checking security headers configuration..."
    grep -r "add_header" nginx/ | grep -E "(Strict-Transport-Security|X-Frame-Options|X-Content-Type-Options)" | head -5 | tee -a "$REPORT_FILE"
}

# Port scan
port_scan() {
    log_section "Open Ports Scan"

    log_info "Scanning for open ports..."
    if command -v netstat &> /dev/null; then
        netstat -tuln | grep LISTEN | tee -a "$REPORT_FILE"
    else
        ss -tuln | grep LISTEN | tee -a "$REPORT_FILE"
    fi

    # Check if only necessary ports are exposed
    EXPOSED_PORTS=$(docker ps --format "table {{.Names}}\t{{.Ports}}" | tail -n +2)
    log_info "Docker exposed ports:"
    echo "$EXPOSED_PORTS" | tee -a "$REPORT_FILE"
}

# File permission check
check_file_permissions() {
    log_section "File Permission Check"

    # Check for world-writable files
    log_info "Checking for world-writable files..."
    find . -type f -perm -002 2>/dev/null | head -20 | tee -a "$REPORT_FILE" || true

    # Check SSL certificate permissions
    if [ -d nginx/ssl ]; then
        log_info "SSL certificate permissions:"
        ls -la nginx/ssl/*.pem 2>/dev/null | tee -a "$REPORT_FILE" || true
    fi

    # Check .env file permissions
    if [ -f .env ]; then
        log_info ".env file permissions:"
        ls -la .env | tee -a "$REPORT_FILE"
        if [ "$(stat -c %a .env)" != "600" ]; then
            log_warn ".env file should have 600 permissions"
        fi
    fi
}

# Check for secrets in code
check_secrets() {
    log_section "Secrets Detection"

    log_info "Scanning for potential secrets..."

    # Check for API keys
    grep -r "api_key\|apikey\|api-key" . --exclude-dir=.git --exclude-dir=node_modules --exclude="*.log" 2>/dev/null | head -10 | tee -a "$REPORT_FILE" || true

    # Check for passwords
    grep -r "password\|passwd\|pwd" . --exclude-dir=.git --exclude-dir=node_modules --exclude="*.log" 2>/dev/null | grep -v "password:" | head -10 | tee -a "$REPORT_FILE" || true

    # Check for private keys
    find . -name "*.key" -o -name "*.pem" 2>/dev/null | grep -v nginx/ssl | head -10 | tee -a "$REPORT_FILE" || true
}

# Check ModSecurity status
check_modsecurity() {
    log_section "ModSecurity WAF Status"

    if docker exec demo-nginx test -f /etc/nginx/modsec/modsecurity.conf 2>/dev/null; then
        log_info "ModSecurity configuration found"
        docker exec demo-nginx grep "SecRuleEngine" /etc/nginx/modsec/modsecurity.conf 2>/dev/null | tee -a "$REPORT_FILE" || true

        # Check if audit log exists
        if docker exec demo-nginx test -f /var/log/nginx/modsec_audit.log 2>/dev/null; then
            log_info "ModSecurity audit log exists"
            docker exec demo-nginx tail -n 5 /var/log/nginx/modsec_audit.log 2>/dev/null | tee -a "$REPORT_FILE" || true
        fi
    else
        log_warn "ModSecurity not configured"
    fi
}

# Generate recommendations
generate_recommendations() {
    log_section "Security Recommendations"

    echo "Based on the scan, consider the following improvements:" | tee -a "$REPORT_FILE"
    echo "" | tee -a "$REPORT_FILE"

    # Check if ModSecurity is in blocking mode
    if grep -q "SecRuleEngine DetectionOnly" nginx/modsec/modsecurity.conf 2>/dev/null; then
        echo "• Enable ModSecurity blocking mode (currently in DetectionOnly)" | tee -a "$REPORT_FILE"
    fi

    # Check if HTTPS is configured
    if [ ! -f nginx/ssl/cert.pem ]; then
        echo "• Configure SSL/TLS certificates for HTTPS" | tee -a "$REPORT_FILE"
    fi

    # Check if firewall is configured
    if ! command -v ufw &> /dev/null && ! command -v iptables &> /dev/null; then
        echo "• Configure a firewall (ufw or iptables)" | tee -a "$REPORT_FILE"
    fi

    # Check for regular backups
    if [ ! -f scripts/backup.sh ]; then
        echo "• Implement regular backup procedures" | tee -a "$REPORT_FILE"
    fi

    echo "" | tee -a "$REPORT_FILE"
}

# Main execution
main() {
    echo "================================="
    echo "Security Scan and Audit"
    echo "================================="

    init_report

    check_docker_security
    scan_container_images
    check_nginx_config
    port_scan
    check_file_permissions
    check_secrets
    check_modsecurity
    generate_recommendations

    log_section "Scan Complete"
    log_info "Report saved to: $REPORT_FILE"

    # Summary
    echo ""
    echo "Summary:"
    WARNINGS=$(grep -c "\[WARN\]" "$REPORT_FILE" || echo "0")
    ERRORS=$(grep -c "\[ERROR\]" "$REPORT_FILE" || echo "0")
    echo "Warnings: $WARNINGS"
    echo "Errors: $ERRORS"

    if [ "$ERRORS" -gt 0 ]; then
        exit 1
    fi
}

# Show usage
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "Usage: $0"
    echo ""
    echo "Performs a comprehensive security scan of the Docker deployment"
    echo "and generates a report with findings and recommendations."
    echo ""
    echo "Reports are saved to: ./security-reports/"
    exit 0
fi

main "$@"