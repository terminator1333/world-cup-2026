"""Everyone's predictions, side by side — styled like the predicting view."""
from __future__ import annotations

from datetime import date as _date

import streamlit as st

from lib import db, theme
from lib.bracket import build_qualifiers, seed_bracket
from lib.data import group_matches, load_groups, matches_for_group
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


_KO_ROUNDS = [("r16", "ROUND OF 32", "+2"), ("qf", "ROUND OF 16", "+3"),
              ("sf", "QUARTER-FINALS", "+5"), ("final", "SEMI-FINALS", "+8"),
              ("champion", "FINAL", "+15")]


def _ko_tree_html(per_game, ko):
    """Read-only bracket tree from a player's group scores + knockout picks."""
    ranked, completed = build_qualifiers(per_game)
    if completed < 12:
        return None
    cur = seed_bracket(ranked)
    cols = ""
    for key, label, pts in _KO_ROUNDS:
        sr = [ko.get("champion")] if key == "champion" else (ko.get(key) or [])
        matches = [(cur[2 * i], cur[2 * i + 1]) for i in range(len(cur) // 2)]
        ties, winners = "", []
        for a, b in matches:
            win = b if (b["team"] in sr and a["team"] not in sr) else a
            winners.append(win)
            rows = "".join(
                f'<div class="rorow {"win" if t["team"] == win["team"] else ""}">'
                f'{flag_img(t["team"], 18)}<span>{t["team"]}</span></div>' for t in (a, b))
            ties += f'<div class="rotie">{rows}</div>'
        cols += (f'<div class="rocol"><div class="rocol-head">{label}<br>'
                 f'<small>{pts} pts</small></div>{ties}</div>')
        cur = winners
    champ = cur[0]["team"]
    cols += (f'<div class="rocol champ"><div class="rocol-head">CHAMPION</div>'
             f'<div class="rochamp">{flag_img(champ, 40)}{champ} 🏆</div></div>')
    return f'<div class="rotree">{cols}</div>'


def _group_tables(per_game):
    gt = {}
    for grp, gteams in groups.items():
        gm = matches_for_group(grp)
        sc = {m["id"]: per_game[m["id"]] for m in gm if per_game.get(m["id"])}
        if len(sc) == len(gm):
            gt[grp] = compute_table(gteams, gm, sc)
    return gt


def _score_rows_by_date(per_game):
    """Predicted group scorelines across all groups, ordered by kickoff date."""
    out, cur_date = "", None
    for m in group_matches():            # already sorted by (date, group)
        p = per_game.get(m["id"])
        if not p:
            continue
        if m["date"] != cur_date:
            cur_date = m["date"]
            d = _date.fromisoformat(m["date"])
            out += f'<div class="apk-grp">{d:%a, %b} {d.day}</div>'
        out += (
            f'<div class="apk-score">{flag_img(m["home"], 20)}'
            f'<span class="apk-tn">{m["home"]}</span>'
            f'<b class="apk-num">{p["hs"]} – {p["as"]}</b>'
            f'<span class="apk-tn rt">{m["away"]}</span>{flag_img(m["away"], 20)}</div>'
        )
    return out


def _ko_score_rows(per_game, ko):
    ranked, completed = build_qualifiers(per_game)
    if completed < 12:
        return ""
    cur = seed_bracket(ranked)
    scores = ko.get("scores") or {}
    out = ""
    for key, label, _pts in _KO_ROUNDS:
        sr = [ko.get("champion")] if key == "champion" else (ko.get(key) or [])
        matches = [(cur[2 * i], cur[2 * i + 1]) for i in range(len(cur) // 2)]
        rows, winners = "", []
        for idx, (a, b) in enumerate(matches):
            winners.append(b if (b["team"] in sr and a["team"] not in sr) else a)
            sc = scores.get(f"{key}_{idx}", {})
            num = (f'{sc["hs"]} – {sc["as"]}' if sc.get("hs") is not None
                   and sc.get("as") is not None else "– – –")
            pens = ' <small>(pens)</small>' if sc.get("pens") else ""
            rows += (
                f'<div class="apk-score">{flag_img(a["team"], 20)}'
                f'<span class="apk-tn">{a["team"]}</span><b class="apk-num">{num}</b>'
                f'<span class="apk-tn rt">{b["team"]}</span>{flag_img(b["team"], 20)}{pens}</div>'
            )
        if rows:
            out += f'<div class="apk-grp">{label}</div>{rows}'
        cur = winners
    return out


def _person(pid):
    st.markdown(f'<div class="apk-name">{names[pid]}</div>', unsafe_allow_html=True)


tab_g, tab_k, tab_s = st.tabs(["🥇 Group stage", "🏆 Knockout", "⚽ Exact scores"])

# --- Group stage ----------------------------------------------------------- #
with tab_g:
    for pid in chosen:
        data = by_pid.get(pid, {})
        with st.container(border=True):
            _person(pid)
            per_game = data.get("per_game") or {}
            group_order = data.get("group_order") or {}
            gt = _group_tables(per_game)
            if not (gt or group_order):
                st.caption("No group predictions yet.")
                continue
            gcols = st.columns(2)
            for idx, (grp, gteams) in enumerate(groups.items()):
                if grp in gt:
                    order, stats = gt[grp]
                elif grp in group_order:
                    order, stats = group_order[grp], None
                else:
                    continue
                with gcols[idx % 2]:
                    st.markdown(f'<div class="apk-grp">GROUP {grp}</div>{_table_html(order, stats)}',
                                unsafe_allow_html=True)
            if gt:
                thirds = best_thirds(gt)
                if thirds:
                    st.markdown('<span class="wc-badge">🥉 3RD-PLACE RACE</span>',
                                unsafe_allow_html=True)
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

# --- Knockout -------------------------------------------------------------- #
with tab_k:
    for pid in chosen:
        data = by_pid.get(pid, {})
        with st.container(border=True):
            _person(pid)
            per_game = data.get("per_game") or {}
            ko = data.get("knockout") or {}
            if ko.get("champion"):
                st.markdown(
                    f'<div class="champ-banner">{flag_img(ko["champion"], 54)}'
                    f'<div><span class="champ-kick">CHAMPION PICK</span><br>'
                    f'{ko["champion"]} 🏆</div></div>', unsafe_allow_html=True)
            tree = _ko_tree_html(per_game, ko) if ko else None
            if tree:
                st.markdown(tree, unsafe_allow_html=True)
            elif not ko:
                st.caption("No knockout bracket yet.")

            scorers = [s for s in (data.get("scorers") or {}).get("top3", []) if s]
            awards = data.get("awards") or {}
            if scorers or awards.get("best_player") or awards.get("golden_glove"):
                st.markdown('<span class="wc-badge">🏅 AWARDS</span>', unsafe_allow_html=True)
                medals = ["🥇", "🥈", "🥉"]
                if scorers:
                    st.markdown("**Top scorers:** "
                                + " · ".join(f"{medals[i]} {s}" for i, s in enumerate(scorers)))
                if awards.get("best_player"):
                    st.markdown(f"⭐ **Best Player:** {awards['best_player']}")
                if awards.get("golden_glove"):
                    st.markdown(f"🧤 **Golden Glove:** {awards['golden_glove']}")

# --- Exact scores ---------------------------------------------------------- #
with tab_s:
    for pid in chosen:
        data = by_pid.get(pid, {})
        with st.container(border=True):
            _person(pid)
            per_game = data.get("per_game") or {}
            ko = data.get("knockout") or {}
            shown = False
            rows = _score_rows_by_date(per_game) if per_game else ""
            if rows:
                shown = True
                st.markdown('<span class="wc-badge">⚽ GROUP MATCH SCORES</span>',
                            unsafe_allow_html=True)
                st.markdown(rows, unsafe_allow_html=True)
            ko_rows = _ko_score_rows(per_game, ko) if ko else ""
            if ko_rows:
                shown = True
                st.markdown('<span class="wc-badge">🏆 KNOCKOUT SCORES</span>',
                            unsafe_allow_html=True)
                st.markdown(ko_rows, unsafe_allow_html=True)
            if not shown:
                st.caption("No scorelines predicted yet.")
