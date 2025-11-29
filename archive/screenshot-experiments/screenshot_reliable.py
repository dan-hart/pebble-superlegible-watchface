#!/usr/bin/env python3
"""
Reliable screenshot capture with process polling and peekaboo.
"""

import subprocess
import time
import re
from pathlib import Path
import sys

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
    with open(SRC_FILE, 'w') as f:
        f.write(content)


def wait_for_emulator_process(max_wait=15):
    """Wait for qemu-pebble process to exist."""
    print(f"  Waiting for emulator process (max {max_wait}s)...")

    for i in range(max_wait):
        result = subprocess.run(["pgrep", "-x", "qemu-pebble"], capture_output=True)
        if result.returncode == 0:
            print(f"  ✅ Emulator process found after {i+1}s")
            return True
        time.sleep(1)

    print(f"  ❌ Emulator process not found after {max_wait}s")
    return False


def capture_with_peekaboo(output_path):
    """Capture screenshot using peekaboo."""
    result = subprocess.run(
        ["peekaboo", "image", "--app", "qemu-pebble", "--path", str(output_path)],
        capture_output=True,
        text=True
    )
    return result.returncode == 0


def manual_capture(hour, minute, output_path):
    """Manual capture with user confirmation."""
    print(f"\n  {'='*50}")
    print(f"  MANUAL MODE")
    print(f"  {'='*50}")
    print(f"  The emulator should be running now.")
    print(f"  Please look at the emulator and verify it shows: {hour:02d}:{minute:02d}")
    print(f"  ")
    input(f"  Press ENTER when you can see the correct time on screen...")

    print(f"  Capturing screenshot...")
    if capture_with_peekaboo(output_path):
        print(f"  ✅ Screenshot captured")
        subprocess.run(["open", str(output_path)])
        return True
    else:
        print(f"  ❌ Screenshot failed")
        return False


def capture_one(hour, minute, is_24h, name, max_attempts=2):
    """Capture one screenshot with automatic retry and manual fallback."""
    output_path = OUTPUT_DIR / f"{name}.png"

    # Check if already exists
    if output_path.exists() and output_path.stat().st_size > 1000:
        print(f"\n✅ Already have valid screenshot for {name}")
        return True

    for attempt in range(1, max_attempts + 1):
        print(f"\n{'='*60}")
        print(f"Capturing: {name} (Attempt {attempt}/{max_attempts})")
        print(f"Time: {hour:02d}:{minute:02d} ({'24h' if is_24h else '12h'})")
        print(f"{'='*60}")

        # Kill existing emulators
        print("Killing existing emulators...")
        subprocess.run(["killall", "qemu-pebble"], capture_output=True)
        time.sleep(3)

        # Update source
        print("Configuring time...")
        update_time(hour, minute, is_24h)

        # Clean build
        print("Building...")
        subprocess.run(["nix-shell", "--run", "pebble clean"], cwd=PROJECT_DIR, capture_output=True)
        result = subprocess.run(["nix-shell", "--run", "pebble build"], cwd=PROJECT_DIR, capture_output=True)

        if result.returncode != 0:
            print("  ❌ Build failed")
            continue

        # Install
        print("Installing to aplite...")
        result = subprocess.run(
            ["nix-shell", "--run", "pebble install --emulator aplite"],
            cwd=PROJECT_DIR,
            capture_output=True
        )

        if result.returncode != 0:
            print("  ❌ Install failed")
            continue

        # Wait for emulator process
        if not wait_for_emulator_process(max_wait=15):
            print("  ❌ Emulator didn't start")
            continue

        # Extended wait for rendering
        print("  Waiting for watchface to fully render (15 seconds)...")
        time.sleep(15)

        # Capture with peekaboo
        print(f"  Capturing with peekaboo...")
        if capture_with_peekaboo(output_path):
            # Verify capture
            if output_path.exists() and output_path.stat().st_size > 1000:
                print(f"  ✅ Screenshot captured successfully ({output_path.stat().st_size} bytes)")
                return True
            else:
                print(f"  ⚠️  Screenshot file too small or missing")
        else:
            print(f"  ❌ Peekaboo capture failed")

        # Clean up bad screenshot
        if output_path.exists():
            output_path.unlink()

    # All automatic attempts failed - try manual mode
    print(f"\n⚠️  Automatic capture failed after {max_attempts} attempts")
    print(f"Switching to MANUAL MODE...")

    # One more build/install for manual mode
    subprocess.run(["killall", "qemu-pebble"], capture_output=True)
    time.sleep(3)
    update_time(hour, minute, is_24h)
    subprocess.run(["nix-shell", "--run", "pebble clean && pebble build"], cwd=PROJECT_DIR, capture_output=True)
    subprocess.run(["nix-shell", "--run", "pebble install --emulator aplite"], cwd=PROJECT_DIR, capture_output=True)

    if wait_for_emulator_process(max_wait=20):
        time.sleep(5)  # Short wait for initial render
        return manual_capture(hour, minute, output_path)
    else:
        print(f"  ❌ Emulator failed to start for manual capture")
        return False


def main():
    print("="*60)
    print("Reliable Screenshot Capture for Aplite")
    print("="*60)
    print("Strategy: Peekaboo + Process Polling + Manual Fallback")
    print("="*60)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    successful = []
    failed = []

    for hour, minute, is_24h, name in ALL_TIMES:
        if capture_one(hour, minute, is_24h, name):
            successful.append(name)
        else:
            failed.append(name)

    # Restore source
    print("\n\nRestoring source code...")
    disable_screenshot_mode()
    subprocess.run(["nix-shell", "--run", "pebble build"], cwd=PROJECT_DIR, capture_output=True)

    # Kill emulators
    subprocess.run(["killall", "qemu-pebble"], capture_output=True)

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"✅ Successful: {len(successful)} - {', '.join(successful)}")
    print(f"❌ Failed: {len(failed)} - {', '.join(failed) if failed else 'none'}")
    print(f"\nScreenshots: {OUTPUT_DIR}")
    print(f"{'='*60}\n")

    if successful:
        print("Opening screenshots folder...")
        subprocess.run(["open", str(OUTPUT_DIR)])

    return 0 if not failed else 1


if __name__ == "__main__":
    exit(main())
