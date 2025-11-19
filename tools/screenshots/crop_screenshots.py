#!/usr/bin/env python3
"""
Crop Pebble emulator screenshots to just the watch display.
Usage:
  python3 crop_screenshots.py <file.png> <width> <height>
  python3 crop_screenshots.py <directory> <width> <height>
"""

import sys
from pathlib import Path
from PIL import Image
import numpy as np


def find_watch_display(img_array, target_width, target_height):
    """
    Find the watch display (black rectangle) in the emulator screenshot.
    Returns (left, top, right, bottom) crop coordinates.
    """
    # Convert to grayscale for easier processing
    if len(img_array.shape) == 3:
        gray = np.mean(img_array, axis=2)
    else:
        gray = img_array

    # The watch display should be a contiguous dark region
    # Strategy: Center crop assuming display is roughly centered
    img_height, img_width = gray.shape

    # Calculate center crop
    left = (img_width - target_width) // 2
    top = (img_height - target_height) // 2
    right = left + target_width
    bottom = top + target_height

    # Ensure we don't go out of bounds
    if right > img_width or bottom > img_height:
        # Image is smaller than expected, try to find the best crop
        # Look for the darkest region
        min_left = max(0, (img_width - target_width) // 2 - 50)
        max_left = min(img_width - target_width, (img_width - target_width) // 2 + 50)
        min_top = max(0, (img_height - target_height) // 2 - 50)
        max_top = min(img_height - target_height, (img_height - target_height) // 2 + 50)

        darkest_score = float('inf')
        best_crop = (left, top, right, bottom)

        for test_left in range(min_left, max_left, 5):
            for test_top in range(min_top, max_top, 5):
                test_right = test_left + target_width
                test_bottom = test_top + target_height

                if test_right <= img_width and test_bottom <= img_height:
                    crop_region = gray[test_top:test_bottom, test_left:test_right]
                    score = np.mean(crop_region)

                    if score < darkest_score:
                        darkest_score = score
                        best_crop = (test_left, test_top, test_right, test_bottom)

        return best_crop

    return (left, top, right, bottom)


def crop_image(input_path, output_path, target_width, target_height):
    """Crop a single image to target dimensions."""
    try:
        img = Image.open(input_path)
        img_array = np.array(img)

        # Find the watch display
        left, top, right, bottom = find_watch_display(img_array, target_width, target_height)

        # Crop
        cropped = img.crop((left, top, right, bottom))

        # Verify dimensions
        if cropped.size != (target_width, target_height):
            print(f"    Warning: Cropped size {cropped.size} != target {(target_width, target_height)}")
            print(f"    Resizing to target dimensions...")
            cropped = cropped.resize((target_width, target_height), Image.Resampling.LANCZOS)

        # Save
        cropped.save(output_path)
        return True
    except Exception as e:
        print(f"    Error cropping {input_path}: {e}")
        return False


def main():
    if len(sys.argv) != 4:
        print("Usage:")
        print("  python3 crop_screenshots.py <file.png> <width> <height>")
        print("  python3 crop_screenshots.py <directory> <width> <height>")
        print("\nExamples:")
        print("  python3 crop_screenshots.py screenshot.png 144 168")
        print("  python3 crop_screenshots.py store-assets/screenshots/aplite/ 144 168")
        return 1

    input_path = Path(sys.argv[1])
    target_width = int(sys.argv[2])
    target_height = int(sys.argv[3])

    if not input_path.exists():
        print(f"Error: {input_path} does not exist")
        return 1

    # Process single file or directory
    if input_path.is_file():
        print(f"Cropping {input_path.name} to {target_width}×{target_height}...")
        success = crop_image(input_path, input_path, target_width, target_height)
        if success:
            print(f"✅ Cropped successfully")
            return 0
        else:
            return 1

    elif input_path.is_dir():
        print(f"Cropping all PNG files in {input_path} to {target_width}×{target_height}...\n")

        png_files = list(input_path.glob("*.png"))
        if not png_files:
            print(f"No PNG files found in {input_path}")
            return 1

        success_count = 0
        for png_file in png_files:
            print(f"Processing {png_file.name}...")
            if crop_image(png_file, png_file, target_width, target_height):
                success_count += 1
                print(f"  ✅ Cropped")
            else:
                print(f"  ❌ Failed")

        print(f"\n✅ Processed {success_count}/{len(png_files)} files")
        return 0

    else:
        print(f"Error: {input_path} is neither a file nor directory")
        return 1


if __name__ == "__main__":
    exit(main())
