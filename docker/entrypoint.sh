#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check FFmpeg installation
log_info "Checking FFmpeg installation..."
if ffmpeg -version > /dev/null 2>&1; then
    log_info "FFmpeg is installed and working"
    ffmpeg -version | head -1
else
    log_error "FFmpeg is not properly installed!"
    exit 1
fi

# Create necessary directories
log_info "Creating necessary directories..."
mkdir -p /app/data /app/output /app/videos /app/audio /app/assets /app/.auth /app/logs

# Check OpenAI API key or alternative provider
if [ -z "$OPENAI_API_KEY" ] && [ "$LLM_PROVIDER" = "openai_api" ]; then
    log_warn "OPENAI_API_KEY is not set. Please set it in .env.docker file"
    log_warn "Or configure an alternative LLM provider"
fi

# Check for authentication tokens if using CLI providers
if [ "$LLM_PROVIDER" = "cli_chatgpt" ] || [ "$LLM_PROVIDER" = "revchatgpt" ]; then
    log_info "Using CLI-based LLM provider: $LLM_PROVIDER"
    if [ ! -f "/app/.auth/${LLM_PROVIDER}.token" ]; then
        log_warn "No authentication token found for $LLM_PROVIDER"
        log_warn "Please run authentication inside the container:"
        log_warn "  docker exec -it demo-app bash"
        log_warn "  Then follow the authentication steps for your provider"
    fi
fi

# Validate Python modules
log_info "Validating Python modules..."
if python -c "import content_generator, layout_generator, video_assembly" 2>/dev/null; then
    log_info "All Python modules are installed correctly"
else
    log_error "Python modules are not properly installed!"
    exit 1
fi

# Check for fonts
log_info "Checking font installation..."
if fc-list | grep -q "Roboto"; then
    log_info "Roboto font family is installed"
else
    log_warn "Roboto font not found, using fallback fonts"
fi

# Execute the main command
log_info "Container is ready!"
log_info "You can now:"
log_info "  - Enter the container: docker exec -it demo-app bash"
log_info "  - Run content generator: python -m content_generator.cli generate 'topic'"
log_info "  - Run layout generator: python -m layout_generator generate script.json"
log_info "  - Run video assembly: python -m video_assembly generate output/"

# Execute passed command or default
exec "$@"