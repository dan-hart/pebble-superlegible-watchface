#!/usr/bin/env python3
"""
Generate 720×320 app store banner showing all 5 Pebble platforms.
Requires screenshots to be captured first.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import sys


# Configuration
PROJECT_DIR = Path("/Users/danhart/Developer/pebble-superlegible-watchface")
SCREENSHOTS_DIR = PROJECT_DIR / "store-assets" / "screenshots"
OUTPUT_PATH = PROJECT_DIR / "store-assets" / "banner.png"

# Banner dimensions
BANNER_WIDTH = 720
BANNER_HEIGHT = 320

# Platforms and their info - all 5 platforms
# Each platform shows a different time for variety
PLATFORMS = [
    ("aplite", "Pebble", (144, 168), "10-08-12h"),
    ("basalt", "Pebble Time", (144, 168), "12-00-12h"),
    ("chalk", "Time Round", (180, 180), "09-41-12h"),
    ("diorite", "Pebble 2", (144, 168), "03-45-12h"),
    ("emery", "Time 2", (200, 228), "23-59-24h"),
]


def create_banner():
    """Create the banner image."""
    print("Creating 720×320 app store banner...")

    # Create blank banner (black background)
    banner = Image.new('RGB', (BANNER_WIDTH, BANNER_HEIGHT), color=(0, 0, 0))
    draw = ImageDraw.Draw(banner)

    # Calculate layout
    # Leave margin at top for text
    text_height = 60
    available_height = BANNER_HEIGHT - text_height
    padding = 10
    platform_width = (BANNER_WIDTH - (padding * 6)) // 5  # 5 platforms with padding

    # Load screenshots and place them
    x_offset = padding
    successful_screenshots = []

    for platform, name, (orig_w, orig_h), time_name in PLATFORMS:
        screenshot_path = SCREENSHOTS_DIR / platform / f"{time_name}.png"

        if not screenshot_path.exists():
            print(f"  Warning: {screenshot_path} not found, skipping {platform}")
            continue

        try:
            # Load screenshot
            img = Image.open(screenshot_path)

            # Scale to fit width while maintaining aspect ratio
            scale = platform_width / img.width
            new_width = platform_width
            new_height = int(img.height * scale)

            # If too tall, scale based on height instead
            if new_height > available_height - 40:  # Leave room for label
                scale = (available_height - 40) / img.height
                new_height = available_height - 40
                new_width = int(img.width * scale)

            # Resize
            img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Center vertically in available space
            y_offset = text_height + ((available_height - 40 - new_height) // 2)

            # Paste onto banner
            banner.paste(img_resized, (x_offset, y_offset))

            # Add platform label below
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)
            except:
                font = ImageFont.load_default()

            label_bbox = draw.textbbox((0, 0), name, font=font)
            label_width = label_bbox[2] - label_bbox[0]
            label_x = x_offset + (platform_width - label_width) // 2
            label_y = y_offset + new_height + 5

            draw.text((label_x, label_y), name, fill=(255, 255, 255), font=font)

            successful_screenshots.append(platform)
            x_offset += platform_width + padding

        except Exception as e:
            print(f"  Error processing {platform}: {e}")
            continue

    # Add title at top
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
        subtitle_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 18)
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()

    title = "Super Legible"
    subtitle = "Maximum Readability • Universal Compatibility"

    # Center title
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (BANNER_WIDTH - title_width) // 2
    draw.text((title_x, 10), title, fill=(255, 255, 255), font=title_font)

    # Center subtitle
    subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
    subtitle_x = (BANNER_WIDTH - subtitle_width) // 2
    draw.text((subtitle_x, 50), subtitle, fill=(180, 180, 180), font=subtitle_font)

    # Save banner
    banner.save(OUTPUT_PATH)
    print(f"\n✅ Banner created: {OUTPUT_PATH}")
    print(f"   Included platforms: {', '.join(successful_screenshots)}")

    if len(successful_screenshots) < 5:
        print(f"\n⚠️  Warning: Only {len(successful_screenshots)}/5 platforms included.")
        print(f"   Missing: {[p for p, _, _, _ in PLATFORMS if p not in successful_screenshots]}")
        print(f"   Generate missing screenshots first for complete banner.")

    return 0


def main():
    if not SCREENSHOTS_DIR.exists():
        print(f"Error: Screenshots directory not found: {SCREENSHOTS_DIR}")
        print("Generate screenshots first using screenshot_one_platform.py")
        return 1

    return create_banner()


if __name__ == "__main__":
    exit(main())
