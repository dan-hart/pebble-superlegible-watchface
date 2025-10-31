#!/usr/bin/env python3
"""
Automated screenshot generation with verification and retry logic.
"""

import sys
import os
import subprocess
import time
import re
from pathlib import Path

PROJECT_DIR = Path("/Users/danhart/Developer/pebble-superlegible-watchface")
SRC_FILE = PROJECT_DIR / "src" / "main.c"
SCREENSHOTS_DIR = PROJECT_DIR / "store-assets" / "screenshots"

TIMES = [
    (10, 8, False, "10-08-12h"),
    (12, 0, False, "12-00-12h"),
    (3, 45, False, "03-45-12h"),
    (9, 41, False, "09-41-12h"),
    (23, 59, True, "23-59-24h"),
]


def kill_emulators():
    """Kill all running emulators."""
    subprocess.run(["killall", "qemu-pebble"], capture_output=True)
    time.sleep(2)


def update_screenshot_mode(hour, minute, is_24h, enabled=True):
    """Update screenshot mode in source code."""
    with open(SRC_FILE, 'r') as f:
        content = f.read()

    if enabled:
        content = re.sub(r'// #define SCREENSHOT_MODE', '#define SCREENSHOT_MODE', content)
        content = re.sub(r'(//\s*)?#define SCREENSHOT_TIME_24H \d+', f'#define SCREENSHOT_TIME_24H {1 if is_24h else 0}', content)
        content = re.sub(r'(//\s*)?#define SCREENSHOT_HOUR \d+', f'#define SCREENSHOT_HOUR {hour}', content)
        content = re.sub(r'(//\s*)?#define SCREENSHOT_MINUTE \d+', f'#define SCREENSHOT_MINUTE {minute}', content)
    else:
        content = re.sub(r'#define SCREENSHOT_MODE', '// #define SCREENSHOT_MODE', content)
        content = re.sub(r'#define SCREENSHOT_TIME_24H', '// #define SCREENSHOT_TIME_24H', content)
        content = re.sub(r'#define SCREENSHOT_HOUR', '// #define SCREENSHOT_HOUR', content)
        content = re.sub(r'#define SCREENSHOT_MINUTE', '// #define SCREENSHOT_MINUTE', content)

    with open(SRC_FILE, 'w') as f:
        f.write(content)


def clean_build():
    """Clean and build the project."""
    print("  Cleaning build...")
    subprocess.run(
        ["nix-shell", "--run", "pebble clean"],
        cwd=PROJECT_DIR,
        capture_output=True
    )

    print("  Building...")
    result = subprocess.run(
        ["nix-shell", "--run", "pebble build"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True
    )
    return result.returncode == 0


def install_to_emulator(platform):
    """Install to emulator."""
    print(f"  Installing to {platform}...")
    result = subprocess.run(
        ["nix-shell", "--run", f"pebble install --emulator {platform}"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True
    )
    return result.returncode == 0


def take_screenshot(platform, output_path):
    """Take screenshot using pebble command."""
    print("  Waiting for emulator to boot...")
    time.sleep(8)

    print("  Waiting 10 seconds after boot for watchface to fully render...")
    time.sleep(10)

    print("  Capturing screenshot with pebble screenshot command...")
    result = subprocess.run(
        ["nix-shell", "--run", f"pebble screenshot --emulator {platform} {output_path}"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True
    )

    return result.returncode == 0


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 screenshot_automated_fix.py <platform>")
        print("Platforms: aplite, basalt")
        return 1

    platform = sys.argv[1]
    if platform not in ["aplite", "basalt"]:
        print("Error: Only aplite and basalt supported")
        return 1

    print(f"\n{'='*60}")
    print(f"Fixing {platform} screenshots")
    print(f"{'='*60}\n")

    output_dir = SCREENSHOTS_DIR / platform
    output_dir.mkdir(parents=True, exist_ok=True)

    # Kill all emulators first
    kill_emulators()

    for hour, minute, is_24h, name in TIMES:
        print(f"\n--- {name} ({hour:02d}:{minute:02d} {'24h' if is_24h else '12h'}) ---")

        # Kill emulator before each screenshot
        kill_emulators()

        # Configure time
        print("  Configuring time...")
        update_screenshot_mode(hour, minute, is_24h, enabled=True)

        # Clean build
        if not clean_build():
            print("  ❌ Build failed")
            continue

        # Install
        if not install_to_emulator(platform):
            print("  ❌ Install failed")
            continue

        # Take screenshot
        output_path = output_dir / f"{name}.png"
        if take_screenshot(platform, output_path):
            print(f"  ✅ Saved: {output_path.name}")
        else:
            print(f"  ❌ Screenshot failed")

    # Restore source
    print("\n\nRestoring source code...")
    update_screenshot_mode(10, 8, False, enabled=False)

    # Final clean build
    print("Final clean build...")
    subprocess.run(
        ["nix-shell", "--run", "pebble build"],
        cwd=PROJECT_DIR,
        capture_output=True
    )

    print(f"\n{'='*60}")
    print(f"✅ Complete! Screenshots in: {output_dir}")
    print(f"{'='*60}\n")
    print(f"Next: Review screenshots and crop if needed")
    print(f"  open {output_dir}")
    print(f"  python3 crop_screenshots.py {output_dir} 144 168")

    return 0


if __name__ == "__main__":
    exit(main())
