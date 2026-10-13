"""Shared frame and ornament finishes, plus consistent palette tinting."""

from PIL import Image, ImageOps
from tint_badge import tint_badge

FINISHES = {
    "bronze": {"shadow": "#000000", "midtone": "#9C6239", "highlight": "#FFFFFF", "ink": "#F0C6A4"},
    "silver": {"shadow": "#000000", "midtone": "#A8AAAD", "highlight": "#FFFFFF", "ink": "#F1F4F8"},
    "gold": {"shadow": "#000000", "midtone": "#C99A2E", "highlight": "#FFFFFF", "ink": "#F5DB92"},
    "steel": {"shadow": "#151D24", "midtone": "#596B79", "highlight": "#B6C4CF", "ink": "#E2ECF5"},
    "black": {"shadow": "#030405", "midtone": "#14181E", "highlight": "#4A525E", "ink": "#E5ECF6"},
    "white": {"shadow": "#939BA6", "midtone": "#E6E9EE", "highlight": "#FFFFFF", "ink": "#26303A"},
}


def finish_image(source: Image.Image, finish: str | dict) -> Image.Image:
    rgba = source.convert("RGBA")
    profile = FINISHES[finish] if isinstance(finish, str) else finish
    image = ImageOps.colorize(
        ImageOps.grayscale(rgba), black=profile["shadow"],
        mid=profile["midtone"], white=profile["highlight"], midpoint=128,
    )
    image.putalpha(rgba.getchannel("A"))
    return image


def palette_image(source: Image.Image, name: str, midtone: str) -> Image.Image:
    """Keep steel's cool shading consistent between its center and ornaments."""
    return finish_image(source, "steel") if name == "steel" else tint_badge(source, midtone)
