#!/usr/bin/env python3
"""Build standalone badge colors, their labeled preview, and the PNG color kit."""

import json
from pathlib import Path
import sys
from zipfile import ZipFile, ZIP_DEFLATED

sys.dont_write_bytecode = True

from PIL import Image, ImageDraw, ImageFont
from badge_finishes import palette_image
from badge_fonts import font as badge_font

ROOT = Path(__file__).resolve().parents[1] / "output/badges"


def main():
    palette = json.loads((ROOT / "palette.json").read_text())
    with Image.open(ROOT / "badge-original.png") as image:
        source = image.convert("RGBA")
    columns, cell = 6, 230
    sheet = Image.new("RGB", (columns * cell, ((len(palette) + columns - 1) // columns) * 275 + 65), "#10141C")
    draw = ImageDraw.Draw(sheet)
    font = badge_font(19)
    draw.text((24, 20), f"Badge colors — {len(palette)} finishes", fill="#F1F5F9", font=font)
    names = ["palette.json", "badge-palette-preview.png"]
    for index, color in enumerate(palette):
        tinted = palette_image(source, color["name"], color["color"])
        name = f"badge-{color['name']}.png"
        path = ROOT / name
        unchanged = False
        if path.exists():
            with Image.open(path) as current:
                unchanged = current.size == tinted.size and current.convert("RGBA").tobytes() == tinted.tobytes()
        if not unchanged:
            tinted.save(path)
        names.append(name)
        thumb = tinted.resize((210, 210), Image.Resampling.LANCZOS)
        x, y = index % columns * cell, index // columns * 275 + 65
        sheet.paste(thumb, (x + 10, y), thumb)
        draw.text((x + cell // 2, y + 230), color["label"], fill="#F1F5F9", font=font, anchor="mm")
        draw.text((x + cell // 2, y + 254), color["color"], fill="#A8B4C7", font=font, anchor="mm")
    sheet.save(ROOT / "badge-palette-preview.png")
    with ZipFile(ROOT / "badge-colors.zip", "w", ZIP_DEFLATED) as archive:
        for name in names:
            archive.write(ROOT / name, name)
    print(f"Rendered {len(palette)} badge colors and updated the preview and PNG kit", flush=True)


if __name__ == "__main__":
    main()
