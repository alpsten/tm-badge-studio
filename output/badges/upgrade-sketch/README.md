# Badge progression sketch

The plate displays rank within the current tier. The first upgrade adds wings
behind the badge and restarts the plate at rank 1. The maximum rank in each tier
is intentionally undecided.

- `progression-preview.png`: the two stages side by side.
- `stage-1-plate-rank-1.png`: badge, plate, and rank marker on transparency.
- `stage-2-wings-rank-1.png`: the same badge, plate, and marker, plus wings.
- `bottom-plate-with-rank-1.png`: a compact preview of the plate with its marker.
- `layers/`: four separate transparent PNGs aligned on a 2048 × 2048 canvas.
- `masters/`: the original neutral silver plate and wing-pair artwork.
- `layout.json`: component placement and layer order.
- `prompts.json`: exact prompts used with the built-in imagegen tool.

Stack the layers at the same origin, using the same displayed size:

1. `layers/wings-gold.png` (wing tier only)
2. `layers/badge.png`
3. `layers/bottom-plate-gold.png`
4. `layers/rank-1.png`

The badge layer retains the existing gold-frame/black-center PNG at its original
1254 × 1254 resolution, positioned at (397, 397). Another existing badge can be
placed at those same coordinates. The rank numeral is separate from the plate.
Only the preview sheet scales the completed badges down.

New ornament artwork was generated with the built-in imagegen tool. The saved
silver masters are unchanged. The render script crops transparent padding,
scales each ornament to its intended size, tints it using `tint_badge.py`, and
places it on the shared canvas. The gold example uses midtone `#C99A2E`.

From the project root, rebuild this sketch with:

```sh
python3 scripts/render_badge_upgrade_sketch.py
```

This command replaces the derived sketch layers and previews. It does not modify
the existing badges or generated masters. The renderer uses Pillow and uses
Arial from macOS when available, with a default-font fallback.
