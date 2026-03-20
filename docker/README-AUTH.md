# LLM Provider Authentication Guide

This guide explains how to authenticate with different LLM providers in the Docker container.

## Quick Start

### Option 1: OpenAI API (Default)

No manual authentication needed. Just set your API key:

```bash
# In .env file or environment
LLM_PROVIDER=openai_api
OPENAI_API_KEY=sk-your-api-key-here
```

### Option 2: CLI-based ChatGPT

Some CLI tools require manual authentication:

```bash
# 1. Start the container
docker-compose up -d

# 2. Enter the container
docker exec -it content-generator-container bash

# 3. Authenticate (depends on your CLI tool)
chatgpt-cli auth login

# 4. Test authentication
chatgpt-cli ask "Hello, are you working?"

# 5. Exit container
exit
```

### Option 3: RevChatGPT (Browser-based)

RevChatGPT uses browser automation and requires session tokens:

```bash
# 1. Enter container
docker exec -it content-generator-container bash

# 2. Run authentication script
python /app/docker/auth_scripts/setup_revchatgpt.py

# 3. Follow the prompts to enter your session tokens
# You'll need to get these from your browser's developer tools

# 4. Test the connection
python -m revchatgpt test

# 5. Exit container
exit
```

## Environment Variables

### Required for Each Provider

**OpenAI API:**
- `LLM_PROVIDER=openai_api`
- `OPENAI_API_KEY=sk-...`

**CLI ChatGPT:**
- `LLM_PROVIDER=cli_chatgpt`
- `CHATGPT_CLI_COMMAND=/usr/local/bin/chatgpt-cli` (optional)

**RevChatGPT:**
- `LLM_PROVIDER=revchatgpt`
- `REVCHATGPT_ACCESS_TOKEN=...` (after authentication)

### Optional Settings

```bash
# Timeouts
TIMEOUT_SECONDS=30
CLI_TIMEOUT=60
REVCHATGPT_TIMEOUT=90

# Retries
MAX_RETRIES=3

# Logging
LOG_LEVEL=INFO
```

## Persistent Authentication

Authentication tokens are stored in a Docker volume to persist across container restarts:

```bash
# View stored auth data
docker exec content-generator-container ls -la /app/.auth/

# Backup auth data
docker cp content-generator-container:/app/.auth ./auth-backup

# Restore auth data
docker cp ./auth-backup content-generator-container:/app/.auth
```

## Switching Providers

You can switch between providers by changing the `LLM_PROVIDER` environment variable:

```bash
# Switch to mock provider for testing
export LLM_PROVIDER=mock
docker-compose restart

# Switch back to OpenAI
export LLM_PROVIDER=openai_api
docker-compose restart
```

## Troubleshooting

### Authentication Fails

1. Check provider is installed:
```bash
docker exec content-generator-container which chatgpt-cli
```

2. Check environment variables:
```bash
docker exec content-generator-container env | grep LLM
```

3. Test provider directly:
```bash
docker exec -it content-generator-container python -c "
from content_generator.llm_providers import get_llm_provider
provider = get_llm_provider()
print(f'Provider: {provider.provider_name}')
"
```

### Container Won't Start

Check logs:
```bash
docker-compose logs content-generator
```

### Permission Issues

Ensure volumes have correct permissions:
```bash
chmod -R 755 ./data ./output
```

## Security Notes

- Never commit `.env` files with API keys
- Use Docker secrets for production deployments
- Rotate API keys regularly
- Limit container network access if not needed

## Provider-Specific Notes

### ChatGPT CLI Tools

Various CLI tools are available:
- `chatgpt-cli` (Node.js based)
- `gpt-cli` (Python based)
- Custom scripts

Each may have different authentication methods. Check the tool's documentation.

### RevChatGPT

RevChatGPT bypasses the official API by automating browser interactions. Note:
- May break if OpenAI changes their UI
- Requires valid ChatGPT Plus subscription for GPT-4
- Session tokens expire and need renewal

## Development Mode

For development, you can mount the source code:

```yaml
# In docker-compose.yml
volumes:
  - ../content_generator:/app/content_generator
```

This allows live code changes without rebuilding.

## Support

If you encounter issues:
1. Check this guide
2. Review logs: `docker-compose logs`
3. Try the mock provider: `LLM_PROVIDER=mock`
4. File an issue with full error details