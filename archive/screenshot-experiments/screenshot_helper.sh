#!/bin/bash
# Helper script for manual screenshot generation
# Usage: ./screenshot_helper.sh <platform> <hour> <minute> <24h> <name>
# Example: ./screenshot_helper.sh aplite 10 8 0 "10-08-12h"

set -e

PLATFORM=$1
HOUR=$2
MINUTE=$3
IS_24H=$4
NAME=$5

if [ -z "$PLATFORM" ] || [ -z "$HOUR" ] || [ -z "$MINUTE" ] || [ -z "$IS_24H" ] || [ -z "$NAME" ]; then
    echo "Usage: $0 <platform> <hour> <minute> <24h> <name>"
    echo "Example: $0 aplite 10 8 0 '10-08-12h'"
    exit 1
fi

PROJECT_DIR="/Users/danhart/Developer/pebble-superlegible-watchface"
SRC_FILE="$PROJECT_DIR/src/main.c"
OUTPUT_DIR="$PROJECT_DIR/store-assets/screenshots/$PLATFORM"

mkdir -p "$OUTPUT_DIR"

echo "=== Generating screenshot for $PLATFORM at $HOUR:$MINUTE ==="

# Update source code with screenshot mode
echo "Updating source code..."
sed -i.bak \
    -e "s|// #define SCREENSHOT_MODE|#define SCREENSHOT_MODE|" \
    -e "s|// #define SCREENSHOT_TIME_24H.*|#define SCREENSHOT_TIME_24H $IS_24H|" \
    -e "s|// #define SCREENSHOT_HOUR.*|#define SCREENSHOT_HOUR $HOUR|" \
    -e "s|// #define SCREENSHOT_MINUTE.*|#define SCREENSHOT_MINUTE $MINUTE|" \
    -e "s|#define SCREENSHOT_TIME_24H.*|#define SCREENSHOT_TIME_24H $IS_24H|" \
    -e "s|#define SCREENSHOT_HOUR.*|#define SCREENSHOT_HOUR $HOUR|" \
    -e "s|#define SCREENSHOT_MINUTE.*|#define SCREENSHOT_MINUTE $MINUTE|" \
    "$SRC_FILE"

# Build
echo "Building..."
cd "$PROJECT_DIR"
nix-shell --run "pebble build"

# Install
echo "Installing to $PLATFORM emulator..."
nix-shell --run "pebble install --emulator $PLATFORM"

# Wait for launch
echo "Waiting for app to launch..."
sleep 3

# Capture
echo "Capturing screenshot..."
peekaboo image --app "qemu-pebble" --path "$OUTPUT_DIR/${NAME}.png"

echo "✅ Screenshot saved to $OUTPUT_DIR/${NAME}.png"
echo ""
echo "Next: Open the screenshot and verify it looks correct"
echo "      open '$OUTPUT_DIR/${NAME}.png'"
