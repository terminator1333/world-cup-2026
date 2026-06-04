"""License-clean city photos.

Priority:
  1. Unsplash  — if UNSPLASH_ACCESS_KEY is set (free use, credit shown).
  2. Openverse — no key needed; Creative-Commons images filtered to
     commercially-usable licences, with attribution.
  3. Picsum    — deterministic free fallback so a card is never broken.

Every lookup is cached for a day, and any failure quietly drops to the next
source, so the page always renders.
"""
from __future__ import annotations

from urllib.parse import quote

import requests
import streamlit as st

from .util import secret

_UA = {"User-Agent": "wc2026-prediction-pool/1.0"}
_TIMEOUT = 12


@st.cache_data(ttl=86_400, show_spinner=False)
def city_photo(city: str, country: str) -> dict:
    """Return {'url', 'credit', 'link'} for a city. Always succeeds."""
    query = f"{city} skyline"
    for source in (_unsplash, _openverse):
        try:
            hit = source(query, country)
            if hit:
                return hit
        except Exception:
            continue
    return {
        "url": f"https://picsum.photos/seed/{quote(city)}/800/360",
        "credit": "Lorem Picsum",
        "link": "https://picsum.photos",
    }


def _unsplash(query: str, country: str) -> dict | None:
    key = secret("UNSPLASH_ACCESS_KEY")
    if not key:
        return None
    r = requests.get(
        "https://api.unsplash.com/search/photos",
        params={"query": query, "per_page": 1, "orientation": "landscape"},
        headers={**_UA, "Authorization": f"Client-ID {key}"},
        timeout=_TIMEOUT,
    )
    r.raise_for_status()
    results = r.json().get("results") or []
    if not results:
        return None
    p = results[0]
    return {
        "url": p["urls"]["regular"],
        "credit": f"Photo: {p['user']['name']} / Unsplash",
        "link": p["links"]["html"],
    }


def _openverse(query: str, country: str) -> dict | None:
    r = requests.get(
        "https://api.openverse.org/v1/images/",
        params={"q": query, "page_size": 3, "license_type": "commercial",
                "mature": "false"},
        headers=_UA, timeout=_TIMEOUT,
    )
    r.raise_for_status()
    results = r.json().get("results") or []
    if not results:
        return None
    p = results[0]
    lic = f"CC {p.get('license', '').upper()} {p.get('license_version', '')}".strip()
    creator = p.get("creator") or "Unknown"
    return {
        "url": p.get("thumbnail") or p.get("url"),
        "credit": f"Photo: {creator} ({lic})",
        "link": p.get("foreign_landing_url") or p.get("url"),
    }
