"""Generate the native Round 2 bitmap variants with Pillow."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SCALE = 4
CELL = (80, 94)
font = ImageFont.truetype(ROOT / "resources/fonts/AtkinsonHyperlegibleMono-ExtraBold.ttf", 128 * SCALE)

# Draw on a shared baseline with space for the antialiasing filter on every side.
masks = []
for digit in range(10):
    mask = Image.new("L", (200 * SCALE, 200 * SCALE))
    ImageDraw.Draw(mask).text((100 * SCALE, 145 * SCALE), str(digit), font=font, anchor="ms", fill=255)
    masks.append(mask.resize((200, 200), Image.Resampling.LANCZOS))

boxes = [mask.getbbox() for mask in masks]
top = min(box[1] for box in boxes)
bottom = max(box[3] for box in boxes)
assert bottom - top <= CELL[1]
for digit, (mask, (left, _, right, _)) in enumerate(zip(masks, boxes)):
    ink = mask.crop((left, top, right, bottom))
    assert ink.width <= CELL[0]
    alpha = Image.new("L", CELL)
    alpha.paste(ink, ((CELL[0] - ink.width) // 2, (CELL[1] - ink.height) // 2))
    bitmap = Image.new("RGBA", CELL, "white")
    bitmap.putalpha(alpha)
    bitmap.save(ROOT / f"resources/images/digit_{digit}~gabbro.png")
