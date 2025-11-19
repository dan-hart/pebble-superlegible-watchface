#!/usr/bin/env python3
"""
Aggressive cropping to remove QEMU window chrome and extract only the display.
"""

from PIL import Image
import numpy as np
from pathlib import Path
import sys


def find_display_bounds(img_array):
    """
    Find the actual black display within QEMU window chrome.
    The display is the darkest rectangular region.
    """
    # Convert to grayscale
    if len(img_array.shape) == 3:
        gray = np.mean(img_array, axis=2)
    else:
        gray = img_array

    height, width = gray.shape

    # Find dark regions (display is typically dark/black)
    # Threshold to find very dark pixels
    threshold = 50
    dark_mask = gray < threshold

    # Find rows and columns with significant dark content
    row_darkness = np.sum(dark_mask, axis=1)
    col_darkness = np.sum(dark_mask, axis=0)

    # Find the boundaries of the dark region
    dark_rows = np.where(row_darkness > width * 0.3)[0]
    dark_cols = np.where(col_darkness > height * 0.3)[0]

    if len(dark_rows) == 0 or len(dark_cols) == 0:
        # Fallback to center crop
        return None

    top = dark_rows[0]
    bottom = dark_rows[-1]
    left = dark_cols[0]
    right = dark_cols[-1]

    return (left, top, right, bottom)


def crop_to_exact_display(img, target_width, target_height):
    """
    Crop image to exact display dimensions, removing all chrome.
    """
    img_array = np.array(img)

    # Find the display bounds
    bounds = find_display_bounds(img_array)

    if bounds is None:
        # Fallback: center crop
        width, height = img.size
        left = (width - target_width) // 2
        top = (height - target_height) // 2
        right = left + target_width
        bottom = top + target_height
    else:
        left, top, right, bottom = bounds

        # Calculate current dimensions
        current_width = right - left
        current_height = bottom - top

        # Adjust to match target aspect ratio
        target_aspect = target_width / target_height
        current_aspect = current_width / current_height

        if current_aspect > target_aspect:
            # Too wide, crop sides
            new_width = int(current_height * target_aspect)
            shrink = (current_width - new_width) // 2
            left += shrink
            right -= shrink
        else:
            # Too tall, crop top/bottom
            new_height = int(current_width / target_aspect)
            shrink = (current_height - new_height) // 2
            top += shrink
            bottom -= shrink

    # Crop
    cropped = img.crop((left, top, right, bottom))

    # Resize to exact target dimensions if needed
    if cropped.size != (target_width, target_height):
        cropped = cropped.resize((target_width, target_height), Image.Resampling.LANCZOS)

    return cropped


def process_screenshots(input_dir, target_width, target_height):
    """Process all screenshots in directory."""
    input_path = Path(input_dir)

    if not input_path.exists():
        print(f"Error: {input_path} does not exist")
        return False

    png_files = list(input_path.glob("*.png"))
    if not png_files:
        print(f"No PNG files found in {input_path}")
        return False

    print(f"Aggressively cropping {len(png_files)} screenshots to {target_width}×{target_height}...")
    print("Removing QEMU window chrome...\n")

    success_count = 0
    for png_file in png_files:
        print(f"Processing {png_file.name}...")

        try:
            img = Image.open(png_file)
            cropped = crop_to_exact_display(img, target_width, target_height)

            # Save
            cropped.save(png_file)

            print(f"  ✅ Cropped to {cropped.size[0]}×{cropped.size[1]}")
            success_count += 1

        except Exception as e:
            print(f"  ❌ Failed: {e}")

    print(f"\n✅ Successfully processed {success_count}/{len(png_files)} files")
    return success_count == len(png_files)


def main():
    if len(sys.argv) != 4:
        print("Usage: python3 crop_qemu_chrome.py <directory> <width> <height>")
        print("Example: python3 crop_qemu_chrome.py store-assets/screenshots/aplite/ 144 168")
        return 1

    input_dir = sys.argv[1]
    target_width = int(sys.argv[2])
    target_height = int(sys.argv[3])

    if process_screenshots(input_dir, target_width, target_height):
        return 0
    else:
        return 1


if __name__ == "__main__":
    exit(main())
