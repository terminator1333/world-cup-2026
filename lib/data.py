"""Static tournament data + derived structures for the 2026 FIFA World Cup.

Group compositions are the real final-draw results. The per-match dates and
venues are scheduled approximations within the official group-stage window
(11–27 June 2026) and the 16 host cities — they exist to make the fixtures
feel real and can be fine-tuned without touching any app logic.
"""
from __future__ import annotations

import json
from datetime import date, datetime, timedelta, timezone
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

# Host city -> (flag, UTC offset in hours during June 2026). US Eastern = -4,
# US Central = -5, US Pacific = -7; Mexico runs no DST so Central = -6.
_CITY_TZ = {
    "Mexico City": ("🇲🇽", -6), "Guadalajara": ("🇲🇽", -6), "Monterrey": ("🇲🇽", -6),
    "Toronto": ("🇨🇦", -4), "Vancouver": ("🇨🇦", -7),
    "Los Angeles": ("🇺🇸", -7), "San Francisco": ("🇺🇸", -7), "Seattle": ("🇺🇸", -7),
    "Dallas": ("🇺🇸", -5), "Kansas City": ("🇺🇸", -5), "Houston": ("🇺🇸", -5),
    "Atlanta": ("🇺🇸", -4), "Miami": ("🇺🇸", -4), "New York / NJ": ("🇺🇸", -4),
    "Philadelphia": ("🇺🇸", -4), "Boston": ("🇺🇸", -4),
}

# Real 2026 group-stage schedule (official fixtures). Each entry is
# (team, team, date, local-kickoff "HH:MM", host city). Matched to a generated
# fixture by its unordered team pair, so only the date/time/venue are applied —
# the match id and home/away orientation (hence saved predictions) are untouched.
# Times are venue-local; the venue's tz offset (above) makes the lock accurate.
_REAL_SCHEDULE = {
    "A": [
        ("Mexico", "South Africa", "2026-06-11", "13:00", "Mexico City"),
        ("South Korea", "Czech Republic", "2026-06-11", "20:00", "Guadalajara"),
        ("Czech Republic", "South Africa", "2026-06-18", "12:00", "Atlanta"),
        ("Mexico", "South Korea", "2026-06-18", "19:00", "Guadalajara"),
        ("Czech Republic", "Mexico", "2026-06-24", "19:00", "Mexico City"),
        ("South Africa", "South Korea", "2026-06-24", "19:00", "Monterrey"),
    ],
    "B": [
        ("Canada", "Bosnia & Herzegovina", "2026-06-12", "15:00", "Toronto"),
        ("Qatar", "Switzerland", "2026-06-13", "12:00", "San Francisco"),
        ("Switzerland", "Bosnia & Herzegovina", "2026-06-18", "12:00", "Los Angeles"),
        ("Canada", "Qatar", "2026-06-18", "15:00", "Vancouver"),
        ("Switzerland", "Canada", "2026-06-24", "12:00", "Vancouver"),
        ("Bosnia & Herzegovina", "Qatar", "2026-06-24", "12:00", "Seattle"),
    ],
    "C": [
        ("Brazil", "Morocco", "2026-06-13", "18:00", "New York / NJ"),
        ("Haiti", "Scotland", "2026-06-13", "21:00", "Boston"),
        ("Scotland", "Morocco", "2026-06-19", "18:00", "Boston"),
        ("Brazil", "Haiti", "2026-06-19", "20:30", "Philadelphia"),
        ("Scotland", "Brazil", "2026-06-24", "18:00", "Miami"),
        ("Morocco", "Haiti", "2026-06-24", "18:00", "Atlanta"),
    ],
    "D": [
        ("United States", "Paraguay", "2026-06-12", "18:00", "Los Angeles"),
        ("Australia", "Turkey", "2026-06-13", "21:00", "Vancouver"),
        ("United States", "Australia", "2026-06-19", "12:00", "Seattle"),
        ("Turkey", "Paraguay", "2026-06-19", "20:00", "San Francisco"),
        ("Turkey", "United States", "2026-06-25", "19:00", "Los Angeles"),
        ("Paraguay", "Australia", "2026-06-25", "19:00", "San Francisco"),
    ],
    "E": [
        ("Germany", "Curaçao", "2026-06-14", "12:00", "Houston"),
        ("Ivory Coast", "Ecuador", "2026-06-14", "19:00", "Philadelphia"),
        ("Germany", "Ivory Coast", "2026-06-20", "16:00", "Toronto"),
        ("Ecuador", "Curaçao", "2026-06-20", "19:00", "Kansas City"),
        ("Curaçao", "Ivory Coast", "2026-06-25", "16:00", "Philadelphia"),
        ("Ecuador", "Germany", "2026-06-25", "16:00", "New York / NJ"),
    ],
    "F": [
        ("Netherlands", "Japan", "2026-06-14", "15:00", "Dallas"),
        ("Sweden", "Tunisia", "2026-06-14", "20:00", "Monterrey"),
        ("Netherlands", "Sweden", "2026-06-20", "12:00", "Houston"),
        ("Tunisia", "Japan", "2026-06-20", "22:00", "Monterrey"),
        ("Japan", "Sweden", "2026-06-25", "18:00", "Dallas"),
        ("Tunisia", "Netherlands", "2026-06-25", "18:00", "Kansas City"),
    ],
    "G": [
        ("Belgium", "Egypt", "2026-06-15", "12:00", "Seattle"),
        ("Iran", "New Zealand", "2026-06-15", "18:00", "Los Angeles"),
        ("Belgium", "Iran", "2026-06-21", "12:00", "Los Angeles"),
        ("New Zealand", "Egypt", "2026-06-21", "18:00", "Vancouver"),
        ("Egypt", "Iran", "2026-06-26", "20:00", "Seattle"),
        ("New Zealand", "Belgium", "2026-06-26", "20:00", "Vancouver"),
    ],
    "H": [
        ("Spain", "Cape Verde", "2026-06-15", "12:00", "Atlanta"),
        ("Saudi Arabia", "Uruguay", "2026-06-15", "18:00", "Miami"),
        ("Spain", "Saudi Arabia", "2026-06-21", "12:00", "Atlanta"),
        ("Uruguay", "Cape Verde", "2026-06-21", "18:00", "Miami"),
        ("Cape Verde", "Saudi Arabia", "2026-06-26", "19:00", "Houston"),
        ("Uruguay", "Spain", "2026-06-26", "18:00", "Guadalajara"),
    ],
    "I": [
        ("France", "Senegal", "2026-06-16", "15:00", "New York / NJ"),
        ("Iraq", "Norway", "2026-06-16", "18:00", "Boston"),
        ("France", "Iraq", "2026-06-22", "17:00", "Philadelphia"),
        ("Norway", "Senegal", "2026-06-22", "20:00", "New York / NJ"),
        ("Norway", "France", "2026-06-26", "15:00", "Boston"),
        ("Senegal", "Iraq", "2026-06-26", "15:00", "Toronto"),
    ],
    "J": [
        ("Argentina", "Algeria", "2026-06-16", "20:00", "Kansas City"),
        ("Austria", "Jordan", "2026-06-16", "21:00", "San Francisco"),
        ("Argentina", "Austria", "2026-06-22", "12:00", "Dallas"),
        ("Jordan", "Algeria", "2026-06-22", "20:00", "San Francisco"),
        ("Algeria", "Austria", "2026-06-27", "21:00", "Kansas City"),
        ("Jordan", "Argentina", "2026-06-27", "21:00", "Dallas"),
    ],
    "K": [
        ("Portugal", "DR Congo", "2026-06-17", "12:00", "Houston"),
        ("Uzbekistan", "Colombia", "2026-06-17", "20:00", "Mexico City"),
        ("Portugal", "Uzbekistan", "2026-06-23", "12:00", "Houston"),
        ("Colombia", "DR Congo", "2026-06-23", "20:00", "Guadalajara"),
        ("Colombia", "Portugal", "2026-06-27", "19:30", "Miami"),
        ("DR Congo", "Uzbekistan", "2026-06-27", "19:30", "Atlanta"),
    ],
    "L": [
        ("Ghana", "Panama", "2026-06-17", "15:00", "Toronto"),
        ("England", "Croatia", "2026-06-17", "15:00", "Dallas"),
        ("England", "Ghana", "2026-06-23", "16:00", "Boston"),
        ("Panama", "Croatia", "2026-06-23", "19:00", "Toronto"),
        ("Panama", "England", "2026-06-27", "17:00", "New York / NJ"),
        ("Croatia", "Ghana", "2026-06-27", "17:00", "Philadelphia"),
    ],
}


@lru_cache(maxsize=1)
def _real_schedule_index() -> dict:
    """{(group, frozenset({teamA, teamB})): (date, time, city, flag, offset)}."""
    idx = {}
    for grp, fixtures in _REAL_SCHEDULE.items():
        for a, b, d, t, city in fixtures:
            flag, off = _CITY_TZ[city]
            idx[(grp, frozenset((a, b)))] = (d, t, city, flag, off)
    return idx

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
    real = _real_schedule_index()
    for m in matches:
        entry = real.get((m["group"], frozenset((m["home"], m["away"]))))
        if entry:
            d, t, city, flag, off = entry
            m.update(date=d, time=t, city=city, city_flag=flag, utc_offset=off)
    matches.sort(key=lambda m: (m["date"], m["time"], m["group"]))
    return matches


def matches_for_group(grp: str) -> list[dict]:
    return [m for m in group_matches() if m["group"] == grp]


def match_kickoff(m: dict) -> datetime:
    """Timezone-aware kickoff datetime, using the venue's UTC offset."""
    tz = timezone(timedelta(hours=m.get("utc_offset", 0)))
    return datetime.fromisoformat(f"{m['date']}T{m['time']}").replace(tzinfo=tz)


def match_played(m: dict, now: datetime | None = None) -> bool:
    """True once a fixture has kicked off (so it can no longer be predicted).

    Compared in UTC, so it's correct no matter what timezone the server runs in.
    """
    return (now or datetime.now(timezone.utc)) >= match_kickoff(m)
