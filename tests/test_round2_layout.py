import json
import re
import unittest
from functools import lru_cache

from test_pt2_layout import ROOT, png_size, rgba_pixels


class Round2LayoutTest(unittest.TestCase):
    def test_every_displayed_digit_clears_the_round_bezel(self):
        manifest = json.loads((ROOT / "package.json").read_text())["pebble"]
        self.assertIn("gabbro", manifest["targetPlatforms"])
        source = (ROOT / "src/main.c").read_text()
        layout = dict((name, int(value)) for name, value in
                      re.findall(r"ROUND2_(\w+) = (\d+)", source))
        width, height = layout["WIDTH"], layout["HEIGHT"]
        column_gap, row_gap = layout["COLUMN_GAP"], layout["ROW_GAP"]
        left = (260 - 2 * width - column_gap) // 2
        right = left + width + column_gap
        top = (260 - 2 * height - row_gap) // 2
        bottom = top + height + row_gap

        ink = {}
        for digit in range(10):
            resource = next(r for r in manifest["resources"]["media"] if r["name"] == f"DIGIT_{digit}")
            self.assertIn("gabbro", resource["targetPlatforms"])
            base = ROOT / "resources" / resource["file"]
            path = base.with_name(base.stem + "~gabbro.png")
            self.assertEqual(png_size(path), (width, height))
            pixels = rgba_pixels(path)
            ink[digit] = [(i % width, i // width) for i, pixel in enumerate(pixels) if pixel[3]]
            self.assertTrue(ink[digit])

        @lru_cache(maxsize=None)
        def check_digit(digit, x, y):
            # Use the farthest corner of each pixel, including faint antialiasing.
            for dx, dy in ink[digit]:
                px, py = x + dx - 130, y + dy - 130
                radius_squared = max(px * px, (px + 1) ** 2) + max(py * py, (py + 1) ** 2)
                self.assertLessEqual(radius_squared, (130 - 8) ** 2, (digit, x, y, dx, dy))

        for hour in range(24):
            for minute in range(60):
                for is_24h in (True, False):
                    shown = hour if is_24h else (hour % 12 or 12)
                    if is_24h or shown >= 10:
                        check_digit(shown // 10, left, top)
                    check_digit(shown % 10, right, top)
                    check_digit(minute // 10, left, bottom)
                    check_digit(minute % 10, right, bottom)
