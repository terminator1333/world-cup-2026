"""Knockout Pool — a SEPARATE competition on the real Round-of-32 bracket.

This is independent of the full-tournament predictions: everyone predicts the
same actual bracket (real qualifiers, fixed FIFA slotting) and is ranked on its
own leaderboard. Predictions lock at the first Round-of-32 kickoff.
"""
from __future__ import annotations

import streamlit as st

from lib import db, ko_pool, theme, util
from lib.flags import flag_img

st.set_page_config(page_title="Knockout Pool · WC2026", page_icon="🥊", layout="wide")
theme.inject()
theme.hero("KNOCKOUT POOL", "A fresh contest on the real Round of 32 — predict every tie to the trophy. 🥊",
           kicker="SEPARATE GAME · ROUND OF 32 → FINAL", cls="ko-hero")

LOCKED = util.ko_is_locked()
lock = util.ko_lock_dt()

# Make the separation unmistakable.
st.markdown(
    '<div class="ko-strip">'
    '<b>🥊 THIS IS A SEPARATE COMPETITION</b>'
    '<span>Different game, different ranking — it does <b>not</b> affect your '
    'full-tournament score. Now that the 32 are known, predict the actual bracket.</span>'
    '</div>', unsafe_allow_html=True)

if LOCKED:
    st.warning(f"🔒 The knockout pool locked at the first Round-of-32 kickoff "
               f"({lock:%b %d, %Y · %H:%M} UTC). You can view picks but no longer edit them.")
else:
    c1, c2 = st.columns([1, 1.3])
    with c1:
        st.markdown('<span class="ko-badge">⏱️ LOCKS AT FIRST KNOCKOUT GAME</span>',
                    unsafe_allow_html=True)
        st.caption(f"Deadline: **{lock:%b %d, %Y · %H:%M} UTC** — South Africa v Canada kickoff.")
    with c2:
        theme.countdown(lock.isoformat(), live_label="Knockout pool locked",
                        fallback=f"⏱️ Locks {lock:%b %d, %H:%M} UTC")

# --------------------------------------------------------------------------- #
# Auth (shares the same accounts as the full-tournament predictions)
# --------------------------------------------------------------------------- #
user = util.current_user()
if user is None:
    st.markdown('<span class="ko-badge">WHO ARE YOU?</span>', unsafe_allow_html=True)
    st.caption("Use the **same name + PIN** as your full-tournament predictions.")
    with st.form("ko_auth"):
        a, b = st.columns(2)
        name = a.text_input("Your name", max_chars=24)
        pin = b.text_input("PIN", type="password", max_chars=12)
        if st.form_submit_button("Enter / Register 🔓", use_container_width=True):
            participant, err = db.upsert_participant(name, pin)
            if err:
                st.error(err)
            else:
                util.set_user(participant)
                st.rerun()
    st.stop()

top = st.columns([3, 1])
top[0].success(f"Signed in as **{user['name']}**")
if top[1].button("Sign out", use_container_width=True):
    util.logout()
    st.rerun()

pid = user["id"]

# Late entrants get their own grace window past the normal pool lock. Any tie
# that already kicked off before their personal deadline scores 0 for them
# regardless of the pick (see lib.scoring — no credit for hindsight picks).
late_deadline = util.ko_late_deadline(user)
my_locked = util.ko_is_locked_for(user)
if late_deadline and not my_locked:
    st.info(f"⏳ **Late entry** — you can fill in your bracket until "
            f"**{late_deadline:%b %d, %Y · %H:%M %Z}**. Ties that already kicked off "
            f"score 0 for you either way; only ties still to come count.")

# --------------------------------------------------------------------------- #
# The bracket — predict a scoreline for every tie; winners cascade to the final
# --------------------------------------------------------------------------- #
st.write("")
st.markdown('<span class="ko-badge">🏆 YOUR KNOCKOUT BRACKET</span>', unsafe_allow_html=True)
st.caption("Enter a scoreline for each tie — the winner advances (pick the penalty winner if level). "
           "Right team through a round scores; nailing the exact score earns a bonus.")

saved = db.get_prediction(pid, "ko_pool") or {}
payload = ko_pool.render_bracket_editor(saved, my_locked, prefix=f"kop_{pid}")

champ = payload.get("champion")
if champ:
    st.markdown(
        f'<div class="champ-banner">{flag_img(champ, 54)}'
        f'<div><span class="champ-kick">YOUR CHAMPION PICK</span><br>{champ} 🏆</div></div>',
        unsafe_allow_html=True,
    )

st.write("")
if st.button("💾 Save my knockout pool bracket", disabled=my_locked, key="save_ko_pool",
             use_container_width=True):
    if my_locked:
        st.error("The knockout pool is locked.")
    else:
        db.save_prediction(pid, "ko_pool", payload)
        st.success("✅ Knockout pool bracket saved!")
        st.balloons()

st.page_link("pages/2_📊_Leaderboard.py", label="See the Knockout Pool leaderboard", icon="📊")
