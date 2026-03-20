#!/bin/bash
# SSL Certificate Setup and Management Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOMAIN="${1:-demo.yourdomain.com}"
EMAIL="${2:-admin@yourdomain.com}"
NGINX_SSL_DIR="./nginx/ssl"
STAGING="${3:-false}"

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

    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi

    if ! command -v openssl &> /dev/null; then
        log_error "OpenSSL is not installed"
        exit 1
    fi

    log_info "Prerequisites check passed"
}

# Create SSL directory
create_ssl_directory() {
    log_info "Creating SSL directory..."
    mkdir -p "$NGINX_SSL_DIR"
    mkdir -p "$NGINX_SSL_DIR/.well-known/acme-challenge"
    chmod 755 "$NGINX_SSL_DIR"
}

# Generate self-signed certificate (for development/fallback)
generate_self_signed() {
    log_info "Generating self-signed certificate for $DOMAIN..."

    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout "$NGINX_SSL_DIR/key.pem" \
        -out "$NGINX_SSL_DIR/cert.pem" \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=$DOMAIN"

    log_info "Self-signed certificate generated"
}

# Generate Diffie-Hellman parameters
generate_dhparam() {
    if [ ! -f "$NGINX_SSL_DIR/dhparam.pem" ]; then
        log_info "Generating Diffie-Hellman parameters (this may take a while)..."
        openssl dhparam -out "$NGINX_SSL_DIR/dhparam.pem" 2048
        log_info "DH parameters generated"
    else
        log_info "DH parameters already exist"
    fi
}

# Setup Let's Encrypt with Certbot
setup_letsencrypt() {
    log_info "Setting up Let's Encrypt certificate for $DOMAIN..."

    # Determine staging flag
    STAGING_FLAG=""
    if [ "$STAGING" = "true" ]; then
        STAGING_FLAG="--staging"
        log_warn "Using Let's Encrypt staging server (for testing)"
    fi

    # Run Certbot in Docker
    docker run -it --rm \
        -v "$(pwd)/nginx/ssl:/etc/letsencrypt" \
        -v "$(pwd)/nginx/ssl/.well-known:/var/www/.well-known" \
        -p 80:80 \
        certbot/certbot certonly \
        --standalone \
        --non-interactive \
        --agree-tos \
        --email "$EMAIL" \
        --domains "$DOMAIN" \
        $STAGING_FLAG

    # Copy certificates to expected locations
    if [ -d "$NGINX_SSL_DIR/live/$DOMAIN" ]; then
        cp "$NGINX_SSL_DIR/live/$DOMAIN/fullchain.pem" "$NGINX_SSL_DIR/cert.pem"
        cp "$NGINX_SSL_DIR/live/$DOMAIN/privkey.pem" "$NGINX_SSL_DIR/key.pem"
        log_info "Let's Encrypt certificate obtained and copied"
    else
        log_error "Let's Encrypt certificate generation failed"
        return 1
    fi
}

# Setup certificate renewal
setup_renewal() {
    log_info "Setting up automatic certificate renewal..."

    # Create renewal script
    cat > "$NGINX_SSL_DIR/renew.sh" << 'EOF'
#!/bin/bash
# Certificate renewal script

DOMAIN="${1:-demo.yourdomain.com}"
SSL_DIR="/etc/nginx/ssl"

# Renew certificate
certbot renew --quiet --no-self-upgrade

# Copy renewed certificates
if [ -d "$SSL_DIR/live/$DOMAIN" ]; then
    cp "$SSL_DIR/live/$DOMAIN/fullchain.pem" "$SSL_DIR/cert.pem"
    cp "$SSL_DIR/live/$DOMAIN/privkey.pem" "$SSL_DIR/key.pem"

    # Reload Nginx
    docker exec demo-nginx nginx -s reload
fi
EOF

    chmod +x "$NGINX_SSL_DIR/renew.sh"

    # Add cron job for renewal (if not exists)
    CRON_JOB="0 0 * * * $(pwd)/$NGINX_SSL_DIR/renew.sh $DOMAIN"
    (crontab -l 2>/dev/null | grep -v "renew.sh" ; echo "$CRON_JOB") | crontab -

    log_info "Automatic renewal configured"
}

# Verify certificate
verify_certificate() {
    log_info "Verifying certificate..."

    if [ -f "$NGINX_SSL_DIR/cert.pem" ]; then
        # Check certificate details
        openssl x509 -in "$NGINX_SSL_DIR/cert.pem" -text -noout | grep -E "(Subject:|Issuer:|Not After)"

        # Check expiry
        EXPIRY=$(openssl x509 -in "$NGINX_SSL_DIR/cert.pem" -noout -enddate | cut -d= -f2)
        log_info "Certificate expires: $EXPIRY"

        # Check if certificate matches private key
        CERT_MD5=$(openssl x509 -noout -modulus -in "$NGINX_SSL_DIR/cert.pem" | openssl md5)
        KEY_MD5=$(openssl rsa -noout -modulus -in "$NGINX_SSL_DIR/key.pem" | openssl md5)

        if [ "$CERT_MD5" = "$KEY_MD5" ]; then
            log_info "Certificate and private key match ✓"
        else
            log_error "Certificate and private key do not match!"
            return 1
        fi
    else
        log_error "Certificate not found"
        return 1
    fi
}

# Main execution
main() {
    echo "==================================="
    echo "SSL Certificate Setup for $DOMAIN"
    echo "==================================="

    check_prerequisites
    create_ssl_directory
    generate_dhparam

    # Try Let's Encrypt first, fall back to self-signed
    if [ "$DOMAIN" != "demo.yourdomain.com" ] && [ "$DOMAIN" != "localhost" ]; then
        if setup_letsencrypt; then
            setup_renewal
        else
            log_warn "Let's Encrypt failed, falling back to self-signed certificate"
            generate_self_signed
        fi
    else
        log_warn "Using self-signed certificate for development"
        generate_self_signed
    fi

    verify_certificate

    echo ""
    log_info "SSL setup complete!"
    log_info "Certificates location: $NGINX_SSL_DIR"
    echo ""
    echo "Next steps:"
    echo "1. Update nginx/sites-available/demo-ssl.conf with your domain"
    echo "2. Restart Nginx: docker-compose restart nginx"
    echo "3. Test HTTPS: https://$DOMAIN"
}

# Show usage
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "Usage: $0 [domain] [email] [staging]"
    echo ""
    echo "Arguments:"
    echo "  domain   - Your domain name (default: demo.yourdomain.com)"
    echo "  email    - Email for Let's Encrypt (default: admin@yourdomain.com)"
    echo "  staging  - Use Let's Encrypt staging server: true/false (default: false)"
    echo ""
    echo "Examples:"
    echo "  $0 mydomain.com admin@mydomain.com false"
    echo "  $0 test.mydomain.com admin@mydomain.com true"
    exit 0
fi

main "$@"