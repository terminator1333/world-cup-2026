"""Render teams as flag + name chips using flagcdn.com (free, no key)."""
from __future__ import annotations

from .data import team_meta


def flag_url(team: str, width: int = 40) -> str:
    code = team_meta(team)["code"]
    return f"https://flagcdn.com/w{width}/{code}.png"


def emoji_flag(team: str) -> str:
    """Unicode flag emoji for a team (usable in plain-text widgets like radios)."""
    code = team_meta(team)["code"]
    if code == "gb-eng":
        return "🏴\U000e0067\U000e0062\U000e0065\U000e006e\U000e0067\U000e007f"
    if code == "gb-sct":
        return "🏴\U000e0067\U000e0062\U000e0073\U000e0063\U000e0074\U000e007f"
    if len(code) == 2:
        return "".join(chr(0x1F1E6 + ord(c) - 97) for c in code.lower())
    return "🏳️"


def text_on(hex_color: str) -> str:
    """Return black or white, whichever is readable on the given hex colour."""
    h = hex_color.lstrip("#")
    if len(h) != 6:
        return "#ffffff"
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return "#05121f" if (0.299 * r + 0.587 * g + 0.114 * b) > 150 else "#ffffff"


def flag_by_code(code: str, width: int = 80, wave: bool = False) -> str:
    """Flag image (public-domain, via flagcdn) for a raw ISO country code.

    wave=True applies the painted, torn-edge waving-cloth treatment.
    """
    if wave:
        # request a wider source so the displacement filter stays crisp
        return (
            f'<img class="flag-wave" src="https://flagcdn.com/w160/{code}.png" '
            f'width="{width}" alt="{code}">'
        )
    return (
        f'<img src="https://flagcdn.com/w{width}/{code}.png" width="{width}" '
        f'style="border-radius:5px;box-shadow:0 3px 12px rgba(0,0,0,.55);" alt="{code}">'
    )


def flag_img(team: str, width: int = 28) -> str:
    return (
        f'<img src="{flag_url(team, 40)}" width="{width}" '
        f'style="border-radius:3px;vertical-align:middle;'
        f'box-shadow:0 1px 4px rgba(0,0,0,.5);" alt="{team}">'
    )


def team_chip(team: str, width: int = 24) -> str:
    """Inline flag + team name, tinted with the team's primary colour."""
    meta = team_meta(team)
    return (
        f'<span style="display:inline-flex;align-items:center;gap:7px;'
        f'padding:3px 10px 3px 6px;border-radius:999px;'
        f'background:linear-gradient(90deg,{meta["primary"]}33,transparent);'
        f'border:1px solid {meta["primary"]}66;font-weight:600;white-space:nowrap;">'
        f'{flag_img(team, width)}<span>{team}</span></span>'
    )
