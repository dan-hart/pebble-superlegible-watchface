#!/usr/bin/env python3
"""
Screenshot capture with verification - only saves if screenshot looks valid.
"""

import subprocess
import time
import re
from pathlib import Path
import os

PROJECT_DIR = Path("/Users/danhart/Developer/pebble-superlegible-watchface")
SRC_FILE = PROJECT_DIR / "src" / "main.c"
OUTPUT_DIR = PROJECT_DIR / "store-assets" / "screenshots" / "aplite"

# All times needed
ALL_TIMES = [
    (10, 8, False, "10-08-12h"),
    (12, 0, False, "12-00-12h"),
    (3, 45, False, "03-45-12h"),
    (9, 41, False, "09-41-12h"),
    (23, 59, True, "23-59-24h"),
]


def update_time(hour, minute, is_24h):
    """Update screenshot mode in source."""
    with open(SRC_FILE, 'r') as f:
        content = f.read()

    content = re.sub(r'// #define SCREENSHOT_MODE', '#define SCREENSHOT_MODE', content)
    content = re.sub(r'(//\s*)?#define SCREENSHOT_TIME_24H \d+', f'#define SCREENSHOT_TIME_24H {1 if is_24h else 0}', content)
    content = re.sub(r'(//\s*)?#define SCREENSHOT_HOUR \d+', f'#define SCREENSHOT_HOUR {hour}', content)
    content = re.sub(r'(//\s*)?#define SCREENSHOT_MINUTE \d+', f'#define SCREENSHOT_MINUTE {minute}', content)

    with open(SRC_FILE, 'w') as f:
        f.write(content)


def disable_screenshot_mode():
    """Disable screenshot mode."""
    with open(SRC_FILE, 'r') as f:
        content = f.read()

    content = re.sub(r'#define SCREENSHOT_MODE', '// #define SCREENSHOT_MODE', content)
    content = re.sub(r'#define SCREENSHOT_TIME_24H', '// #define SCREENSHOT_TIME_24H', content)
    content = re.sub(r'#define SCREENSHOT_HOUR', '// #define SCREENSHOT_HOUR', content)
    content = re.sub(r'#define SCREENSHOT_MINUTE', '// #define SCREENSHOT_MINUTE', content)

    with open(SRC_FILE, 'w') as f:
        f.write(content)


def check_existing():
    """Check which screenshots already exist."""
    existing = []
    missing = []

    for hour, minute, is_24h, name in ALL_TIMES:
        output_path = OUTPUT_DIR / f"{name}.png"
        if output_path.exists() and output_path.stat().st_size > 500:
            existing.append(name)
        else:
            missing.append((hour, minute, is_24h, name))

    return existing, missing


def capture_one(hour, minute, is_24h, name, max_attempts=3):
    """Capture one screenshot with verification and retries."""
    output_path = OUTPUT_DIR / f"{name}.png"

    for attempt in range(1, max_attempts + 1):
        print(f"\n{'='*60}")
        print(f"Capturing: {name} (Attempt {attempt}/{max_attempts})")
        print(f"Time: {hour:02d}:{minute:02d} ({'24h' if is_24h else '12h'})")
        print(f"{'='*60}")

        # Kill emulators
        print("Killing existing emulators...")
        subprocess.run(["killall", "qemu-pebble"], capture_output=True)
        time.sleep(3)

        # Update time
        print("Configuring time in source code...")
        update_time(hour, minute, is_24h)

        # Clean and build
        print("Clean build...")
        subprocess.run(
            ["nix-shell", "--run", "pebble clean"],
            cwd=PROJECT_DIR,
            capture_output=True
        )

        result = subprocess.run(
            ["nix-shell", "--run", "pebble build"],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"  ❌ Build failed on attempt {attempt}")
            continue

        # Install
        print("Installing to aplite emulator...")
        result = subprocess.run(
            ["nix-shell", "--run", "pebble install --emulator aplite"],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"  ❌ Install failed on attempt {attempt}")
            continue

        # Wait for full boot and render
        print("Waiting for emulator to boot (8 seconds)...")
        time.sleep(8)

        print("Waiting for watchface to render (10 seconds)...")
        time.sleep(10)

        # Capture screenshot
        print(f"Capturing screenshot to {output_path.name}...")
        result = subprocess.run(
            ["nix-shell", "--run", f"pebble screenshot --emulator aplite {output_path}"],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True
        )

        # Verify screenshot
        if result.returncode == 0 and output_path.exists():
            file_size = output_path.stat().st_size

            if file_size > 500:  # Reasonable size check
                print(f"  ✅ Screenshot captured successfully ({file_size} bytes)")
                print(f"  ✅ VERIFIED: {name}")
                return True
            else:
                print(f"  ❌ Screenshot file too small ({file_size} bytes)")
        else:
            print(f"  ❌ Screenshot command failed on attempt {attempt}")

        if attempt < max_attempts:
            print(f"  Retrying in 5 seconds...")
            time.sleep(5)

    print(f"  ❌ Failed after {max_attempts} attempts")
    return False


def main():
    print("="*60)
    print("Verified Screenshot Capture for Aplite")
    print("="*60)

    # Check what we have
    existing, missing = check_existing()

    print(f"\n✅ Already have: {', '.join(existing) if existing else 'none'}")
    print(f"📸 Need to capture: {len(missing)} screenshots\n")

    if not missing:
        print("All screenshots already exist!")
        return 0

    # Capture missing ones
    successful = []
    failed = []

    for hour, minute, is_24h, name in missing:
        if capture_one(hour, minute, is_24h, name):
            successful.append(name)
        else:
            failed.append(name)

    # Restore source
    print("\n\nRestoring source code...")
    disable_screenshot_mode()

    # Final build
    print("Final clean build...")
    subprocess.run(
        ["nix-shell", "--run", "pebble build"],
        cwd=PROJECT_DIR,
        capture_output=True
    )

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"✅ Successful: {len(successful)} - {', '.join(successful)}")
    print(f"❌ Failed: {len(failed)} - {', '.join(failed)}")
    print(f"\nScreenshots saved to: {OUTPUT_DIR}")
    print(f"{'='*60}\n")

    # Open all screenshots for review
    if successful:
        print("Opening all screenshots for review...")
        subprocess.run(["open", str(OUTPUT_DIR)])

    return 0 if not failed else 1


if __name__ == "__main__":
    exit(main())
