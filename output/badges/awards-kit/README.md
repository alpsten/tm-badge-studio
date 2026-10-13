# Modular badge ornaments and podium awards

## Preview sheets

- `podium-preview.png`: Champion, 2nd place, and 3rd place.
- `progression-preview.png`: all seven milestones across six gold ornament combinations.
- `progression-{finish}-preview.png`: the same milestones in bronze, silver,
  steel, black, and white.
- `rank-plates-preview.png`: all seven numbers fitted to all six plate finishes.
- `assets-preview.png`: the independent ornament designs, including the crown.
- `wing-comparison-preview.png`: the six combinations side by side at badge size.
- `outer-border-preview.png`: the same badge with and without the optional rim.

## Ready-to-use awards

- `awards/champion.png`: gold frame and crest, exclusive gold laurels, a central crown,
  and a CHAMPION plate.
- `awards/second-place.png`: silver frame, crest and ascendant wings, placement 2,
  and a 2ND PLACE plate.
- `awards/third-place.png`: bronze frame, crest and ascendant wings, placement 3,
  and a 3RD PLACE plate.

All three are transparent 2048 × 2048 PNGs. The Champion has a laurel silhouette;
the two other podium awards use wings. These award placements are independent of
the progression tier and rank.

## Interchangeable layers

`layers/{finish}/` supports bronze, silver, gold, steel, black, and white.
Each contains aligned transparent PNGs for the badge, bottom plate, small wing
pair, ascendant wing pair, crest, outer border, and rank markers
**1, 3, 5, 10, 20, 25, 50**. Placement numerals and award titles are additional
separate layers. Gold also contains the exclusive Champion laurels and central
crown. The Champion does not use a placement numeral 1.

The outer border is optional and independent of wings/crest. Stack
`layers/{finish}/outer-border.png` after wings but before crest and badge.
`examples/{finish}/outer-border-rank-1.png` provides one assembled example per finish.
It adds a second beveled rim around the original badge without changing its pixels.
Use `wings-small-border.png` or `wings-border.png` when that rim is enabled.
These translate each wing outward by 68 pixels without scaling or clipping,
so the wings attach to the outer rim. Normal wings keep their original position.
The `wing_attachment` entry in `layout.json` records the offset and layer names.
The website mixer also supports independent outer-border colors; the corporation
renderer extends the six original finishes to the full ornament color palette.

Every layer uses the same 2048 × 2048 canvas. Stack layers at the same origin and
display size. `layout.json` lists the exact layer order for all 252 progression
badges and three awards, plus component positions, text bounds, and finish profiles.

`progression/{finish}/` contains every combination of six ornament arrangements and
the seven milestones. `plates/{finish}/` contains compact transparent
numbered plates for all seven milestones (42 files). The aligned blank plate and
number layers are also retained for mixing and matching.

The original 1254 × 1254 badge is placed at (397, 397) without resizing or
changing its pixels. Any of the existing framed badges can replace that layer
at the same position. The sample center is black.

The rank numeral is separate from the plate. Each tier uses the sequence
1, 3, 5, 10, 20, 25, 50; a newly unlocked ornament starts a new tier at rank 1.
The renderer measures each numeral including its shadow, adjusts its size if
needed, and centers it within a safe rectangle inside the recessed plate face.
Award titles use the same fitting logic.

## Artwork and rebuild

Wings and crest are independently selectable: no wings, one small pair, or one
ascendant pair; crest off or on. This gives plate alone, crest only, small wings,
small wings + crest, ascendant wings, and ascendant wings + crest.

`layers/{finish}/wings-small.png` uses the restored small-wing master at its
original position. `layers/{finish}/wings.png` uses the approved tall ascendant
pair. Second and third place use the ascendant pair. Only the superseded old
full-wing design remains retired outside the active kit.

The `styles` metadata records the file prefix and layer order for every choice.
Existing three-stage filenames are retained for compatibility; the new prefixes
are `crest-only`, `small-wings`, and `small-wings-crest`, followed by `-rank-{n}`.

`masters/` contains seven neutral silver ornament masters and a gold wide-hexagon
concept. The crest, wings,
laurels, and crown were generated with the built-in imagegen tool; original
prompts are recorded in the JSON files in this directory, including historical
prompts for discarded designs. The approved plate and small wings are reused.
The new master is `masters/wings-ascendant-silver.png`; its exact built-in imagegen
prompt and reference are recorded in `ascendant-wings-prompt.json`.
The border and wide-badge masters were generated with the built-in imagegen tool;
their exact prompts are saved in `border-and-wide-prompts.json`.

`concepts/wide-hex-gold.png` is a cropped blank wide six-sided badge for text.
Its center is intentionally blank so the website can render live text. It has
different proportions from the standard badge and needs its own ornament positions.

The renderer scales and positions the ornaments, uses deterministic finish
profiles from `scripts/badge_finishes.py`, and draws labels as separate layers. It does not
regenerate or redraw the existing badge. The only laurels exported for use are
gold; the silver master is retained as editable source artwork.

From the project root:

```sh
python3 scripts/render_badge_awards.py
```

First run `python3 scripts/render_badge_frames.py` if frame profiles have changed.
The awards renderer replaces derived files within `output/badges/awards-kit/`
and rebuilds `output/badges/badge-awards-and-ornaments.zip`.
It leaves existing framed badge files and active master images intact.
It requires Pillow and uses Arial from macOS when available, with a default-font
fallback. The ZIP contains all assets, previews, this guide, and the layout and
prompt manifests.
