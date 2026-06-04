"""Admin — enter actual results (PIN-gated). Drives the leaderboard."""
from __future__ import annotations

import streamlit as st

from lib import db, theme, util
from lib.data import KNOCKOUT_ROUNDS, all_teams, load_groups, matches_for_group

st.set_page_config(page_title="Admin · WC2026", page_icon="🔐", layout="wide")
theme.inject()
theme.hero("ADMIN · RESULTS", "Enter what actually happened. Scores recompute instantly.")

ADMIN_PIN = util.secret("ADMIN_PIN", "change-me")

if not st.session_state.get("is_admin"):
    pin = st.text_input("Admin PIN", type="password")
    if st.button("Unlock 🔐"):
        if pin and pin == ADMIN_PIN:
            st.session_state["is_admin"] = True
            st.rerun()
        else:
            st.error("Wrong PIN.")
    st.stop()

st.success("Admin unlocked.")
results = db.get_results()
groups = load_groups()
teams = all_teams()

tab_g, tab_m, tab_t, tab_k, tab_s = st.tabs(
    ["🥇 Group final tables", "⚽ Match scores", "🥉 3rd-place qualifiers",
     "🏆 Knockout", "🥇 Top scorers"]
)

# --- Group final standings ------------------------------------------------- #
with tab_g:
    st.caption("Set each group's final 1st–4th. Drives group + qualifier scoring.")
    out = {}
    cols = st.columns(3)
    for idx, (grp, gteams) in enumerate(groups.items()):
        with cols[idx % 3]:
            st.markdown(f'<div class="wc-card"><b>GROUP {grp}</b>', unsafe_allow_html=True)
            existing = results.get(("group_order", grp)) or gteams
            chosen, order = [], []
            for pos in range(4):
                opts = [t for t in gteams if t not in chosen]
                default = existing[pos] if pos < len(existing) and existing[pos] in opts else opts[0]
                pick = st.selectbox(f"{pos + 1}.", opts, index=opts.index(default),
                                    key=f"ag_{grp}_{pos}")
                chosen.append(pick)
                order.append(pick)
            out[grp] = order
            st.markdown("</div>", unsafe_allow_html=True)
    if st.button("💾 Save group tables"):
        for grp, order in out.items():
            db.save_result("group_order", grp, order)
        st.success("Group tables saved.")

# --- Match scores ---------------------------------------------------------- #
with tab_m:
    st.caption("Tick a match once it's played, enter the score, then save.")
    pending = {}
    for grp in groups:
        with st.expander(f"Group {grp}"):
            for m in matches_for_group(grp):
                mid = m["id"]
                ex = results.get(("per_game", mid))
                c0, c1, c2, c3 = st.columns([3, 1, 1, 1])
                c0.write(f"**{m['home']}** vs **{m['away']}**")
                played = c1.checkbox("Played", value=ex is not None, key=f"pl_{mid}")
                hs = c2.number_input("H", 0, 20, value=int(ex["hs"]) if ex else 0,
                                     key=f"ah_{mid}", label_visibility="collapsed")
                as_ = c3.number_input("A", 0, 20, value=int(ex["as"]) if ex else 0,
                                      key=f"aa_{mid}", label_visibility="collapsed")
                if played:
                    outcome = "H" if hs > as_ else "A" if as_ > hs else "D"
                    pending[mid] = {"hs": int(hs), "as": int(as_), "outcome": outcome}
    if st.button("💾 Save match scores"):
        for mid, actual in pending.items():
            db.save_result("per_game", mid, actual)
        st.success(f"Saved {len(pending)} match result(s).")

# --- Third-place qualifiers ------------------------------------------------ #
with tab_t:
    st.caption("The 8 third-placed teams that actually advanced.")
    ex = results.get(("third_place", "advancing")) or []
    adv = st.multiselect("Advancing 3rd-placed teams", teams, default=ex, max_selections=8)
    if st.button("💾 Save 3rd-place qualifiers"):
        db.save_result("third_place", "advancing", adv)
        st.success("3rd-place qualifiers saved.")

# --- Knockout -------------------------------------------------------------- #
with tab_k:
    st.caption("Teams that actually reached each round, the champion, and the Golden Boot winner.")
    for key, label, size, _pts in KNOCKOUT_ROUNDS:
        ex = results.get(("knockout", key)) or []
        sel = st.multiselect(f"{label} ({size})", teams, default=ex,
                             max_selections=size, key=f"ak_{key}")
        if st.button(f"💾 Save {label}", key=f"sak_{key}"):
            db.save_result("knockout", key, sel)
            st.success(f"{label} saved.")
        st.divider()

    champ_ex = results.get(("knockout", "champion")) or "—"
    champ_opts = ["—"] + teams
    champ = st.selectbox("🏆 Champion", champ_opts,
                         index=champ_opts.index(champ_ex) if champ_ex in champ_opts else 0)
    if st.button("💾 Save champion"):
        db.save_result("knockout", "champion", None if champ == "—" else champ)
        st.success("Champion saved.")

# --- Top scorers ----------------------------------------------------------- #
with tab_s:
    st.caption("The actual top 3 goalscorers, in order (1st = Golden Boot).")
    ex = (results.get(("scorers", "top3")) or ["", "", ""])
    ex = (list(ex) + ["", "", ""])[:3]
    labels = ["🥇 Golden Boot (1st)", "🥈 2nd", "🥉 3rd"]
    top3 = [st.text_input(labels[i], value=str(ex[i]), key=f"asc_{i}") for i in range(3)]
    if st.button("💾 Save top scorers"):
        db.save_result("scorers", "top3", [t.strip() for t in top3])
        st.success("Top scorers saved.")
