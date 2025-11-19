# Development Tools

This directory contains utilities for developing and maintaining the Superlegible watchface.

## Directory Structure

```
tools/
├── screenshots/    # Screenshot generation and processing
│   ├── generate_screenshots_programmatic.py
│   └── crop_screenshots.py
└── banner/         # Store banner generation
    └── generate_banner.py
```

## Screenshot Tools

### generate_screenshots_programmatic.py

**Purpose**: Automatically generate all required screenshots for the Pebble App Store.

**What it does**:
- Launches Pebble emulators for each platform (Aplite, Basalt, Chalk, Diorite, Emery)
- Sets time to display all digits clearly
- Captures screenshots programmatically
- Saves to `store-assets/screenshots/[platform]/`

**Usage**:
```bash
# Generate screenshots for all platforms
python3 tools/screenshots/generate_screenshots_programmatic.py

# Requirements:
# - Pebble SDK installed and in PATH
# - Emulators configured
# - Built .pbw file in build/
```

**When to use**:
- Before submitting to App Store
- After visual changes to the watchface
- To ensure consistent screenshots across platforms

### crop_screenshots.py

**Purpose**: Crop and resize screenshots to exact dimensions.

**What it does**:
- Crops screenshots to remove emulator chrome
- Resizes to match platform display dimensions
- Maintains aspect ratio
- Supports batch processing

**Usage**:
```bash
# Crop all screenshots in a directory
python3 tools/screenshots/crop_screenshots.py <directory> <width> <height>

# Example: Crop Basalt screenshots to 144x168
python3 tools/screenshots/crop_screenshots.py \
  store-assets/screenshots/basalt/ 144 168
```

**When to use**:
- After manual screenshot capture
- When screenshots include emulator UI elements
- To standardize screenshot dimensions

## Banner Tool

### generate_banner.py

**Purpose**: Generate the App Store banner image.

**What it does**:
- Creates 1024x1024 banner with watchface preview
- Adds title and branding
- Uses consistent styling
- Exports high-quality PNG

**Usage**:
```bash
# Generate store banner
python3 tools/banner/generate_banner.py

# Output: store-assets/banner.png
```

**When to use**:
- Before App Store submission
- After branding changes
- To update marketing materials

## Archived Tools

The `archive/screenshot-experiments/` directory contains experimental scripts developed during the project. These are kept for reference but are not intended for regular use:

- Various screenshot automation attempts
- Manual capture helpers
- Platform-specific experiments
- QEMU emulator cropping scripts

**Note**: Use the tools in `tools/` instead, as they represent the refined, working versions.

## Development Workflow

### Creating Store Assets

1. **Build the watchface**:
   ```bash
   pebble build
   ```

2. **Generate screenshots**:
   ```bash
   python3 tools/screenshots/generate_screenshots_programmatic.py
   ```

3. **Crop if needed**:
   ```bash
   python3 tools/screenshots/crop_screenshots.py \
     store-assets/screenshots/basalt/ 144 168
   ```

4. **Generate banner**:
   ```bash
   python3 tools/banner/generate_banner.py
   ```

5. **Review assets**:
   ```bash
   ls -la store-assets/screenshots/*/
   open store-assets/banner.png
   ```

### Adding New Tools

When adding new development utilities:

1. Choose appropriate subdirectory (`screenshots/`, `banner/`, or create new)
2. Add clear comments and usage instructions in the script
3. Update this README with:
   - Purpose of the tool
   - How to use it
   - When to use it
4. Add executable permissions: `chmod +x tools/[dir]/[script].py`
5. Test thoroughly before committing

## Tool Requirements

All tools assume:
- Python 3.6+
- Pebble SDK installed (for screenshot tools)
- Built watchface in `build/` directory
- Appropriate Python packages (PIL/Pillow, pyautogui for screenshot tools)

Install Python dependencies:
```bash
pip3 install pillow pyautogui
```

## Troubleshooting

### Screenshots Not Generating

- Ensure Pebble SDK is in PATH: `which pebble`
- Check emulators are working: `pebble install --emulator basalt`
- Verify build exists: `ls build/*.pbw`

### Cropping Not Working

- Install Pillow: `pip3 install pillow`
- Check input directory exists and contains images
- Verify dimensions match platform specs

### Banner Generation Fails

- Check Design/ directory for source files
- Install required image libraries
- Verify output directory is writable

---

**For more information**, see:
- Main README: `../README.md`
- Screenshot Guide: `../SCREENSHOT_GUIDE.md`
- App Store Checklist: `../store-assets/RELEASE_CHECKLIST.md`
