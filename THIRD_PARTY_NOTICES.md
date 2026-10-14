# Third-party notices

The raster-to-vector code was extracted from Ironvellum's exercise-art pipeline,
Copyright (C) 2026 Alex Mollard, GPL-3.0-or-later. Its tracing and reweighting
functions retain their algorithms and constants.

The dependencies are installed from their published packages; their source,
copyright and licence notices remain with those distributions. They are not
vendored into this repository.

| Dependency | Purpose | Licence |
|---|---|---|
| NumPy | Binary masks and numerical arrays | BSD-3-Clause; bundled components retain their notices |
| Pillow | PNG decoding and resampling | MIT-CMU |
| potracer | Potrace-compatible vector tracing | GPL-2.0-or-later |
| resvg_py | SVG rasterization | MIT; bundled Rust dependencies retain their notices |
| scikit-image | Skeletonization | BSD family; bundled components retain their notices |
| SciPy | Distance transforms and connected components | BSD family; bundled components retain their notices |
| ImageIO | scikit-image dependency | BSD-2-Clause |
| lazy-loader | Lazy imports | BSD-3-Clause |
| NetworkX | scikit-image dependency | BSD-3-Clause |
| packaging | Dependency version parsing | Apache-2.0 OR BSD-2-Clause |
| tifffile | ImageIO/scikit-image dependency | BSD-3-Clause |

The GPL-2.0-or-later tracing dependency permits choosing GPL version 3 or later
for the combined conversion toolchain. See LICENSE for this project's code terms.

The artwork's inspiration and creator credit are recorded in ATTRIBUTION.md and
PROVENANCE.md. Artwork and catalogue data use CC BY-SA 4.0, separately from code.
