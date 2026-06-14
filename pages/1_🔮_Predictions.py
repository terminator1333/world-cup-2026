"""Make predictions — register, then fill any sections you like."""
from __future__ import annotations

import streamlit as st

from datetime import date

from lib import db, theme, util
from lib.assets import find_asset, slugify
from lib.data import (KNOCKOUT_ROUNDS, all_teams, knockout_meta, load_groups,
                      match_played, matches_for_group, team_meta)
from lib.flags import emoji_flag, flag_img, team_chip, text_on
from lib.standings import best_thirds, compute_table
from lib.bracket import build_qualifiers, seed_bracket

st.set_page_config(page_title="Predictions · WC2026", page_icon="🔮", layout="wide")
theme.inject()
theme.hero("YOUR PREDICTIONS", "Pick as much or as little as you like — every section is optional.")

LOCKED = util.is_locked()

# --------------------------------------------------------------------------- #
# Auth
# --------------------------------------------------------------------------- #
user = util.current_user()
if user is None:
    st.markdown('<span class="wc-badge">STEP 1 · WHO ARE YOU?</span>', unsafe_allow_html=True)
    with st.form("auth"):
        a, b = st.columns(2)
        name = a.text_input("Your name", max_chars=24)
        pin = b.text_input("PIN", type="password", max_chars=12,
                            help="A short secret so only you can edit your picks.")
        if st.form_submit_button("Enter / Register 🔓", use_container_width=True):
            participant, err = db.upsert_participant(name, pin)
            if err:
                st.error(err)
            else:
                util.set_user(participant)
                st.rerun()
    st.stop()

top = st.columns([3, 1])
top[0].success(f"Signed in as **{user['name']}**")
if top[1].button("Sign out", use_container_width=True):
    util.logout()
    st.rerun()

# Some participants keep editing fixtures that haven't kicked off yet.
EDITOR = util.is_unplayed_editor(user)

if LOCKED and not EDITOR:
    st.warning(f"🔒 Predictions locked at kickoff ({util.lock_dt():%b %d, %Y %H:%M}). "
               "You can view your picks but no longer edit them.")
elif LOCKED and EDITOR:
    st.info("✏️ You can still edit predictions for games that **haven't kicked off yet**. "
            "Matches that have already started are locked.")


def _match_locked(m) -> bool:
    """A fixture is editable while unlocked, or — for editors — until kickoff."""
    if not LOCKED:
        return False
    if EDITOR and not match_played(m):
        return False
    return True


pid = user["id"]
groups = load_groups()
teams = all_teams()


def save(category, payload, label):
    if LOCKED and not EDITOR:
        st.error("Predictions are locked.")
        return
    db.save_prediction(pid, category, payload)
    st.success(f"✅ {label} saved!")
    st.balloons()


tab_g, tab_k, tab_s = st.tabs(
    ["⚽ Groups & Matches", "🏆 Knockout bracket", "🏅 Awards"])

# --------------------------------------------------------------------------- #
# Groups & Matches — predict scores; tables + qualifiers + 3rd-place auto-update
# --------------------------------------------------------------------------- #
_ADV = [("🥇 ADV", "adv-1"), ("🥈 ADV", "adv-2"), ("🥉 3RD", "adv-3"), ("❌ OUT", "adv-out")]


def _mini_team(team, side):
    return (f'<div class="mt {side}">{flag_img(team, 24)}'
            f'<span class="mt-n">{team}</span></div>')


def _table_html(order, stats):
    rows = ""
    for pos, t in enumerate(order):
        label, cls = _ADV[pos]
        s = stats[t]
        rows += (
            f'<div class="tbl-row"><span class="pos-num">{pos + 1}</span>'
            f'{flag_img(t, 22)}<span class="tbl-name">{t}</span>'
            f'<span class="adv-badge {cls}">{label}</span>'
            f'<span class="tbl-gd">{s["GD"]:+d}</span>'
            f'<span class="tbl-pts">{s["Pts"]}<small>pt</small></span></div>'
        )
    return f'<div class="mini-table">{rows}</div>'


def _city_thumb(city):
    url, ext = find_asset("cities", slugify(city))
    if url and ext not in (".webm", ".mp4"):
        return f'<img class="mthumb" src="{url}" alt="">'
    return ""


def _match_meta(m):
    d = date.fromisoformat(m["date"])
    return (f'<div class="m-meta">{_city_thumb(m["city"])}'
            f'<span>{d:%b} {d.day} · {m["time"]} · {m["city"]} {m["city_flag"]}</span></div>')


with tab_g:
    saved_pg = db.get_prediction(pid, "per_game") or {}
    picks = {}
    group_tables = {}

    gcols = st.columns(2)
    for idx, (grp, gteams) in enumerate(groups.items()):
        gmatches = matches_for_group(grp)
        has_prev = any(saved_pg.get(m["id"]) for m in gmatches)
        group_editable = any(not _match_locked(m) for m in gmatches)
        with gcols[idx % 2]:
            with st.container(border=True):
                head = st.columns([2.6, 1.4])
                head[0].markdown(f'<span class="wc-badge">GROUP {grp}</span>',
                                 unsafe_allow_html=True)
                on = head[1].toggle("Predict", value=has_prev,
                                    key=f"grp_on_{pid}_{grp}", disabled=not group_editable)
                scores = {}
                for m in gmatches:
                    mid, prev = m["id"], saved_pg.get(m["id"], {})
                    m_locked = _match_locked(m)
                    st.markdown(_match_meta(m), unsafe_allow_html=True)
                    r = st.columns([2.3, 0.85, 0.2, 0.85, 2.3])
                    r[0].markdown(_mini_team(m["home"], "home"), unsafe_allow_html=True)
                    hs = r[1].number_input(m["home"], 0, 20, value=int(prev.get("hs") or 0),
                                           key=f"hs_{mid}", label_visibility="collapsed",
                                           disabled=m_locked or not on)
                    r[2].markdown("<div class='mt-dash'>–</div>", unsafe_allow_html=True)
                    as_ = r[3].number_input(m["away"], 0, 20, value=int(prev.get("as") or 0),
                                            key=f"as_{mid}", label_visibility="collapsed",
                                            disabled=m_locked or not on)
                    r[4].markdown(_mini_team(m["away"], "away"), unsafe_allow_html=True)
                    if on:
                        scores[mid] = {"hs": int(hs), "as": int(as_)}
                        picks[mid] = {"outcome": "H" if hs > as_ else "A" if as_ > hs else "D",
                                      "hs": int(hs), "as": int(as_)}
                if on:
                    order, stats = compute_table(gteams, gmatches, scores)
                    group_tables[grp] = (order, stats)
                    st.markdown(_table_html(order, stats), unsafe_allow_html=True)

    # 3rd-place race — auto-computed from the predicted groups
    thirds = best_thirds(group_tables) if group_tables else []
    if thirds:
        st.write("")
        st.markdown('<span class="wc-badge">🥉 3RD-PLACE RACE · TOP 8 QUALIFY</span>',
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

    st.write("")
    if st.button(f"💾 Save predictions  ·  {len(group_tables)} group(s), {len(picks)} matches",
                 disabled=LOCKED and not EDITOR, key="save_groups", use_container_width=True):
        if LOCKED and not EDITOR:
            st.error("Predictions are locked.")
        else:
            go = {g: list(group_tables[g][0]) for g in group_tables}
            adv = [t for (_g, t, _s) in best_thirds(group_tables)[:8]]
            db.save_prediction(pid, "per_game", picks)
            db.save_prediction(pid, "group_order", go)
            db.save_prediction(pid, "third_place", {"advancing": adv})
            st.success("✅ Saved games, group tables and 3rd-place qualifiers!")
            st.balloons()

# --------------------------------------------------------------------------- #
# 4) Knockout bracket
# --------------------------------------------------------------------------- #
def _ko_meta(meta):
    url, ext = find_asset("cities", slugify(meta["city"]))
    img = (f'<img class="ko-meta-img" src="{url}">'
           if url and ext not in (".webm", ".mp4") else "")
    d = date.fromisoformat(meta["date"])
    return (f'<div class="ko-meta">{img}'
            f'<span>{d:%b} {d.day} · {meta["time"]}<br>{meta["city"]} {meta["city_flag"]}</span>'
            f'</div>')


def _tree_slot(a, b, key, i, saved, meta, scores_out):
    """One bracket tie: enter the scoreline; the winner advances (pens if level)."""
    base = f"kop_{pid}_{key}_{i}"
    prev = (saved.get("scores") or {}).get(f"{key}_{i}", {})
    with st.container(border=True):
        st.markdown('<span class="kotie"></span>' + _ko_meta(meta), unsafe_allow_html=True)
        goals = []
        for idx, t in enumerate((a, b)):
            r = st.columns([2.2, 1])
            r[0].markdown(
                f'<div class="ko-team">{flag_img(t["team"], 20)}'
                f'<span>{t["team"]} <small>{t["grp"]}{t["pos"]}</small></span></div>',
                unsafe_allow_html=True)
            goals.append(int(r[1].number_input(
                t["team"], 0, 30, value=int(prev.get("hs" if idx == 0 else "as") or 0),
                key=f"{base}_g{idx}", label_visibility="collapsed",
                disabled=LOCKED and not EDITOR)))
        ga, gb = goals
        pens = None
        if ga > gb:
            winner = a
        elif gb > ga:
            winner = b
        else:
            default = 1 if prev.get("pens") == b["team"] else 0
            pw = st.radio("pens", [a["team"], b["team"]], index=default, horizontal=True,
                          label_visibility="collapsed", key=f"{base}_pw",
                          disabled=LOCKED and not EDITOR)
            winner = a if pw == a["team"] else b
            pens = winner["team"]
        st.markdown(f'<div class="ko-adv">✓ {winner["team"]} advance{" (pens)" if pens else ""}</div>',
                    unsafe_allow_html=True)
    rec = {"hs": ga, "as": gb}
    if pens:
        rec["pens"] = pens
    scores_out[f"{key}_{i}"] = rec
    return winner


with tab_k:
    saved = db.get_prediction(pid, "knockout") or {}
    saved_pg = db.get_prediction(pid, "per_game") or {}
    ranked, completed = build_qualifiers(saved_pg)

    if completed < 12:
        st.warning(f"⚽ Predict **all 12 groups** in the *Groups & Matches* tab to unlock your "
                   f"bracket — **{completed}/12** complete.")
        st.progress(completed / 12)
    else:
        slotted = seed_bracket(ranked)
        rounds = [("r16", "ROUND OF 32"), ("qf", "ROUND OF 16"), ("sf", "QUARTER-FINALS"),
                  ("final", "SEMI-FINALS"), ("champion", "FINAL")]
        ko_pts = {"r16": "+2", "qf": "+3", "sf": "+5", "final": "+8", "champion": "+15"}
        # round headers in their own aligned row, with the points each pick is worth
        for hc, (key, label) in zip(st.columns(len(rounds)), rounds):
            hc.markdown(f'<div class="rnd-head">{label}<br><small>{ko_pts[key]} pts each</small></div>',
                        unsafe_allow_html=True)
        # the bracket itself — each column's ties are flex-distributed to centre them
        payload, cur, ko_scores = {}, slotted, {}
        cols = st.columns(len(rounds))
        for ci, (key, label) in enumerate(rounds):
            with cols[ci]:
                matches = [(cur[2 * i], cur[2 * i + 1]) for i in range(len(cur) // 2)]
                winners = [_tree_slot(a, b, key, i, saved, knockout_meta(ci, i), ko_scores)
                           for i, (a, b) in enumerate(matches)]
                if key == "champion":
                    payload["champion"] = winners[0]["team"]
                else:
                    payload[key] = [w["team"] for w in winners]
                    cur = winners
        payload["scores"] = ko_scores

        champ = payload["champion"]
        st.markdown(
            f'<div class="champ-banner">{flag_img(champ, 54)}'
            f'<div><span class="champ-kick">WORLD CHAMPIONS</span><br>{champ} 🏆</div></div>',
            unsafe_allow_html=True,
        )
        st.caption("⚽ Predict the Golden Boot & top scorers in the **Top Scorers** tab.")
        if st.button("💾 Save knockout bracket", disabled=LOCKED and not EDITOR,
                     key="save_ko", use_container_width=True):
            save("knockout", payload, "Knockout bracket")

# --------------------------------------------------------------------------- #
# 5) Individual awards — top scorers, best player, golden glove
# --------------------------------------------------------------------------- #
with tab_s:
    st.markdown('<span class="wc-badge">🥇 TOP 3 GOALSCORERS</span>', unsafe_allow_html=True)
    st.write("Name the **top 3 goalscorers**, in order. Right player **and** rank = **+6** · "
             "right player, wrong rank = **+3**. Slot 1 is your **Golden Boot** pick.")
    saved_s = ((db.get_prediction(pid, "scorers") or {}).get("top3", []) + ["", "", ""])[:3]
    medals = ["🥇 Golden Boot (1st)", "🥈 2nd top scorer", "🥉 3rd top scorer"]
    top3 = [st.text_input(medals[i], value=saved_s[i], key=f"sc_{pid}_{i}", max_chars=40,
                          disabled=LOCKED and not EDITOR,
                          placeholder="e.g. Kylian Mbappé") for i in range(3)]

    st.write("")
    st.markdown('<span class="wc-badge">🏅 INDIVIDUAL AWARDS · +6 EACH</span>', unsafe_allow_html=True)
    saved_a = db.get_prediction(pid, "awards") or {}
    bp = st.text_input("⭐ Best Player (Golden Ball)", value=saved_a.get("best_player", ""),
                       key=f"bp_{pid}", max_chars=40, disabled=LOCKED and not EDITOR,
                       placeholder="best player of the tournament")
    gg = st.text_input("🧤 Golden Glove (best goalkeeper)", value=saved_a.get("golden_glove", ""),
                       key=f"gg_{pid}", max_chars=40, disabled=LOCKED and not EDITOR,
                       placeholder="best goalkeeper")

    if st.button("💾 Save awards", disabled=LOCKED and not EDITOR, key="save_scorers",
                 use_container_width=True):
        db.save_prediction(pid, "scorers", {"top3": [t.strip() for t in top3]})
        db.save_prediction(pid, "awards",
                           {"best_player": bp.strip(), "golden_glove": gg.strip()})
        st.success("✅ Awards saved!")
        st.balloons()
