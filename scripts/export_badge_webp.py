#!/usr/bin/env python3
"""Export website-sized badge copies without changing PNG source artwork."""

from concurrent.futures import ThreadPoolExecutor, as_completed
from hashlib import sha256
import argparse
import json
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

from PIL import Image, features


ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "output/badges"
OUTPUT = ROOT / "public/badges"
SIZES = (256, 512)
QUALITY = 95


def catalog():
    items = []

    def add(source, target, category, *, aligned=False, lossless=False):
        items.append({"source": SOURCES / source, "target": target, "category": category, "aligned": aligned, "lossless": lossless})

    palette = json.loads((SOURCES / "palette.json").read_text())
    for color in palette:
        add(f"badge-{color['name']}.png", f"colors/{color['name']}.webp", "colors")

    combinations = json.loads((SOURCES / "framed/combinations.json").read_text())
    for item in combinations:
        source = f"framed/{item['file']}"
        add(source, f"framed/{item['frame']}/{item['center']}.webp", "framed")
        # Framed originals fill their own 1254 px square. Pad to the ornament
        # canvas BEFORE resizing so every center color can replace the badge layer.
        add(source, f"layers/{item['frame']}/badges/{item['center']}.webp", "colored-badge-layers", aligned=True)

    for category in ("layers", "progression", "awards", "plates", "examples", "concepts"):
        for path in sorted((SOURCES / "awards-kit" / category).rglob("*.png")):
            relative = path.relative_to(SOURCES / "awards-kit")
            text = category == "layers" and path.stem.startswith(("rank-", "placement-", "title-"))
            add(f"awards-kit/{relative.as_posix()}", relative.with_suffix(".webp").as_posix(), category, lossless=text)

    for folder, target in (("badges", "corporations"), ("ornaments", "corporation-ornaments"), ("modular", "modular")):
        for path in sorted((SOURCES / "corporations" / folder).rglob("*.png")):
            relative = path.relative_to(SOURCES / "corporations" / folder).with_suffix(".webp")
            add(path.relative_to(SOURCES).as_posix(), f"{target}/{relative.as_posix()}", target, lossless=path.stem.startswith("rank-"))

    for path in sorted((SOURCES / "logos/layers").glob("*.png")):
        add(path.relative_to(SOURCES).as_posix(), f"logos/{path.stem}.webp", "logos", lossless=True)
    targets = [item["target"] for item in items]
    if len(set(targets)) != len(targets):
        raise ValueError("Duplicate output asset paths")
    for item in items:
        if not item["source"].is_file():
            raise FileNotFoundError(item["source"])
    return items


def export(item):
    with Image.open(item["source"]) as source:
        original = source.convert("RGBA")
    source_size = original.size
    if item["aligned"]:
        if source_size != (1254, 1254):
            raise ValueError(f"Unexpected badge dimensions: {item['source']}")
        padded = Image.new("RGBA", (2048, 2048), (0, 0, 0, 0))
        padded.paste(original, (397, 397))
        original = padded

    result = {"id": item["target"], "category": item["category"], "source": item["source"].relative_to(ROOT).as_posix(), "source_size": source_size, "canvas_before_resize": original.size, "encoding": "lossless" if item["lossless"] else f"quality-{QUALITY}", "variants": {}}
    for size in SIZES:
        scale = min(size / original.width, size / original.height, 1)
        dimensions = (round(original.width * scale), round(original.height * scale))
        resized = original.resize(dimensions, Image.Resampling.LANCZOS)
        relative = f"{size}/{item['target']}"
        path = OUTPUT / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        options = {"format": "WEBP", "method": 6}
        if item["lossless"]:
            options.update(lossless=True, quality=80, exact=True)
        else:
            options.update(quality=QUALITY, alpha_quality=100)
        resized.save(path, **options)
        with Image.open(path) as decoded:
            decoded = decoded.convert("RGBA")
            if decoded.size != resized.size:
                raise AssertionError(f"Dimensions changed during encoding: {relative}")
            if decoded.getchannel("A").tobytes() != resized.getchannel("A").tobytes():
                raise AssertionError(f"Transparency changed during encoding: {relative}")
            if item["lossless"] and decoded.tobytes() != resized.tobytes():
                raise AssertionError(f"Pixels changed during lossless encoding: {relative}")
        result["variants"][str(size)] = {"path": relative, "width": dimensions[0], "height": dimensions[1], "bytes": path.stat().st_size}
    return result


def web_path(path):
    return str(Path(path).with_suffix(".webp"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--unchanged-checkpoint", type=Path, help="Reuse files matching this pre-edit SHA-256 checkpoint; encode new or changed assets")
    args = parser.parse_args()
    if not features.check("webp"):
        raise RuntimeError("Pillow needs WebP support to run this exporter.")
    items = catalog()
    # Retire only generated files tracked by the previous manifest. This keeps
    # removed wing designs and tiers out of the public directory and download.
    expected_paths = {f"{size}/{item['target']}" for item in items for size in SIZES}
    previous_manifest = OUTPUT / "manifest.json"
    previous = {}
    if previous_manifest.exists():
        previous = json.loads(previous_manifest.read_text())
        for asset in previous.get("assets", []):
            for variant in asset["variants"].values():
                relative = variant["path"]
                path = (OUTPUT / relative).resolve()
                if relative not in expected_paths and path.is_relative_to(OUTPUT.resolve()) and path.suffix == ".webp" and path.is_file():
                    path.unlink()
    source_hashes = {path: sha256(path.read_bytes()).hexdigest() for path in {item["source"] for item in items}}
    results = []
    pending = items
    if args.unchanged_checkpoint:
        checkpoint = json.loads(args.unchanged_checkpoint.read_text())
        if previous.get("sizes") != list(SIZES) or previous.get("quality") != QUALITY or previous.get("alpha_quality") != 100 or not previous.get("text_layers_lossless"):
            raise ValueError("Export settings differ; run a full export without a checkpoint")
        old_assets = {asset["id"]: asset for asset in previous["assets"]}
        pending = []
        for item in items:
            old = old_assets.get(item["target"])
            if old is None:
                pending.append(item)
                continue
            source_name = item["source"].relative_to(ROOT).as_posix()
            encoding = "lossless" if item["lossless"] else f"quality-{QUALITY}"
            if old["source"] != source_name or old["encoding"] != encoding or source_hashes[item["source"]] != checkpoint.get(source_name):
                pending.append(item)
                continue
            valid = True
            for variant in old["variants"].values():
                path = OUTPUT / variant["path"]
                name = path.relative_to(ROOT).as_posix()
                if not path.is_file() or sha256(path.read_bytes()).hexdigest() != checkpoint.get(name):
                    valid = False
                    break
            if valid:
                results.append(old)
            else:
                pending.append(item)
        print(f"Reusing {len(results)} unchanged assets; exporting {len(pending)} new or changed assets", flush=True)
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = [pool.submit(export, item) for item in pending]
        for future in as_completed(futures):
            results.append(future.result())
            if len(results) % 40 == 0 or len(results) == len(items):
                print(f"Exported and verified {len(results)}/{len(items)} assets at both sizes", flush=True)
    results.sort(key=lambda item: item["id"])
    for path, digest in source_hashes.items():
        if sha256(path.read_bytes()).hexdigest() != digest:
            raise AssertionError(f"PNG source changed: {path}")

    source_layout = json.loads((SOURCES / "awards-kit/layout.json").read_text())
    layout = {
        "sizes": list(SIZES),
        "ranks": source_layout["ranks"],
        "metals": source_layout["metals"],
        "finishes": source_layout["finishes"],
        "tiers": source_layout["tiers"],
        "styles": source_layout["styles"],
        "wing_attachment": source_layout["wing_attachment"],
        "optional_layers": {name: {**value, "path": web_path(value["path"])} for name, value in source_layout.get("optional_layers", {}).items()},
        "wide_concept": {**source_layout["wide_concept"], "file": web_path(source_layout["wide_concept"]["file"])},
        "assemblies": {web_path(name): [web_path(layer) for layer in layers] for name, layers in source_layout["assemblies"].items()},
        "colored_badge_layer": "layers/{metal}/badges/{color}.webp",
        "corporation_logos": {"manifest": "logos.json", "path": "logos/{corporation}.webp", "order": "After badge center/frame, before bottom plate and rank"},
        "expansion_logos": {"manifest": "logos.json", "path": "logos/{expansion}.webp", "order": "After badge center/frame, before bottom plate and rank"},
        "coordinates": {},
        "notes": ["Paths are relative to either the 256/ or 512/ directory.", "Stack all layers from one size directory at the same origin and display size.", "Replace layers/{metal}/badge.webp with layers/{metal}/badges/{color}.webp for another center color.", "Standalone colors/ and framed/ images use a tighter canvas; use the aligned layers/ paths when adding ornaments.", "Plates are compact exports with their aspect ratio retained.", "Choose a precomposed progression/ or awards/ image for a single image request, or layers/ to build a combination."],
    }
    for size in SIZES:
        factor = size / 2048
        layout["coordinates"][str(size)] = {
            "canvas": [size, size],
            "badge_box": [value * factor for value in (397, 397, 1651, 1651)],
            "plate_text_box": [value * factor for value in source_layout["plate_text_box"]],
        }
    (OUTPUT / "layout.json").write_text(json.dumps(layout, indent=2) + "\n")

    source_bytes = sum(path.stat().st_size for path in source_hashes)
    size_bytes = {str(size): sum(item["variants"][str(size)]["bytes"] for item in results) for size in SIZES}
    manifest = {
        "sizes": list(SIZES),
        "quality": QUALITY,
        "alpha_quality": 100,
        "text_layers_lossless": True,
        "verified_original_pngs_unchanged": True,
        "verified_export_alpha_matches_resized_source": True,
        "asset_count": len(results),
        "webp_file_count": len(results) * len(SIZES),
        "unique_source_png_bytes": source_bytes,
        "bytes_by_size": size_bytes,
        "assets": results,
    }
    (OUTPUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

    expected_files = {item["variants"][str(size)]["path"] for item in results for size in SIZES}
    expected_files.update(("layout.json", "manifest.json", "README.md", "preview.html", "preview.js", "corporations.js", "corporations.json", "corporations.md", "logos.js", "logos.json"))
    archive = SOURCES / "badge-webp-testing-kit.zip"
    with ZipFile(archive, "w", compression=ZIP_DEFLATED) as bundle:
        for name in sorted(expected_files):
            path = OUTPUT / name
            if not path.is_file():
                raise FileNotFoundError(path)
            bundle.write(path, arcname=name)
    with ZipFile(archive) as bundle:
        if set(bundle.namelist()) != expected_files or bundle.testzip() is not None:
            raise AssertionError("ZIP verification failed")
    print(json.dumps({"assets": len(results), "webp_files": len(results) * len(SIZES), "source_png_mb": round(source_bytes / 1024**2, 2), "webp_mb_by_size": {size: round(count / 1024**2, 2) for size, count in size_bytes.items()}, "zip_mb": round(archive.stat().st_size / 1024**2, 2), "destination": str(OUTPUT), "zip": str(archive)}, indent=2), flush=True)


if __name__ == "__main__":
    main()
