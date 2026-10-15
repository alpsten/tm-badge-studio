# Badge colors

`tint_badge.py` uses Python and Pillow to recolor an existing badge. It performs
no AI generation, resizing, or redrawing. Every output has the original pixel
dimensions and exactly the same alpha channel, including partially transparent
edge pixels.

Install Pillow if needed: `python3 -m pip install Pillow`.

Run from the project root:

```sh
python3 scripts/tint_badge.py \
  output/badges/badge-original.png \
  output/badges/badge-custom.png \
  --color '#6366f1'
```

Replace the hex color and output filename for each variant. The blue example uses
`#2563eb`. Always start from `badge-original.png`; tinting an already colored
variant will change the shading. Existing output files are never overwritten.

The script converts the original RGB values to grayscale brightness, then maps
black to black, medium gray (128) to the chosen color, and white to white, with
smooth gradients between those points. This retains the placement of facets,
shadows, and highlights. The chosen hex is the **midtone**, rather than a uniform
fill. Perceived brightness can vary by color; the original RGB values are changed.

The 29 generated variants are in `output/badges/`, with their exact midtone colors
in `output/badges/palette.json`. Black uses charcoal and white uses off-white so
both retain visible shading. `badge-palette-preview.png` shows a labeled overview;
the individual PNGs retain the full original resolution and transparency.
`badge-colors.zip` contains all 29 variants, the palette, and the preview.
Run `python3 scripts/render_badge_palette.py` after editing the palette to update
the standalone colors, preview, and ZIP. Identical PNGs are reused unchanged.
Orange (#E98026) is joined by Dark orange (#B84A08) and Bright orange (#FF9A00).
Dark grey (#70757D) keeps the existing `gray` key and asset paths so saved
corporation references keep their color. Light grey (#BFC3C9) uses `light-gray`.
Dark yellow uses #A68B08. Steel is also a center color: `palette_image` in
`badge_finishes.py` applies the steel finish's shadow, midtone, and highlight
to standalone steel badges and every steel center. Other center colors retain
their original black-to-midtone-to-white tint map.

## Separate frame and center colors

Use the saved center mask to color the frame and center independently:

```sh
python3 scripts/tint_badge.py \
  output/badges/badge-original.png \
  output/badges/badge-gold-frame-black-center.png \
  --color '#C99A2E' \
  --center-mask output/badges/badge-center-mask.png \
  --center-color '#181A1E'
```

The example output already exists; choose a new filename for another combination.
With a mask, `--color` sets the frame color. Omit `--center-color` to keep the
original center pixels. The grayscale mask is white inside the center and black
outside, with antialiased edges traced through the recessed border. It matches
the original 1254 × 1254 badge; a differently shaped badge needs its own mask.
The original transparency is retained across the entire output.

## Six frame finishes

All 29 center colors have six frame variants (174 PNGs total) in:

- `output/badges/framed/bronze-frame/`
- `output/badges/framed/silver-frame/`
- `output/badges/framed/gold-frame/`
- `output/badges/framed/steel-frame/`
- `output/badges/framed/black-frame/`
- `output/badges/framed/white-frame/`

Each directory uses the center color in its filename, for example `badge-blue.png`.
Run `python3 scripts/render_badge_frames.py` to rebuild these, their previews,
the manifest, and the framed-colors ZIP. Finish profiles live in
`badge_finishes.py`: steel uses a darker cool range, black uses subdued highlights,
and white uses soft satin shading distinct from silver. Center pixels match
the corresponding original color variant, except for the antialiased transition
along the mask boundary. The original bronze, silver, and gold profiles are
preserved. All individual assets retain the original dimensions and alpha.

`output/badges/framed/badge-frame-finishes-preview.png` compares all six frames.
The six `badge-*-frame-preview.png` files show one frame finish at a time.
`output/badges/badge-framed-colors.zip` contains all 174 PNGs, the previews, and a
`combinations.json` manifest listing each file, finish profile, and center color.

## Modular upgrade sketch

`render_badge_upgrade_sketch.py` builds the first two progression concepts from
the saved neutral ornament masters: a bottom plate with rank 1, then the same
plate with separate wings added and rank reset to 1. It reuses `tint_badge.py`.
See `output/badges/upgrade-sketch/README.md` for the layer order, individual
transparent assets, image-generation prompts, and rebuild command.
This is historical concept artwork; the current kit provides small and approved ascendant wing pairs.

## Complete ornaments and podium awards

`render_badge_awards.py` assembles the expanded kit in `output/badges/awards-kit/`:
crest and wing upgrades, gold Champion laurels, separate rank markers, and
the Champion / 2nd place / 3rd place award badges. Shared accessories have bronze,
silver, gold, steel, black, and white variants on the same 2048 × 2048 canvas. See that directory's
`README.md` and `layout.json` for usage and exact assembly order.

Plate milestones are **1, 3, 5, 10, 20, 25, 50**. The renderer fits and centers
every marker inside the plate face and exports all 252 combinations of six
finishes, six ornament arrangements, and seven milestones. The Champion uses a separate crown
layer in place of the central numeral 1.

## WebP copies for website testing

Run `python3 scripts/export_badge_webp.py` to export the current colors, framed
badges, aligned layers, progression milestones, awards, and numbered plates to
`public/badges/256/` and `public/badges/512/`. Artwork uses WebP quality 95 with
lossless alpha; text layers use lossless WebP. Source PNGs are left unchanged.

The exporter verifies every file, writes path and size manifests, and packages
`output/badges/badge-webp-testing-kit.zip`. Serve `public/` with
`python3 -m http.server 8000 --directory public` and open
`http://localhost:8000/badges/preview.html`. See `public/badges/README.md` for usage and
the distinction between standalone badges and aligned badge layers.

There are exactly two wing pairs: `masters/wings-small-silver.png` is exported
as `layers/{finish}/wings-small`; `masters/wings-ascendant-silver.png` is exported
as `layers/{finish}/wings`. The crest is an independent optional layer. The
preview provides separate Wings and Crest controls and compares all six choices.
The superseded old full-wing design remains retired. Its replacement prompt is
in `output/badges/awards-kit/ascendant-wings-prompt.json`.
The exporter removes retired WebPs tracked by its previous manifest.

The optional outer border uses `masters/outer-border-silver.png` and is exported
as `layers/{finish}/outer-border`. It goes behind the badge and crest, in front
of any wings. The preview has an independent On/Off control and each finish has
an assembled example under `examples/`. The renderer also crops the wide gold
hexagon master into `concepts/wide-hex-gold.png` for the editable-text preview.
Generation prompts are in `output/badges/awards-kit/border-and-wide-prompts.json`.

When the border is enabled, use `wings-small-border` or `wings-border`. These
shift each wing outward by 68 master pixels without scaling or clipping. The
preview selects the attachment variant automatically. Normal wing assets remain
unchanged. `layout.json` records both sets of attachment names.

## Corporation palettes and additional border colors

`corporation_badges.json` records all 47 user-proposed palettes, preserving
slash-separated colors as alternatives (53 combinations). Suggested third colors
are explicitly optional, including distinctions between repeated pairs.
Run `python3 scripts/render_corporation_badges.py` after the awards renderer.

It builds `output/badges/corporations/`: aligned corporation badges, ornaments
in 24 additional colors, 30 modular center layers, and 30 modular frame layers.
The frame mask and opaque center underlay reconstruct the original two-color
blend while retaining its alpha. The renderer checks that the center transition
stays within opaque artwork. All tinting starts from the neutral originals.

The generated `public/badges/corporations.json`, `corporations.js`, and
`corporations.md` drive the preview's searchable **All corporations** tab.
Custom colors offer independent center, frame, wing, crest, and outer-border
selectors. Wing and crest colors reuse the existing WebPs in all 30 finishes;
changing the controls does not require regenerating artwork. Automatic matching
keeps wings in the frame color and the crest in the palette's optional accent.
Each of the 30 finishes has both wing attachment variants and every rank marker.

Rebuild in order: `render_badge_palette.py`, `render_badge_frames.py`, `render_badge_awards.py`,
`render_corporation_badges.py`, `render_badge_logos.py`, then `export_badge_webp.py`. The WebP ZIP includes
the complete preview, corporation data, and all exported colors and layers.

For an additive update, the exporter can accept `--unchanged-checkpoint PATH`:
a pre-edit JSON mapping of project-relative PNG and WebP paths to SHA-256 hashes.
It reuses previous exports only when all their source and output hashes still
match and the export settings agree. Changed or new files are encoded and checked
normally; incompatible export settings require a normal full export.

## Corporation and expansion logo layers

`scripts/badge_logos.json` maps the 47 supplied images to their corporation IDs.
Its separate `expansions` list adds Venus, Colonies, Turmoil, Prelude, Prelude II, and Promos to the mixer's
**Logo → Expansions** choices. Expansion IDs share the logo namespace but do not
create corporation presets or entries in the corporation gallery.
Splice uses the supplied `splice-logo-2.png` artwork.
Import originals and render the aligned layers with:

```sh
python3 scripts/render_badge_logos.py --source-dir /path/to/new-logo-artwork
```

The source folder is read only. Exact copies are kept in
`output/badges/logos/originals/`; later runs can omit `--source-dir` to use these
copies. Generated layers and placement data live in `output/badges/logos/`.
Venus, Colonies, and Turmoil originals retain their supplied WebP format and alpha.
Prelude and Prelude II use matching polished gold outer rims. Prelude retains its
white chevron; Prelude II uses two broad white bars with a generous gap. Prelude,
Prelude II, and Promo use PNG copies of their generated achievement masters; the supplied references live beside those masters in `references/`. Their
`allow_upscale` setting enlarges the small source icons only while fitting the
2048 px master canvas, keeping a useful display size in the 256/512 px exports.
This does not add detail or change the imported source files.
The script keeps colors, proportions, and source pixels intact before resizing;
only fully transparent margins are trimmed. The Mons Insurance square is retained
in full, including its orange background, per the user's preference. Manutech and
Kuiper Cooperative use their updated artwork with transparent outer backgrounds,
retaining the white areas within each logo. Vitor and Valley Trust also retain
their supplied transparency.

Fitting uses the existing center mask inset by 40 master pixels. It measures each
logo's actual alpha silhouette and verifies that the preview's maximum 110% size
stays within that safe area. All layers use the same 2048 px canvas and center
(1024, 1015); no frame, wing, crest, or base image is altered.

Run the WebP exporter afterward. It encodes logos losslessly at 256 and 512 px,
verifies every resized RGBA pixel, and includes `logos.js` and `logos.json` in the
preview ZIP. Stack the logo after the base center/frame and before plate/rank.
Shadow and outline options are preview-only CSS effects on the logo layer.
