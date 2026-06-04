"""Drop-in animated assets.

Generate your own images/animations and drop them in:
    static/cities/<city-slug>.<ext>      → animated background for a city card
    static/legends/<legend-slug>.<ext>   → animated figure for a legend
    static/hero.<ext>                    → animated hero background (optional)

Supported (first match wins, video preferred):
    .webm .mp4   → rendered as autoplaying, looping, muted <video>
    .gif .webp .apng .png .jpg .jpeg → rendered as <img>

Files are served by Streamlit at `app/static/...` (enableStaticServing=true).
If no file exists for a slug, the app falls back to the photo/flag it used before,
so everything keeps working until you add your assets.
"""
from __future__ import annotations

import re
from pathlib import Path

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
VIDEO_EXT = (".webm", ".mp4")
IMG_EXT = (".gif", ".webp", ".apng", ".png", ".jpg", ".jpeg")
_ORDER = VIDEO_EXT + IMG_EXT


def slugify(name: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", name.lower())).strip("-")


def find_asset(subdir: str, slug: str):
    """Return (url, ext) for the first matching asset file, or (None, None)."""
    base = STATIC_DIR / subdir
    prefix = "app/static" if subdir in (".", "") else f"app/static/{subdir}"
    for ext in _ORDER:
        if (base / f"{slug}{ext}").exists():
            return f"{prefix}/{slug}{ext}", ext
    return None, None


def has_any(subdir: str) -> bool:
    base = STATIC_DIR / subdir
    return base.exists() and any(
        p.suffix.lower() in _ORDER for p in base.iterdir() if p.is_file()
    )


def media_html(url: str, ext: str, *, cls: str = "", style: str = "") -> str:
    """Render an asset as a looping muted <video> or an <img>."""
    if ext in VIDEO_EXT:
        return (
            f'<video class="{cls}" style="{style}" autoplay loop muted playsinline '
            f'preload="auto"><source src="{url}"></video>'
        )
    return f'<img class="{cls}" style="{style}" src="{url}" loading="lazy" alt="">'
