#!/bin/bash
# Setup script for content generator

echo "Setting up Content Generator..."
echo "=============================="

# Check Python version
echo -n "Checking Python version... "
python_version=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
major=$(echo $python_version | cut -d. -f1)
minor=$(echo $python_version | cut -d. -f2)

if [ "$major" -ge 3 ] && [ "$minor" -ge 10 ]; then
    echo "✓ Python $python_version"
else
    echo "✗ Python 3.10+ required (found $python_version)"
    exit 1
fi

# Create virtual environment
echo -n "Creating virtual environment... "
python3 -m venv venv
echo "✓"

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt

# Create directories
echo -n "Creating directories... "
mkdir -p data/scripts data/logs cache templates
echo "✓"

# Check for .env file
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file and add your OpenAI API key"
    echo "   vim .env"
else
    echo "✓ .env file exists"
fi

# Install package in development mode
echo -n "Installing package... "
pip install -e . > /dev/null 2>&1
echo "✓"

echo ""
echo "Setup complete!"
echo ""
echo "To activate the virtual environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To test the installation, run:"
echo "  python -m content_generator setup"
echo ""
echo "To generate your first script, run:"
echo "  python -m content_generator generate 'Your topic here'"