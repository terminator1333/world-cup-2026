"""World Cup 2026 Prediction Pool — landing page."""
from __future__ import annotations

import streamlit as st

from lib import db, theme
from lib.data import all_teams, group_matches, load_groups
from lib.scoring import leaderboard

st.set_page_config(page_title="WC2026 Prediction Pool", page_icon="🏆", layout="wide")
theme.inject()

theme.hero(
    "PREDICT THE<br>WORLD CUP",
    "Lock in your picks. Out-predict your friends. Lift the trophy. 🏆",
)
theme.countdown()

if not db.using_supabase():
    st.info("⚙️ Running on the **local fallback store** — add Supabase keys to "
            "`.streamlit/secrets.toml` to share picks with friends online.", icon="🛰️")

st.write("")

# --- Quick stats ----------------------------------------------------------- #
groups = load_groups()
c1, c2, c3, c4 = st.columns(4)
c1.metric("Teams", len(all_teams()))
c2.metric("Groups", len(groups))
c3.metric("Group matches", len(group_matches()))
c4.metric("Players in pool", len(db.list_participants()))

st.write("")

left, right = st.columns([1.1, 1])

with left:
    st.markdown('<span class="wc-badge">HOW IT WORKS</span>', unsafe_allow_html=True)
    st.markdown(
        """
- **🔮 Predictions** — register with a name + PIN, then pick **whatever you like**:
  group standings, individual match results, the best 3rd-placed teams, and the
  full knockout bracket all the way to the champion. Every section is optional.
- **📊 Leaderboard** — points are awarded automatically as results come in.
- **👀 All Picks** — once predictions lock at kickoff, see everyone's calls.
- Predictions **lock at the first kickoff** — June 11, 2026.
        """
    )
    st.page_link("pages/1_🔮_Predictions.py", label="Make your predictions", icon="🔮")
    st.page_link("pages/5_🖼️_Gallery.py", label="Browse the cities & legends gallery", icon="🖼️")

with right:
    st.markdown('<span class="wc-badge">🏆 CURRENT STANDINGS</span>', unsafe_allow_html=True)
    st.write("")
    board = leaderboard(db.all_predictions(), db.list_participants(), db.get_results())
    if not board:
        st.caption("No players yet — be the first to register on the Predictions page!")
    else:
        medals = {0: "🥇", 1: "🥈", 2: "🥉"}
        for i, row in enumerate(board[:8]):
            cls = f"lb-row lb-{i + 1}" if i < 3 else "lb-row"
            rank = medals.get(i, f"{i + 1}")
            st.markdown(
                f'<div class="{cls}"><div class="lb-rank">{rank}</div>'
                f'<div class="lb-name">{row["name"]}</div>'
                f'<div class="lb-score">{row["total"]} pts</div></div>',
                unsafe_allow_html=True,
            )
        st.page_link("pages/2_📊_Leaderboard.py", label="Full leaderboard", icon="📊")
