# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Alex Mollard
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

import numpy as np
from PIL import Image
import resvg_py

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import pipeline
from convert import convert_png, to_svg
from build import check, load_catalogue


class ConversionTest(unittest.TestCase):
    def test_svg_preserves_geometry_translation_holes_and_accessible_title(self):
        drawing = 'M10 10L90 10L90 90L10 90ZM30 30L70 30L70 70L30 70Z'
        paths = pipeline.write_paths((0, 0, 100, 100), [(2, 3)], [drawing])
        svg = to_svg(paths, 'Push & Pull <exercise>')
        root = ET.fromstring(svg)
        path = root.find('{http://www.w3.org/2000/svg}path')
        self.assertEqual(path.get('d'), drawing)
        self.assertEqual(path.get('transform'), 'translate(2 3)')
        self.assertEqual(path.get('fill-rule'), 'evenodd')
        image = Image.open(io.BytesIO(resvg_py.svg_to_bytes(svg_string=svg, width=100))).convert('RGBA')
        self.assertEqual(image.getpixel((50, 50))[3], 0)
        self.assertGreater(image.getpixel((20, 20))[3], 240)
        self.assertEqual(root.find('{http://www.w3.org/2000/svg}title').text, 'Push & Pull <exercise>')

    def test_multiframe_input_is_rejected(self):
        paths = pipeline.write_paths((0, 0, 10, 10), [(0, 0), (0, 0)], ['M0 0Z', 'M1 1Z'])
        with self.assertRaisesRegex(ValueError, 'one frame'):
            to_svg(paths, 'Exercise')

    def test_blank_png_cannot_be_published_as_an_exercise(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'blank.png'
            Image.new('RGBA', (128, 128), (255, 255, 255, 0)).save(path)
            with self.assertRaisesRegex(ValueError, 'no usable contour ink'):
                convert_png(path, 'Blank')

    def test_tracing_retains_a_hole_when_rasterized(self):
        mask = np.zeros((120, 120), dtype=bool)
        mask[10:110, 10:110] = True
        mask[25:95, 25:95] = False
        drawing = pipeline.trace(mask)
        svg = to_svg(pipeline.write_paths((0, 0, 120, 120), [(0, 0)], [drawing]), 'Ring')
        rendered = Image.open(io.BytesIO(resvg_py.svg_to_bytes(svg_string=svg, width=120))).convert('RGBA')
        ink = np.asarray(rendered)[:, :, 3] > 127
        self.assertGreater((ink & mask).sum() / mask.sum(), .97)
        self.assertEqual(rendered.getpixel((60, 60))[3], 0)

    def test_hairlines_and_heavy_lines_are_normalized(self):
        for thickness in (2, 14):
            mask = np.zeros((400, 400), dtype=bool)
            mask[20:380, 20:380] = True
            mask[20 + thickness:380 - thickness, 20 + thickness:380 - thickness] = False
            self.assertAlmostEqual(pipeline.stroke_width(pipeline.reweight(mask, 6)), 6, delta=1.5)

    def test_catalogue_cannot_escape_asset_directories(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'catalogue.json').write_text(json.dumps({'exercises': [{
                'id': '../outside', 'png': {'file': 'png/../outside.png'}, 'svg': {'file': 'svg/../outside.svg'}
            }]}), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'Invalid exercise ID'):
                load_catalogue(root)

    def test_all_committed_assets_match_the_catalogue(self):
        check(ROOT)

    def test_changed_source_hash_is_rejected(self):
        catalogue = load_catalogue(ROOT)
        catalogue['exercises'][0]['png']['sha256'] = 'wrong hash'
        with patch('build.load_catalogue', return_value=catalogue):
            with self.assertRaisesRegex(ValueError, 'Hash mismatch'):
                check(ROOT)


if __name__ == '__main__':
    unittest.main()
