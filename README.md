# Terraforming Mars Badge Studio

A standalone badge mixer and achievement gallery. Everything shown in the browser
is bundled here: no database, API keys, npm install, or build step is required.

Includes 47 corporation logos and their color presets, 6 expansion/Promo logos, 122 achievement emblems in
13 sections, the three podium awards, and 2,584 WebP badge/layer exports at 256 and
512 pixels. Mix center/frame colors, wings, crests, borders, rank plates, and logos.

## Preview locally

From this repository's root:

```sh
python3 -m http.server 8000 --directory public
```

Open <http://localhost:8000/>. The entry page opens the badge studio; its
**Achievement gallery** link opens all achievement sections.

## Files

| Location | Contents |
| --- | --- |
| `public/badges/preview.html` / `preview.js` | Badge studio and corporation gallery |
| `public/badges/achievement-concepts/` | Achievement gallery, section pages, emblems, and prompts |
| `public/badges/256/` / `512/` | All web badge and layer exports |
| `scripts/` | Python renderers, palette/logo settings, and verification |
| `output/badges/badge-original.png` / `badge-center-mask.png` | Original badge and center mask |
| `output/badges/awards-kit/masters/` | Original ornament and wide-badge artwork |
| `output/badges/logos/originals/` | Original artwork for 47 corporations and 6 expansion/Promo emblems |
| `output/imagegen/achievements/` | Achievement masters, placement metadata, and prompts |
| `output/badges/upgrade-sketch/masters/` | Earlier progression sketch source artwork |
| `docs/` | Achievement and progression design notes |

The initial local copy also retains the full PNG render archive, preview sheets,
retired drafts, and ZIP bundles. These large derived files are ignored by Git.
All current artwork is included in the web exports, and its source masters are
included in Git so the full-resolution current PNGs can be rebuilt after cloning.
Generation prompts use repository-relative paths; historical reference filenames
describe earlier generation attempts and are not build dependencies.

## Verify and rebuild

Check the website's links, WebP manifest, logo sources, achievement hashes, and
required master artwork using Python's standard library:

```sh
python3 scripts/verify_assets.py
```

The website is already rendered. Rebuilding is optional and needs Python 3.10+
and Pillow with WebP support:

```sh
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 scripts/render_badge_palette.py
python3 scripts/render_badge_frames.py
python3 scripts/render_badge_awards.py
python3 scripts/render_corporation_badges.py
python3 scripts/render_badge_logos.py
python3 scripts/export_badge_webp.py
python3 scripts/sync_achievements.py
python3 scripts/verify_assets.py
```

On Windows activate the environment with `.venv\Scripts\activate` instead.
Allow approximately 2 GB for the generated full-resolution PNGs and ZIPs.
Rebuilding uses the originals stored in this repository; it does not call an image
generation service. The optional historical sketch renderer is documented in
[scripts/README.md](scripts/README.md).

Fonts resolve to Arial, Liberation Sans, DejaVu Sans, or Pillow's default font.
The bundled artwork is unchanged; newly rendered labels may vary by installed
font. Set `BADGE_FONT_REGULAR` and `BADGE_FONT_BOLD` to local font files if needed.

Edit corporation palettes in `scripts/corporation_badges.json` and logo fitting
in `scripts/badge_logos.json`. The authoritative achievement catalogue is the local,
Git-ignored `docs/achievements-plan.md`; it is not included when cloning this repo.
The gallery's current names, descriptions, and fitted positions live in each
`output/imagegen/achievements/<section>/concepts.json`. Reflect reviewed catalogue
changes there, then run `sync_achievements.py` to copy the metadata and unchanged
masters into the gallery. The script does not read the local Markdown plan.
When replacing an emblem, update its crop, fitted positions, and SHA-256 together.
When adding a section, create its page and register it in the gallery's
`sections.js`. See [scripts/README.md](scripts/README.md) for the rendering details.

The gallery previews achievement artwork and descriptions. It does not evaluate
tournament results or award achievements to accounts.
