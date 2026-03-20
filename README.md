# TikTok Content Generation System

AI-powered system for generating TikTok educational content about parenting, featuring automated script generation and split-screen layout rendering.

## Features

### 1. Content Generator
- Uses OpenAI GPT-4 to transform parenting topics into "Right vs Wrong" comparison scripts
- Generates structured JSON with titles, descriptions, and slide content
- Supports Vietnamese and English languages
- CLI and Python API interfaces

### 2. Layout Generator
- Renders split-screen comparison images (1080x1920) from JSON scripts
- Supports Vietnamese text rendering with proper fonts
- Customizable styling through YAML configuration
- Automatic icon placement (X/✓) and logo watermarking
- Batch processing capabilities

## Installation

```bash
# Clone repository
git clone https://github.com/sherlock-126/demo.git
cd demo

# Install dependencies
pip install -r requirements.txt

# Download fonts and create assets
bash scripts/download_assets.sh

# Install package
pip install -e .
```

## Quick Start

### Generate Content Script

```bash
# Generate script from topic
python -m content_generator generate "Cách dạy con không la mắng"

# Or use the CLI
content-generator generate "Teaching methods" --slides 5 --output script.json
```

### Generate Layout Images

```bash
# Generate images from script
python -m layout_generator generate script.json --output images/

# Or use the CLI
layout-generator generate examples/sample_output.json

# Batch processing
layout-generator batch scripts/ --output-dir output/
```

### Python API Usage

```python
# Generate script
from content_generator import ScriptGenerator

generator = ScriptGenerator(api_key="your-api-key")
script = generator.generate(
    topic="Cách dạy con không la mắng",
    num_slides=5
)

# Generate images
from layout_generator import LayoutGenerator

layout_gen = LayoutGenerator()
result = layout_gen.generate_from_script(script)
print(f"Generated {len(result.images)} images")
```

## Configuration

### Content Generator
Set your OpenAI API key in `.env`:
```
OPENAI_API_KEY=your-api-key-here
```

### Layout Generator
Customize styling in `config/default.yaml`:
```yaml
layout:
  width: 1080
  height: 1920
  padding: 60

colors:
  background:
    wrong: "#FFE8E8"
    right: "#E8FFE8"
  text:
    title: "#2C3E50"
    label_wrong: "#E74C3C"
    label_right: "#27AE60"
```

## Project Structure

```
demo/
├── content_generator/     # Script generation module
│   ├── generator.py      # Main generator logic
│   ├── openai_client.py  # OpenAI API integration
│   └── models.py         # Data models
├── layout_generator/      # Image rendering module
│   ├── generator.py      # Main layout generator
│   ├── renderer.py       # Slide renderer
│   └── components/       # Rendering components
├── config/               # Configuration files
│   ├── default.yaml      # Default styling
│   └── minimal.yaml      # Minimal style variant
├── assets/               # Static assets
│   ├── fonts/           # Vietnamese-supporting fonts
│   ├── icons/           # X/✓ icons
│   └── logo/            # Brand logos
└── examples/            # Example scripts
```

## Development

### Running Tests
```bash
pytest tests/
```

### Code Style
```bash
black .
ruff check .
```

## License

MIT
