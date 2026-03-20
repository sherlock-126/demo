#!/bin/bash
# Download fonts and create placeholder assets

echo "Setting up assets for Layout Generator..."

# Create directories
mkdir -p assets/fonts
mkdir -p assets/icons
mkdir -p assets/logo

# Download Roboto fonts (Vietnamese support)
echo "Downloading Roboto fonts..."
FONT_BASE="https://github.com/google/fonts/raw/main/apache/roboto/static"

wget -q "$FONT_BASE/Roboto-Regular.ttf" -O assets/fonts/Roboto-Regular.ttf
wget -q "$FONT_BASE/Roboto-Bold.ttf" -O assets/fonts/Roboto-Bold.ttf
wget -q "$FONT_BASE/Roboto-Medium.ttf" -O assets/fonts/Roboto-Medium.ttf
wget -q "$FONT_BASE/Roboto-Black.ttf" -O assets/fonts/Roboto-Black.ttf

# Create placeholder icons using Python/Pillow
python3 - <<EOF
from PIL import Image, ImageDraw

# Create X mark icon (red)
img = Image.new('RGBA', (200, 200), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)
draw.line([(40, 40), (160, 160)], fill=(231, 76, 60, 255), width=20)
draw.line([(40, 160), (160, 40)], fill=(231, 76, 60, 255), width=20)
img.save('assets/icons/x-mark.png')

# Create check mark icon (green)
img = Image.new('RGBA', (200, 200), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)
points = [(50, 110), (80, 140), (150, 70)]
draw.line(points[0:2], fill=(39, 174, 96, 255), width=20)
draw.line(points[1:3], fill=(39, 174, 96, 255), width=20)
img.save('assets/icons/check-mark.png')

# Create placeholder logo
img = Image.new('RGBA', (400, 160), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)
draw.rounded_rectangle([(10, 10), (390, 150)], radius=20, fill=(52, 73, 94, 200))
draw.text((200, 80), "LOGO", fill=(255, 255, 255, 255), anchor="mm")
img.save('assets/logo/placeholder.png')

print("✅ Placeholder assets created")
EOF

echo "✅ Assets setup complete!"
echo ""
echo "Assets created:"
echo "  - Fonts: assets/fonts/ (Roboto family)"
echo "  - Icons: assets/icons/ (x-mark.png, check-mark.png)"
echo "  - Logo: assets/logo/placeholder.png"
echo ""
echo "You can replace these with your actual assets."