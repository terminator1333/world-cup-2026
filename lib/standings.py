"""Compute group tables and the best-third-placed teams from match scores.

Used to make the Groups tab game-driven: enter scorelines, and the standings,
qualifiers and 3rd-place race all fall out of these pure functions.

Tiebreakers (a pragmatic subset of FIFA's): points → goal difference →
goals scored → original seed order. Good enough for a prediction pool.
"""
from __future__ import annotations


def empty_stat():
    return {"P": 0, "W": 0, "D": 0, "L": 0, "GF": 0, "GA": 0, "GD": 0, "Pts": 0}


def compute_table(teams: list[str], matches: list[dict], scores: dict):
    """Return (ordered_teams, stats_by_team).

    matches: dicts with 'id', 'home', 'away'.
    scores:  {match_id: {'hs': int, 'as': int}} (missing → match not counted).
    """
    stats = {t: empty_stat() for t in teams}
    for m in matches:
        s = scores.get(m["id"])
        if not s:
            continue
        h, a = m["home"], m["away"]
        hs, as_ = int(s["hs"]), int(s["as"])
        for t, gf, ga in ((h, hs, as_), (a, as_, hs)):
            stats[t]["P"] += 1
            stats[t]["GF"] += gf
            stats[t]["GA"] += ga
        if hs > as_:
            stats[h]["W"] += 1; stats[a]["L"] += 1; stats[h]["Pts"] += 3
        elif as_ > hs:
            stats[a]["W"] += 1; stats[h]["L"] += 1; stats[a]["Pts"] += 3
        else:
            stats[h]["D"] += 1; stats[a]["D"] += 1
            stats[h]["Pts"] += 1; stats[a]["Pts"] += 1
    for t in teams:
        stats[t]["GD"] = stats[t]["GF"] - stats[t]["GA"]

    order = sorted(
        teams,
        key=lambda t: (-stats[t]["Pts"], -stats[t]["GD"], -stats[t]["GF"], teams.index(t)),
    )
    return order, stats


def best_thirds(group_tables: dict, advance: int = 8):
    """group_tables: {grp: (order, stats)}. Return ranked list of
    (grp, team, stats) for every 3rd-placed team, best first."""
    thirds = []
    for grp, (order, stats) in group_tables.items():
        if len(order) >= 3:
            t = order[2]
            thirds.append((grp, t, stats[t]))
    thirds.sort(key=lambda x: (-x[2]["Pts"], -x[2]["GD"], -x[2]["GF"], x[0]))
    return thirds
