# Open Exercise Art

**Consistent exercise illustrations. Open assets. Reproducible tools.**

553 approved exercise illustrations, each available as a transparent PNG and a
standard SVG. Built for fitness apps, exercise guides and other projects that
need a consistent set of single-frame exercise drawings.

| Push-up | Goblet squat | L-sit |
|---|---|---|
| ![Push-up](svg/push-up.svg) | ![Goblet squat](svg/goblet-squat.svg) | ![L-sit](svg/l-sit.svg) |

Browse the [exercise index](INDEX.md), use the machine-readable
[catalogue](catalogue.json), or open the searchable gallery locally:

```sh
python -m http.server 8000 --bind 127.0.0.1
```

Visit `http://127.0.0.1:8000/`. The gallery uses local files, system fonts and
plain HTML, CSS and JavaScript. No account, framework, analytics or CDN is needed.

## Use an illustration

Download the relevant file from `png/` or `svg/`. Both folders use the same
exercise slug, such as `push-up.png` and `push-up.svg`. There is one still per
exercise and no animation frames. The catalogue includes names, aliases,
dimensions and SHA-256 hashes.

```html
<img src="svg/push-up.svg" alt="Push-up exercise" width="240">
```

SVGs have transparent backgrounds and use `fill="currentColor"`; they default to
black ink. Inline an SVG to inherit a surrounding CSS `color`. An SVG loaded via
`<img>` does not inherit the parent page's colour: edit its fill or set a colour
inside the SVG if needed. Preserve `fill-rule="evenodd"`, which keeps the body
and equipment interiors transparent. The paths describe contour ribbons;
setting `fill="none"` removes the drawing.

PNGs contain white contour lines on transparency and work best on a dark
background. SVGs have a tight padded viewBox; PNGs retain the original square
canvas. Use `object-fit: contain` and preserve the aspect ratio.

## Build SVGs locally

The raster-to-vector toolchain is free and open-source. Using the committed
images, rebuilding SVGs and viewing the gallery require no AI model or paid service.
Python 3.13 is the tested environment; dependency versions are pinned.

```sh
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
python -m pip install -r requirements.txt
python tools/build.py --check
python -m unittest discover -s tests
```

Rebuild one exercise or the whole collection:

```sh
python tools/build.py --slug push-up --output .tmp/rebuilt
python tools/build.py --output .tmp/rebuilt --jobs 4
```

Omit `--output` to rebuild `svg/` in place. Review the result and its diff before
publishing. `--check` validates the committed file hashes, SVG structure and PNG
transparency without retracing. It never approves changed images.

Convert your own contour PNG:

```sh
python tools/convert.py my-exercise.png --output my-exercise.svg --title "My exercise"
```

Input should be white lines on transparency or black lines on pure white, with
empty interiors. The converter thresholds the ink, traces it with potracer,
then redraws the centre lines at 0.8% of the drawing's long side. It cannot fix
incorrect anatomy, remove unwanted fills or recover detail missing from the PNG.
See [the pipeline documentation](docs/PIPELINE.md).

## Licences and origin

- **Artwork and exercise catalogue: CC BY-SA 4.0.** See [LICENSE-ARTWORK.md](LICENSE-ARTWORK.md).
  Credit Open Exercise Art / Alex Mollard, link the licence and note modifications.
  Adapted artwork must retain the same licence. An example credit is in [ATTRIBUTION.md](ATTRIBUTION.md).
- **Tools, gallery and documentation: GPL-3.0-or-later.** See [LICENSE](LICENSE).
- Dependencies retain their own FOSS licences; see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

The source PNGs were AI-generated for Ironvellum and individually reviewed and
approved by its owner. The original image-generation service/model is not
included and is not an open-source dependency of this conversion toolchain.
The initial SVGs preserve the approved Ironvellum vector geometry.
Visual inspiration came from Everkinetic (Greg Priday) and Workout Guide (Bryl Lim).
No upstream drawing files or animation archives are bundled. This repository
does not claim the collection is public domain. See [PROVENANCE.md](PROVENANCE.md).

Contributions are welcome; please read [CONTRIBUTING.md](CONTRIBUTING.md).
