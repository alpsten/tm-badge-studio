# WebP badge testing kit

Optimized copies of the PNG artwork. The original PNGs remain in `output/badges/`.

## Test in the website

Serve the `public/` folder with `python3 -m http.server 8000 --directory public`,
then open `http://localhost:8000/badges/preview.html`. On GitHub Pages, paths sit
beneath your repository name; the studio uses relative links automatically.
That page lets you combine center colors, frame finishes, wings, a crest, and milestones and
compare the 256 px and 512 px exports on dark or light backgrounds.
Wings and crest have independent controls: **Wings = None / Small pair / Ascendant
pair**, **Crest = Off / On**. This allows the crest alone or with either wing pair.
**Wing color** and **Crest color** each offer all 30 finishes independently of
the center, frame, and outer border. Wing color defaults to **Match frame**;
crest color defaults to **Match badge palette**, including optional suggested
accents. Choosing a specific color overrides that match in the mixer, comparison
badges, and corporation gallery. A color control is disabled while its ornament
is off and remembers its selection when you turn the ornament back on.
The comparison follows the selected frame, center, and milestone. **Outer border**
has independent On/Off and color controls. Choose **Match badge palette** to follow
the frame (or optional suggested accent), or pick any of the 30 outer-border colors.

The **All corporations** tab (`badges/preview.html#corporations`) shows all 47
proposed corporation palettes. **Palette = Distinct colors** is the default: every
corporation has a unique center/frame pair, with 12 palettes revised to separate
the repeated groups. **Original colors** keeps all 53 original combinations,
including the selectable slash-color alternatives. The palette switch applies
to the mixer and gallery; custom colors stay as you set them.
Use **Revised palettes only**, or `badges/preview.html?changed=1#corporations`, to
compare the 12 changes. Hide logos to compare just their colors. Search matches
the colors in the active palette. Related shades can still look similar, so names
and logos remain useful identifiers. Suggested third-color accents are optional
and off by default. The repeated-pair list follows the selected palette.
See `corporations.md` for the full table and the reasons for each proposal.
Open any card in the mixer, then choose **Customize these colors** to edit its pair.

## Corporation logos

Forty-seven supplied logos are available: Aphrodite, Arcadian Communities, Aridor, Arklight,
Astrodrill, Celestic, Cheung Shing Mars, Credicor, Ecoline, Ecotec, Factorum, Helion, Interplanetary
Cinematics, Inventrix, Kuiper Cooperative, Lakefront Resorts, Manutech, Mining Guild,
Mons Insurance, Morning Star Inc., Nirgal Enterprises,
Palladin Shipping, Pharmacy Union, Philares, PhoboLog, Point Luna, Polyphemos,
Poseidon, Pristar, Recyclon, Robinson Industries, Sagitta, Saturn Systems, Septem Tribus,
Spire, Splice, Stormcraft Incorporated, Teractor, Terralabs Research, Tharsis Republic,
Thorgate, Tycho Magnetics,
United Nations Mars Initiative (UNMI), Utopia Invest, Valley Trust, Viron, and Vitor.
The mixer starts with Aphrodite. **Logo = Match corporation** selects the matching
artwork. You can also choose any available logo explicitly when experimenting with custom colors.
**Customize these colors** keeps the current logo while unlocking the colors.

**Show logos** toggles the layer without clearing its selection. **Logo size**
offers 85%, fitted 100%, and 110%. **Logo contrast** offers a soft shadow,
unaltered artwork, or a light outline. These controls affect the mixer and style
comparisons. The gallery uses each corporation's own logo, with the same size,
contrast, and visibility settings; it never assigns a different corporation's
logo because of a manual mixer selection.

Use **With logos only**, or open `badges/preview.html?logos=1#corporations`, to
compare all available logo badges together. Corporations without artwork keep a blank center.
Color and logo adjustments remain preview-only and do not overwrite saved presets.

Logos are separate aligned layers in `logos/`, placed above the badge and below
the bottom plate and rank. Their original colors and proportions are preserved;
only completely transparent margins are trimmed before fitting. Opaque backgrounds
are retained, including the supplied Inventrix, Credicor, and Interplanetary Cinematics
artwork and Mons Insurance's original orange square. Point Luna, Pristar,
Manutech, and Kuiper Cooperative use updated artwork with transparent outer
backgrounds. White areas within the logos are retained. Both the normal and 110% sizes
fit inside an inset center mask, without clipping or covering the frame.
`logos.json` records the source hashes, crop and placement bounds, and layer paths;
`logos.js` supplies the same data to the preview without requiring a fetch.
Per-logo `offset` values in `scripts/badge_logos.json` adjust optical alignment in
2048 px canvas coordinates without changing scale. Celestic is shifted 32 px left.
Credicor and Pharmacy Union use transparent rounded corners, with
`corner_radius_fraction` set to 0.14 to resemble Arklight's silhouette. Their
original source files stay intact; Pharmacy Union retains its yellow background
inside the rounded rectangle.

There are exactly two wing assets: `layers/{metal}/wings-small.webp` is the small
pair; `layers/{metal}/wings.webp` is the approved tall, upward-sweeping pair.
`layers/{metal}/crest.webp` is independent. The superseded old full-wing design
(`wings-extended`) remains retired.

Custom mode offers 30 colors for centers, frames, and ornaments.
Orange has three choices: the original Orange (#E98026), Dark orange (#B84A08),
and Bright orange (#FF9A00), available for every independently colored part.
The former Gray is now labeled Dark grey (#70757D). Light grey (#BFC3C9) is
also available for each part, with soft shading on frames and ornaments.
Steel is available as a center, using the same cool shading as the steel frame.
Dark yellow (#A68B08) is available for every independently colored part.
The six original finishes include bronze, silver, gold, steel, black, and white.
Steel is cool and darker than silver; black has subdued charcoal highlights;
white has satin shading rather than silver's strong reflective contrast. All
finishes include matching wings, plates, crests, and all seven rank markers.

The files are in `public/badges`, so an example URL is:

```html
<img
  src="badges/256/awards/champion.webp"
  srcset="badges/256/awards/champion.webp 256w,
          badges/512/awards/champion.webp 512w"
  sizes="256px"
  width="256"
  height="256"
  alt="Champion"
/>
```

Use the 512 px copies when displaying a 256 px canvas on a 2× screen. If you
display these larger than that, export a larger version from the PNG masters.
The compact `plates/` exports keep their aspect ratio; 256 and 512 indicate their
maximum edge length, not a square canvas.

## Folder contents

Each size directory includes:

- `colors/`: 29 standalone badge colors.
- `framed/`: 174 standalone frame/center combinations across six finishes.
- `layers/`: the aligned ornaments, rank markers, award text, and badge layers.
- `layers/{metal}/badges/`: all 29 center colors aligned to each metal's ornaments.
- `progression/`: 252 assembled combination/milestone badges with black centers.
- `awards/`: Champion with a crown, 2nd place, and 3rd place.
- `plates/`: all seven milestones on each finish (42 plates).
- `examples/`: six assembled outer-border examples, one per finish.
- `concepts/wide-hex-gold.webp`: a blank wide hexagon concept, with aspect ratio retained.
- `corporations/`: 65 aligned corporation badge color combinations (53 originals and 12 revisions).
- `corporation-ornaments/`: wings, crests, borders, plates, and seven rank markers in 24 additional colors.
- `modular/centers/` and `modular/frames/`: 30 center layers and 30 frame layers for arbitrary color pairs.
- `logos/`: forty-seven separate corporation logo layers, encoded as lossless WebP.

`corporations.json` lists presets, alternatives, optional accents, colors, and all
paths for the expanded palette. Each corporation keeps its original `variants`
and adds a `distinct_variant` and `distinct_changed` flag. `corporations.js`
provides the same data to the preview, including when opened from a local folder.
To revise a proposal, edit `distinct_palette` in `scripts/corporation_badges.json`,
run `python3 scripts/render_corporation_badges.py --palettes-only`, then export
the WebP copies. The renderer rejects duplicate pairs in the distinct palette.

`layout.json` lists the exact layer order for every assembled example. Its paths
are relative to a size directory, such as `512/`. Replace
`layers/gold/badge.webp` with `layers/gold/badges/blue.webp` to use a blue center.
Its `styles` list describes all six ornament combinations. Existing `stage-1-plate`,
`stage-2-wings`, and `stage-3-crest` filenames are retained; the latter two use the
ascendant wings. `crest-only`, `small-wings`, and `small-wings-crest` are the added
filename prefixes. Each is followed by `-rank-{number}.webp`.

To add the extra rim, insert `layers/{metal}/outer-border.webp` after the wing
layer and before the crest and badge. It shares the standard square canvas.
`layout.json` records this optional layer and the six ready-made examples.
With the border on, use `wings-small-border.webp` or `wings-border.webp` instead
of the normal wing layer. Each wing is shifted outward by 68 pixels on the 2048 px
master canvas, keeping every feather visible. Switch back to the normal layer
when the border is off. The preview does this automatically for every color.
You can choose a different color for the outer border than the frame and wings;
use the color's `ornament_roots` path in `corporations.json`.

For arbitrary center/frame pairs, stack the matching `modular/centers/` layer
first and the `modular/frames/` layer over it. Both use the standard aligned
canvas; their masks preserve the badge silhouette. Use a combined corporation
badge layer for a predefined pair to save one image request.

The wide concept has its own proportions and text area. Its preview includes
editable HTML title/subtitle text, automatically fitted to the central area.
The narrow-ended shape needs its own ornament positions before using the existing
wing/crest layers with it; this concept currently previews the text area alone.

All images under `layers/` share a square canvas. Stack them at the same origin
and displayed size, using the same export resolution for every layer. Their
transparent padding is intentional and keeps attachments aligned. Standalone
`colors/` and `framed/` images use a tighter canvas and should not directly replace
the aligned badge layer.

Example CSS for stacking:

```css
.badge { position: relative; width: 256px; aspect-ratio: 1; }
.badge img { position: absolute; inset: 0; width: 100%; height: 100%; }
```

For a fixed combination, use a precomposed `progression/` or `awards/` image for a
single request. Use the separate layers to mix colors and ornaments dynamically.

## Compression and verification

- Artwork uses WebP quality 95.
- Rank numbers, award text, and corporation logos use lossless WebP.
- Alpha is lossless relative to the resized source for every export.
- Images are resized without cropping or upscaling, preserving layout geometry.
- Every export is decoded to check dimensions and alpha. Lossless artwork also has
  every RGBA pixel checked. Source PNG hashes are checked to confirm no changes.
- `manifest.json` includes all paths, dimensions, encoding modes, and file sizes.

From the project root, rebuild the copies and ZIP with:

```sh
python3 scripts/export_badge_webp.py
```

The script requires Pillow with WebP support. It overwrites generated WebP copies
and manifests, removes obsolete WebP files tracked by the previous manifest,
and rebuilds `output/badges/badge-webp-testing-kit.zip`.
