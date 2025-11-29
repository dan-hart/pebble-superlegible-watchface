#!/usr/bin/env python3
"""Capture only missing screenshots for aplite."""

import subprocess
import time
import re
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent
SRC_FILE = PROJECT_DIR / "src" / "main.c"
OUTPUT_DIR = PROJECT_DIR / "store-assets" / "screenshots" / "aplite"

# Missing screenshots
MISSING = [
    (12, 0, False, "12-00-12h"),
    (9, 41, False, "09-41-12h"),
    (23, 59, True, "23-59-24h"),
]


def update_time(hour, minute, is_24h):
    with open(SRC_FILE, 'r') as f:
        content = f.read()

    content = re.sub(r'// #define SCREENSHOT_MODE', '#define SCREENSHOT_MODE', content)
    content = re.sub(r'(//\s*)?#define SCREENSHOT_TIME_24H \d+', f'#define SCREENSHOT_TIME_24H {1 if is_24h else 0}', content)
    content = re.sub(r'(//\s*)?#define SCREENSHOT_HOUR \d+', f'#define SCREENSHOT_HOUR {hour}', content)
    content = re.sub(r'(//\s*)?#define SCREENSHOT_MINUTE \d+', f'#define SCREENSHOT_MINUTE {minute}', content)

    with open(SRC_FILE, 'w') as f:
        f.write(content)


for hour, minute, is_24h, name in MISSING:
    print(f"\n{'='*50}")
    print(f"Capturing: {name}")
    print(f"{'='*50}")

    # Kill emulators
    subprocess.run(["killall", "qemu-pebble"], capture_output=True)
    time.sleep(3)

    # Update time
    update_time(hour, minute, is_24h)

    # Clean and build
    print("Building...")
    subprocess.run(["nix-shell", "--run", "pebble clean && pebble build"], cwd=PROJECT_DIR, capture_output=True)

    # Install
    print("Installing...")
    subprocess.run(["nix-shell", "--run", "pebble install --emulator aplite"], cwd=PROJECT_DIR, capture_output=True)

    # Wait
    print("Waiting 18 seconds total...")
    time.sleep(18)

    # Screenshot
    output = OUTPUT_DIR / f"{name}.png"
    print(f"Capturing to {output.name}...")
    result = subprocess.run(
        ["nix-shell", "--run", f"pebble screenshot --emulator aplite {output}"],
        cwd=PROJECT_DIR,
        capture_output=True
    )

    if result.returncode == 0:
        print(f"✅ Success!")
    else:
        print(f"❌ Failed")

# Restore
print("\nRestoring source...")
with open(SRC_FILE, 'r') as f:
    content = f.read()
content = re.sub(r'#define SCREENSHOT_MODE', '// #define SCREENSHOT_MODE', content)
with open(SRC_FILE, 'w') as f:
    f.write(content)

print("\n✅ Done! Check screenshots:")
print(f"open {OUTPUT_DIR}")
