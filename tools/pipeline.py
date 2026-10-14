# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Alex Mollard
"""Raster-to-vector core extracted from Ironvellum; algorithms and line weights preserved."""
import io
from pathlib import Path

import numpy as np
import resvg_py
from PIL import Image
from scipy import ndimage

MIN_INK = 40
WEIGHT = 0.008
WEIGHT_RES = 1024
OWNER_WIDTH = 1024

def _owner_mask(path):
    """One owner drawing -> ink mask at OWNER_WIDTH. Ink is the alpha channel; an opaque image is read as dark-on-light
    or light-on-dark by its corners."""
    if path.suffix == ".svg":
        b = resvg_py.svg_to_bytes(svg_path=str(path), width=OWNER_WIDTH)
        im = Image.open(io.BytesIO(b)).convert("RGBA")
    else:
        im = Image.open(path).convert("RGBA")
        im = im.resize((OWNER_WIDTH, max(1, round(im.height * OWNER_WIDTH / im.width))), Image.LANCZOS)
    a = np.asarray(im)
    if a[:, :, 3].min() < 250:
        return a[:, :, 3] > 127
    lum = np.asarray(im.convert("L"))
    corner = float(np.median([lum[0, 0], lum[0, -1], lum[-1, 0], lum[-1, -1]]))
    return lum < 128 if corner > 127 else lum > 127


def trace(mask, turdsize=10, tolerance=0.9):
    """Ink mask -> compact SVG path data, one path for the whole pose (potrace; holes by even-odd)."""
    import potrace
    try:
        plist = potrace.Bitmap(~mask).trace(turdsize=turdsize, alphamax=1.0, opticurve=True, opttolerance=tolerance)
    except ValueError:
        # potracer's curve optimiser can take a square root of a negative on a near-degenerate corner; trace unoptimised.
        plist = potrace.Bitmap(~mask).trace(turdsize=turdsize, alphamax=1.0, opticurve=False)

    def p(v):
        return str(int(round(v)))

    parts = []
    for curve in plist:
        s = curve.start_point
        parts.append("M%s %s" % (p(s.x), p(s.y)))
        for seg in curve.segments:
            if seg.is_corner:
                parts.append("L%s %s L%s %s" % (p(seg.c.x), p(seg.c.y), p(seg.end_point.x), p(seg.end_point.y)))
            else:
                parts.append("C%s %s %s %s %s %s" % (p(seg.c1.x), p(seg.c1.y), p(seg.c2.x), p(seg.c2.y),
                                                     p(seg.end_point.x), p(seg.end_point.y)))
        parts.append("Z")
    return "".join(parts)


def bounds(mask):
    """(x0, y0, x1, y1) of the ink, ignoring specks; x1 and y1 are exclusive."""
    lab, n = ndimage.label(mask, structure=np.ones((3, 3)))
    if n == 0:
        return None
    sizes = ndimage.sum(mask, lab, range(1, n + 1))
    keep = np.isin(lab, [i + 1 for i, s in enumerate(sizes) if s >= MIN_INK]) if n else mask
    ys, xs = np.where(keep)
    if xs.size == 0:
        return None
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def stroke_width(mask):
    """Median stroke width in px: twice the median distance-to-edge along the ink's skeleton ridge."""
    from skimage.morphology import skeletonize
    dist = ndimage.distance_transform_edt(mask)
    sk = skeletonize(mask)
    return float(2 * np.median(dist[sk])) if sk.any() else 0.0


def reweight(mask, target):
    """Redraws the ink around its centre lines so the median line is `target` px wide. Each line keeps its own taper (its
    width scales with the frame's), and none is thinner than about a third of the target."""
    from skimage.morphology import skeletonize
    sk = skeletonize(mask)
    if not sk.any():
        return mask
    dist = ndimage.distance_transform_edt(mask)
    scale = np.clip(target / (2 * np.median(dist[sk])), 0.25, 4.0)
    reach, (iy, ix) = ndimage.distance_transform_edt(~sk, return_indices=True)
    # A line drawn out to radius r measures 2r + 2 by stroke_width's own count, hence the - 1.
    return reach <= np.maximum(dist[iy, ix] * scale - 1, target * 0.35)


def reweight_paths(text, tracer=None):
    """A .paths file with every frame redrawn at the house line weight (WEIGHT), retraced in a WEIGHT_RES px window."""
    (_, _, w, h), frames = read_paths(text)
    s = WEIGHT_RES / max(w, h)
    size = (round(w * s), round(h * s))
    imgs = render_paths(text, width=size[0], height=size[1], ink="#ffffff", ground="#000000")
    ds = [(tracer or trace)(reweight(np.asarray(i.convert("L")) > 127, WEIGHT * WEIGHT_RES)) for i in imgs]
    return write_paths((0, 0) + size, [(0, 0)] * len(ds), ds)


def register(items, hanging):
    """items: [(d, mask)] of the kept frames -> (window, [(dx, dy)]).

    Every frame is shifted so its ground line (lowest ink row; the top for hanging movements) and the horizontal centre of
    its ink agree with the first frame's. Only translation: scale is shared by construction, the geometry untouched.
    """
    bs = [bounds(m) for _, m in items]
    ref = bs[0]
    shifts = []
    for b in bs:
        dx = (ref[0] + ref[2]) / 2 - (b[0] + b[2]) / 2
        dy = (ref[1] - b[1]) if hanging else (ref[3] - b[3])
        shifts.append((dx, dy))
    x0 = min(b[0] + s[0] for b, s in zip(bs, shifts))
    y0 = min(b[1] + s[1] for b, s in zip(bs, shifts))
    x1 = max(b[2] + s[0] for b, s in zip(bs, shifts))
    y1 = max(b[3] + s[1] for b, s in zip(bs, shifts))
    pad = 0.015 * max(x1 - x0, y1 - y0)
    window = (x0 - pad, y0 - pad, x1 - x0 + 2 * pad, y1 - y0 + 2 * pad)
    return window, shifts


def fmt(v):
    s = ("%.2f" % v).rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def write_paths(window, shifts, ds):
    lines = ["v1 " + " ".join(fmt(v) for v in window)]
    for (dx, dy), d in zip(shifts, ds):
        lines.append("%s %s %s" % (fmt(dx), fmt(dy), d))
    return "\r\n".join(lines) + "\r\n"


def read_paths(text):
    """-> (window, [(dx, dy, d)])"""
    rows = [r for r in text.splitlines() if r.strip()]
    head = rows[0].split()
    assert head[0] == "v1"
    window = tuple(float(v) for v in head[1:5])
    frames = []
    for r in rows[1:]:
        a, b, d = r.split(" ", 2)
        frames.append((float(a), float(b), d))
    return window, frames


def render_paths(text, height=None, width=None, ink="#e8e0cf", ground="#121110"):
    """Render a .paths file's frames to PIL images through resvg (the same path strings the app parses)."""
    (x, y, w, h), frames = read_paths(text)
    out = []
    for dx, dy, d in frames:
        svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="%s %s %s %s"><rect x="%s" y="%s" width="%s" height="%s" fill="%s"/>'
               '<path fill="%s" fill-rule="evenodd" transform="translate(%s %s)" d="%s"/></svg>'
               % (x, y, w, h, x, y, w, h, ground, ink, dx, dy, d))
        b = resvg_py.svg_to_bytes(svg_string=svg, width=width, height=height)
        out.append(Image.open(io.BytesIO(b)).convert("RGB"))
    return out
