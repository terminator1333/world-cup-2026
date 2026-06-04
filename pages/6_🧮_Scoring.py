"""How scoring works — a clear, visual breakdown driven by the real point values."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from lib import theme
from lib.data import CHAMPION_POINTS, KNOCKOUT_ROUNDS, group_matches, load_groups
from lib.scoring import (PTS_GAME_EXACT, PTS_GAME_OUTCOME, PTS_GROUP_POSITION,
                         PTS_GROUP_QUALIFIERS, PTS_GROUP_WINNER, PTS_SCORER_EXACT,
                         PTS_SCORER_IN_TOP3, PTS_THIRD_PLACE)

st.set_page_config(page_title="Scoring · WC2026", page_icon="🧮", layout="wide")
theme.inject()
theme.hero("HOW SCORING WORKS", "Every correct call earns points. Highest total lifts the trophy. 🏆")

n_matches = len(group_matches())
n_groups = len(load_groups())
ko = {k: p for k, _l, _s, p in KNOCKOUT_ROUNDS}

# Max points reachable per category (a feel for what's worth chasing).
max_pts = {
    "Match scores": n_matches * (PTS_GAME_OUTCOME + PTS_GAME_EXACT),
    "Group order": n_groups * (PTS_GROUP_WINNER + 3 * PTS_GROUP_POSITION + PTS_GROUP_QUALIFIERS),
    "3rd-place": 8 * PTS_THIRD_PLACE,
    "Knockout": 16 * ko["r16"] + 8 * ko["qf"] + 4 * ko["sf"] + 2 * ko["final"] + CHAMPION_POINTS,
    "Top scorers": 3 * PTS_SCORER_EXACT,
}


def cards(items):
    cols = st.columns(len(items))
    for col, (num, lbl) in zip(cols, items):
        col.markdown(
            f'<div class="record"><div class="record-num">{num}</div>'
            f'<div class="record-lbl">{lbl}</div></div>', unsafe_allow_html=True)


# --- the big picture ------------------------------------------------------- #
st.markdown('<span class="wc-badge">🎯 POINTS UP FOR GRABS — BY CATEGORY</span>',
            unsafe_allow_html=True)
st.bar_chart(pd.DataFrame({"Max points": max_pts}), horizontal=True, color="#00E5A0")
st.caption(f"Total points available across everything: **{sum(max_pts.values())}**. "
           "Every section is optional — predict what you like.")

st.divider()

# --- per category ---------------------------------------------------------- #
st.markdown('<span class="wc-badge">⚽ MATCH SCORES</span>', unsafe_allow_html=True)
cards([(f"+{PTS_GAME_OUTCOME}", "Correct result (W/D/L)"),
       (f"+{PTS_GAME_EXACT}", "Bonus: exact scoreline")])
st.write(f"Predict any group game. Right outcome = **+{PTS_GAME_OUTCOME}**; nail the exact score "
         f"and you bank **+{PTS_GAME_OUTCOME + PTS_GAME_EXACT}** total. "
         "_Example: you say Brazil 2–1, it ends 2–1 → +5. It ends 3–0 (still a Brazil win) → +3._")

st.markdown('<span class="wc-badge">🥇 GROUP ORDER</span>', unsafe_allow_html=True)
cards([(f"+{PTS_GROUP_WINNER}", "Correct group winner"),
       (f"+{PTS_GROUP_POSITION}", "Each other exact spot"),
       (f"+{PTS_GROUP_QUALIFIERS}", "Right top-2 (any order)")])
st.write("Your group standings come straight from the scores you enter. "
         f"_Example: winner correct (+{PTS_GROUP_WINNER}), 2nd & 3rd exact (+{2*PTS_GROUP_POSITION}), "
         f"and the top-2 set right (+{PTS_GROUP_QUALIFIERS})._")

st.markdown('<span class="wc-badge">🥉 3RD-PLACE RACE</span>', unsafe_allow_html=True)
cards([(f"+{PTS_THIRD_PLACE}", "Per 3rd-placed team that advances")])
st.write("8 of the 12 third-placed teams reach the Round of 32. Each one you call correctly scores.")

st.markdown('<span class="wc-badge">🏆 KNOCKOUT BRACKET</span>', unsafe_allow_html=True)
cards([(f"+{ko['r16']}", "Reaches R16"), (f"+{ko['qf']}", "Reaches QF"),
       (f"+{ko['sf']}", "Reaches SF"), (f"+{ko['final']}", "Reaches Final"),
       (f"+{CHAMPION_POINTS}", "Correct champion")])
st.write("Each team you send to a round scores when they actually get there — the deeper the run, "
         f"the more it's worth. Calling the **champion** is the single biggest pick at **+{CHAMPION_POINTS}**.")

st.markdown('<span class="wc-badge">🥇 TOP SCORERS</span>', unsafe_allow_html=True)
cards([(f"+{PTS_SCORER_EXACT}", "Right scorer & right rank"),
       (f"+{PTS_SCORER_IN_TOP3}", "Right scorer, wrong rank")])
st.write(f"Name the top 3 goalscorers in order. Exact rank = **+{PTS_SCORER_EXACT}** "
         f"(your #1 is your Golden Boot pick); right player in the wrong slot still scores "
         f"**+{PTS_SCORER_IN_TOP3}**.")

st.divider()
st.markdown('<span class="wc-badge">📊 LEADERBOARD</span>', unsafe_allow_html=True)
st.write("Your total is the sum of everything you got right, shown with a per-category breakdown on "
         "the **📊 Leaderboard** page. Results are entered as matches finish, so scores climb live "
         "throughout the tournament.")
