#!/usr/bin/env python3
"""Capture the two missing screenshots."""

import subprocess
import time
import re
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent
SRC_FILE = PROJECT_DIR / "src" / "main.c"
OUTPUT_DIR = PROJECT_DIR / "store-assets" / "screenshots" / "aplite"

MISSING = [
    (10, 8, False, "10-08-12h"),
    (12, 0, False, "12-00-12h"),
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
    for attempt in range(3):
        print(f"\n{name} - Attempt {attempt + 1}/3")

        # Kill and wait
        subprocess.run(["killall", "qemu-pebble"], capture_output=True)
        time.sleep(3)

        # Configure
        update_time(hour, minute, is_24h)

        # Build
        subprocess.run(["nix-shell", "--run", "pebble clean && pebble build"], cwd=PROJECT_DIR, capture_output=True)

        # Install
        subprocess.run(["nix-shell", "--run", "pebble install --emulator aplite"], cwd=PROJECT_DIR, capture_output=True)

        # Wait
        time.sleep(18)

        # Capture
        output = OUTPUT_DIR / f"{name}.png"
        result = subprocess.run(
            ["nix-shell", "--run", f"pebble screenshot --emulator aplite {output}"],
            cwd=PROJECT_DIR,
            capture_output=True
        )

        if result.returncode == 0 and output.exists():
            print(f"  ✅ Success!")
            break
        else:
            print(f"  ❌ Failed, retrying...")

# Restore
with open(SRC_FILE, 'r') as f:
    content = f.read()
content = re.sub(r'#define SCREENSHOT_MODE', '// #define SCREENSHOT_MODE', content)
with open(SRC_FILE, 'w') as f:
    f.write(content)

print("\nDone! Check screenshots:")
subprocess.run(["open", str(OUTPUT_DIR)])
