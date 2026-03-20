# Demo Project - Deployment Guide

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose installed
- At least 4GB RAM available
- OpenAI API key (or alternative LLM provider configured)

### 1. Clone and Setup
```bash
git clone https://github.com/sherlock-126/demo.git
cd demo
```

### 2. Configure Environment
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=your_api_key_here
```

### 3. Start All Services
```bash
# Build and start all containers
docker-compose up -d --build

# Or start with full stack including frontend
docker-compose --profile full up -d --build
```

## 📍 Service Endpoints

After startup, the following services will be available:

| Service | URL | Description |
|---------|-----|-------------|
| **Streamlit Dashboard** | http://localhost:8501 | Main UI for TikTok content generation |
| **FastAPI Backend** | http://localhost:8000 | REST API backend |
| **Next.js Frontend** | http://localhost:3001 | Modern web dashboard (when using --profile full) |

## 🎯 Core Features

### Content Generation
1. Access Streamlit UI at http://localhost:8501
2. Navigate to "Generate Script" page
3. Enter a parenting topic
4. System will generate AI-powered "Right vs Wrong" scripts

### Image Generation
1. After script generation, go to "Preview Images"
2. System renders split-screen comparison images (1080x1920)
3. Images include branding, icons, and Vietnamese text

### Video Assembly
1. Navigate to "Create Video" page
2. Select generated images
3. Add background music
4. Export as TikTok-ready video or carousel

## 🔧 Service Management

### View Service Status
```bash
docker-compose ps
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f streamlit
docker-compose logs -f frontend
```

### Stop Services
```bash
docker-compose down
```

### Reset Everything
```bash
docker-compose down -v
rm -rf data/* output/* videos/* logs/*
```

## 🐳 Docker Configuration

### Resource Limits
All containers are configured with Windows Hyper-V optimized limits:
- CPU: 0.5 cores (50% of 1 CPU)
- Memory: 2GB RAM per container

### Volumes
- `./data` - Application data and database
- `./output` - Generated images
- `./videos` - Assembled videos
- `./assets` - Static assets (fonts, logos)
- `./audio` - Background music files

## 🔒 Production Deployment

For production deployment with Nginx, SSL, and monitoring:

```bash
# Start with production configuration
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# With monitoring stack
docker-compose -f docker-compose.yml -f docker-compose.prod.yml -f docker-compose.monitoring.yml up -d
```

### Production Features
- Nginx reverse proxy with ModSecurity WAF
- SSL/TLS with Let's Encrypt
- Prometheus + Grafana monitoring
- Centralized logging with Loki
- Rate limiting and DDoS protection

## 🧪 Testing

### Test API Endpoints
```bash
# Test content generation
curl -X POST http://localhost:8000/api/v1/scripts/generate \
  -H "Content-Type: application/json" \
  -d '{"topic": "Teaching children to brush teeth"}'

# Health check
curl http://localhost:8000/health
```

### Run Test Scripts
```bash
# Test image generation
python test_generate_images.py

# Test API integration
python test_api.py
```

## 📝 Environment Variables

Key environment variables in `.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key for GPT-4 | Required |
| `LLM_PROVIDER` | LLM provider (openai_api, chatgpt_cli, etc) | openai_api |
| `LOG_LEVEL` | Logging level | INFO |
| `CORS_ORIGINS` | Allowed CORS origins | http://localhost:3001,http://localhost:8501 |

## 🛠 Troubleshooting

### Port Already in Use
```bash
# Find process using port
lsof -i :8000  # or 3001, 8501

# Kill process
kill -9 <PID>
```

### Container Won't Start
```bash
# Check logs
docker-compose logs <service_name>

# Rebuild specific service
docker-compose build --no-cache <service_name>
```

### Out of Memory
Increase Docker's memory allocation in Docker Desktop settings or reduce container limits in docker-compose.yml.

### FFmpeg Issues
```bash
# Verify FFmpeg is installed in container
docker exec demo-streamlit ffmpeg -version
```

## 📚 Additional Documentation

- [Architecture Overview](./CLAUDE.md)
- [Video Setup Guide](./VIDEO_SETUP.md)
- [API Documentation](http://localhost:8000/docs) (when backend is running)

## 🤝 Support

For issues or questions:
1. Check the logs: `docker-compose logs -f`
2. Verify environment variables are set correctly
3. Ensure all required ports are available
4. Report issues at: https://github.com/sherlock-126/demo/issues

---

**Ready to create amazing TikTok content!** 🎥✨