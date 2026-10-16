"""Derive the per-OS app icons from icons/iconbasis.png.

Run with `uv run make_icons.py` after changing the base image. Writes:
- icons/RemEYEnder.icns  macOS app bundle (PyInstaller --icon)
- icons/RemEYEnder.ico   Windows executable (PyInstaller --icon)
- icons/RemEYEnder.png   Linux .desktop entry and the in-app window icon
- icons/RemEYEnder-small.png  in-app window icon at small sizes (eyes only)
"""

import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw

ICONS_DIR: Path = Path(__file__).parent / "icons"
BASE: Path = ICONS_DIR / "iconbasis.png"
# Eyes and brows only; the clock and tree are unreadable at 16-32 px.
EYES_BOX: tuple[int, int, int, int] = (285, 65, 960, 525)
# Sizes at or below this use the eyes-only artwork.
SMALL_MAX: int = 32
MASTER: int = 1024
# Rounded tile in the artwork's background colour, roughly Apple's grid:
# 824 of 1024 with a ~185 corner radius.
TILE_FRACTION: float = 824 / 1024
RADIUS_FRACTION: float = 185 / 824
ART_FRACTION: float = 0.86  # artwork size relative to the tile
SMALL_ART_FRACTION: float = 0.94


def tile(
    art: Image.Image, size: int, tile_fraction: float, art_fraction: float
) -> Image.Image:
    """Center `art` on a rounded square inside a transparent `size` canvas."""
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    tile_px = round(size * tile_fraction)
    offset = (size - tile_px) // 2
    box = (offset, offset, offset + tile_px - 1, offset + tile_px - 1)
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle(
        box, radius=round(tile_px * RADIUS_FRACTION), fill=art.getpixel((0, 0)),
        outline=(200, 200, 200, 255), width=max(1, size // 256),
    )
    fitted = art.copy()
    fitted.thumbnail((round(tile_px * art_fraction),) * 2, Image.LANCZOS)
    canvas.alpha_composite(
        fitted.convert("RGBA"),
        ((size - fitted.width) // 2, (size - fitted.height) // 2),
    )
    return canvas


def render(full: Image.Image, eyes: Image.Image, size: int) -> Image.Image:
    """Icon at `size`, drawn at 1024 and downscaled so outlines stay smooth."""
    small = size <= SMALL_MAX
    # Small icons drop most of the margin: every pixel counts at 16 px.
    if small:
        image = tile(eyes, MASTER, 0.98, SMALL_ART_FRACTION)
    else:
        image = tile(full, MASTER, TILE_FRACTION, ART_FRACTION)
    return image.resize((size, size), Image.LANCZOS)


def write_icns(full: Image.Image, eyes: Image.Image) -> None:
    """Via Apple's iconutil: Pillow's writer omits the 16 and 32 px @1x slots."""
    target = ICONS_DIR / "RemEYEnder.icns"
    if sys.platform != "darwin":
        print(f"Skipping {target.name}: iconutil is macOS-only (only macOS builds need it).")
        return
    with tempfile.TemporaryDirectory() as tmp:
        iconset = Path(tmp) / "RemEYEnder.iconset"
        iconset.mkdir()
        for size in (16, 32, 128, 256, 512):
            render(full, eyes, size).save(iconset / f"icon_{size}x{size}.png")
            render(full, eyes, size * 2).save(iconset / f"icon_{size}x{size}@2x.png")
        subprocess.run(["iconutil", "-c", "icns", "-o", str(target), str(iconset)], check=True)


def main() -> None:
    full = Image.open(BASE).convert("RGB")
    eyes = full.crop(EYES_BOX)

    master = render(full, eyes, MASTER)
    master.save(ICONS_DIR / "RemEYEnder.png")
    render(full, eyes, SMALL_MAX).save(ICONS_DIR / "RemEYEnder-small.png")

    write_icns(full, eyes)
    # Pillow picks each embedded size from append_images when one matches.
    ico_sizes = [16, 24, 32, 48, 64, 128, 256]
    render(full, eyes, 256).save(
        ICONS_DIR / "RemEYEnder.ico",
        sizes=[(s, s) for s in ico_sizes],
        append_images=[render(full, eyes, s) for s in ico_sizes[:-1]],
    )


if __name__ == "__main__":
    main()
