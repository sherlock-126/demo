#!/bin/bash

# Script to download required fonts for the application
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Base directories
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
FONTS_DIR="$PROJECT_ROOT/assets/fonts"

# Create fonts directory if it doesn't exist
mkdir -p "$FONTS_DIR"

echo -e "${GREEN}Downloading fonts to $FONTS_DIR${NC}"

# Function to download font
download_font() {
    local url=$1
    local filename=$2

    if [ -f "$FONTS_DIR/$filename" ]; then
        echo -e "${YELLOW}$filename already exists, skipping...${NC}"
    else
        echo -e "Downloading $filename..."
        curl -L -o "$FONTS_DIR/$filename" "$url" || {
            echo -e "${RED}Failed to download $filename${NC}"
            return 1
        }
        echo -e "${GREEN}Successfully downloaded $filename${NC}"
    fi
}

# Download Roboto fonts from Google Fonts
echo -e "${GREEN}Downloading Roboto font family...${NC}"
download_font "https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Regular.ttf" "Roboto-Regular.ttf"
download_font "https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Bold.ttf" "Roboto-Bold.ttf"
download_font "https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Medium.ttf" "Roboto-Medium.ttf"
download_font "https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Black.ttf" "Roboto-Black.ttf"

# Download Noto Sans for Vietnamese support
echo -e "${GREEN}Downloading Noto Sans for Vietnamese support...${NC}"
download_font "https://github.com/google/fonts/raw/main/ofl/notosans/NotoSans-Regular.ttf" "NotoSans-Regular.ttf"
download_font "https://github.com/google/fonts/raw/main/ofl/notosans/NotoSans-Bold.ttf" "NotoSans-Bold.ttf"

# Set proper permissions
echo -e "Setting permissions..."
chmod 644 "$FONTS_DIR"/*.ttf 2>/dev/null || true

# Verify downloads
echo -e "\n${GREEN}Font installation complete!${NC}"
echo -e "Fonts installed in: $FONTS_DIR"
echo -e "Total fonts: $(ls -1 "$FONTS_DIR"/*.ttf 2>/dev/null | wc -l)"

# List installed fonts
if [ -n "$(ls -A "$FONTS_DIR"/*.ttf 2>/dev/null)" ]; then
    echo -e "\nInstalled fonts:"
    ls -1 "$FONTS_DIR"/*.ttf | xargs -n1 basename
else
    echo -e "${YELLOW}No fonts found. Please check the downloads.${NC}"
    exit 1
fi

echo -e "\n${GREEN}Done!${NC}"