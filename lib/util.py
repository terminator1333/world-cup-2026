"""Small shared helpers (prediction lock + auth session)."""
from __future__ import annotations

from datetime import datetime

import streamlit as st

DEFAULT_LOCK = "2026-06-11T11:00:00"


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


def current_user():
    return st.session_state.get("participant")


def set_user(participant):
    st.session_state["participant"] = participant


def logout():
    st.session_state.pop("participant", None)
