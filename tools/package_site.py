# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Alex Mollard
"""Package the public gallery and verified assets without copying tools or local files."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
SITE_FILES = ('index.html', 'gallery.css', 'gallery.js', 'catalogue.json',
              'LICENSE', 'LICENSE-ARTWORK.md', 'ATTRIBUTION.md', 'PROVENANCE.md')


def package(destination, root=ROOT):
    destination = Path(destination)
    if destination.exists():
        raise ValueError('Output directory already exists; choose a new path')
    entries = json.loads((root / 'catalogue.json').read_text(encoding='utf-8'))['exercises']
    if not entries or len({entry['id'] for entry in entries}) != len(entries):
        raise ValueError('Catalogue must contain unique exercise IDs')
    sources = list(SITE_FILES)
    for entry in entries:
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', entry['id']):
            raise ValueError('Invalid exercise ID')
        for extension in ('png', 'svg'):
            relative = f"{extension}/{entry['id']}.{extension}"
            if entry[extension]['file'] != relative:
                raise ValueError('Noncanonical asset path')
            path = root / relative
            if path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest() != entry[extension]['sha256']:
                raise ValueError(f'Asset does not match its catalogue hash: {relative}')
            sources.append(relative)
    for relative in sources:
        path = root / relative
        if not path.is_file() or path.is_symlink():
            raise ValueError(f'Missing or unsupported site file: {relative}')
    destination.mkdir(parents=True)
    for relative in sources:
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root / relative, target)
    (destination / '.nojekyll').write_text('', encoding='utf-8')
    print(f'Packaged {len(entries)} illustrations in PNG and SVG at {destination}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    package(args.output)


if __name__ == '__main__':
    main()
