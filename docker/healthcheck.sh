#!/bin/bash

# Health check script for Docker container

# Check FFmpeg
if ! ffmpeg -version > /dev/null 2>&1; then
    echo "FFmpeg check failed"
    exit 1
fi

# Check Python modules
if ! python -c "import content_generator, layout_generator, video_assembly" 2>/dev/null; then
    echo "Python modules check failed"
    exit 1
fi

# Check critical directories are writable
for dir in /app/data /app/output /app/videos; do
    if [ ! -d "$dir" ] || [ ! -w "$dir" ]; then
        echo "Directory $dir check failed"
        exit 1
    fi
done

# Check OpenAI API connectivity (if configured)
if [ ! -z "$OPENAI_API_KEY" ]; then
    if ! python -c "import openai; openai.api_key='$OPENAI_API_KEY'; print('API OK')" 2>/dev/null; then
        echo "OpenAI API check failed"
        exit 1
    fi
fi

echo "Health check passed"
exit 0