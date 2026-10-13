#!/usr/bin/env python3
"""Render user-proposed corporation palettes using the original badge geometry."""

from collections import defaultdict
from itertools import product
import argparse
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True

from PIL import Image, ImageDraw, ImageChops, ImageFilter
from badge_finishes import FINISHES, finish_image, palette_image
from render_badge_awards import accessory, blank, font, lettering, wings_for_outer_border, RANKS, PLATE_TEXT_BOX

ROOT = Path(__file__).resolve().parents[1]
BADGES = ROOT / "output/badges"
OUTPUT = BADGES / "corporations"
WEB = ROOT / "public/badges"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--palettes-only", action="store_true", help="Reuse existing shared ornaments and modular layers when only corporation palettes change")
    args = parser.parse_args()
    config = json.loads((ROOT / "scripts/corporation_badges.json").read_text())
    colors = {c["name"]: {"label": c["label"], "hex": c["color"]} for c in json.loads((BADGES / "palette.json").read_text())}
    colors["slime"] = {"label": "Slime", "hex": config["slime_hex"]}
    center_colors = list(colors)
    requested = set(colors)
    profiles, roots = {}, {}
    for key in sorted(requested):
        if key in FINISHES:
            profiles[key] = FINISHES[key]
            roots[key] = f"layers/{key}"
            continue
        value = colors[key]["hex"]
        rgb = tuple(int(value[i:i+2], 16) for i in (1, 3, 5))
        brightness = sum(channel * weight for channel, weight in zip(rgb, (0.2126, 0.7152, 0.0722)))
        profile = {"shadow": "#000000", "midtone": value, "highlight": "#FFFFFF", "ink": "#17202A" if brightness > 165 else "#F1F4F8"}
        if key == "gray":
            profile.update(shadow="#252930", highlight="#ADB2BA")
        elif key == "light-gray":
            profile.update(shadow="#747A84", highlight="#E0E3E8")
        profiles[key] = profile
        roots[key] = f"corporation-ornaments/{key}"
        if args.palettes_only:
            continue
        folder = OUTPUT / "ornaments" / key
        folder.mkdir(parents=True, exist_ok=True)
        for component in ("wings", "wings-small", "crest", "outer-border", "bottom-plate"):
            image, _ = accessory(component, profile)
            image.save(folder / f"{component}.png")
            if component.startswith("wings"):
                wings_for_outer_border(image).save(folder / f"{component}-border.png")
        for rank in RANKS:
            lettering(str(rank), profile, (1024, 1600), 108, fit_box=PLATE_TEXT_BOX).save(folder / f"rank-{rank}.png")

    with Image.open(BADGES / "badge-original.png") as image:
        original = image.convert("RGBA")
    with Image.open(BADGES / "badge-center-mask.png") as image:
        mask = image.convert("L")
    alpha = original.getchannel("A")
    # The mask transition is inside the opaque badge. An opaque center underlay
    # plus the inverse-mask frame reproduces the original two-color blend without
    # multiplying edge alpha or generating every color-pair permutation.
    # Extend the opaque underlay beneath the opaque frame by one full Lanczos
    # footprint at the smallest export size (2048 / 256 * 3 = 24 pixels).
    # Otherwise resizing separate masks creates a translucent interior seam.
    center_alpha = mask.point(lambda n: 255 if n > 0 else 0).filter(ImageFilter.MaxFilter(49))
    if ImageChops.multiply(center_alpha, ImageChops.invert(alpha)).getbbox():
        raise ValueError("Center-mask transition must stay within opaque artwork")
    frame_alpha = ImageChops.multiply(alpha, ImageChops.invert(mask))
    modular_centers, modular_frames = {}, {}
    for key in center_colors:
        if args.palettes_only:
            path = OUTPUT / "modular" / "centers" / f"{key}.png"
            if not path.is_file():
                raise FileNotFoundError(path)
            modular_centers[key] = f"modular/centers/{key}.webp"
            continue
        image = palette_image(original, key, colors[key]["hex"])
        image.putalpha(center_alpha)
        layer = blank()
        layer.paste(image, (397, 397))
        path = OUTPUT / "modular" / "centers" / f"{key}.png"
        path.parent.mkdir(parents=True, exist_ok=True)
        layer.save(path)
        modular_centers[key] = f"modular/centers/{key}.webp"
    for key in requested:
        if args.palettes_only:
            path = OUTPUT / "modular" / "frames" / f"{key}.png"
            if not path.is_file():
                raise FileNotFoundError(path)
            modular_frames[key] = f"modular/frames/{key}.webp"
            continue
        image = finish_image(original, profiles[key])
        image.putalpha(frame_alpha)
        layer = blank()
        layer.paste(image, (397, 397))
        path = OUTPUT / "modular" / "frames" / f"{key}.png"
        path.parent.mkdir(parents=True, exist_ok=True)
        layer.save(path)
        modular_frames[key] = f"modular/frames/{key}.webp"
    presets, pairs, distinct_pairs = [], defaultdict(set), defaultdict(set)
    asset_variant_count = 0
    for corp in config["corporations"]:
        original_pairs = list(product(corp["center_options"], corp["frame_options"]))
        proposal = corp.get("distinct_palette", {})
        distinct_pair = (proposal.get("center", original_pairs[0][0]), proposal.get("frame", original_pairs[0][1]))
        rendered = {}
        for center, frame in dict.fromkeys([*original_pairs, distinct_pair]):
            filename = f"{center}-{frame}"
            image = Image.composite(palette_image(original, center, colors[center]["hex"]), finish_image(original, profiles[frame]), mask)
            image.putalpha(alpha)
            layer = blank()
            layer.paste(image, (397, 397))
            path = OUTPUT / "badges" / corp["id"] / f"{filename}.png"
            path.parent.mkdir(parents=True, exist_ok=True)
            layer.save(path)
            rendered[(center, frame)] = {"id": filename, "center": center, "frame": frame, "label": f"{colors[center]['label']} / {colors[frame]['label']}", "badge": f"corporations/{corp['id']}/{filename}.webp"}
        variants = [rendered[pair] for pair in original_pairs]
        for center, frame in original_pairs:
            pairs[(center, frame)].add(corp["name"])
        distinct_pairs[distinct_pair].add(corp["name"])
        asset_variant_count += len(rendered)
        presets.append({**corp, "variants": variants, "distinct_variant": rendered[distinct_pair], "distinct_changed": distinct_pair != original_pairs[0]})
    duplicates = [{"center": center, "frame": frame, "corporations": sorted(names)} for (center, frame), names in sorted(pairs.items()) if len(names) > 1]
    distinct_duplicates = [{"center": center, "frame": frame, "corporations": sorted(names)} for (center, frame), names in sorted(distinct_pairs.items()) if len(names) > 1]
    if distinct_duplicates:
        raise ValueError(f"Distinct palettes must use unique center/frame pairs: {distinct_duplicates}")
    data = {"version": config["version"], "source": config["source"], "slash_policy": config["slash_policy"], "colors": colors, "center_colors": center_colors, "finish_colors": list(colors), "modular_centers": modular_centers, "modular_frames": modular_frames, "ornament_roots": roots, "frame_profiles": profiles, "accent_placement": config["accent_placement"], "corporations": presets, "duplicates": duplicates, "distinct_duplicates": distinct_duplicates, "default_palette": "distinct", "distinct_changed_count": sum(c["distinct_changed"] for c in presets), "corporation_count": len(presets), "variant_count": sum(len(c["variants"]) for c in presets), "asset_variant_count": asset_variant_count}
    OUTPUT.mkdir(parents=True, exist_ok=True)
    WEB.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(data, indent=2) + "\n"
    (OUTPUT / "presets.json").write_text(encoded)
    (WEB / "corporations.json").write_text(encoded)
    (WEB / "corporations.js").write_text("window.BADGE_CORPORATIONS = " + json.dumps(data, ensure_ascii=True) + ";\n")

    lines = ["# Corporation badge color proposals", "", "Center is the first color; frame is the second. These are design proposals, not official color specifications.", f"The Distinct palette uses {len(presets)} unique pairs, with {data['distinct_changed_count']} revised palettes. Original slash alternatives remain available in Original mode.", "", "## Revised palettes", "", "| Corporation | Original center / frame | Distinct center / frame | Design reason |", "| --- | --- | --- | --- |"]
    for corp in presets:
        if corp["distinct_changed"]:
            lines.append(f"| {corp['name']} | {corp['variants'][0]['label']} | {corp['distinct_variant']['label']} | {corp['distinct_palette']['reason']} |")
    lines += ["", "## All corporation palettes", "", "| Corporation | Distinct center / frame | Original center | Original frame | Optional accent |", "| --- | --- | --- | --- | --- |"]
    for corp in presets:
        labels = lambda keys: " / ".join(colors[key]["label"] for key in keys)
        accent = colors[corp["suggested_accent"]]["label"] if corp["suggested_accent"] else "—"
        lines.append(f"| {corp['name']} | {corp['distinct_variant']['label']} | {labels(corp['center_options'])} | {labels(corp['frame_options'])} | {accent} |")
    lines += ["", "## Repeated pairs in the original palettes", "", "The Distinct palette has no repeated center/frame pairs. The following repeats are retained for comparison in Original mode:", ""]
    for group in duplicates:
        lines.append(f"- **{colors[group['center']]['label']} / {colors[group['frame']]['label']}**: {', '.join(group['corporations'])}.")
    lines += ["", "Suggested accents color the outer border, crest, and bottom plate by default. Wings match the frame by default. Independent wing, crest, and outer-border color selectors can override these defaults.", f"Custom mode provides {len(center_colors)} centers and {len(colors)} colors each for frames, wings, crests, and outer borders, using separate aligned layers.", "Badge names stay visible in the gallery so color is not the only identifier.", "", "Names normalized against the project include Inventrix, PhoboLog, Terralabs Research, and Tharsis Republic; Gul means yellow. Slime is provisionally #B6D52D.", "", "Edit `scripts/corporation_badges.json`, then run `python3 scripts/render_corporation_badges.py` and the WebP exporter."]
    (WEB / "corporations.md").write_text("\n".join(lines) + "\n")

    # Compact labeled overview of the distinct proposal for every corporation.
    columns, cell_w, cell_h = 5, 300, 330
    sheet = Image.new("RGB", (columns * cell_w, ((len(presets) + columns - 1) // columns) * cell_h + 75), "#10141C")
    draw = ImageDraw.Draw(sheet)
    draw.text((24, 22), "Corporation badges — distinct center / frame colors", font=font(29, True), fill="#F1F5F9")
    for index, corp in enumerate(presets):
        variant = corp["distinct_variant"]
        x, y = (index % columns) * cell_w, (index // columns) * cell_h + 75
        with Image.open(OUTPUT / "badges" / corp["id"] / f"{variant['id']}.png") as source:
            badge = source.crop((397, 397, 1651, 1651)).resize((230, 230), Image.Resampling.LANCZOS)
        sheet.paste(badge, (x + 35, y), badge)
        size = 18
        while draw.textlength(corp["name"], font=font(size, True)) > cell_w - 12:
            size -= 1
        draw.text((x + cell_w // 2, y + 252), corp["name"], font=font(size, True), fill="#F1F5F9", anchor="mm")
        draw.text((x + cell_w // 2, y + 282), variant["label"], font=font(17), fill="#A8B4C7", anchor="mm")
    sheet.save(OUTPUT / "corporations-preview.png")
    print(f"Rendered {len(presets)} distinct pairs ({data['distinct_changed_count']} revised), {data['variant_count']} original alternatives, and {asset_variant_count} total badge assets", flush=True)


if __name__ == "__main__":
    main()
