"""Everyone's predictions, side by side — styled like the predicting view."""
from __future__ import annotations

import streamlit as st

from lib import db, theme
from lib.data import load_groups, matches_for_group
from lib.flags import flag_img, team_chip
from lib.standings import best_thirds, compute_table

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

if not names:
    st.info("No players yet — be the first to register on the Predictions page!")
    st.stop()

who = st.selectbox("Show picks for", ["Everyone"] + sorted(names.values()))
chosen = [pid for pid, n in names.items() if who in ("Everyone", n)]

_ADV = [("🥇 ADV", "adv-1"), ("🥈 ADV", "adv-2"), ("🥉 3RD", "adv-3"), ("❌ OUT", "adv-out")]
_KO_LABELS = [("r16", "Last 16"), ("qf", "Quarter-finalists"),
              ("sf", "Semi-finalists"), ("final", "Finalists")]


def _table_html(order, stats=None):
    rows = ""
    for pos, t in enumerate(order[:4]):
        label, cls = _ADV[pos]
        s = stats.get(t) if stats else None
        gd = f'{s["GD"]:+d}' if s else ""
        pts = f'{s["Pts"]}<small>pt</small>' if s else ""
        rows += (
            f'<div class="tbl-row"><span class="pos-num">{pos + 1}</span>'
            f'{flag_img(t, 22)}<span class="tbl-name">{t}</span>'
            f'<span class="adv-badge {cls}">{label}</span>'
            f'<span class="tbl-gd">{gd}</span><span class="tbl-pts">{pts}</span></div>'
        )
    return f'<div class="mini-table">{rows}</div>'


def _score_rows(grp, per_game):
    out = ""
    for m in matches_for_group(grp):
        p = per_game.get(m["id"])
        if not p:
            continue
        out += (
            f'<div class="apk-score">{flag_img(m["home"], 20)}'
            f'<span class="apk-tn">{m["home"]}</span>'
            f'<b class="apk-num">{p["hs"]} – {p["as"]}</b>'
            f'<span class="apk-tn rt">{m["away"]}</span>{flag_img(m["away"], 20)}</div>'
        )
    return out


for pid in chosen:
    data = by_pid.get(pid, {})
    with st.container(border=True):
        st.markdown(f'<div class="apk-name">{names[pid]}</div>', unsafe_allow_html=True)
        if not data:
            st.caption("No predictions submitted yet.")
            continue

        per_game = data.get("per_game") or {}
        group_order = data.get("group_order") or {}
        ko = data.get("knockout") or {}

        # champion banner
        if ko.get("champion"):
            st.markdown(
                f'<div class="champ-banner">{flag_img(ko["champion"], 54)}'
                f'<div><span class="champ-kick">CHAMPION PICK</span><br>{ko["champion"]} 🏆</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        # group standings (computed from their scores → same look as predicting)
        group_tables = {}
        for grp, gteams in groups.items():
            gm = matches_for_group(grp)
            scores = {m["id"]: per_game[m["id"]] for m in gm if per_game.get(m["id"])}
            if len(scores) == len(gm):
                group_tables[grp] = compute_table(gteams, gm, scores)

        if group_tables or group_order:
            st.markdown('<span class="wc-badge">🥇 GROUP STANDINGS</span>', unsafe_allow_html=True)
            gcols = st.columns(2)
            for idx, (grp, gteams) in enumerate(groups.items()):
                if grp in group_tables:
                    order, stats = group_tables[grp]
                elif grp in group_order:
                    order, stats = group_order[grp], None
                else:
                    continue
                with gcols[idx % 2]:
                    st.markdown(f'<div class="apk-grp">GROUP {grp}</div>{_table_html(order, stats)}',
                                unsafe_allow_html=True)

        # 3rd-place race
        if group_tables:
            thirds = best_thirds(group_tables)
            if thirds:
                st.markdown('<span class="wc-badge">🥉 3RD-PLACE RACE</span>', unsafe_allow_html=True)
                rows = ""
                for i, (grp, t, s) in enumerate(thirds):
                    cls, tag = ("adv-2", "✅ QUALIFIES") if i < 8 else ("adv-out", "OUT")
                    rows += (
                        f'<div class="tbl-row"><span class="pos-num">{i + 1}</span>'
                        f'{flag_img(t, 22)}<span class="tbl-name">{t} <small>· {grp}</small></span>'
                        f'<span class="adv-badge {cls}">{tag}</span>'
                        f'<span class="tbl-gd">{s["GD"]:+d}</span>'
                        f'<span class="tbl-pts">{s["Pts"]}<small>pt</small></span></div>'
                    )
                st.markdown(f'<div class="mini-table">{rows}</div>', unsafe_allow_html=True)
        elif data.get("third_place", {}).get("advancing"):
            st.markdown('<span class="wc-badge">🥉 3RD-PLACE QUALIFIERS</span>', unsafe_allow_html=True)
            st.markdown(" ".join(team_chip(t) for t in data["third_place"]["advancing"]),
                        unsafe_allow_html=True)

        # match scores
        if per_game:
            with st.expander(f"⚽ Match scores ({len(per_game)})"):
                for grp in groups:
                    rows = _score_rows(grp, per_game)
                    if rows:
                        st.markdown(f'<div class="apk-grp">GROUP {grp}</div>{rows}',
                                    unsafe_allow_html=True)

        # knockout bracket
        if ko:
            with st.expander("🏆 Knockout run"):
                for key, label in _KO_LABELS:
                    if ko.get(key):
                        st.markdown(f'<div class="apk-grp">{label}</div>'
                                    + " ".join(team_chip(t) for t in ko[key]),
                                    unsafe_allow_html=True)
                if ko.get("top_scorer"):
                    st.markdown(f"**⚽ Golden Boot:** {ko['top_scorer']}")
