"""Shared logic for the **Knockout Pool** — a separate competition played on the
REAL 2026 Round-of-32 bracket (actual qualifiers, fixed FIFA slotting).

Unlike the full-tournament "knockout" prediction (which seeds each player's own
predicted group results), every player here predicts the SAME real bracket:
South Africa v Canada, Brazil v Japan, USA v Bosnia, … all the way to the final.

A pool payload looks like:
    {"r32": [16 winners], "r16": [8], "qf": [4], "sf": [2], "champion": "Team",
     "scores": {"r32_0": {"hs":2,"as":1,"pens":"Team"?}, ...}}
Winner lists are in bracket order; `scores` is keyed by f"{round}_{index}".

This module is import-light (no Streamlit at module load) so `scoring.py` can use
`bracket_matches` in plain Python. The interactive editor lazily imports Streamlit.
"""
from __future__ import annotations

from datetime import date as _date

from .assets import find_asset, slugify
from .data import KO_POOL_POINTS, KO_POOL_ROUNDS, ko_r32_ties, ko_round_meta
from .flags import flag_img


# --------------------------------------------------------------------------- #
# Pure bracket logic
# --------------------------------------------------------------------------- #
def r32_slots() -> list[dict]:
    """The 32 starting teams as {team, grp, pos} dicts, in bracket order
    (home0, away0, home1, away1, …) so consecutive pairs are R32 ties."""
    slots = []
    for tie in ko_r32_ties():
        for side in ("home", "away"):
            seed = tie[f"{side}_seed"]
            slots.append({"team": tie[side], "grp": seed[0], "pos": seed[1:]})
    return slots


def team_slot_map() -> dict:
    """{team_name: slot dict} — lets later rounds show a team's group seed."""
    return {s["team"]: s for s in r32_slots()}


def derive_winner(a_team: str, b_team: str, score: dict | None):
    """Winning team name for a tie, or None if undecided. Level → penalty pick."""
    if not score:
        return None
    hs, as_ = score.get("hs"), score.get("as")
    if hs is None or as_ is None:
        return None
    if hs > as_:
        return a_team
    if as_ > hs:
        return b_team
    return score.get("pens")  # chosen on penalties (team name) or None


def bracket_matches(payload: dict | None) -> dict:
    """Reconstruct every round's ties from a payload's stored winners.

    Returns {round_key: [{'a','b','winner','score'}, …]} where each round's
    matchups follow the previous round's winners (so a partial bracket still
    renders), keyed positionally to mirror `scores`.
    """
    payload = payload or {}
    cur = [s["team"] for s in r32_slots()]
    scores = payload.get("scores") or {}
    out: dict = {}
    for key, _lbl, _play, _n in KO_POOL_ROUNDS:
        n = len(cur) // 2
        winners = ([payload.get("champion")] if key == "champion"
                   else list(payload.get(key) or []))
        ties, nxt = [], []
        for i in range(n):
            a, b = cur[2 * i], cur[2 * i + 1]
            w = winners[i] if i < len(winners) else None
            ties.append({"a": a, "b": b, "winner": w, "score": scores.get(f"{key}_{i}")})
            nxt.append(w)
        out[key] = ties
        cur = nxt
    return out


def advancing_sets(payload: dict | None, require_played: bool = False) -> dict:
    """{round_key: set(teams advancing out of that round)} from a payload.

    With `require_played=True`, a tie only counts once its score is flagged
    "played" — so an admin-entered *actual* bracket never scores rounds whose
    games haven't happened yet (the editor pre-fills placeholder winners)."""
    sets = {}
    for key, ties in bracket_matches(payload).items():
        s = set()
        for t in ties:
            sc = t.get("score") or {}
            if require_played and not sc.get("played"):
                continue
            if t["winner"]:
                s.add(t["winner"])
        sets[key] = s
    return sets


def actual_progress(actual: dict | None):
    """From a played-flagged actual bracket, return
    (advanced_by_round, eliminated_teams) — used to mark picks ✓ / ✗."""
    advanced, eliminated = {}, set()
    for key, ties in bracket_matches(actual).items():
        s = set()
        for t in ties:
            sc = t.get("score") or {}
            if not sc.get("played"):
                continue
            w = t["winner"]
            if w:
                s.add(w)
            for tm in (t["a"], t["b"]):
                if tm and tm != w:
                    eliminated.add(tm)
        advanced[key] = s
    return advanced, eliminated


# --------------------------------------------------------------------------- #
# Read-only HTML tree (All Picks)
# --------------------------------------------------------------------------- #
def _seed_of(slot: dict, team: str) -> str:
    s = slot.get(team)
    return f'{s["grp"]}{s["pos"]}' if s else ""


def tree_html(payload: dict | None, actual: dict | None = None) -> str:
    """Read-only bracket tree for a saved pool payload. If `actual` (the real
    played-flagged bracket) is given, a pick is marked ✓ once that team has
    actually advanced and ✗ once it's been knocked out; undecided ties stay
    unmarked (so future rounds never show a misleading red)."""
    bm = bracket_matches(payload)
    advanced, eliminated = actual_progress(actual) if actual else ({}, set())
    slot = team_slot_map()
    cols = ""
    for key, _lbl, play, _n in KO_POOL_ROUNDS:
        pts = KO_POOL_POINTS.get(key)
        body = ""
        for t in bm[key]:
            win = t["winner"]
            rows = ""
            for tm in (t["a"], t["b"]):
                cls = "win" if tm and tm == win else ""
                mark = ""
                if actual is not None and tm and tm == win:
                    if tm in advanced.get(key, set()):
                        cls += " ok"; mark = " ✓"
                    elif tm in eliminated:
                        cls += " miss"; mark = " ✗"
                rows += (f'<div class="rorow {cls}">{flag_img(tm, 18) if tm else ""}'
                         f'<span>{tm or "—"}</span><small>{_seed_of(slot, tm)}{mark}</small></div>')
            sc = t["score"] or {}
            num = (f'{sc["hs"]}–{sc["as"]}' if sc.get("hs") is not None
                   and sc.get("as") is not None else "")
            pens = " (p)" if sc.get("pens") else ""
            scline = f'<div class="rotie-sc">{num}{pens}</div>' if num else ""
            body += f'<div class="rotie">{rows}{scline}</div>'
        head = f'{play}<br><small>+{pts} pts</small>' if pts else play
        cols += f'<div class="rocol"><div class="rocol-head">{head}</div>{body}</div>'
    champ = (payload or {}).get("champion")
    if champ:
        cols += (f'<div class="rocol champ"><div class="rocol-head">CHAMPION</div>'
                 f'<div class="rochamp">{flag_img(champ, 40)}{champ} 🏆</div></div>')
    return f'<div class="rotree">{cols}</div>'


# --------------------------------------------------------------------------- #
# Interactive bracket editor (Streamlit) — shared by the pool page + Admin
# --------------------------------------------------------------------------- #
def _meta_html(meta: dict) -> str:
    if not meta:
        return ""
    url, ext = find_asset("cities", slugify(meta.get("city", "")))
    img = (f'<img class="ko-meta-img" src="{url}">'
           if url and ext not in (".webm", ".mp4") else "")
    try:
        dd = _date.fromisoformat(meta.get("date", ""))
        ds = f"{dd:%b} {dd.day}"
    except (ValueError, TypeError):
        ds = meta.get("date", "")
    t = f' · {meta["time"]}' if meta.get("time") else ""
    return (f'<div class="ko-meta">{img}'
            f'<span>{ds}{t}<br>{meta.get("city", "")}</span></div>')


def _tie_widget(st, a, b, key, i, saved_scores, meta, scores_out, locked, prefix,
                played_toggle=False):
    base = f"{prefix}_{key}_{i}"
    prev = saved_scores.get(f"{key}_{i}", {})
    with st.container(border=True):
        st.markdown('<span class="kotie"></span>' + _meta_html(meta), unsafe_allow_html=True)
        played = None
        if played_toggle:
            played = st.checkbox("Played", value=bool(prev.get("played")),
                                 key=f"{base}_pl")
        goals = []
        for idx, t in enumerate((a, b)):
            r = st.columns([2.2, 1])
            r[0].markdown(
                f'<div class="ko-team">{flag_img(t["team"], 20)}'
                f'<span>{t["team"]} <small>{t["grp"]}{t["pos"]}</small></span></div>',
                unsafe_allow_html=True)
            goals.append(int(r[1].number_input(
                t["team"], 0, 30, value=int(prev.get("hs" if idx == 0 else "as") or 0),
                key=f"{base}_g{idx}", label_visibility="collapsed", disabled=locked)))
        ga, gb = goals
        pens = None
        if ga > gb:
            winner = a
        elif gb > ga:
            winner = b
        else:
            default = 1 if prev.get("pens") == b["team"] else 0
            pw = st.radio("pens", [a["team"], b["team"]], index=default, horizontal=True,
                          label_visibility="collapsed", key=f"{base}_pw", disabled=locked)
            winner = a if pw == a["team"] else b
            pens = winner["team"]
        st.markdown(
            f'<div class="ko-adv">✓ {winner["team"]} advance{" (pens)" if pens else ""}</div>',
            unsafe_allow_html=True)
    rec = {"hs": ga, "as": gb}
    if pens:
        rec["pens"] = pens
    if played_toggle:
        rec["played"] = bool(played)
    scores_out[f"{key}_{i}"] = rec
    return winner


def render_bracket_editor(saved: dict | None, locked: bool, prefix: str,
                          played_toggle: bool = False) -> dict:
    """Render the real bracket with a score box per tie; winners cascade to the
    next round. Returns the full pool payload. Streamlit imported lazily."""
    import streamlit as st

    saved = saved or {}
    saved_scores = saved.get("scores") or {}
    slot = team_slot_map()

    cur = []
    for tie in ko_r32_ties():
        cur.append(slot[tie["home"]])
        cur.append(slot[tie["away"]])

    for hc, (key, _lbl, play, _n) in zip(st.columns(len(KO_POOL_ROUNDS)), KO_POOL_ROUNDS):
        hc.markdown(
            f'<div class="rnd-head">{play}<br><small>+{KO_POOL_POINTS[key]} pts each</small></div>',
            unsafe_allow_html=True)

    payload, scores_out = {}, {}
    cols = st.columns(len(KO_POOL_ROUNDS))
    r32 = ko_r32_ties()
    for ci, (key, _lbl, _play, _n) in enumerate(KO_POOL_ROUNDS):
        with cols[ci]:
            matches = [(cur[2 * i], cur[2 * i + 1]) for i in range(len(cur) // 2)]
            winners = []
            for i, (a, b) in enumerate(matches):
                meta = r32[i] if key == "r32" else ko_round_meta(key, i)
                winners.append(_tie_widget(st, a, b, key, i, saved_scores, meta,
                                           scores_out, locked, prefix, played_toggle))
            if key == "champion":
                payload["champion"] = winners[0]["team"]
            else:
                payload[key] = [w["team"] for w in winners]
                cur = winners
    payload["scores"] = scores_out
    return payload
