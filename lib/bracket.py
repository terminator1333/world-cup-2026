"""Build a seeded knockout bracket from the user's group-stage predictions.

The 32 qualifiers (12 winners + 12 runners-up + 8 best 3rd-placed) are taken
straight from the predicted match scores, ranked by performance, and seeded into
a standard single-elimination bracket so stronger predicted teams meet later.
"""
from __future__ import annotations

from .data import load_groups, matches_for_group
from .standings import compute_table


def _tier_key(item):
    s = item["stats"]
    return (-s["Pts"], -s["GD"], -s["GF"], item["grp"])


def build_qualifiers(per_game: dict):
    """Return (ranked_qualifiers, groups_completed).

    ranked_qualifiers: up to 32 dicts {team, grp, pos, stats}, best first.
    A group counts only once all 6 of its matches are predicted.
    """
    per_game = per_game or {}
    winners, runners, thirds = [], [], []
    completed = 0
    for grp, gteams in load_groups().items():
        gm = matches_for_group(grp)
        scores = {m["id"]: per_game[m["id"]] for m in gm if per_game.get(m["id"])}
        if len(scores) < len(gm):
            continue
        completed += 1
        order, stats = compute_table(gteams, gm, scores)
        winners.append({"team": order[0], "grp": grp, "pos": 1, "stats": stats[order[0]]})
        runners.append({"team": order[1], "grp": grp, "pos": 2, "stats": stats[order[1]]})
        thirds.append({"team": order[2], "grp": grp, "pos": 3, "stats": stats[order[2]]})

    winners.sort(key=_tier_key)
    runners.sort(key=_tier_key)
    thirds.sort(key=_tier_key)
    ranked = winners + runners + thirds[:8]
    return ranked, completed


def seed_order(n: int) -> list[int]:
    """Standard tournament seed positions for a bracket of size n (power of 2)."""
    order = [0]
    while len(order) < n:
        m = len(order) * 2
        order = [v for x in order for v in (x, m - 1 - x)]
    return order


def seed_bracket(ranked: list[dict]) -> list[dict]:
    """Place ranked qualifiers into bracket slot order (consecutive pairs = matches)."""
    n = len(ranked)
    return [ranked[s] for s in seed_order(n)]
