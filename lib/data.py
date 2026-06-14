"""Static tournament data + derived structures for the 2026 FIFA World Cup.

Group compositions are the real final-draw results. The per-match dates and
venues are scheduled approximations within the official group-stage window
(11–27 June 2026) and the 16 host cities — they exist to make the fixtures
feel real and can be fine-tuned without touching any app logic.
"""
from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from functools import lru_cache
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# 16 host cities across USA / Mexico / Canada.
HOST_CITIES = [
    ("Mexico City", "🇲🇽"), ("Guadalajara", "🇲🇽"), ("Monterrey", "🇲🇽"),
    ("Toronto", "🇨🇦"), ("Vancouver", "🇨🇦"),
    ("Los Angeles", "🇺🇸"), ("San Francisco", "🇺🇸"), ("Seattle", "🇺🇸"),
    ("Dallas", "🇺🇸"), ("Kansas City", "🇺🇸"), ("Houston", "🇺🇸"),
    ("Atlanta", "🇺🇸"), ("Miami", "🇺🇸"), ("New York / NJ", "🇺🇸"),
    ("Philadelphia", "🇺🇸"), ("Boston", "🇺🇸"),
]

GROUP_STAGE_START = date(2026, 6, 11)

# Knockout schedule: (round start date, number of days it spans).
_KO_SCHEDULE = [
    (date(2026, 6, 28), 6),   # Round of 32
    (date(2026, 7, 4), 4),    # Round of 16
    (date(2026, 7, 9), 3),    # Quarter-finals
    (date(2026, 7, 14), 2),   # Semi-finals
    (date(2026, 7, 19), 1),   # Final
]


def knockout_meta(round_idx: int, match_idx: int) -> dict:
    """Date / kickoff / host city for a knockout tie (deterministic, plausible)."""
    start, span = _KO_SCHEDULE[round_idx]
    times = ["13:00", "16:00", "19:00", "22:00"]
    if round_idx == len(_KO_SCHEDULE) - 1:        # the Final → MetLife, New York / NJ
        city, flag = "New York / NJ", "🇺🇸"
        day = start
    else:
        city, flag = HOST_CITIES[(round_idx * 7 + match_idx) % len(HOST_CITIES)]
        day = start + timedelta(days=match_idx % span)
    return {"date": day.isoformat(), "time": times[match_idx % len(times)],
            "city": city, "city_flag": flag}

# Standard 4-team round-robin pairing order (indices into a group's team list).
_RR_PAIRS = [(0, 1), (2, 3), (0, 2), (1, 3), (0, 3), (1, 2)]

# Manual corrections to the synthetic schedule, keyed by match id. Times are
# the real kickoff converted to the app's clock (Israel time), so the lock
# fires when the game actually starts. Sourced from the official 2026 schedule.
_SCHEDULE_OVERRIDES = {
    "E1-01": {"date": "2026-06-14", "time": "21:00"},  # Germany v Curaçao  (13:00 CDT, Houston)
    "F1-01": {"date": "2026-06-14", "time": "23:00"},  # Netherlands v Japan (15:00 CDT, Arlington)
}

# Knockout rounds we let people predict, with their size and per-team points.
KNOCKOUT_ROUNDS = [
    ("r16", "Round of 16", 16, 2),
    ("qf", "Quarter-finals", 8, 3),
    ("sf", "Semi-finals", 4, 5),
    ("final", "Final", 2, 8),
]
CHAMPION_POINTS = 15


@lru_cache(maxsize=1)
def load_teams() -> dict:
    return json.loads((DATA_DIR / "teams.json").read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def load_groups() -> dict:
    return json.loads((DATA_DIR / "groups.json").read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def load_stadiums() -> list[dict]:
    return json.loads((DATA_DIR / "stadiums.json").read_text(encoding="utf-8"))


def all_teams() -> list[str]:
    return list(load_teams().keys())


def team_meta(team: str) -> dict:
    return load_teams().get(team, {"code": "un", "primary": "#888", "secondary": "#444"})


@lru_cache(maxsize=1)
def group_matches() -> list[dict]:
    """All 72 group-stage fixtures with id, group, teams, date, venue."""
    groups = load_groups()
    matches: list[dict] = []
    city_idx = 0
    kickoffs = ["13:00", "16:00", "19:00", "22:00"]
    for matchday, (i, j) in enumerate(_RR_PAIRS):
        # Spread each round-robin matchday across a couple of calendar days.
        day = GROUP_STAGE_START + timedelta(days=matchday * 2 + (0 if matchday < 3 else 1))
        for grp, teams in groups.items():
            city, flag = HOST_CITIES[city_idx % len(HOST_CITIES)]
            matches.append({
                "id": f"{grp}{matchday + 1}-{i}{j}",
                "group": grp,
                "home": teams[i],
                "away": teams[j],
                "date": day.isoformat(),
                "time": kickoffs[city_idx % len(kickoffs)],
                "city": city,
                "city_flag": flag,
            })
            city_idx += 1
    for m in matches:
        m.update(_SCHEDULE_OVERRIDES.get(m["id"], {}))
    matches.sort(key=lambda m: (m["date"], m["group"]))
    return matches


def matches_for_group(grp: str) -> list[dict]:
    return [m for m in group_matches() if m["group"] == grp]


def match_kickoff(m: dict) -> datetime:
    """Naive kickoff datetime for a fixture, from its date + time fields."""
    return datetime.fromisoformat(f"{m['date']}T{m['time']}")


def match_played(m: dict, now: datetime | None = None) -> bool:
    """True once a fixture has kicked off (so it can no longer be predicted)."""
    return (now or datetime.now()) >= match_kickoff(m)
