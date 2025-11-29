#!/usr/bin/env python3
"""
Generate Pebble store screenshots for Super Legible watch face.
Creates 5 screenshots per platform (25 total) at different times.
"""

import os
import subprocess
import time
import re
from pathlib import Path
from PIL import Image

# Configuration
PROJECT_DIR = Path(__file__).resolve().parent.parent.parent
SRC_FILE = PROJECT_DIR / "src" / "main.c"
SCREENSHOTS_DIR = PROJECT_DIR / "store-assets" / "screenshots"

# Platforms and their display sizes
PLATFORMS = {
    "aplite": {"size": (144, 168), "name": "Pebble (Aplite)"},
    "basalt": {"size": (144, 168), "name": "Pebble Time (Basalt)"},
    "chalk": {"size": (180, 180), "name": "Pebble Time Round (Chalk)"},
    "diorite": {"size": (144, 168), "name": "Pebble 2 (Diorite)"},
    "emery": {"size": (200, 228), "name": "Pebble Time 2 (Emery)"},
}

# Times to capture (format: hour, minute, is_24h, display_name)
SCREENSHOT_TIMES = [
    (10, 8, False, "10-08-12h"),   # 10:08 AM
    (12, 0, False, "12-00-12h"),   # 12:00 PM
    (3, 45, False, "03-45-12h"),   # 3:45 PM
    (9, 41, False, "09-41-12h"),   # 9:41 AM (Apple signature time)
    (23, 59, True, "23-59-24h"),   # 23:59 (24h format)
]


def enable_screenshot_mode(hour, minute, is_24h):
    """Enable screenshot mode in source code with specific time."""
    print(f"  Configuring for {hour:02d}:{minute:02d} ({'24h' if is_24h else '12h'})...")

    with open(SRC_FILE, 'r') as f:
        content = f.read()

    # Replace the screenshot mode defines
    pattern = r'// #define SCREENSHOT_MODE\n// #define SCREENSHOT_TIME_24H \d+\n// #define SCREENSHOT_HOUR \d+\n// #define SCREENSHOT_MINUTE \d+'
    replacement = f'#define SCREENSHOT_MODE\n#define SCREENSHOT_TIME_24H {1 if is_24h else 0}\n#define SCREENSHOT_HOUR {hour}\n#define SCREENSHOT_MINUTE {minute}'

    content = re.sub(pattern, replacement, content)

    with open(SRC_FILE, 'w') as f:
        f.write(content)


def disable_screenshot_mode():
    """Disable screenshot mode in source code."""
    with open(SRC_FILE, 'r') as f:
        content = f.read()

    # Comment out the screenshot mode defines
    pattern = r'#define SCREENSHOT_MODE\n#define SCREENSHOT_TIME_24H \d+\n#define SCREENSHOT_HOUR \d+\n#define SCREENSHOT_MINUTE \d+'
    replacement = '// #define SCREENSHOT_MODE\n// #define SCREENSHOT_TIME_24H 0\n// #define SCREENSHOT_HOUR 10\n// #define SCREENSHOT_MINUTE 8'

    content = re.sub(pattern, replacement, content)

    with open(SRC_FILE, 'w') as f:
        f.write(content)


def build_and_install(platform):
    """Build watch face and install to emulator."""
    print(f"  Building and installing to {platform}...")

    # Build
    result = subprocess.run(
        ["nix-shell", "--run", "pebble build"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"    Build failed: {result.stderr}")
        return False

    # Install to emulator
    result = subprocess.run(
        ["nix-shell", "--run", f"pebble install --emulator {platform}"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"    Install failed: {result.stderr}")
        return False

    return True


def capture_screenshot(output_path):
    """Capture screenshot using peekaboo."""
    print(f"  Capturing screenshot...")

    # Wait for app to fully launch
    time.sleep(2)

    result = subprocess.run(
        ["peekaboo", "image", "--app", "qemu-pebble", "--path", str(output_path)],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"    Capture failed: {result.stderr}")
        return False

    return True


def crop_to_display(image_path, display_size):
    """Crop screenshot to just the watch display."""
    print(f"  Cropping to display size {display_size}...")

    try:
        img = Image.open(image_path)

        # Find the black rectangle (watch display) in the screenshot
        # Strategy: Look for continuous black regions that match expected size
        # For now, we'll center crop based on expected display size

        # Get image dimensions
        img_width, img_height = img.size
        display_width, display_height = display_size

        # Calculate center crop coordinates
        left = (img_width - display_width) // 2
        top = (img_height - display_height) // 2
        right = left + display_width
        bottom = top + display_height

        # Crop and save
        cropped = img.crop((left, top, right, bottom))
        cropped.save(image_path)

        print(f"    Cropped to {display_width}x{display_height}")
        return True

    except Exception as e:
        print(f"    Crop failed: {e}")
        return False


def generate_platform_screenshots(platform):
    """Generate all screenshots for a single platform."""
    print(f"\n=== Generating screenshots for {PLATFORMS[platform]['name']} ===")

    # Create platform directory
    platform_dir = SCREENSHOTS_DIR / platform
    platform_dir.mkdir(parents=True, exist_ok=True)

    for hour, minute, is_24h, display_name in SCREENSHOT_TIMES:
        print(f"\nTime: {display_name}")

        # Enable screenshot mode with this time
        enable_screenshot_mode(hour, minute, is_24h)

        # Build and install
        if not build_and_install(platform):
            print("  ❌ Build/install failed, skipping...")
            continue

        # Capture screenshot
        output_path = platform_dir / f"{display_name}.png"
        if not capture_screenshot(output_path):
            print("  ❌ Screenshot capture failed, skipping...")
            continue

        # Crop to display size
        if not crop_to_display(output_path, PLATFORMS[platform]["size"]):
            print("  ❌ Crop failed, but keeping raw screenshot")

        print(f"  ✅ Saved to {output_path}")

    # Disable screenshot mode
    disable_screenshot_mode()


def main():
    """Main script execution."""
    print("=" * 60)
    print("Super Legible - Screenshot Generator")
    print("=" * 60)
    print(f"\nGenerating 25 screenshots (5 platforms × 5 times)")
    print(f"Output directory: {SCREENSHOTS_DIR}")

    # Check that peekaboo is available
    if subprocess.run(["which", "peekaboo"], capture_output=True).returncode != 0:
        print("\n❌ Error: peekaboo not found. Please install it first.")
        return 1

    # Check permissions
    result = subprocess.run(["peekaboo", "permissions"], capture_output=True, text=True)
    if "Screen Recording: ✅" not in result.stdout:
        print("\n⚠️  Warning: Screen Recording permission may not be granted.")
        print("    Check with: System Settings > Privacy & Security > Screen Recording")

    # Generate screenshots for each platform
    for platform in PLATFORMS.keys():
        generate_platform_screenshots(platform)

    # Restore original source code
    print("\n\nRestoring original source code (disabling screenshot mode)...")
    disable_screenshot_mode()

    # Final build to ensure clean state
    print("Building final clean version...")
    subprocess.run(
        ["nix-shell", "--run", "pebble build"],
        cwd=PROJECT_DIR,
        capture_output=True
    )

    print("\n" + "=" * 60)
    print("✅ Screenshot generation complete!")
    print(f"   Screenshots saved to: {SCREENSHOTS_DIR}")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    exit(main())
