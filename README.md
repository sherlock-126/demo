# AI Topic & Scripting Engine

An AI-powered content generator that transforms parenting topics into engaging "Right vs Wrong" comparison scripts for TikTok, using OpenAI GPT-4.

## Features

- 🤖 **AI-Powered Generation**: Uses OpenAI GPT-4 to create educational parenting content
- 🎭 **Split-Screen Format**: Generates "SAI vs ĐÚNG" (Wrong vs Right) comparisons
- 🌏 **Multi-language Support**: Vietnamese and English content generation
- 📝 **Structured Output**: JSON format with titles, descriptions, and overlay text
- 🔄 **Batch Processing**: Generate multiple scripts at once
- 💾 **Persistent Storage**: Save and retrieve generated scripts
- 🛡️ **Robust Error Handling**: Retry logic and comprehensive validation

## Installation

### Requirements
- Python 3.10+
- OpenAI API key

### Setup

1. Clone the repository:
```bash
git clone https://github.com/sherlock-126/demo.git
cd demo
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your OpenAI API key:
```bash
cp .env.example .env
# Edit .env and add your API key
```

## Usage

### Command Line Interface

#### Generate a single script:
```bash
python -m content_generator generate "Cách dạy con không la mắng"
```

#### Generate with options:
```bash
python -m content_generator generate "Topic" --slides 5 --language vi --output script.json
```

#### Batch processing:
```bash
# Create a file with topics (one per line)
echo "Cách dạy con tự lập" > topics.txt
echo "Cách xử lý khi con ăn vạ" >> topics.txt

# Generate scripts for all topics
python -m content_generator batch topics.txt --output-dir scripts/
```

#### List generated scripts:
```bash
python -m content_generator list --limit 10
```

#### View a script:
```bash
python -m content_generator show "20240320_120000_topic.json" --format text
```

### Python API

```python
from content_generator import ScriptGenerator

# Initialize generator
generator = ScriptGenerator(api_key="sk-your-api-key")

# Generate a script
script = generator.generate(
    topic="Cách dạy con không la mắng",
    num_slides=5,
    language="vi"
)

# Access script data
print(script.main_title)
print(script.subtitle)
for slide in script.slides:
    print(f"SAI: {slide.left_side.text}")
    print(f"ĐÚNG: {slide.right_side.text}")

# Export to different formats
json_output = generator.export_script(script, format="json")
text_output = generator.export_script(script, format="text")
```

## Output Format

The generated script follows this structure:

```json
{
  "topic": "Cách dạy con không la mắng",
  "main_title": "Dạy Con Không La Mắng: Bí Quyết Vàng",
  "subtitle": "Phương pháp giáo dục tích cực cho bé",
  "slides": [
    {
      "left_side": {
        "description": "Parent yelling at child who spilled milk...",
        "text": "La mắng khi con làm đổ",
        "label": "SAI"
      },
      "right_side": {
        "description": "Parent calmly helping child clean up...",
        "text": "Bình tĩnh hướng dẫn dọn dẹp",
        "label": "ĐÚNG"
      }
    }
  ],
  "metadata": {
    "generated_at": "2024-03-20T12:00:00",
    "model": "gpt-4-turbo-preview",
    "tokens_used": 1500,
    "language": "vi"
  }
}
```

## Configuration

Environment variables (`.env` file):

```bash
# Required
OPENAI_API_KEY=sk-your-api-key-here

# Optional
OPENAI_MODEL=gpt-4-turbo-preview
MAX_RETRIES=3
TIMEOUT_SECONDS=30
LOG_LEVEL=INFO
DATA_DIR=data
CACHE_ENABLED=false
```

## Project Structure

```
demo/
├── content_generator/      # Core package
│   ├── api.py             # Public API interface
│   ├── generator.py       # Main orchestrator
│   ├── openai_client.py   # OpenAI integration
│   ├── models.py          # Data models
│   └── ...
├── templates/             # Prompt templates
├── examples/              # Usage examples
├── tests/                 # Test suite
└── data/                  # Generated scripts
```

## Development

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black content_generator/
ruff check content_generator/
```

### Type Checking
```bash
mypy content_generator/
```

## License

MIT