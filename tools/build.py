# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Alex Mollard
"""Rebuild the SVG collection or validate the committed catalogue and assets."""
import argparse
from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
import math
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parent))
from convert import convert_png
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_catalogue(root=ROOT):
    catalogue = json.loads((root / "catalogue.json").read_text(encoding="utf-8"))
    entries = catalogue["exercises"]
    slugs = [e["id"] for e in entries]
    if not entries or len(slugs) != len(set(slugs)):
        raise ValueError("Catalogue must contain unique exercise IDs")
    for entry in entries:
        slug = entry["id"]
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
            raise ValueError(f"Invalid exercise ID: {slug}")
        if entry["png"]["file"] != f"png/{slug}.png" or entry["svg"]["file"] != f"svg/{slug}.svg":
            raise ValueError(f"Noncanonical asset path: {slug}")
    return catalogue


def check(root=ROOT):
    catalogue = load_catalogue(root)
    entries = catalogue["exercises"]
    for extension in ("png", "svg"):
        expected = {f"{e['id']}.{extension}" for e in entries}
        actual = {p.name for p in (root / extension).iterdir() if p.is_file()}
        if expected != actual:
            raise ValueError(f"Missing or extra {extension.upper()} files: {expected ^ actual}")
    namespace = "{http://www.w3.org/2000/svg}"
    for entry in entries:
        for extension in ("png", "svg"):
            path = root / entry[extension]["file"]
            if digest(path) != entry[extension]["sha256"]:
                raise ValueError(f"Hash mismatch: {path.name}")
        with Image.open(root / entry["png"]["file"]) as image:
            image.load()
            if image.mode != "RGBA" or list(image.size) != entry["png"]["size"]:
                raise ValueError(f"PNG mode or dimensions changed: {entry['id']}")
            if image.getextrema()[3][0] != 0:
                raise ValueError(f"PNG background is not transparent: {entry['id']}")
        svg = ET.parse(root / entry["svg"]["file"]).getroot()
        allowed = {namespace + tag for tag in ("svg", "title", "metadata", "path")}
        if svg.tag != namespace + "svg" or any(element.tag not in allowed for element in svg.iter()):
            raise ValueError(f"Unexpected SVG element: {entry['id']}")
        box = [float(v) for v in svg.attrib["viewBox"].split()]
        if len(box) != 4 or not all(math.isfinite(v) for v in box) or min(box[2:]) <= 0:
            raise ValueError(f"Invalid SVG viewBox: {entry['id']}")
        paths = svg.findall(namespace + "path")
        if len(paths) != 1 or not paths[0].get("d") or paths[0].get("fill-rule") != "evenodd":
            raise ValueError(f"Expected one contour path with transparent holes: {entry['id']}")
        if paths[0].get("fill") != "currentColor":
            raise ValueError(f"SVG must inherit its ink colour: {entry['id']}")
    print(f"Verified {len(entries)} PNGs, {len(entries)} SVGs, catalogue hashes and transparency")


def rebuild_one(job):
    source, title, output = job
    svg = convert_png(source, title)
    Path(output).write_bytes(svg.encode("utf-8"))
    return Path(output).name


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Validate without modifying files")
    parser.add_argument("--slug", help="Rebuild only this exercise")
    parser.add_argument("--output", type=Path, default=ROOT / "svg", help="SVG output directory")
    parser.add_argument("--jobs", type=int, default=4)
    args = parser.parse_args()
    if args.check:
        check()
        return
    entries = load_catalogue()["exercises"]
    if args.slug:
        entries = [e for e in entries if e["id"] == args.slug]
        if not entries:
            parser.error("Unknown exercise ID")
    if args.jobs < 1:
        parser.error("--jobs must be at least 1")
    args.output.mkdir(parents=True, exist_ok=True)
    jobs = [(str(ROOT / e["png"]["file"]), e["name"], str(args.output / (e["id"] + ".svg"))) for e in entries]
    with ProcessPoolExecutor(max_workers=args.jobs) as pool:
        for number, name in enumerate(pool.map(rebuild_one, jobs), 1):
            print(f"{number}/{len(jobs)} {name}", flush=True)
    print("SVG build complete. Review changes before updating catalogue hashes or publishing.")


if __name__ == "__main__":
    main()
