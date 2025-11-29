#!/usr/bin/env python3
"""
Generate screenshots for a single Pebble platform.
Usage: python3 screenshot_one_platform.py <platform>
Example: python3 screenshot_one_platform.py aplite
"""

import sys
import os
import subprocess
import time
import re
from pathlib import Path

# Configuration
PROJECT_DIR = Path(__file__).resolve().parent.parent.parent
SRC_FILE = PROJECT_DIR / "src" / "main.c"
SCREENSHOTS_DIR = PROJECT_DIR / "store-assets" / "screenshots"

# Times to capture
TIMES = [
    (10, 8, False, "10-08-12h"),
    (12, 0, False, "12-00-12h"),
    (3, 45, False, "03-45-12h"),
    (9, 41, False, "09-41-12h"),
    (23, 59, True, "23-59-24h"),
]

# Platform display sizes
SIZES = {
    "aplite": (144, 168),
    "basalt": (144, 168),
    "chalk": (180, 180),
    "diorite": (144, 168),
    "emery": (200, 228),
}


def update_screenshot_mode(hour, minute, is_24h, enabled=True):
    """Enable or disable screenshot mode in source code."""
    with open(SRC_FILE, 'r') as f:
        content = f.read()

    if enabled:
        # Enable with specific time
        content = re.sub(
            r'// #define SCREENSHOT_MODE',
            '#define SCREENSHOT_MODE',
            content
        )
        content = re.sub(
            r'(//\s*)?#define SCREENSHOT_TIME_24H \d+',
            f'#define SCREENSHOT_TIME_24H {1 if is_24h else 0}',
            content
        )
        content = re.sub(
            r'(//\s*)?#define SCREENSHOT_HOUR \d+',
            f'#define SCREENSHOT_HOUR {hour}',
            content
        )
        content = re.sub(
            r'(//\s*)?#define SCREENSHOT_MINUTE \d+',
            f'#define SCREENSHOT_MINUTE {minute}',
            content
        )
    else:
        # Disable (comment out)
        content = re.sub(
            r'#define SCREENSHOT_MODE',
            '// #define SCREENSHOT_MODE',
            content
        )
        content = re.sub(
            r'#define SCREENSHOT_TIME_24H',
            '// #define SCREENSHOT_TIME_24H',
            content
        )
        content = re.sub(
            r'#define SCREENSHOT_HOUR',
            '// #define SCREENSHOT_HOUR',
            content
        )
        content = re.sub(
            r'#define SCREENSHOT_MINUTE',
            '// #define SCREENSHOT_MINUTE',
            content
        )

    with open(SRC_FILE, 'w') as f:
        f.write(content)


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 screenshot_one_platform.py <platform>")
        print("Platforms: aplite, basalt, chalk, diorite, emery")
        return 1

    platform = sys.argv[1]
    if platform not in SIZES:
        print(f"Error: Unknown platform '{platform}'")
        print("Valid platforms: aplite, basalt, chalk, diorite, emery")
        return 1

    print(f"\n{'='*60}")
    print(f"Generating screenshots for {platform}")
    print(f"{'='*60}\n")

    # Create output directory
    output_dir = SCREENSHOTS_DIR / platform
    output_dir.mkdir(parents=True, exist_ok=True)

    # Kill any existing emulators to avoid multi-window issues
    print("Closing any existing emulators...")
    subprocess.run(["killall", "qemu-pebble"], capture_output=True)
    time.sleep(1)

    for hour, minute, is_24h, name in TIMES:
        print(f"\n--- {name} ({hour:02d}:{minute:02d} {'24h' if is_24h else '12h'}) ---")

        # Update source code
        print("  Configuring time...")
        update_screenshot_mode(hour, minute, is_24h, enabled=True)

        # Build
        print("  Building...")
        result = subprocess.run(
            ["nix-shell", "--run", "pebble build"],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"  ❌ Build failed: {result.stderr}")
            continue

        # Install
        print(f"  Installing to {platform}...")
        result = subprocess.run(
            ["nix-shell", "--run", f"pebble install --emulator {platform}"],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"  ❌ Install failed: {result.stderr}")
            continue

        # Wait for launch and rendering
        print("  Waiting for emulator to fully render...")
        time.sleep(8)

        # Try using pebble screenshot first (more reliable)
        output_path = output_dir / f"{name}.png"
        print(f"  Capturing screenshot...")

        # Try pebble screenshot command
        result = subprocess.run(
            ["nix-shell", "--run", f"pebble screenshot --emulator {platform} {output_path}"],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            # Fallback to peekaboo
            print("    Pebble screenshot failed, trying peekaboo...")
            result = subprocess.run(
                ["peekaboo", "image", "--app", "qemu-pebble", "--path", str(output_path)],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                print(f"  ❌ Screenshot failed: {result.stderr}")
                continue

        print(f"  ✅ Saved: {output_path.name}")

    # Restore source code
    print("\n\nRestoring source code...")
    update_screenshot_mode(10, 8, False, enabled=False)

    print(f"\n{'='*60}")
    print(f"✅ Complete! Screenshots in: {output_dir}")
    print(f"{'='*60}\n")
    print("Next steps:")
    print(f"  1. Review screenshots: open {output_dir}")
    print(f"  2. Crop if needed: python3 crop_screenshots.py {output_dir} {SIZES[platform][0]} {SIZES[platform][1]}")

    return 0


if __name__ == "__main__":
    exit(main())
