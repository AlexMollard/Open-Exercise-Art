# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Alex Mollard
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from package_site import package, SITE_FILES


class SitePackageTest(unittest.TestCase):
    def fixture(self, root):
        for name in SITE_FILES:
            (root / name).write_text('Example site content', encoding='utf-8')
        entry = {'id': 'example'}
        for extension in ('png', 'svg'):
            folder = root / extension
            folder.mkdir()
            path = folder / ('example.' + extension)
            path.write_bytes(b'example asset bytes')
            entry[extension] = {'file': f'{extension}/{path.name}',
                                'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
        (root / 'catalogue.json').write_text(json.dumps({'exercises': [entry]}), encoding='utf-8')
        return entry

    def test_only_public_site_files_and_catalogued_assets_are_copied(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.fixture(root)
            (root / '.env').write_text('private configuration', encoding='utf-8')
            (root / 'png/unreviewed.png').write_bytes(b'not catalogued')
            destination = root / 'site'
            package(destination, root)
            files = {p.relative_to(destination).as_posix() for p in destination.rglob('*') if p.is_file()}
            self.assertEqual(files, set(SITE_FILES) | {'png/example.png', 'svg/example.svg', '.nojekyll'})

    def test_changed_asset_is_rejected_before_creating_a_bundle(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.fixture(root)
            (root / 'png/example.png').write_bytes(b'changed')
            destination = root / 'site'
            with self.assertRaisesRegex(ValueError, 'catalogue hash'):
                package(destination, root)
            self.assertFalse(destination.exists())

    def test_existing_output_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary)
            marker = destination / 'keep.txt'
            marker.write_text('keep', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'already exists'):
                package(destination)
            self.assertEqual(marker.read_text(encoding='utf-8'), 'keep')
