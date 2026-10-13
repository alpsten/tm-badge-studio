#!/usr/bin/env python3
"""Import corporation artwork and fit separate logo layers inside the badge."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
import shutil

from PIL import Image, ImageChops, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
BADGES = ROOT / "output/badges"
OUTPUT = BADGES / "logos"
WEB = ROOT / "public/badges"


def positioned(image, scale, center):
    dimensions = tuple(max(1, round(edge * scale)) for edge in image.size)
    resized = image.resize(dimensions, Image.Resampling.LANCZOS)
    x, y = (round(axis - edge / 2) for axis, edge in zip(center, dimensions))
    return resized, (x, y, x + dimensions[0], y + dimensions[1])


def fits(image, bounds, safe):
    return not ImageChops.multiply(image.getchannel("A"), ImageChops.invert(safe.crop(bounds))).getbbox()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, help="Import original files from this folder; otherwise use the imported copies")
    args = parser.parse_args()
    config = json.loads((ROOT / "scripts/badge_logos.json").read_text())
    corporations = {corp["id"]: corp["name"] for corp in json.loads((WEB / "corporations.json").read_text())["corporations"]}
    size, center = config["canvas"], config["center"]
    # Keep a 40-master-pixel gap inside the existing center mask. Validate the
    # enlarged preview setting too; fitting never relies on clipping the logo.
    with Image.open(BADGES / "badge-center-mask.png") as source:
        inner = source.convert("L").point(lambda n: 255 if n >= 250 else 0).filter(ImageFilter.MinFilter(81))
    safe = Image.new("L", (size, size))
    safe.paste(inner, (397, 397))
    for folder in ("originals", "layers"):
        (OUTPUT / folder).mkdir(parents=True, exist_ok=True)
    entries = []
    for item in config["logos"]:
        identifier = item["corporation"]
        if identifier not in corporations:
            raise ValueError(f"Unknown corporation: {identifier}")
        path = OUTPUT / "originals" / item["file"]
        if args.source_dir:
            incoming = args.source_dir / item["file"]
            if incoming.resolve() != path.resolve():
                shutil.copy2(incoming, path)
        digest = sha256(path.read_bytes()).hexdigest()
        with Image.open(path) as original:
            rgba = original.convert("RGBA")
        # Trim only completely transparent margins. Mons keeps its opaque square,
        # including the original orange background, as requested by the user.
        crop = (0, 0, *rgba.size) if item.get("keep_original_square") else rgba.getchannel("A").getbbox()
        if crop is None:
            raise ValueError(f"Empty logo: {path}")
        artwork = rgba.crop(crop)
        low, high = 0.0, min(1.0, 1100 / max(artwork.size))
        for _ in range(16):
            candidate = (low + high) / 2
            resized, bounds = positioned(artwork, candidate, center)
            if fits(resized, bounds, safe):
                low = candidate
            else:
                high = candidate
        scale = low * config["default_fit_fraction"]
        # Round only requested logo backgrounds after fitting, so the logo keeps
        # its existing scale. Subsequent resizing antialiases the transparent edge.
        corner_radius = item.get("corner_radius_fraction", 0)
        if corner_radius:
            if not 0 < corner_radius <= 0.5:
                raise ValueError(f"Invalid corner radius: {identifier}")
            rounded = Image.new("L", artwork.size)
            ImageDraw.Draw(rounded).rounded_rectangle(
                (0, 0, artwork.width - 1, artwork.height - 1),
                radius=round(min(artwork.size) * corner_radius), fill=255,
            )
            artwork.putalpha(ImageChops.multiply(artwork.getchannel("A"), rounded))
        # Apply optical adjustments after fitting to preserve the artwork's size.
        # CSS preview scaling also scales the offset around the shared center.
        offset = item.get("offset", [0, 0])
        logo_center = [axis + delta for axis, delta in zip(center, offset)]
        preview_scale = config["maximum_preview_scale"]
        enlarged_center = [axis + delta * preview_scale for axis, delta in zip(center, offset)]
        resized, bounds = positioned(artwork, scale, logo_center)
        enlarged, large_bounds = positioned(artwork, scale * preview_scale, enlarged_center)
        if not fits(enlarged, large_bounds, safe):
            raise AssertionError(f"Logo would overlap the frame: {identifier}")
        layer = Image.new("RGBA", (size, size))
        layer.paste(resized, bounds[:2])
        layer.save(OUTPUT / "layers" / f"{identifier}.png")
        if sha256(path.read_bytes()).hexdigest() != digest:
            raise AssertionError(f"Original logo changed: {path}")
        entries.append({"corporation": identifier, "name": corporations[identifier], "path": f"logos/{identifier}.webp", "source": item["file"], "source_sha256": digest, "source_size": rgba.size, "crop": crop, "offset": offset, "corner_radius_fraction": corner_radius, "bounds": bounds, "maximum_scale_bounds": large_bounds, "keep_original_square": bool(item.get("keep_original_square"))})
    data = {"version": 1, "canvas": size, "center": center, "maximum_preview_scale": config["maximum_preview_scale"], "logos": entries, "notes": ["Separate layers: after the badge center/frame and before the bottom plate and rank.", "Original colors and proportions are preserved. Only fully transparent margins are trimmed.", "Requested corner rounding is recorded per logo and applied only to the derived layers.", "Mons Insurance retains its original opaque square artwork.", "The 110% preview size is checked against an inset badge-center mask."]}
    encoded = json.dumps(data, indent=2) + "\n"
    (OUTPUT / "layout.json").write_text(encoded)
    (WEB / "logos.json").write_text(encoded)
    (WEB / "logos.js").write_text("window.BADGE_LOGOS = " + json.dumps(data) + ";\n")
    print(f"Imported and fitted {len(entries)} logos; originals preserved, including the Mons Insurance square", flush=True)


if __name__ == "__main__":
    main()
