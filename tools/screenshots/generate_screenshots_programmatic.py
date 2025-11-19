#!/usr/bin/env python3
"""
Generate screenshots by compositing digit images.

This approach bypasses the unreliable emulator screenshot process by
directly compositing the watchface digit bitmaps into screenshots.

Benefits:
- Instant generation (<1 second)
- 100% reliable, no emulator timing issues
- Pixel-perfect accuracy
- Easy to maintain and regenerate

Usage:
    python3 generate_screenshots_programmatic.py

Generates screenshots for aplite platform (144×168). For basalt, simply
copy the aplite screenshots as they have identical display dimensions.
"""

from PIL import Image
from pathlib import Path

# Paths
RESOURCES = Path("resources/images")
OUTPUT_DIR = Path("store-assets/screenshots/aplite")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Times to generate (hour, minute, is_24h, filename)
TIMES = [
    (10, 8, False, "10-08-12h"),   # 10:08 AM (12h mode)
    (12, 0, False, "12-00-12h"),   # 12:00 PM (12h mode)
    (3, 45, False, "03-45-12h"),   # 3:45 AM (12h mode)
    (9, 41, False, "09-41-12h"),   # 9:41 AM (12h mode) - Apple's marketing time
    (23, 59, True, "23-59-24h"),   # 23:59 (24h mode)
]

def load_digit(num):
    """Load a digit image from resources."""
    path = RESOURCES / f"digit_{num}.png"
    if not path.exists():
        raise FileNotFoundError(f"Digit image not found: {path}")
    return Image.open(path)

def generate_screenshot(hour, minute, is_24h, name):
    """
    Generate a screenshot for a specific time.

    Args:
        hour: Hour (0-23 for 24h, 1-12 for 12h)
        minute: Minute (0-59)
        is_24h: Whether to use 24h format
        name: Output filename (without extension)

    Returns:
        Path to generated screenshot
    """
    # Convert hour based on format
    if not is_24h:
        hour = hour % 12
        if hour == 0:
            hour = 12

    # Get digits
    hour_tens = hour // 10
    hour_ones = hour % 10
    min_tens = minute // 10
    min_ones = minute % 10

    # Create black background (144x168 for aplite/basalt)
    screenshot = Image.new('RGB', (144, 168), (0, 0, 0))

    # Load digit images
    digits = {
        'hour_tens': load_digit(hour_tens),
        'hour_ones': load_digit(hour_ones),
        'min_tens': load_digit(min_tens),
        'min_ones': load_digit(min_ones),
    }

    # Quadrant dimensions
    # Top row: 72×83 (each quadrant)
    # Bottom row: 72×84 (each quadrant)
    # 1px padding between rows
    quad_width = 72
    quad_height_top = 83

    # Place digits in 2×2 grid
    # Top-left: hour tens (hide if 0 in 12h mode)
    if not (not is_24h and hour_tens == 0):
        screenshot.paste(digits['hour_tens'], (0, 0))

    # Top-right: hour ones
    screenshot.paste(digits['hour_ones'], (quad_width, 0))

    # Bottom-left: minute tens (with 1px padding)
    screenshot.paste(digits['min_tens'], (0, quad_height_top + 1))

    # Bottom-right: minute ones
    screenshot.paste(digits['min_ones'], (quad_width, quad_height_top + 1))

    # Save
    output_path = OUTPUT_DIR / f"{name}.png"
    screenshot.save(output_path)

    return output_path

def main():
    """Generate all screenshots."""
    print("Generating screenshots from digit images...")
    print("=" * 50)

    for hour, minute, is_24h, name in TIMES:
        output_path = generate_screenshot(hour, minute, is_24h, name)
        print(f"✅ Generated: {name}.png")

    print("=" * 50)
    print(f"✅ Complete! All screenshots in: {OUTPUT_DIR}")
    print()
    print("Next steps:")
    print("  1. Copy to basalt: cp store-assets/screenshots/aplite/*.png store-assets/screenshots/basalt/")
    print("  2. Regenerate banner: python3 generate_banner.py")

if __name__ == "__main__":
    main()
