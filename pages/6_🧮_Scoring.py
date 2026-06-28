"""How scoring works — a clear, visual breakdown driven by the real point values."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from lib import theme
from lib.data import (CHAMPION_POINTS, KNOCKOUT_ROUNDS, KO_POOL_EXACT_SCORE,
                     KO_POOL_POINTS, group_matches, load_groups)
from lib.scoring import (PTS_AWARD, PTS_GAME_EXACT, PTS_GAME_OUTCOME, PTS_GROUP_POSITION,
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
    "Awards": 2 * PTS_AWARD,
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

st.markdown('<span class="wc-badge">🏅 INDIVIDUAL AWARDS</span>', unsafe_allow_html=True)
cards([(f"+{PTS_AWARD}", "Correct Best Player (Golden Ball)"),
       (f"+{PTS_AWARD}", "Correct Golden Glove (best GK)")])
st.write("Call the tournament's standout player and best goalkeeper — "
         f"**+{PTS_AWARD}** each if you name them right.")

st.divider()

# --- Knockout Pool — the separate game ------------------------------------- #
st.markdown('<span class="ko-badge">🥊 KNOCKOUT POOL · SEPARATE GAME</span>', unsafe_allow_html=True)
st.write("A standalone contest on the **real** Round-of-32 bracket, with its **own leaderboard** — "
         "it does **not** affect your full-tournament total. Each team you correctly send through "
         "a round scores, the deeper the better:")
cards([(f"+{KO_POOL_POINTS['r32']}", "Wins R32 (into R16)"),
       (f"+{KO_POOL_POINTS['r16']}", "Wins R16 (into QF)"),
       (f"+{KO_POOL_POINTS['qf']}", "Wins QF (into SF)"),
       (f"+{KO_POOL_POINTS['sf']}", "Wins SF (into Final)"),
       (f"+{KO_POOL_POINTS['champion']}", "Champion")])
st.write(f"Plus **+{KO_POOL_EXACT_SCORE}** for every tie where you nail the exact scoreline. "
         "Your champion banks points from every round they win, so calling the winner is the "
         "biggest prize. Predictions lock at the **first knockout game**.")

st.divider()
st.markdown('<span class="wc-badge">📊 LEADERBOARD</span>', unsafe_allow_html=True)
st.write("Two boards on the **📊 Leaderboard** page — **Full Tournament** and **Knockout Pool** — "
         "each scored automatically as results come in.")
