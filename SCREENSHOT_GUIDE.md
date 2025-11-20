# Screenshot Generation Guide

This guide explains how to generate the 25 screenshots needed for the Pebble store (5 platforms × 5 times).

## Platforms to Test

1. **aplite** - Pebble (B&W) - 144×168
2. **basalt** - Pebble Time (Color) - 144×168
3. **chalk** - Pebble Time Round (Color, Round) - 180×180
4. **diorite** - Pebble 2 (B&W) - 144×168
5. **emery** - Pebble Time 2 (Color) - 200×228

## Times to Capture

For each platform, capture these 5 times:

1. **10:08 (12h)** - Good digit variety, leading 1
2. **12:00 (12h)** - Classic noon time
3. **3:45 (12h)** - Unique digit combination
4. **9:41 (12h)** - Apple signature marketing time
5. **23:59 (24h)** - Demonstrates 24-hour format

## Method 1: Automated (Per Platform)

If basalt is problematic, skip it and do the others:

```bash
cd ~/Developer/pebble-superlegible-watchface

# Do each platform one at a time
python3 screenshot_one_platform.py aplite
python3 screenshot_one_platform.py chalk
python3 screenshot_one_platform.py diorite
python3 screenshot_one_platform.py emery

# Skip basalt if it's not working
# python3 screenshot_one_platform.py basalt
```

## Method 2: Manual (Most Reliable)

For problematic platforms or more control:

### Step 1: Configure Time

Edit `src/main.c` and uncomment the screenshot mode section:

```c
// Change from:
// #define SCREENSHOT_MODE
// #define SCREENSHOT_TIME_24H 0
// #define SCREENSHOT_HOUR 10
// #define SCREENSHOT_MINUTE 8

// To (for 10:08 AM):
#define SCREENSHOT_MODE
#define SCREENSHOT_TIME_24H 0
#define SCREENSHOT_HOUR 10
#define SCREENSHOT_MINUTE 8
```

### Step 2: Build and Deploy

```bash
cd ~/Developer/pebble-superlegible-watchface
pebble build && pebble install --emulator aplite
```

### Step 3: Screenshot

Wait 2-3 seconds for the emulator to launch, then:

```bash
sleep 2
peekaboo image --app "qemu-pebble" --path "store-assets/screenshots/aplite/10-08-12h.png"
```

### Step 4: Verify and Crop

```bash
open store-assets/screenshots/aplite/10-08-12h.png
```

If it looks good, crop it:

```bash
python3 crop_screenshots.py store-assets/screenshots/aplite/10-08-12h.png 144 168
```

### Step 5: Repeat

Repeat for each time, then for each platform.

## Method 3: Use Existing Pebble Screenshot Tool

If emulators are being difficult, you can also use the built-in Pebble screenshot command:

```bash
pebble screenshot --emulator aplite store-assets/screenshots/aplite/10-08-12h.png
```

This might be more reliable than peekaboo for capturing emulators.

## Cropping Screenshots

After capturing, screenshots may include emulator chrome. Crop to just the display:

```bash
# Crop single file
python3 crop_screenshots.py <input.png> <width> <height>

# Crop entire platform directory
python3 crop_screenshots.py store-assets/screenshots/aplite/ 144 168
```

Display sizes:
- aplite, basalt, diorite: 144×168
- chalk: 180×180
- emery: 200×228

## Troubleshooting

### Multiple emulator instances

If peekaboo captures the wrong window:

1. Close all emulator instances: `killall qemu-pebble`
2. Launch only the one you need
3. Verify with: `peekaboo list windows --app "qemu-pebble"`

### Basalt emulator issues

If basalt emulator is crashing or hanging:

1. Try `pebble kill` to stop all emulators
2. Try launching from Pebble Tool directly
3. As last resort, skip basalt and use aplite screenshots (same display size)

### Screenshot is blank

Increase the sleep delay:

```bash
sleep 5  # Wait longer for app to render
peekaboo image --app "qemu-pebble" --path output.png
```

## Quick Reference

Times configuration:

```
10:08 AM  → HOUR=10, MINUTE=8,  24H=0
12:00 PM  → HOUR=12, MINUTE=0,  24H=0
3:45 PM   → HOUR=3,  MINUTE=45, 24H=0
9:41 AM   → HOUR=9,  MINUTE=41, 24H=0
23:59     → HOUR=23, MINUTE=59, 24H=1
```

## Final Steps

Once all screenshots are captured and cropped:

1. Verify you have 25 screenshots (5 per platform)
2. Run the organization script: `python3 organize_screenshots.py`
3. Review all images: `open store-assets/screenshots/*/`
