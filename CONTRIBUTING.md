# Contributing

Use stable lowercase, hyphen-separated exercise IDs. Put one approved source
PNG in `png/<id>.png` and one vector export in `svg/<id>.svg`. Add its name,
aliases, dimensions and SHA-256 hashes to `catalogue.json`.

Follow [the source-image requirements](docs/PIPELINE.md). Review anatomy,
equipment, grips, framing and transparency before proposing an addition or fix.
Include before/after previews and identify the exercise clearly. Keep drafts and
rejected alternatives out of the committed collection.

Run locally before submitting a pull request:

```sh
python tools/build.py --check
python -m unittest discover -s tests
```

For changed PNGs, rebuild the SVG, visually inspect it, and update the affected
catalogue dimensions and hashes. Preserve approved drawings during tooling
changes unless their visual change is intentional and reviewed. Update the
alphabetical INDEX.md when adding or renaming an exercise.

By submitting a contribution, you agree to license artwork and catalogue data
under CC BY-SA 4.0 and code, gallery and documentation under GPL-3.0-or-later.
Provide the origin and any required attribution for your contribution. Do not
submit materials you lack permission to redistribute under those terms.

The initial PNGs were AI-generated and human-reviewed. Clearly disclose the
provenance of new contributions rather than claiming the original generation
service is part of the FOSS conversion toolchain.

Tests run locally. Do not add automatic GitHub Actions, Git LFS, analytics,
external fonts, paid services or credentials to this project.
