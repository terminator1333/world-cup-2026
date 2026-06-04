"""Persistence layer.

Uses Supabase (hosted Postgres) when SUPABASE_URL/KEY are present in
st.secrets. Otherwise transparently falls back to a local JSON file
(.localdb.json) so the app runs end-to-end for local development.

Public API (backend-agnostic):
    upsert_participant(name, pin)  -> (participant_dict, error_or_None)
    auth_participant(name, pin)    -> (participant_dict_or_None, error_or_None)
    list_participants()            -> list[dict]
    save_prediction(pid, category, payload)
    get_prediction(pid, category)  -> payload or None
    all_predictions()              -> list[dict]
    save_result(category, key, actual)
    get_results()                  -> {(category, key): actual}
"""
from __future__ import annotations

import hashlib
import json
import uuid
from pathlib import Path

import streamlit as st

from .util import secret

_LOCAL_PATH = Path(__file__).resolve().parent.parent / ".localdb.json"
_SALT = "wc2026-pool"


def _hash_pin(pin: str) -> str:
    return hashlib.sha256(f"{_SALT}:{pin}".encode()).hexdigest()


# --------------------------------------------------------------------------- #
# Backend selection
# --------------------------------------------------------------------------- #
@st.cache_resource(show_spinner=False)
def _supabase():
    url = secret("SUPABASE_URL", "")
    key = secret("SUPABASE_KEY", "")
    if not url or not key or "YOUR-PROJECT" in url:
        return None
    from supabase import create_client
    return create_client(url, key)


def using_supabase() -> bool:
    return _supabase() is not None


# --------------------------------------------------------------------------- #
# Local JSON fallback
# --------------------------------------------------------------------------- #
def _local_load() -> dict:
    if _LOCAL_PATH.exists():
        return json.loads(_LOCAL_PATH.read_text(encoding="utf-8"))
    return {"participants": [], "predictions": [], "results": []}


def _local_save(db: dict) -> None:
    _LOCAL_PATH.write_text(json.dumps(db, indent=2, ensure_ascii=False), encoding="utf-8")


# --------------------------------------------------------------------------- #
# Participants
# --------------------------------------------------------------------------- #
def upsert_participant(name: str, pin: str):
    """Create a participant, or verify the PIN if the name already exists."""
    name = name.strip()
    if not name:
        return None, "Please enter a name."
    if not pin.strip():
        return None, "Please choose a PIN."

    existing, _ = auth_participant(name, pin, _quiet=True)
    if existing is not None:
        return existing, None

    # Does the name exist with a *different* pin?
    if _participant_by_name(name) is not None:
        return None, "That name is taken and the PIN doesn't match."

    row = {"id": str(uuid.uuid4()), "name": name, "pin_hash": _hash_pin(pin)}
    sb = _supabase()
    if sb:
        sb.table("participants").insert(row).execute()
    else:
        db = _local_load()
        db["participants"].append(row)
        _local_save(db)
    return _public(row), None


def auth_participant(name: str, pin: str, _quiet: bool = False):
    row = _participant_by_name(name.strip())
    if row is None:
        return None, (None if _quiet else "No such participant — submit once to register.")
    if row["pin_hash"] != _hash_pin(pin):
        return None, (None if _quiet else "Wrong PIN.")
    return _public(row), None


def _participant_by_name(name: str):
    sb = _supabase()
    if sb:
        res = sb.table("participants").select("*").eq("name", name).execute()
        return res.data[0] if res.data else None
    return next((p for p in _local_load()["participants"] if p["name"] == name), None)


def list_participants() -> list[dict]:
    sb = _supabase()
    if sb:
        res = sb.table("participants").select("id,name").execute()
        return res.data or []
    return [_public(p) for p in _local_load()["participants"]]


def _public(row: dict) -> dict:
    return {"id": row["id"], "name": row["name"]}


# --------------------------------------------------------------------------- #
# Predictions
# --------------------------------------------------------------------------- #
def save_prediction(pid: str, category: str, payload: dict) -> None:
    sb = _supabase()
    if sb:
        sb.table("predictions").upsert(
            {"participant_id": pid, "category": category, "payload": payload},
            on_conflict="participant_id,category",
        ).execute()
        return
    db = _local_load()
    for p in db["predictions"]:
        if p["participant_id"] == pid and p["category"] == category:
            p["payload"] = payload
            _local_save(db)
            return
    db["predictions"].append({"participant_id": pid, "category": category, "payload": payload})
    _local_save(db)


def get_prediction(pid: str, category: str):
    sb = _supabase()
    if sb:
        res = (
            sb.table("predictions").select("payload")
            .eq("participant_id", pid).eq("category", category).execute()
        )
        return res.data[0]["payload"] if res.data else None
    return next(
        (p["payload"] for p in _local_load()["predictions"]
         if p["participant_id"] == pid and p["category"] == category),
        None,
    )


def all_predictions() -> list[dict]:
    sb = _supabase()
    if sb:
        return sb.table("predictions").select("*").execute().data or []
    return _local_load()["predictions"]


# --------------------------------------------------------------------------- #
# Results (admin-entered truth)
# --------------------------------------------------------------------------- #
def save_result(category: str, key: str, actual) -> None:
    sb = _supabase()
    if sb:
        sb.table("results").upsert(
            {"category": category, "key": key, "actual": actual},
            on_conflict="category,key",
        ).execute()
        return
    db = _local_load()
    for r in db["results"]:
        if r["category"] == category and r["key"] == key:
            r["actual"] = actual
            _local_save(db)
            return
    db["results"].append({"category": category, "key": key, "actual": actual})
    _local_save(db)


def get_results() -> dict:
    sb = _supabase()
    if sb:
        rows = sb.table("results").select("*").execute().data or []
    else:
        rows = _local_load()["results"]
    return {(r["category"], r["key"]): r["actual"] for r in rows}
