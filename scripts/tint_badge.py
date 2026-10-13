#!/usr/bin/env python3
"""Recolor a grayscale badge without resizing, redrawing, or changing alpha."""

import argparse
from pathlib import Path
import re

from PIL import Image, ImageOps


def hex_color(value: str) -> str:
    if not re.fullmatch(r"#[0-9a-fA-F]{6}", value):
        raise argparse.ArgumentTypeError("Use a six-digit hex color, e.g. '#2563eb'.")
    return value


def tint_badge(
    source: Image.Image,
    color: str,
    *,
    center_mask: Image.Image | None = None,
    center_color: str | None = None,
) -> Image.Image:
    """Map source brightness to black → chosen midtone → white; retain alpha."""
    rgba = source.convert("RGBA")
    brightness = ImageOps.grayscale(rgba)
    tinted = ImageOps.colorize(
        brightness,
        black="#000000",
        mid=color,
        white="#ffffff",
        midpoint=128,
    )
    tinted.putalpha(rgba.getchannel("A"))
    if center_color is not None and center_mask is None:
        raise ValueError("A center color requires a center mask.")
    if center_mask is not None:
        if center_mask.size != rgba.size:
            raise ValueError("Center mask must have the same dimensions as the source.")
        center = tint_badge(rgba, center_color) if center_color else rgba
        tinted = Image.composite(center, tinted, center_mask.convert("L"))
        tinted.putalpha(rgba.getchannel("A"))
    return tinted


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Original grayscale badge")
    parser.add_argument("output", type=Path, help="New PNG file (never overwritten)")
    parser.add_argument("--color", required=True, type=hex_color, help="Midtone hex color")
    parser.add_argument("--center-mask", type=Path, help="Grayscale mask: white=center, black=frame")
    parser.add_argument("--center-color", type=hex_color, help="Center midtone; omit to retain original center")
    args = parser.parse_args()

    if args.center_color and not args.center_mask:
        parser.error("--center-color requires --center-mask.")
    if args.output.suffix.lower() != ".png":
        parser.error("Output must use .png to retain transparency and avoid compression loss.")
    if args.source.resolve() == args.output.resolve():
        parser.error("Use a separate output file to preserve the original.")
    if args.output.exists():
        parser.error(f"Output already exists: {args.output}")

    try:
        center_mask = None
        if args.center_mask:
            with Image.open(args.center_mask) as mask:
                center_mask = mask.convert("L")
        with Image.open(args.source) as source:
            tinted = tint_badge(
                source, args.color, center_mask=center_mask, center_color=args.center_color
            )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("xb") as output:
            tinted.save(output, format="PNG")
    except (OSError, ValueError) as error:
        parser.exit(1, f"Error: {error}\n")

    print(f"Saved {args.output} ({tinted.width} × {tinted.height}), tint {args.color}")


if __name__ == "__main__":
    main()
