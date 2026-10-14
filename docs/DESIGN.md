# Open Exercise Art design

The initial scope is a standalone public collection owned by AlexMollard:
553 approved PNGs, their matching standard SVGs, the FOSS conversion tools,
an exercise catalogue and a searchable local gallery. The repository name is
Open-Exercise-Art. Code uses GPL-3.0-or-later; artwork and catalogue use CC BY-SA 4.0.

PNG and SVG files share stable exercise slugs. The catalogue records their
names, aliases, dimensions and hashes. The initial PNGs are byte-identical to
the approved source collection; initial SVGs preserve its approved vector
geometry. The original AI model is outside the conversion toolchain.

The converter preserves Ironvellum's mask threshold, Potrace-compatible tracing,
crop margin, centre-line redraw and 0.8% house weight. The SVG wrapper preserves
even-odd contour holes, uses currentColor and includes accessible exercise names.
The catalogue validator checks asset membership, file hashes, PNG transparency
and SVG structure. Rebuilding into a separate output directory allows exact
comparison without changing the approved collection.

The gallery uses local catalogue and SVG files with no build system, external
fonts, analytics or framework. Search includes exercise names, IDs and aliases.
Each card links to both downloadable formats. Keyboard navigation and narrow
screens must remain usable.

Success means all 553 PNG hashes match the source approvals, all 553 SVGs retain
the approved geometry, a fresh environment can run tests and rebuild the
collection, and the personal GitHub repository contains only the intended public
assets, code and documentation. No private review reports, caches, credentials,
virtual environments, upstream animations, automatic Actions or Git LFS are published.

## Implementation and verification

- [x] Import the approved PNGs and export the approved vector geometry as SVG.
- [x] Extract the conversion core and add standalone conversion and validation commands.
- [x] Add split licence texts, provenance, dependency notices and contribution documentation.
- [x] Add the alphabetical index and searchable gallery.
- [x] Verify all assets and tests in a newly installed environment.
- [x] Rebuild all SVGs and compare their hashes with the approved exports.
- [x] Check the gallery, search, downloads and responsive layout locally.

Publication target: `AlexMollard/Open-Exercise-Art`, public, on `main`.
Local commit identity: `AlexMollard <AlexMollard@users.noreply.github.com>`.
The publication check must confirm that the remote tree matches the verified
local tree and contains no workflows, caches, virtual environments or private data.
