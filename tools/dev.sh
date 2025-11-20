#!/bin/bash
# Pebble development automation script
set -e

PLATFORM="${1:-basalt}"
ACTION="${2:-run}"

cd ~/Developer/pebble-superlegible-watchface

echo "🔨 Building watchface..."
pebble clean
pebble build

if [ "$ACTION" = "run" ] || [ "$ACTION" = "screenshot" ]; then
  echo "🚀 Installing to $PLATFORM emulator..."
  pebble kill 2>/dev/null || true
  sleep 1
  pebble install --emulator "$PLATFORM"
fi

if [ "$ACTION" = "screenshot" ]; then
  echo "⏳ Waiting for emulator to render..."
  sleep 3
  
  mkdir -p screenshots
  TIMESTAMP=$(date +%Y%m%d_%H%M%S)
  SCREENSHOT_PATH="screenshots/${PLATFORM}_${TIMESTAMP}.png"
  
  echo "📸 Capturing screenshot..."
  peekaboo image --app "qemu-pebble" --path "$SCREENSHOT_PATH"
  
  echo "✅ Screenshot saved: $SCREENSHOT_PATH"
  open "$SCREENSHOT_PATH"
fi

echo "✅ Done! Run 'pebble kill' to stop emulator"
