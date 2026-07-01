"""Small shared helpers (prediction lock + auth session)."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import streamlit as st

DEFAULT_LOCK = "2026-06-11T11:00:00"
# The knockout pool is a separate competition that locks at the first Round-of-32
# kickoff (South Africa v Canada, 28 Jun 2026, 12:00 PT = 19:00 UTC). Override via
# the KO_LOCK_DATETIME secret (ISO 8601; a bare time is treated as UTC).
DEFAULT_KO_LOCK = "2026-06-28T19:00:00+00:00"

# Participants allowed to keep editing predictions for fixtures that have not
# kicked off yet, even after the global lock. Matched case-insensitively.
UNPLAYED_EDITORS = {"tomer"}

ISRAEL_TZ = timezone(timedelta(hours=3))  # IDT (no DST transitions during the tournament)

# Knockout-pool players who registered after the pool's normal lock. Each gets a
# personal deadline (their own grace window) instead of the shared KO_LOCK_DATETIME.
# Ties that already kicked off before that deadline score 0 for them — no credit
# for picks made with hindsight — while ties after it (which they had to call
# blind, since they can no longer edit past their own deadline) score normally.
# Matched case-insensitively.
KO_LATE_ENTRANTS = {
    "lebron james": datetime(2026, 7, 1, 20, 0, tzinfo=ISRAEL_TZ),
}


def secret(key: str, default=None):
    """Read a Streamlit secret without crashing when no secrets file exists."""
    try:
        return st.secrets.get(key, default)
    except Exception:
        return default


def lock_dt() -> datetime:
    raw = secret("LOCK_DATETIME", DEFAULT_LOCK)
    try:
        return datetime.fromisoformat(raw)
    except (ValueError, TypeError):
        return datetime.fromisoformat(DEFAULT_LOCK)


def is_locked() -> bool:
    return datetime.now() >= lock_dt()


def ko_lock_dt() -> datetime:
    """Timezone-aware lock for the knockout pool (assumes UTC if no offset given)."""
    raw = secret("KO_LOCK_DATETIME", DEFAULT_KO_LOCK)
    try:
        dt = datetime.fromisoformat(raw)
    except (ValueError, TypeError):
        dt = datetime.fromisoformat(DEFAULT_KO_LOCK)
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def ko_is_locked() -> bool:
    return datetime.now(timezone.utc) >= ko_lock_dt()


def is_unplayed_editor(user) -> bool:
    """True if this participant may edit not-yet-played fixtures past the lock."""
    return bool(user) and user.get("name", "").strip().lower() in UNPLAYED_EDITORS


def ko_late_deadline(user) -> datetime | None:
    """This participant's personal knockout-pool deadline, if they're a late
    entrant granted a grace window past the normal pool lock (see KO_LATE_ENTRANTS)."""
    if not user:
        return None
    return KO_LATE_ENTRANTS.get(user.get("name", "").strip().lower())


def ko_is_locked_for(user) -> bool:
    """Like ko_is_locked(), but a late entrant stays editable until their own
    personal deadline instead of the shared pool lock."""
    deadline = ko_late_deadline(user)
    if deadline is not None:
        return datetime.now(timezone.utc) >= deadline
    return ko_is_locked()


def current_user():
    return st.session_state.get("participant")


def set_user(participant):
    st.session_state["participant"] = participant


def logout():
    st.session_state.pop("participant", None)
