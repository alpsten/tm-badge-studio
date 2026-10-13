"""Resolve preview/marker fonts on macOS, Windows, and Linux."""

from pathlib import Path
import os

from PIL import ImageFont


def font(size: int, bold: bool = False):
    override = os.environ.get('BADGE_FONT_BOLD' if bold else 'BADGE_FONT_REGULAR')
    if override:
        return ImageFont.truetype(override, size)
    filename = 'Arial Bold.ttf' if bold else 'Arial.ttf'
    windows = Path(os.environ.get('WINDIR', 'C:/Windows')) / 'Fonts'
    candidates = [
        Path('/System/Library/Fonts/Supplemental') / filename,
        windows / ('arialbd.ttf' if bold else 'arial.ttf'),
        Path('/usr/share/fonts/truetype/liberation2') / ('LiberationSans-Bold.ttf' if bold else 'LiberationSans-Regular.ttf'),
        Path('/usr/share/fonts/truetype/dejavu') / ('DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf'),
    ]
    for path in candidates:
        if path.is_file():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default(size=size)
