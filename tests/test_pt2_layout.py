import json
import struct
import unittest
import zlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STANDARD_PLATFORMS = ["aplite", "basalt", "chalk", "diorite"]
EMERY_PADDING = 10
EMERY_DIGIT_SIZE = (90, 104)
EMERY_BACKGROUND_COLOR = "GColorFromHEX(0x000055)"
EMERY_DIGIT_COLOR = (255, 85, 0)


def png_size(path):
    with path.open("rb") as file:
        header = file.read(24)
    if header[:8] != b"\x89PNG\r\n\x1a\n":
        raise AssertionError(f"{path} is not a PNG")
    return struct.unpack(">II", header[16:24])


def rgba_pixels(path):
    data = path.read_bytes()
    width, height = struct.unpack(">II", data[16:24])
    offset = 8
    chunks = []
    color_type = None

    while offset < len(data):
        length = struct.unpack(">I", data[offset:offset + 4])[0]
        chunk_type = data[offset + 4:offset + 8]
        chunk_data = data[offset + 8:offset + 8 + length]

        if chunk_type == b"IHDR":
            color_type = chunk_data[9]
        elif chunk_type == b"IDAT":
            chunks.append(chunk_data)
        elif chunk_type == b"IEND":
            break

        offset += length + 12

    if color_type != 6:
        raise AssertionError(f"{path} is not an RGBA PNG")

    raw = zlib.decompress(b"".join(chunks))
    stride = width * 4
    previous = bytearray(stride)
    pixels = []

    for row in range(height):
        start = row * (stride + 1)
        filter_type = raw[start]
        scanline = bytearray(raw[start + 1:start + 1 + stride])

        if filter_type == 1:
            for i in range(stride):
                scanline[i] = (scanline[i] + (scanline[i - 4] if i >= 4 else 0)) & 0xFF
        elif filter_type == 2:
            for i in range(stride):
                scanline[i] = (scanline[i] + previous[i]) & 0xFF
        elif filter_type == 3:
            for i in range(stride):
                left = scanline[i - 4] if i >= 4 else 0
                scanline[i] = (scanline[i] + ((left + previous[i]) // 2)) & 0xFF
        elif filter_type == 4:
            for i in range(stride):
                left = scanline[i - 4] if i >= 4 else 0
                up = previous[i]
                upper_left = previous[i - 4] if i >= 4 else 0
                predictor = left + up - upper_left
                distances = (
                    abs(predictor - left),
                    abs(predictor - up),
                    abs(predictor - upper_left),
                )
                paeth = (left, up, upper_left)[distances.index(min(distances))]
                scanline[i] = (scanline[i] + paeth) & 0xFF
        elif filter_type != 0:
            raise AssertionError(f"Unsupported PNG filter {filter_type} in {path}")

        for i in range(0, stride, 4):
            pixels.append(tuple(scanline[i:i + 4]))
        previous = scanline

    return pixels


class PebbleTime2LayoutTest(unittest.TestCase):
    def setUp(self):
        with (ROOT / "package.json").open() as file:
            self.appinfo = json.load(file)["pebble"]
        self.media = {
            resource["name"]: resource
            for resource in self.appinfo["resources"]["media"]
        }
        self.source = (ROOT / "src" / "main.c").read_text()

    def test_emery_uses_padded_digit_bitmaps(self):
        for digit in range(10):
            resource = self.media[f"DIGIT_EMERY_{digit}"]
            self.assertEqual(resource["type"], "bitmap")
            self.assertEqual(resource["targetPlatforms"], ["emery"])

            image_path = ROOT / "resources" / resource["file"]
            self.assertEqual(png_size(image_path), EMERY_DIGIT_SIZE)

    def test_standard_digit_bitmaps_are_not_bundled_for_emery(self):
        for digit in range(10):
            resource = self.media[f"DIGIT_{digit}"]
            self.assertEqual(resource["targetPlatforms"], STANDARD_PLATFORMS)

    def test_main_selects_emery_resources_and_padded_layers(self):
        self.assertIn("#ifdef PBL_PLATFORM_EMERY", self.source)
        self.assertIn("RESOURCE_ID_DIGIT_EMERY_0", self.source)
        self.assertIn("RESOURCE_ID_DIGIT_0", self.source)
        self.assertIn(f"int16_t padding = {EMERY_PADDING};", self.source)
        self.assertIn("GRect(padding, padding, adjusted_width, adjusted_height)", self.source)
        self.assertIn(
            "GRect(padding + adjusted_width, padding + adjusted_height, adjusted_width, adjusted_height)",
            self.source,
        )

    def test_emery_uses_navy_background_and_neon_orange_digits(self):
        self.assertIn(EMERY_BACKGROUND_COLOR, self.source)
        self.assertIn("GColorBlack", self.source)

        for digit in range(10):
            resource = self.media[f"DIGIT_EMERY_{digit}"]
            image_path = ROOT / "resources" / resource["file"]
            visible_colors = {
                pixel[:3]
                for pixel in rgba_pixels(image_path)
                if pixel[3] > 0
            }
            self.assertEqual(visible_colors, {EMERY_DIGIT_COLOR})


if __name__ == "__main__":
    unittest.main()
