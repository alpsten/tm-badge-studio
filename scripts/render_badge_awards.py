#!/usr/bin/env python3
"""Render modular badge ornaments, progression sketches, and podium awards."""

import json
from pathlib import Path
import sys
from zipfile import ZipFile, ZIP_DEFLATED

sys.dont_write_bytecode = True

from PIL import Image, ImageDraw, ImageFont

from badge_finishes import FINISHES, finish_image
from badge_fonts import font


ROOT = Path(__file__).resolve().parents[1]
BADGES = ROOT / "output/badges"
OUTPUT = BADGES / "awards-kit"
SIZE = (2048, 2048)
BORDER_WING_SHIFT = 68
METALS = {name: profile["midtone"] for name, profile in FINISHES.items()}
INK = {name: profile["ink"] for name, profile in FINISHES.items()}
RANKS = (1, 3, 5, 10, 20, 25, 50)
PLATE_TEXT_BOX = (804, 1558, 1244, 1642)
COMPONENTS = {
    "bottom-plate": ("bottom-plate-silver.png", 640, 1510),
    "outer-border": ("outer-border-silver.png", 1260, 316),
    "wings": ("wings-ascendant-silver.png", 1900, 140),
    "wings-small": ("wings-small-silver.png", 1900, 680),
    "crest": ("crest-silver.png", 560, 210),
    "laurels": ("laurels-silver.png", 1660, 260),
    "crown": ("crown-silver.png", 560, 830),
}
STYLES = [
    ("plate", "stage-1-plate", ["badge", "bottom-plate"], "Plate"),
    ("crest-only", "crest-only", ["crest", "badge", "bottom-plate"], "Crest only"),
    ("small-wings", "small-wings", ["wings-small", "badge", "bottom-plate"], "Small wings"),
    ("small-wings-crest", "small-wings-crest", ["wings-small", "crest", "badge", "bottom-plate"], "Small wings + Crest"),
    ("wings", "stage-2-wings", ["wings", "badge", "bottom-plate"], "Ascendant wings"),
    ("crest", "stage-3-crest", ["wings", "crest", "badge", "bottom-plate"], "Ascendant wings + Crest"),
]


def blank() -> Image.Image:
    return Image.new("RGBA", SIZE, (0, 0, 0, 0))


def wings_for_outer_border(layer: Image.Image) -> Image.Image:
    """Move each wing outward without scaling it or clipping visible pixels."""
    result = blank()
    result.paste(layer.crop((0, 0, 1024, 2048)), (-BORDER_WING_SHIFT, 0))
    result.paste(layer.crop((1024, 0, 2048, 2048)), (1024 + BORDER_WING_SHIFT, 0))
    if result.getchannel("A").histogram() != layer.getchannel("A").histogram():
        raise ValueError("Outer-border wing placement clips artwork")
    return result


def save(image: Image.Image, relative: str) -> None:
    path = OUTPUT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)


def accessory(component: str, metal: str | dict) -> tuple[Image.Image, dict]:
    filename, width, top = COMPONENTS[component]
    with Image.open(OUTPUT / "masters" / filename) as source:
        source = source.convert("RGBA")
    bounds = source.getchannel("A").point(lambda value: 255 if value >= 16 else 0).getbbox()
    if bounds is None:
        raise ValueError(f"No visible artwork in {filename}")
    x0, y0, x1, y1 = bounds
    crop = (max(0, x0 - 4), max(0, y0 - 4), min(source.width, x1 + 4), min(source.height, y1 + 4))
    cropped = source.crop(crop)
    height = round(cropped.height * width / cropped.width)
    position = ((SIZE[0] - width) // 2, top)
    layer = blank()
    resized = cropped.resize((width, height), Image.Resampling.LANCZOS)
    layer.alpha_composite(finish_image(resized, metal), position)
    return layer, {"master": f"masters/{filename}", "crop": crop, "size": [width, height], "position": position}


def lettering(text: str, metal: str | dict, center: tuple[int, int], size: int, *, fit_box=None) -> Image.Image:
    layer = blank()
    ink = metal["ink"] if isinstance(metal, dict) else INK[metal]
    draw = ImageDraw.Draw(layer)
    if fit_box is not None:
        x0, y0, x1, y1 = fit_box
        while size > 0:
            face = font(size, True)
            offset = max(2, size // 35)
            left, top, right, bottom = draw.textbbox((0, 0), text, font=face, stroke_width=1)
            width, height = right - left, bottom - top + offset
            if width <= x1 - x0 and height <= y1 - y0:
                break
            size -= 1
        if size == 0:
            raise ValueError(f"Text does not fit plate: {text}")
        x = x0 + (x1 - x0 - width) // 2 - left
        y = y0 + (y1 - y0 - height) // 2 - top
        draw.text((x, y + offset), text, font=face, fill="#14171C", stroke_width=1)
        draw.text((x, y), text, font=face, fill=ink)
        layer.info["font_size"] = size
        return layer
    offset = max(2, size // 35)
    draw.text((center[0], center[1] + offset), text, font=font(size, True), fill="#14171C", anchor="mm", stroke_width=1)
    draw.text(center, text, font=font(size, True), fill=ink, anchor="mm")
    return layer


def rank_plates_preview() -> None:
    pad, gap, tile_w, tile_h = 32, 14, 270, 170
    width = pad * 2 + len(RANKS) * tile_w + (len(RANKS) - 1) * gap
    sheet = Image.new("RGB", (width, 184 + len(METALS) * 222), "#10141C")
    draw = ImageDraw.Draw(sheet)
    draw.text((pad, 28), "Plate milestones — 1, 3, 5, 10, 20, 25, 50", font=font(34, True), fill="#F1F5F9")
    draw.text((pad, 80), "All seven numbers fit inside the recessed plate face. Marker and plate remain separate layers.", font=font(21), fill="#A8B4C7")
    for row, metal in enumerate(METALS):
        y = 170 + row * 222
        draw.text((pad, y - 36), metal.upper(), font=font(23, True), fill="#F1F5F9")
        for col, rank in enumerate(RANKS):
            x = pad + col * (tile_w + gap)
            draw.rounded_rectangle((x, y, x + tile_w, y + tile_h), radius=14, fill="#1B2230")
            with Image.open(OUTPUT / f"plates/{metal}/plate-rank-{rank}.png") as plate:
                plate.thumbnail((250, 104), Image.Resampling.LANCZOS)
                sheet.paste(plate, (x + (tile_w - plate.width) // 2, y + 30), plate)
            draw.text((x + tile_w // 2, y + 137), str(rank), font=font(22, True), fill="#F1F5F9", anchor="mm")
    save(sheet, "rank-plates-preview.png")


def progression_preview(metal, styles) -> None:
    pad, gap, cell, row_height = 28, 14, 264, 330
    width = pad * 2 + len(RANKS) * cell + (len(RANKS) - 1) * gap
    sheet = Image.new("RGB", (width, 140 + len(styles) * row_height), "#10141C")
    draw = ImageDraw.Draw(sheet)
    draw.text((pad, 28), f"{metal.title()} badge milestones", font=font(34, True), fill="#F1F5F9")
    draw.text((pad, 78), "Six ornament combinations, each with milestones 1, 3, 5, 10, 20, 25, 50.", font=font(21), fill="#A8B4C7")
    for row, (_, prefix, _, title) in enumerate(styles):
        y = 154 + row * row_height
        draw.text((pad, y - 27), title, font=font(21, True), fill="#F1F5F9")
        for col, rank in enumerate(RANKS):
            x = pad + col * (cell + gap)
            draw.rounded_rectangle((x, y, x + cell, y + 288), radius=14, fill="#1B2230")
            with Image.open(OUTPUT / f"progression/{metal}/{prefix}-rank-{rank}.png") as badge:
                thumb = badge.resize((cell, cell), Image.Resampling.LANCZOS)
                sheet.paste(thumb, (x, y - 4), thumb)
            draw.text((x + cell // 2, y + 267), str(rank), font=font(20, True), fill="#F1F5F9", anchor="mm")
    save(sheet, "progression-preview.png" if metal == "gold" else f"progression-{metal}-preview.png")


def preview(title: str, subtitle: str, cards: list, filename: str, *, card_width: int, image_size: int) -> None:
    gap, pad, header = 20, 30, 120
    width = 2 * pad + len(cards) * card_width + (len(cards) - 1) * gap
    height = header + image_size + 150
    sheet = Image.new("RGB", (width, height), "#10141C")
    draw = ImageDraw.Draw(sheet)
    draw.text((pad, 26), title, font=font(34, True), fill="#F1F5F9")
    draw.text((pad, 76), subtitle, font=font(21), fill="#A8B4C7")
    for index, (image, heading, caption, accent) in enumerate(cards):
        x = pad + index * (card_width + gap)
        draw.rounded_rectangle((x, header, x + card_width, height - 26), radius=20, fill="#1B2230")
        thumb = image.resize((image_size, image_size), Image.Resampling.LANCZOS)
        sheet.paste(thumb, (x + (card_width - image_size) // 2, header + 4), thumb)
        draw.text((x + card_width // 2, header + image_size + 38), heading, font=font(27, True), fill=accent, anchor="mm")
        draw.text((x + card_width // 2, header + image_size + 80), caption, font=font(19), fill="#A8B4C7", anchor="mm")
    save(sheet, filename)


def wing_comparison_preview() -> None:
    sheet = Image.new("RGB", (900, 720), "#10141C")
    draw = ImageDraw.Draw(sheet)
    for index, (_, prefix, _, title) in enumerate(STYLES):
        x, y = (index % 3) * 300, (index // 3) * 360
        with Image.open(OUTPUT / f"progression/gold/{prefix}-rank-1.png") as badge:
            thumb = badge.resize((272, 272), Image.Resampling.LANCZOS)
            sheet.paste(thumb, (x + 14, y + 12), thumb)
        draw.text((x + 150, y + 318), title, font=font(19, True), fill=INK["gold"], anchor="mm")
    save(sheet, "wing-comparison-preview.png")


def wide_badge_concept() -> dict:
    with Image.open(OUTPUT / "masters/wide-hex-gold.png") as source:
        image = source.convert("RGBA")
    bounds = image.getchannel("A").point(lambda value: 255 if value >= 16 else 0).getbbox()
    if bounds is None:
        raise ValueError("Wide hexagon master is empty")
    x0, y0, x1, y1 = bounds
    crop = (max(0, x0 - 4), max(0, y0 - 4), min(image.width, x1 + 4), min(image.height, y1 + 4))
    image = image.crop(crop)
    save(image, "concepts/wide-hex-gold.png")
    return {"master": "masters/wide-hex-gold.png", "file": "concepts/wide-hex-gold.png", "crop": crop, "size": image.size, "text_box_fraction": [0.18, 0.24, 0.82, 0.76], "note": "Wide badge concept; overlay live text. Its proportions need their own ornament positions."}


def main() -> None:
    layers = {}
    manifest = {"canvas": SIZE, "badge_position": [397, 397], "metals": METALS, "finishes": FINISHES, "ranks": RANKS, "plate_text_box": PLATE_TEXT_BOX, "components": {}, "assemblies": {}, "plates": {}, "text": {}}

    def register(metal, name, image):
        path = f"layers/{metal}/{name}.png"
        layers[path] = image
        save(image, path)
        return path

    for metal in METALS:
        badge = blank()
        with Image.open(BADGES / "framed" / f"{metal}-frame" / "badge-black.png") as source:
            badge.paste(source, (397, 397))
        register(metal, "badge", badge)
        for component in COMPONENTS:
            if component in ("laurels", "crown") and metal != "gold":
                continue
            layer, placement = accessory(component, metal)
            path = register(metal, component, layer)
            manifest["components"][path] = placement
            if component in ("wings", "wings-small"):
                border_path = register(metal, f"{component}-border", wings_for_outer_border(layer))
                manifest["components"][border_path] = {"source_layer": path, "left_offset": [-BORDER_WING_SHIFT, 0], "right_offset": [BORDER_WING_SHIFT, 0]}
        for rank in RANKS:
            marker = lettering(str(rank), metal, (1024, 1600), 108, fit_box=PLATE_TEXT_BOX)
            marker_path = register(metal, f"rank-{rank}", marker)
            manifest["text"][marker_path] = {"text": str(rank), "fit_box": PLATE_TEXT_BOX, "font_size": marker.info["font_size"], "bounds": marker.getchannel("A").getbbox()}
            plate_path = f"layers/{metal}/bottom-plate.png"
            plate = layers[plate_path].copy()
            plate.alpha_composite(marker)
            crop = layers[plate_path].getchannel("A").getbbox()
            filename = f"plates/{metal}/plate-rank-{rank}.png"
            save(plate.crop(crop), filename)
            manifest["plates"][filename] = {"layers": [plate_path, marker_path], "crop": crop}

    def assemble(filename, metal, names):
        image = blank()
        paths = [f"layers/{metal}/{name}.png" for name in names]
        for path in paths:
            image.alpha_composite(layers[path])
        save(image, filename)
        manifest["assemblies"][filename] = paths
        return image

    manifest["styles"] = [{"id": slug, "file_prefix": prefix, "layers": order, "label": title} for slug, prefix, order, title in STYLES]
    manifest["tiers"] = manifest["styles"]
    for metal in METALS:
        for _, prefix, order, _ in STYLES:
            for rank in RANKS:
                assemble(f"progression/{metal}/{prefix}-rank-{rank}.png", metal, order + [f"rank-{rank}"])
        progression_preview(metal, STYLES)
    rank_plates_preview()
    wing_comparison_preview()

    podium = []
    awards = [
        ("champion", "gold", None, "CHAMPION", "Gold crown and exclusive laurels", ["laurels", "crest"]),
        ("second-place", "silver", "2", "2ND PLACE", "Silver crest and ascendant wings", ["wings", "crest"]),
        ("third-place", "bronze", "3", "3RD PLACE", "Bronze crest and ascendant wings", ["wings", "crest"]),
    ]
    for slug, metal, number, label, caption, ornaments in awards:
        symbol = "crown"
        if number is not None:
            symbol = f"placement-{number}"
            number_layer = register(metal, symbol, lettering(number, metal, (1024, 1000), 430))
            manifest["text"][number_layer] = {"text": number, "center": [1024, 1000], "font_size": 430}
        label_image = lettering(label, metal, (1024, 1600), 69, fit_box=PLATE_TEXT_BOX)
        label_layer = register(metal, f"title-{slug}", label_image)
        manifest["text"][label_layer] = {"text": label, "fit_box": PLATE_TEXT_BOX, "font_size": label_image.info["font_size"], "bounds": label_image.getchannel("A").getbbox()}
        image = assemble(f"awards/{slug}.png", metal, ornaments + ["badge", symbol, "bottom-plate", f"title-{slug}"])
        podium.append((image, label, caption, INK[metal]))
    preview("Tournament podium awards", "Gold for the Champion, silver for 2nd place, bronze for 3rd. Laurels belong to the Champion only.", podium, "podium-preview.png", card_width=760, image_size=750)

    for metal in METALS:
        assemble(f"examples/{metal}/outer-border-rank-1.png", metal, ["wings-small-border", "outer-border", "crest", "badge", "bottom-plate", "rank-1"])
    with Image.open(OUTPUT / "progression/gold/small-wings-crest-rank-1.png") as plain, Image.open(OUTPUT / "examples/gold/outer-border-rank-1.png") as bordered:
        preview("Optional outer border", "The extra rim is a separate layer. Wings and crest remain independent.", [(plain, "BORDER OFF", "Standard badge rim", INK["gold"]), (bordered, "BORDER ON", "Reinforced double rim", INK["gold"])], "outer-border-preview.png", card_width=540, image_size=512)
    manifest["optional_layers"] = {"outer-border": {"path": "layers/{metal}/outer-border.png", "order": "After wings, before crest and badge", "available_finishes": list(METALS)}}
    manifest["wing_attachment"] = {"outer_border_offset": BORDER_WING_SHIFT, "normal": {"small": "wings-small", "ascendant": "wings"}, "outer_border": {"small": "wings-small-border", "ascendant": "wings-border"}, "note": "Border variants translate each wing outward separately; they retain the original pixels and canvas."}
    manifest["wide_concept"] = wide_badge_concept()

    # A component gallery shows the gold set separately from any badge.
    gallery = Image.new("RGB", (1720, 1110), "#10141C")
    draw = ImageDraw.Draw(gallery)
    draw.text((32, 28), "Interchangeable ornament assets", font=font(34, True), fill="#F1F5F9")
    draw.text((32, 78), "Six finishes: bronze / silver / gold / steel / black / white. Winner laurels: gold only.", font=font(21), fill="#A8B4C7")
    for index, (component, title) in enumerate([("bottom-plate", "BOTTOM PLATE"), ("wings-small", "SMALL WINGS"), ("crest", "CREST"), ("wings", "ASCENDANT WINGS"), ("laurels", "CHAMPION LAURELS"), ("crown", "CHAMPION CROWN")]):
        x = 32 + (index % 3) * 562
        y = 134 + (index // 3) * 470
        draw.rounded_rectangle((x, y, x + 532, y + 440), radius=18, fill="#1B2230")
        layer = layers[f"layers/gold/{component}.png"]
        bounds = layer.getchannel("A").point(lambda value: 255 if value >= 16 else 0).getbbox()
        thumb = layer.crop(bounds)
        thumb.thumbnail((480, 330), Image.Resampling.LANCZOS)
        gallery.paste(thumb, (x + (532 - thumb.width) // 2, y + 30 + (330 - thumb.height) // 2), thumb)
        draw.text((x + 266, y + 399), title, font=font(23, True), fill=INK["gold"], anchor="mm")
    save(gallery, "assets-preview.png")

    manifest["notes"] = ["All layers share a 2048 × 2048 transparent canvas.", "Badge pixels are retained at their original size; new accessories are scaled into place.", "Six independently selectable ornament styles each support milestones 1, 3, 5, 10, 20, 25, 50.", "Small wings and ascendant wings are separate designs; the superseded old full wings remain retired.", "Every plate marker and title is measured and centered within the plate's safe text area.", "Podium awards are independent of progression styles.", "Champion uses a central crown and exclusive gold laurels; no placement numeral 1."]
    (OUTPUT / "layout.json").write_text(json.dumps(manifest, indent=2) + "\n")
    with ZipFile(BADGES / "badge-awards-and-ornaments.zip", "w", ZIP_DEFLATED) as bundle:
        for path in sorted(OUTPUT.rglob("*")):
            if path.is_file() and path.suffix in (".png", ".json", ".md"):
                bundle.write(path, arcname=path.relative_to(OUTPUT))
    print(f"Saved {len(layers)} layers, {len(METALS) * len(STYLES) * len(RANKS)} progression badges, {len(METALS) * len(RANKS)} numbered plates and three awards to {OUTPUT}")


if __name__ == "__main__":
    main()
