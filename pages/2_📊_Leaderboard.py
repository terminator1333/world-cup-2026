"""Live leaderboard — two separate competitions: full tournament + knockout pool."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from lib import db, theme
from lib.scoring import (CATEGORY_LABELS, KO_POOL_CATEGORY_LABELS, ko_pool_leaderboard,
                         leaderboard)

st.set_page_config(page_title="Leaderboard · WC2026", page_icon="📊", layout="wide")
theme.inject()
theme.hero("LEADERBOARD", "Points update automatically as results roll in.")

preds = db.all_predictions()
parts = db.list_participants()
results = db.get_results()

view = st.radio(
    "Competition", ["🏆 Full Tournament", "🥊 Knockout Pool"],
    horizontal=True, label_visibility="collapsed",
)
medals = {0: "🥇", 1: "🥈", 2: "🥉"}

# --------------------------------------------------------------------------- #
if view.startswith("🏆"):
    st.caption("The original season-long game — group standings, match scores, the "
               "best-third race, the derived knockout run, top scorers and awards.")
    board = leaderboard(preds, parts, results)
    if not board:
        st.info("No players yet. Head to **Predictions** to register and get on the board!")
        st.stop()
    for i, row in enumerate(board):
        cls = f"lb-row lb-{i + 1}" if i < 3 else "lb-row"
        rank = medals.get(i, f"{i + 1}")
        bits = " · ".join(
            f"{CATEGORY_LABELS[c]} {row['breakdown'][c]}"
            for c in row["breakdown"] if row["breakdown"][c]
        ) or "no points yet"
        st.markdown(
            f'<div class="{cls}"><div class="lb-rank">{rank}</div>'
            f'<div class="lb-name">{row["name"]}'
            f'<div style="font-size:12px;color:#8ea0c4;font-weight:600;">{bits}</div></div>'
            f'<div class="lb-score">{row["total"]} pts</div></div>',
            unsafe_allow_html=True,
        )
    st.write("")
    with st.expander("📋 Full breakdown table"):
        df = pd.DataFrame([
            {"Player": r["name"], **{CATEGORY_LABELS[c]: r["breakdown"][c] for c in r["breakdown"]},
             "Total": r["total"]}
            for r in board
        ])
        st.dataframe(df, use_container_width=True, hide_index=True)

# --------------------------------------------------------------------------- #
else:
    st.markdown('<span class="ko-badge">🥊 SEPARATE RANKING</span>', unsafe_allow_html=True)
    st.caption("A standalone contest on the real Round-of-32 bracket. Completely "
               "independent of the full-tournament board above.")
    board = ko_pool_leaderboard(preds, parts, results)
    players = [r for r in board if r["played"]]
    if not players:
        st.info("No knockout-pool brackets submitted yet — make yours on the "
                "**🥊 Knockout Pool** page before the first game!")
        st.stop()
    for i, row in enumerate(players):
        cls = f"lb-row lb-{i + 1}" if i < 3 else "lb-row"
        rank = medals.get(i, f"{i + 1}")
        bd = row["breakdown"]
        bits = " · ".join(
            f"{KO_POOL_CATEGORY_LABELS[c]} {bd[c]}"
            for c in KO_POOL_CATEGORY_LABELS if bd.get(c)
        ) or "no points yet"
        st.markdown(
            f'<div class="{cls}"><div class="lb-rank">{rank}</div>'
            f'<div class="lb-name">{row["name"]}'
            f'<div style="font-size:12px;color:#e9c4d8;font-weight:600;">{bits}</div></div>'
            f'<div class="lb-score ko">{row["total"]} pts</div></div>',
            unsafe_allow_html=True,
        )
    st.write("")
    with st.expander("📋 Knockout pool breakdown"):
        df = pd.DataFrame([
            {"Player": r["name"],
             **{KO_POOL_CATEGORY_LABELS[c]: r["breakdown"].get(c, 0) for c in KO_POOL_CATEGORY_LABELS},
             "Total": r["total"]}
            for r in players
        ])
        st.dataframe(df, use_container_width=True, hide_index=True)
