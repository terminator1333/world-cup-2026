"""Gallery — browse every host city.

Shows your generated art from static/cities/ when present, falling back to free
Creative-Commons photos otherwise.
"""
from __future__ import annotations

import streamlit as st

from lib import theme
from lib.assets import find_asset, media_html, slugify
from lib.data import load_stadiums
from lib.flags import flag_by_code
from lib.photos import city_photo

st.set_page_config(page_title="Gallery · WC2026", page_icon="🖼️", layout="wide")
theme.inject()

_hero_url, _hero_ext = find_asset(".", "hero")
theme.hero("HOST CITIES", "16 cities · 3 nations · one trophy. "
           "<span class='wc-float'>🏆</span>",
           bg_html=media_html(_hero_url, _hero_ext, cls="wc-hero-bg") if _hero_url else "")


def _city_media(s) -> str:
    url, ext = find_asset("cities", slugify(s["city"]))
    if url:
        return media_html(url, ext, cls="gal-img")
    photo = city_photo(s["city"], s["country"])
    return f'<img class="gal-img" src="{photo["url"]}" loading="lazy" alt="{s["city"]}">'


cols = st.columns(3)
for i, s in enumerate(load_stadiums()):
    with cols[i % 3]:
        tag = (f'<div class="stad-tag" style="position:absolute;top:10px;right:10px;'
               f'z-index:3;">{s["tag"]}</div>' if s["tag"] else "")
        st.markdown(
            f'<div class="gal-tile">{tag}{_city_media(s)}'
            f'<div class="gal-flag">{flag_by_code(s["cc"], 40, wave=True)}</div>'
            f'<div class="gal-cap"><b>{s["city"]}</b>'
            f'<span>{s["name"]} · {s["region"]}, {s["country"]} · ~{s["cap"]:,}</span></div>'
            f'</div>',
            unsafe_allow_html=True,
        )
