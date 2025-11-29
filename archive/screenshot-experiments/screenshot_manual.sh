#!/bin/bash
# Manual screenshot capture with verification
# Usage: ./screenshot_manual.sh <platform> <hour> <minute> <is_24h> <name>

set -e

if [ $# -ne 5 ]; then
    echo "Usage: $0 <platform> <hour> <minute> <is_24h> <name>"
    echo "Example: $0 aplite 10 8 0 '10-08-12h'"
    exit 1
fi

PLATFORM=$1
HOUR=$2
MINUTE=$3
IS_24H=$4
NAME=$5

PROJECT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
OUTPUT_DIR="$PROJECT_DIR/store-assets/screenshots/$PLATFORM"
SRC_FILE="$PROJECT_DIR/src/main.c"

mkdir -p "$OUTPUT_DIR"

echo "=========================================="
echo "Manual Screenshot: $PLATFORM at $HOUR:$MINUTE"
echo "=========================================="

# Kill existing emulators
echo "Killing any existing emulators..."
killall qemu-pebble 2>/dev/null || true
sleep 2

# Update source code
echo "Enabling screenshot mode..."
sed -i.bak \
    -e 's|// #define SCREENSHOT_MODE|#define SCREENSHOT_MODE|' \
    -e "s|.*#define SCREENSHOT_TIME_24H.*|#define SCREENSHOT_TIME_24H $IS_24H|" \
    -e "s|.*#define SCREENSHOT_HOUR.*|#define SCREENSHOT_HOUR $HOUR|" \
    -e "s|.*#define SCREENSHOT_MINUTE.*|#define SCREENSHOT_MINUTE $MINUTE|" \
    "$SRC_FILE"

# Build
echo "Building..."
cd "$PROJECT_DIR"
nix-shell --run "pebble build"

# Clean build if needed
echo "Cleaning and rebuilding..."
nix-shell --run "pebble clean && pebble build"

# Install
echo "Installing to $PLATFORM emulator..."
nix-shell --run "pebble install --emulator $PLATFORM"

# Wait for emulator to fully start
echo "Waiting 10 seconds for emulator to fully load..."
sleep 10

# Verify emulator is running
if ! pgrep -x "qemu-pebble" > /dev/null; then
    echo "ERROR: Emulator not running!"
    exit 1
fi

echo "Emulator is running. Press ENTER when you can see the time is correct on screen..."
read

# Take screenshot using pebble command
echo "Capturing screenshot..."
OUTPUT_FILE="$OUTPUT_DIR/${NAME}.png"
nix-shell --run "pebble screenshot --emulator $PLATFORM $OUTPUT_FILE"

if [ -f "$OUTPUT_FILE" ]; then
    echo "✅ Screenshot saved: $OUTPUT_FILE"
    echo "Opening for verification..."
    open "$OUTPUT_FILE"
else
    echo "❌ Screenshot failed!"
    exit 1
fi

# Restore source
echo "Restoring source code..."
sed -i.bak \
    -e 's|#define SCREENSHOT_MODE|// #define SCREENSHOT_MODE|' \
    -e 's|#define SCREENSHOT_TIME_24H|// #define SCREENSHOT_TIME_24H|' \
    -e 's|#define SCREENSHOT_HOUR|// #define SCREENSHOT_HOUR|' \
    -e 's|#define SCREENSHOT_MINUTE|// #define SCREENSHOT_MINUTE|' \
    "$SRC_FILE"

echo ""
echo "✅ Done! Review the screenshot and run again if needed."
