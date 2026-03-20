# Docker Deployment Guide

This guide covers deploying the TikTok Content Generation System using Docker Compose with Nginx reverse proxy.

## Prerequisites

### System Requirements

- **Docker Engine**: 20.10+ with BuildKit support
- **Docker Compose**: 2.0+ (compose plugin)
- **RAM**: 8GB minimum (2GB per container × 3 services)
- **Disk**: 20GB free space
- **OS**: Windows 10/11 (with WSL2), Linux, or macOS

### Windows-Specific Setup (Hyper-V/WSL2)

1. **Enable WSL2**:
   ```bash
   wsl --install
   wsl --set-default-version 2
   ```

2. **Configure WSL2 memory** (create `%USERPROFILE%\.wslconfig`):
   ```ini
   [wsl2]
   memory=8GB
   processors=4
   swap=0
   ```

3. **Install Docker Desktop** with WSL2 backend enabled

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/sherlock-126/demo.git
cd demo
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.docker .env

# Edit configuration
nano .env
```

**Required settings**:
- `OPENAI_API_KEY`: Your OpenAI API key
- `JWT_SECRET`: Random string for production

### 3. Deploy Services

#### Development Mode (Streamlit only)

```bash
# Using the deployment script
./scripts/deploy.sh deploy dev

# Or manually with docker-compose
docker-compose up -d streamlit
```

#### Production Mode (All services with Nginx)

```bash
# Using the deployment script
./scripts/deploy.sh deploy prod

# Or manually with docker-compose
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### 4. Access Services

- **Streamlit Dashboard**: http://localhost:8501
- **FastAPI Backend**: http://localhost:8000/docs
- **Next.js Frontend**: http://localhost:3001

## Resource Management

### Container Limits

Each container is configured with:
- **CPU**: 0.5 cores (50% of 1 CPU)
- **Memory**: 2GB RAM
- **Restart Policy**: unless-stopped

### Monitoring Resources

```bash
# Real-time resource usage
docker stats

# Check container health
docker-compose ps

# View logs
docker-compose logs -f streamlit
```

## Nginx Configuration

### Development Setup

The default configuration serves HTTP on port 80:

```bash
# Start Nginx proxy (production only)
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d nginx
```

### Production SSL/TLS Setup

1. **Generate SSL certificates**:
   ```bash
   # Using Let's Encrypt
   certbot certonly --standalone -d demo.yourdomain.com

   # Copy certificates
   cp /etc/letsencrypt/live/demo.yourdomain.com/fullchain.pem nginx/ssl/cert.pem
   cp /etc/letsencrypt/live/demo.yourdomain.com/privkey.pem nginx/ssl/key.pem
   ```

2. **Update Nginx config** (`nginx/sites-available/demo.conf`):
   - Uncomment HTTPS server block
   - Update `server_name` with your domain

3. **Restart Nginx**:
   ```bash
   docker-compose restart nginx
   ```

## LLM Provider Configuration

### Option 1: OpenAI API (Default)

```bash
# In .env file
LLM_PROVIDER=openai_api
OPENAI_API_KEY=sk-your-key-here
```

### Option 2: CLI-based ChatGPT

```bash
# Enter container
docker exec -it demo-streamlit bash

# Authenticate
chatgpt-cli auth login

# Exit container
exit
```

### Option 3: RevChatGPT

```bash
# Set in .env file
LLM_PROVIDER=revchatgpt
REVCHATGPT_ACCESS_TOKEN=your-token
```

## Backup and Restore

### Create Backup

```bash
# Automated backup
./scripts/backup.sh backup

# Manual backup
tar -czf backup_$(date +%Y%m%d).tar.gz data output videos .auth logs
```

### Restore Backup

```bash
# List available backups
./scripts/backup.sh list

# Restore specific backup
./scripts/backup.sh restore backups/demo_backup_20240320_120000.tar.gz
```

## Troubleshooting

### Common Issues

#### 1. Container Won't Start

```bash
# Check logs
docker-compose logs streamlit

# Verify environment
docker-compose config

# Rebuild image
docker-compose build --no-cache streamlit
```

#### 2. High CPU Usage (Windows)

```bash
# Check WSL2 memory usage
wsl --status

# Restart WSL2
wsl --shutdown
wsl
```

#### 3. Permission Errors

```bash
# Fix volume permissions
docker exec -it demo-streamlit bash -c "chown -R 1000:1000 /app/data"
```

#### 4. Port Conflicts

```bash
# Check port usage (Linux/Mac)
lsof -i :8501

# Windows PowerShell
netstat -an | findstr :8501

# Change port in docker-compose.yml
ports:
  - "8502:8501"  # Use different host port
```

### Health Checks

Services include health checks that verify:
- Streamlit: `/_stcore/health` endpoint
- FastAPI: `/health` endpoint
- Next.js: `/api/health` endpoint

Check health status:
```bash
docker-compose ps
docker inspect demo-streamlit --format='{{.State.Health.Status}}'
```

## Security Considerations

### Production Checklist

- [ ] Change `JWT_SECRET` to random value
- [ ] Configure HTTPS with valid SSL certificates
- [ ] Restrict port bindings to localhost (127.0.0.1)
- [ ] Enable firewall rules for exposed ports
- [ ] Use Docker secrets for sensitive data
- [ ] Implement rate limiting in Nginx
- [ ] Regular security updates

### Firewall Configuration

```bash
# UFW (Ubuntu)
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable

# firewalld (CentOS/RHEL)
firewall-cmd --permanent --add-service=http
firewall-cmd --permanent --add-service=https
firewall-cmd --reload
```

## Monitoring

### Logs

```bash
# Application logs
tail -f logs/*.log

# Nginx logs
tail -f logs/nginx/access.log
tail -f logs/nginx/error.log

# Docker logs
docker-compose logs -f --tail=100
```

### Metrics

```bash
# Container metrics
docker stats --no-stream

# Disk usage
df -h
du -sh data/ output/ videos/

# Network connections
docker exec demo-nginx netstat -an
```

## Maintenance

### Updates

```bash
# Pull latest changes
git pull

# Rebuild and deploy
./scripts/deploy.sh restart prod
```

### Cleanup

```bash
# Remove stopped containers
docker-compose down

# Clean volumes (WARNING: data loss)
docker-compose down -v

# Remove unused images
docker image prune -a

# Clean build cache
docker builder prune
```

## Tailscale Integration (Optional)

For secure remote access without exposing ports:

```bash
# Install Tailscale
curl -fsSL https://tailscale.com/install.sh | sh

# Start Tailscale
tailscale up

# Access via Tailscale IP
http://100.x.x.x:8501
```

## Support

For issues or questions:
1. Check logs: `docker-compose logs`
2. Review this guide's troubleshooting section
3. Open an issue on GitHub

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Streamlit Deployment](https://docs.streamlit.io/deploy)