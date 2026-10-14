# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Alex Mollard
"""Convert a contour PNG into a standard, transparent SVG using the house pipeline."""
import argparse
from pathlib import Path
import sys
from xml.sax.saxutils import escape, quoteattr

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pipeline


def to_svg(paths, title):
    """Wrap a single approved vector frame without changing its geometry."""
    window, frames = pipeline.read_paths(paths)
    if len(frames) != 1 or min(window[2:]) <= 0:
        raise ValueError("Expected one frame and a positive viewBox")
    dx, dy, drawing = frames[0]
    box = " ".join(pipeline.fmt(v) for v in window)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{box}" '
        f'width="{pipeline.fmt(window[2])}" height="{pipeline.fmt(window[3])}" '
        f'role="img" aria-label={quoteattr(title)}>\n'
        f'  <title>{escape(title)}</title>\n'
        '  <metadata>Open Exercise Art; artwork: CC-BY-SA-4.0; '
        'https://github.com/AlexMollard/Open-Exercise-Art</metadata>\n'
        f'  <path fill="currentColor" fill-rule="evenodd" '
        f'transform="translate({pipeline.fmt(dx)} {pipeline.fmt(dy)})" d={quoteattr(drawing)}/>\n'
        '</svg>\n'
    )


def convert_png(source, title):
    source = Path(source)
    if source.suffix.lower() != ".png":
        raise ValueError("Input must be a PNG")
    mask = pipeline._owner_mask(source)
    if pipeline.bounds(mask) is None:
        raise ValueError("PNG has no usable contour ink")
    drawing = pipeline.trace(mask)
    window, shifts = pipeline.register([(drawing, mask)], hanging=False)
    paths = pipeline.reweight_paths(pipeline.write_paths(window, shifts, [drawing]))
    return to_svg(paths, title)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--title", help="Accessible exercise name; defaults to the input filename")
    args = parser.parse_args()
    svg = convert_png(args.source, args.title or args.source.stem.replace("-", " ").title())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(svg.encode("utf-8"))
    print(args.output)


if __name__ == "__main__":
    main()
