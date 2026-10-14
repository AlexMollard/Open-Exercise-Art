# Raster-to-vector pipeline

`png/` contains the approved source images. `svg/` contains the distributable
vector images. `catalogue.json` connects exercise IDs and names to both formats.

`tools/pipeline.py` preserves the relevant conversion functions extracted from
Ironvellum. `tools/convert.py` converts one PNG and wraps its resulting path in
a standard SVG. `tools/build.py` applies that converter to catalogue entries or
checks the committed assets. There is no Android or Ironvellum dependency.

1. Resample the PNG to 1024 pixels wide, preserving its aspect ratio.
2. Threshold alpha above 50%. For fully opaque inputs, infer black-on-white or
   white-on-black polarity from the corners and threshold luminance instead.
3. Trace the binary ink mask using potracer. Ignore tiny specks when measuring
   the illustration's bounding box and add a 1.5% framing margin.
4. Render the traced drawing at a 1024-pixel long side, skeletonize the ink and
   redraw around its centre lines at the house line weight: 0.8% of the long side.
   Taper survives within the pipeline's minimum and maximum width limits.
5. Trace the reweighted mask and write one filled contour path using the SVG
   even-odd rule. The figure and equipment interiors stay transparent.

Use the pinned dependencies to reproduce the initial vectors. Different
versions of numerical, rasterization or tracing libraries can change the output.
The source PNGs are the human-reviewed authority for the depicted anatomy and
equipment. Automated checks establish file integrity and vector validity, not
whether a drawing teaches correct exercise form.

The SVG viewBox preserves the approved vector framing. Its long side is 1024
units and the short side follows the drawing's padded aspect ratio. Source PNGs
retain their original canvas dimensions. This framing difference is intentional.

## Source-image requirements

Use a smooth faceless, earless figure, plain shorts, bare feet, clean single
contours and minimal equipment. All enclosed interiors must be empty. Do not
use glow, gradients, hatching, grey shading, textured alpha or filled silhouettes.
The binary threshold cannot preserve those effects. Keep hands, grips, joints
and equipment connections anatomically plausible and inspect the final SVG.

## Verification

```sh
python tools/build.py --check
python -m unittest discover -s tests
python tools/build.py --output .tmp/rebuilt --jobs 4
```

The tests cover contour holes, raster/vector round trips, blank images,
line-weight normalization and catalogue integrity. A full rebuild can be
compared with the committed SVG hashes without changing the approved assets.
No automated GitHub workflows or metered services are configured.
