"""Live leaderboard with per-category breakdown."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from lib import db, theme
from lib.scoring import CATEGORY_LABELS, leaderboard

st.set_page_config(page_title="Leaderboard · WC2026", page_icon="📊", layout="wide")
theme.inject()
theme.hero("LEADERBOARD", "Points update automatically as results roll in.")

board = leaderboard(db.all_predictions(), db.list_participants(), db.get_results())

if not board:
    st.info("No players yet. Head to **Predictions** to register and get on the board!")
    st.stop()

medals = {0: "🥇", 1: "🥈", 2: "🥉"}
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
