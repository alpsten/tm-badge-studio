#!/usr/bin/env python3
"""Assemble the modular plate/rank/wing concept from saved silver artwork."""

import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True

from PIL import Image, ImageDraw, ImageFont

from tint_badge import tint_badge
from badge_fonts import font


ROOT = Path(__file__).resolve().parents[1]
BADGES = ROOT / "output/badges"
OUTPUT = BADGES / "upgrade-sketch"
SIZE = (2048, 2048)
GOLD = "#C99A2E"


def blank() -> Image.Image:
    return Image.new("RGBA", SIZE, (0, 0, 0, 0))


def accessory(filename: str, width: int, top: int) -> tuple[Image.Image, dict]:
    with Image.open(OUTPUT / "masters" / filename) as image:
        original = image.convert("RGBA")
    # Use visible alpha to locate the object, ignoring isolated near-invisible
    # pixels in generated padding. Keep four pixels around the visible outline.
    bounds = original.getchannel("A").point(lambda value: 255 if value >= 16 else 0).getbbox()
    if bounds is None:
        raise ValueError(f"No visible artwork in {filename}")
    left, upper, right, lower = bounds
    crop = (max(0, left - 4), max(0, upper - 4), min(original.width, right + 4), min(original.height, lower + 4))
    cropped = original.crop(crop)
    height = round(cropped.height * width / cropped.width)
    resized = cropped.resize((width, height), Image.Resampling.LANCZOS)
    layer = blank()
    position = ((SIZE[0] - width) // 2, top)
    layer.alpha_composite(tint_badge(resized, GOLD), position)
    return layer, {"source": f"masters/{filename}", "source_crop": crop, "size": [width, height], "position": position, "midtone": GOLD}


def stack(*layers: Image.Image) -> Image.Image:
    result = blank()
    for layer in layers:
        result.alpha_composite(layer)
    return result


def main() -> None:
    layers_dir = OUTPUT / "layers"
    layers_dir.mkdir(parents=True, exist_ok=True)
    badge = blank()
    with Image.open(BADGES / "badge-gold-frame-black-center.png") as original:
        badge.paste(original, (397, 397))

    plate, plate_layout = accessory("bottom-plate-silver.png", 640, 1510)
    wings, wings_layout = accessory("wings-silver.png", 1900, 680)

    marker = blank()
    marker_draw = ImageDraw.Draw(marker)
    marker_center = (1024, 1600)
    marker_draw.text((marker_center[0], marker_center[1] + 3), "1", font=font(98, bold=True), fill="#443215", anchor="mm", stroke_width=1)
    marker_draw.text(marker_center, "1", font=font(98, bold=True), fill="#F5DB92", anchor="mm")

    for name, layer in {"badge": badge, "bottom-plate-gold": plate, "rank-1": marker, "wings-gold": wings}.items():
        layer.save(layers_dir / f"{name}.png")

    stage_one = stack(badge, plate, marker)
    stage_two = stack(wings, badge, plate, marker)
    stage_one.save(OUTPUT / "stage-1-plate-rank-1.png")
    stage_two.save(OUTPUT / "stage-2-wings-rank-1.png")
    plate_and_rank = stack(plate, marker)
    plate_and_rank.crop(plate.getchannel("A").getbbox()).save(OUTPUT / "bottom-plate-with-rank-1.png")

    preview = Image.new("RGB", (1800, 1170), "#10141C")
    draw = ImageDraw.Draw(preview)
    draw.text((48, 35), "Badge progression — first sketch", font=font(34, bold=True), fill="#F1F5F9")
    draw.text((48, 84), "The plate carries the rank. Wings mark the next tier; the plate restarts at 1.", font=font(22), fill="#A8B4C7")
    for x, composite, heading, caption in [
        (36, stage_one, "PLATE TIER  /  RANK 1", "Badge + bottom plate + separate rank marker"),
        (916, stage_two, "WING TIER  /  RANK 1", "Same badge and plate + independent wing layer"),
    ]:
        draw.rounded_rectangle((x, 144, x + 848, 1060), radius=20, fill="#1B2230")
        thumbnail = composite.resize((828, 828), Image.Resampling.LANCZOS)
        preview.paste(thumbnail, (x + 10, 142), thumbnail)
        draw.text((x + 424, 982), heading, font=font(25, bold=True), fill="#F5DB92", anchor="mm")
        draw.text((x + 424, 1020), caption, font=font(19), fill="#A8B4C7", anchor="mm")
    draw.text((48, 1102), "Reusable layers · shared 2048 × 2048 canvas · original badge pixels retained", font=font(21), fill="#A8B4C7")
    preview.save(OUTPUT / "progression-preview.png")

    layout = {
        "canvas": SIZE,
        "badge": {"source": "../badge-gold-frame-black-center.png", "position": [397, 397], "size": [1254, 1254], "resized": False},
        "plate": plate_layout,
        "wings": wings_layout,
        "rank": {"text": "1", "center": marker_center, "font_size": 98, "color": "#F5DB92"},
        "stage_one_order": ["badge", "bottom-plate-gold", "rank-1"],
        "stage_two_order": ["wings-gold", "badge", "bottom-plate-gold", "rank-1"],
        "tier_logic": "The plate tracks rank within a tier. Adding wings starts a new tier at rank 1; no rank cap is defined by this sketch.",
    }
    (OUTPUT / "layout.json").write_text(json.dumps(layout, indent=2) + "\n")
    print(f"Saved two stage previews, four aligned layers, rank plate, and layout to {OUTPUT}")


if __name__ == "__main__":
    main()
