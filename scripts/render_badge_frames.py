#!/usr/bin/env python3
"""Render all center colors in the six shared frame finishes."""

import json
from pathlib import Path
import sys
from zipfile import ZIP_DEFLATED, ZipFile

sys.dont_write_bytecode = True

from PIL import Image, ImageDraw, ImageFont
from badge_finishes import FINISHES, finish_image, palette_image
from badge_fonts import font

ROOT = Path(__file__).resolve().parents[1] / "output/badges"
OUTPUT = ROOT / "framed"


def main():
    palette = json.loads((ROOT / "palette.json").read_text())
    with Image.open(ROOT / "badge-original.png") as image:
        source = image.convert("RGBA")
    with Image.open(ROOT / "badge-center-mask.png") as image:
        mask = image.convert("L")
    alpha = source.getchannel("A")
    entries = []
    face = font(20, True)
    all_preview = Image.new("RGB", (6 * 228, 330), "#10141C")
    for index, (finish, profile) in enumerate(FINISHES.items()):
        frame = finish_image(source, finish)
        sheet = Image.new("RGB", (6 * 228, ((len(palette) + 5) // 6) * 270 + 70), "#10141C")
        draw = ImageDraw.Draw(sheet)
        draw.text((28, 24), f"{finish.title()} frame — all {len(palette)} centers", fill="#F1F5F9", font=face)
        for number, color in enumerate(palette):
            center = palette_image(source, color["name"], color["color"])
            badge = Image.composite(center, frame, mask)
            badge.putalpha(alpha)
            filename = f"{finish}-frame/badge-{color['name']}.png"
            path = OUTPUT / filename
            path.parent.mkdir(parents=True, exist_ok=True)
            badge.save(path)
            thumb = badge.resize((216, 216), Image.Resampling.LANCZOS)
            x, y = (number % 6) * 228 + 6, (number // 6) * 270 + 70
            sheet.paste(thumb, (x, y), thumb)
            draw.text((x + 108, y + 237), color["label"], fill="#F1F5F9", font=face, anchor="mm")
            if color["name"] == "blue":
                all_preview.paste(thumb, (index * 228 + 6, 28), thumb)
            entries.append({"file": filename, "frame": finish, "frame_color": profile["midtone"], "frame_profile": profile, "center": color["name"], "center_label": color["label"], "center_color": color["color"]})
        sheet.save(OUTPUT / f"badge-{finish}-frame-preview.png")
        ImageDraw.Draw(all_preview).text((index * 228 + 114, 285), finish.title(), fill="#F1F5F9", font=face, anchor="mm")
    all_preview.save(OUTPUT / "badge-frame-finishes-preview.png")
    (OUTPUT / "combinations.json").write_text(json.dumps(entries, indent=2) + "\n")
    with ZipFile(ROOT / "badge-framed-colors.zip", "w", ZIP_DEFLATED) as bundle:
        names = [item["file"] for item in entries] + [f"badge-{name}-frame-preview.png" for name in FINISHES] + ["badge-frame-finishes-preview.png", "combinations.json"]
        for name in names:
            bundle.write(OUTPUT / name, arcname=name)
    print(f"Saved {len(entries)} frames across {len(FINISHES)} finishes", flush=True)


if __name__ == "__main__":
    main()
