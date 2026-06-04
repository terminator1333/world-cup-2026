"""Everyone's predictions, side by side."""
from __future__ import annotations

import streamlit as st

from lib import db, theme
from lib.data import KNOCKOUT_ROUNDS, load_groups
from lib.flags import flag_img, team_chip

st.set_page_config(page_title="All Picks · WC2026", page_icon="👀", layout="wide")
theme.inject()
theme.hero("EVERYONE'S PICKS", "See what everyone is predicting.")

participants = db.list_participants()
preds = db.all_predictions()
by_pid: dict[str, dict] = {}
for row in preds:
    by_pid.setdefault(row["participant_id"], {})[row["category"]] = row["payload"]

groups = load_groups()
names = {p["id"]: p["name"] for p in participants}

who = st.selectbox("Show picks for", ["Everyone"] + sorted(names.values()))
chosen = [pid for pid, n in names.items() if who in ("Everyone", n)]

for pid in chosen:
    data = by_pid.get(pid, {})
    st.markdown(f'<span class="wc-badge">{names[pid]}</span>', unsafe_allow_html=True)
    if not data:
        st.caption("No predictions submitted.")
        st.divider()
        continue

    ko = data.get("knockout") or {}
    if ko.get("champion"):
        st.markdown(f'🏆 **Champion pick:** {flag_img(ko["champion"], 30)} **{ko["champion"]}**',
                    unsafe_allow_html=True)

    if data.get("group_order"):
        with st.expander("🥇 Group standings"):
            for grp, order in data["group_order"].items():
                st.markdown(f"**{grp}:** " + " ▸ ".join(team_chip(t) for t in order),
                            unsafe_allow_html=True)

    if data.get("third_place"):
        with st.expander("🥉 3rd-place qualifiers"):
            st.markdown(" ".join(team_chip(t) for t in data["third_place"].get("advancing", [])),
                        unsafe_allow_html=True)

    if ko:
        with st.expander("🏆 Knockout bracket"):
            for key, label, _s, _p in KNOCKOUT_ROUNDS:
                if ko.get(key):
                    st.markdown(f"**{label}:** " + " ".join(team_chip(t) for t in ko[key]),
                                unsafe_allow_html=True)
            if ko.get("top_scorer"):
                st.markdown(f"**⚽ Golden Boot:** {ko['top_scorer']}")

    if data.get("per_game"):
        with st.expander(f"⚽ Match predictions ({len(data['per_game'])})"):
            st.json(data["per_game"], expanded=False)
    st.divider()
