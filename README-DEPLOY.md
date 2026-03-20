# Docker Deployment Guide

This guide provides comprehensive instructions for deploying the Demo Content Generator application using Docker, with specific considerations for Windows (Hyper-V/WSL2) environments.

## Prerequisites

### System Requirements
- Docker Desktop 20.10+ (Windows/Mac) or Docker Engine (Linux)
- Docker Compose v2.0+
- Minimum 4GB RAM available for Docker
- 10GB free disk space
- Internet connection for downloading dependencies

### Windows-Specific Setup
1. **Enable WSL2** (Windows Subsystem for Linux 2):
   ```powershell
   wsl --install
   ```

2. **Install Docker Desktop**:
   - Download from [docker.com](https://www.docker.com/products/docker-desktop/)
   - During installation, ensure "Use WSL 2 based engine" is checked
   - After installation, go to Settings → Resources → WSL Integration
   - Enable integration with your WSL2 distro

3. **Configure Resources** (Docker Desktop → Settings → Resources):
   - CPUs: 2 minimum (4 recommended)
   - Memory: 4GB minimum (8GB recommended)
   - Swap: 1GB
   - Disk: 20GB minimum

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/sherlock-126/demo.git
cd demo
```

### 2. Configure Environment Variables
```bash
# Copy the example environment file
cp .env.docker.example .env.docker

# Edit the configuration
nano .env.docker  # or use your preferred editor
```

Required environment variables:
```bash
# OpenAI API Configuration (for default provider)
OPENAI_API_KEY=sk-your-api-key-here

# Optional: LLM Provider Selection
LLM_PROVIDER=openai_api  # Options: openai_api, cli_chatgpt, revchatgpt

# Optional: Logging
LOG_LEVEL=INFO  # Options: DEBUG, INFO, WARNING, ERROR
```

### 3. Build the Docker Image
```bash
# Build the image
docker-compose -f docker/docker-compose.yml build

# Or build with specific platform (for M1 Macs)
docker-compose -f docker/docker-compose.yml build --build-arg BUILDKIT_PROGRESS=plain
```

### 4. Start the Container
```bash
# Start in detached mode
docker-compose -f docker/docker-compose.yml up -d

# View logs
docker-compose -f docker/docker-compose.yml logs -f app

# Verify the container is running
docker ps
```

## Usage

### Entering the Container
```bash
# Interactive bash shell
docker exec -it demo-app bash

# Or using docker-compose
docker-compose -f docker/docker-compose.yml exec app bash
```

### Running the Application

Once inside the container:

#### Content Generation (AI Script Creation)
```bash
# Generate a single script
python -m content_generator.cli generate "Cách dạy con không la mắng"

# Generate with custom parameters
python -m content_generator.cli generate "topic" --slides 5 --language vi --output script.json

# Batch processing
python -m content_generator.cli batch topics.txt --output-dir scripts/
```

#### Layout Generation (Image Creation)
```bash
# Generate images from script
python -m layout_generator generate script.json --output images/

# Batch processing
python -m layout_generator batch scripts/ --output-dir output/
```

#### Video Assembly (Create TikTok Videos)
```bash
# Create video from images
python -m video_assembly generate output/ --output video.mp4

# Add background music
python -m video_assembly generate output/ --music audio/background.mp3 --output video.mp4
```

### Complete Pipeline Example
```bash
# Inside the container
cd /app

# Step 1: Generate script
python -m content_generator.cli generate "Teaching kids patience" --output data/script.json

# Step 2: Create images
python -m layout_generator generate data/script.json --output output/

# Step 3: Assemble video
python -m video_assembly generate output/ --music audio/sample.mp3 --output videos/final.mp4
```

## Manual Authentication (For CLI-based LLM Providers)

If you're using alternative LLM providers that require manual authentication:

### ChatGPT CLI Authentication
```bash
# Enter the container
docker exec -it demo-app bash

# Set the provider
export LLM_PROVIDER=cli_chatgpt

# Run authentication
chatgpt-cli auth login

# Follow the prompts to authenticate
# The token will be saved to /app/.auth/cli_chatgpt.token
```

### RevChatGPT Authentication
```bash
# Enter the container
docker exec -it demo-app bash

# Set the provider
export LLM_PROVIDER=revchatgpt

# Run authentication
python -m revchatgpt.auth

# Follow the browser-based authentication
# Tokens will be saved to /app/.auth/revchatgpt.token
```

## Volume Management

The application uses several volumes for data persistence:

| Volume Path | Purpose | Host Path |
|------------|---------|-----------|
| `/app/data` | Generated scripts and data | `./data` |
| `/app/output` | Generated images | `./output` |
| `/app/videos` | Generated videos | `./videos` |
| `/app/audio` | Background music files | `./audio` |
| `/app/assets` | Fonts, icons, logos | `./assets` |
| `/app/.auth` | Authentication tokens | Docker volume |
| `/app/logs` | Application logs | `./logs` |

### Adding Assets

#### Fonts
Place custom fonts in `./assets/fonts/`:
```bash
# Download Roboto fonts
cd assets/fonts
wget https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Regular.ttf
wget https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Bold.ttf
```

#### Music Files
Add background music to `./audio/`:
```bash
# Copy music files
cp ~/Music/*.mp3 ./audio/
```

## Troubleshooting

### Common Issues

#### 1. Container Won't Start
```bash
# Check logs
docker-compose -f docker/docker-compose.yml logs app

# Rebuild without cache
docker-compose -f docker/docker-compose.yml build --no-cache
```

#### 2. FFmpeg Not Working
```bash
# Verify FFmpeg inside container
docker exec demo-app ffmpeg -version

# Reinstall if needed
docker exec -u root demo-app apt-get update && apt-get install -y ffmpeg
```

#### 3. Permission Denied Errors
```bash
# Fix permissions on host
chmod -R 777 ./data ./output ./videos

# Or inside container (as root)
docker exec -u root demo-app chown -R appuser:appuser /app
```

#### 4. Out of Memory Errors
Increase Docker memory allocation:
- Docker Desktop → Settings → Resources → Memory → Increase to 6-8GB

#### 5. Slow Performance on Windows
- Ensure WSL2 is being used (not Hyper-V)
- Store project files in WSL filesystem, not Windows filesystem
- Access via: `\\wsl$\Ubuntu\home\username\projects\demo`

### Health Checks
```bash
# Check container health
docker inspect demo-app --format='{{.State.Health.Status}}'

# Run health check manually
docker exec demo-app /app/docker/healthcheck.sh
```

## Stopping and Cleanup

### Stop the Container
```bash
# Stop services
docker-compose -f docker/docker-compose.yml down

# Stop and remove volumes (WARNING: deletes data)
docker-compose -f docker/docker-compose.yml down -v
```

### Remove Images
```bash
# Remove the application image
docker rmi demo-content-generator:latest

# Clean up all unused Docker resources
docker system prune -a
```

## Production Considerations

### Security
1. Never commit `.env.docker` with real API keys
2. Use Docker secrets for sensitive data in production
3. Run container as non-root user (already configured)
4. Regularly update base images for security patches

### Performance Optimization
1. Use BuildKit for faster builds:
   ```bash
   DOCKER_BUILDKIT=1 docker build -t demo-content-generator .
   ```

2. Enable caching for pip packages:
   ```dockerfile
   RUN --mount=type=cache,target=/root/.cache/pip \
       pip install -r requirements.txt
   ```

3. Use multi-stage builds (already implemented)

### Monitoring
```bash
# Monitor resource usage
docker stats demo-app

# View detailed information
docker inspect demo-app
```

## Support

For issues or questions:
1. Check the logs: `docker-compose logs app`
2. Verify environment variables are set correctly
3. Ensure all prerequisites are met
4. Create an issue on GitHub with error details

## License

See LICENSE file in the repository root.