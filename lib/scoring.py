"""Pure scoring functions: (predictions x actual results) -> points.

All point values live here so they're trivial to tune. Every function is
defensive about missing/partial data, since predictions are optional per user
and results arrive incrementally over the tournament.
"""
from __future__ import annotations

from .data import KNOCKOUT_ROUNDS, CHAMPION_POINTS

# --- point values ---------------------------------------------------------- #
PTS_GAME_OUTCOME = 3
PTS_GAME_EXACT = 2          # bonus on top of a correct outcome
PTS_GROUP_WINNER = 5
PTS_GROUP_POSITION = 3      # per exact non-winner position
PTS_GROUP_QUALIFIERS = 2    # correct top-2 set, any order
PTS_THIRD_PLACE = 3         # per correctly predicted advancing 3rd-placed team
PTS_TOP_SCORER = 5

CATEGORIES = ["per_game", "group_order", "third_place", "knockout"]
CATEGORY_LABELS = {
    "per_game": "Per-game",
    "group_order": "Group order",
    "third_place": "3rd place",
    "knockout": "Knockout",
}


def _r(results: dict, category: str, key: str):
    return results.get((category, key))


# --------------------------------------------------------------------------- #
def score_per_game(payload: dict, results: dict) -> int:
    pts = 0
    for mid, pick in (payload or {}).items():
        actual = _r(results, "per_game", mid)
        if not actual or not pick:
            continue
        if pick.get("outcome") and pick["outcome"] == actual.get("outcome"):
            pts += PTS_GAME_OUTCOME
            if (pick.get("hs") is not None and pick.get("as") is not None
                    and pick["hs"] == actual.get("hs") and pick["as"] == actual.get("as")):
                pts += PTS_GAME_EXACT
    return pts


def score_group_order(payload: dict, results: dict) -> int:
    pts = 0
    for grp, predicted in (payload or {}).items():
        actual = _r(results, "group_order", grp)
        if not actual or not predicted:
            continue
        for i, team in enumerate(predicted):
            if i < len(actual) and team == actual[i]:
                pts += PTS_GROUP_WINNER if i == 0 else PTS_GROUP_POSITION
        if set(predicted[:2]) == set(actual[:2]):
            pts += PTS_GROUP_QUALIFIERS
    return pts


def score_third_place(payload: dict, results: dict) -> int:
    actual = _r(results, "third_place", "advancing")
    if not actual or not payload:
        return 0
    picked = set(payload.get("advancing", []))
    return PTS_THIRD_PLACE * len(picked & set(actual))


def score_knockout(payload: dict, results: dict) -> int:
    if not payload:
        return 0
    pts = 0
    for key, _label, _size, per_team in KNOCKOUT_ROUNDS:
        actual = _r(results, "knockout", key)
        if not actual:
            continue
        picked = set(payload.get(key, []))
        pts += per_team * len(picked & set(actual))

    champ_actual = _r(results, "knockout", "champion")
    if champ_actual and payload.get("champion") == champ_actual:
        pts += CHAMPION_POINTS

    ts_actual = _r(results, "knockout", "top_scorer")
    if ts_actual and payload.get("top_scorer") and \
            payload["top_scorer"].strip().lower() == str(ts_actual).strip().lower():
        pts += PTS_TOP_SCORER
    return pts


_SCORERS = {
    "per_game": score_per_game,
    "group_order": score_group_order,
    "third_place": score_third_place,
    "knockout": score_knockout,
}


def score_participant(preds_by_cat: dict, results: dict) -> dict:
    """preds_by_cat: {category: payload}. Returns {'total', 'breakdown'}."""
    breakdown = {}
    for cat, scorer in _SCORERS.items():
        breakdown[cat] = scorer(preds_by_cat.get(cat), results)
    return {"total": sum(breakdown.values()), "breakdown": breakdown}


def leaderboard(all_predictions: list[dict], participants: list[dict], results: dict) -> list[dict]:
    """Build a sorted leaderboard from raw prediction rows."""
    by_pid: dict[str, dict] = {}
    for row in all_predictions:
        by_pid.setdefault(row["participant_id"], {})[row["category"]] = row["payload"]

    names = {p["id"]: p["name"] for p in participants}
    table = []
    for pid, name in names.items():
        scored = score_participant(by_pid.get(pid, {}), results)
        table.append({"name": name, "total": scored["total"], "breakdown": scored["breakdown"]})
    table.sort(key=lambda r: (-r["total"], r["name"].lower()))
    return table
