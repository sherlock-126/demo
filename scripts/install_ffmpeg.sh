#!/bin/bash

# FFmpeg installation script for different platforms

echo "FFmpeg Installation Helper"
echo "=========================="
echo ""

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Detected Linux system"

    # Check if apt-get is available (Debian/Ubuntu)
    if command -v apt-get &> /dev/null; then
        echo "Installing FFmpeg using apt-get..."
        sudo apt-get update
        sudo apt-get install -y ffmpeg
    # Check if yum is available (RedHat/CentOS)
    elif command -v yum &> /dev/null; then
        echo "Installing FFmpeg using yum..."
        sudo yum install -y ffmpeg
    # Check if pacman is available (Arch)
    elif command -v pacman &> /dev/null; then
        echo "Installing FFmpeg using pacman..."
        sudo pacman -S ffmpeg
    else
        echo "Could not detect package manager"
        echo "Please install FFmpeg manually from: https://ffmpeg.org/download.html"
        exit 1
    fi

elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Detected macOS system"

    # Check if Homebrew is installed
    if command -v brew &> /dev/null; then
        echo "Installing FFmpeg using Homebrew..."
        brew install ffmpeg
    else
        echo "Homebrew not found. Installing Homebrew first..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        brew install ffmpeg
    fi

elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "win32" ]]; then
    echo "Detected Windows system"
    echo ""
    echo "Please download FFmpeg from: https://www.gyan.dev/ffmpeg/builds/"
    echo "1. Download the 'full' build"
    echo "2. Extract the archive"
    echo "3. Add the 'bin' folder to your PATH environment variable"
    echo ""
    echo "Or use Chocolatey if available:"
    echo "  choco install ffmpeg"
    exit 0

else
    echo "Unknown operating system: $OSTYPE"
    echo "Please install FFmpeg manually from: https://ffmpeg.org/download.html"
    exit 1
fi

# Verify installation
echo ""
echo "Verifying FFmpeg installation..."
if command -v ffmpeg &> /dev/null; then
    echo "✓ FFmpeg installed successfully!"
    ffmpeg -version | head -n 1
else
    echo "✗ FFmpeg installation failed"
    echo "Please install manually from: https://ffmpeg.org/download.html"
    exit 1
fi