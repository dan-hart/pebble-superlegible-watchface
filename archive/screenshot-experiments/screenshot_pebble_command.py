#!/usr/bin/env python3
"""
Screenshot capture using pebble screenshot command (no window chrome).
"""

import subprocess
import time
import re
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent
SRC_FILE = PROJECT_DIR / "src" / "main.c"
OUTPUT_DIR = PROJECT_DIR / "store-assets" / "screenshots" / "aplite"

ALL_TIMES = [
    (10, 8, False, "10-08-12h"),
    (12, 0, False, "12-00-12h"),
    (3, 45, False, "03-45-12h"),
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


def disable_screenshot_mode():
    with open(SRC_FILE, 'r') as f:
        content = f.read()
    content = re.sub(r'#define SCREENSHOT_MODE', '// #define SCREENSHOT_MODE', content)
    with open(SRC_FILE, 'w') as f:
        f.write(content)


def wait_for_process():
    print("  Waiting for emulator process...")
    for i in range(20):
        result = subprocess.run(["pgrep", "-x", "qemu-pebble"], capture_output=True)
        if result.returncode == 0:
            print(f"  ✅ Process found after {i+1}s")
            return True
        time.sleep(1)
    return False


def capture_one(hour, minute, is_24h, name):
    output_path = OUTPUT_DIR / f"{name}.png"

    print(f"\n{'='*60}")
    print(f"{name}: {hour:02d}:{minute:02d} ({'24h' if is_24h else '12h'})")
    print(f"{'='*60}")

    # Kill emulators
    subprocess.run(["killall", "qemu-pebble"], capture_output=True)
    time.sleep(3)

    # Update source
    update_time(hour, minute, is_24h)

    # Clean build
    print("Building...")
    subprocess.run(["nix-shell", "--run", "pebble clean"], cwd=PROJECT_DIR, capture_output=True)
    subprocess.run(["nix-shell", "--run", "pebble build"], cwd=PROJECT_DIR, capture_output=True)

    # Install
    print("Installing...")
    subprocess.run(["nix-shell", "--run", "pebble install --emulator aplite"], cwd=PROJECT_DIR, capture_output=True)

    # Wait for process
    if not wait_for_process():
        print("  ❌ Emulator didn't start")
        return False

    # Wait for render
    print("  Waiting 15 seconds for rendering...")
    time.sleep(15)

    # Capture with pebble screenshot (no chrome)
    print(f"  Capturing with pebble screenshot command...")
    result = subprocess.run(
        ["nix-shell", "--run", f"pebble screenshot --emulator aplite {output_path}"],
        cwd=PROJECT_DIR,
        capture_output=True
    )

    if result.returncode == 0 and output_path.exists():
        size = output_path.stat().st_size
        print(f"  ✅ Captured ({size} bytes)")
        return True
    else:
        print(f"  ❌ Failed")
        return False


def main():
    print("="*60)
    print("Aplite Screenshot Capture (Pebble Command - No Chrome)")
    print("="*60)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    successful = []
    failed = []

    for hour, minute, is_24h, name in ALL_TIMES:
        if capture_one(hour, minute, is_24h, name):
            successful.append(name)
        else:
            failed.append(name)

    # Restore
    print("\n\nRestoring source...")
    disable_screenshot_mode()
    subprocess.run(["nix-shell", "--run", "pebble build"], cwd=PROJECT_DIR, capture_output=True)
    subprocess.run(["killall", "qemu-pebble"], capture_output=True)

    # Summary
    print(f"\n{'='*60}")
    print(f"✅ Success: {len(successful)} - {', '.join(successful)}")
    print(f"❌ Failed: {len(failed)} - {', '.join(failed) if failed else 'none'}")
    print(f"{'='*60}\n")

    subprocess.run(["open", str(OUTPUT_DIR)])
    return 0 if not failed else 1


if __name__ == "__main__":
    exit(main())
