"""Vibrant FIFA-game-inspired styling: global CSS, hero banner, live countdown."""
from __future__ import annotations

import random

import streamlit as st
import streamlit.components.v1 as components

KICKOFF_ISO = "2026-06-11T11:00:00"

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Anton&family=Rajdhani:wght@500;600;700&display=swap');

:root {
  --neon: #00E5A0;
  --neon2: #18A0FB;
  --gold: #FFD23F;
  --magenta: #FF2E93;
  --bg: #0A0E1A;
}

html, body, [class*="css"], .stApp, .stMarkdown, p, div, span, label {
  font-family: 'Rajdhani', system-ui, sans-serif;
}

.stApp {
  background:
    radial-gradient(1100px 720px at 6% -8%, #18A0FB33, transparent 60%),
    radial-gradient(1000px 640px at 104% 2%, #FF2E932e, transparent 58%),
    radial-gradient(900px 760px at 46% 124%, #00E5A028, transparent 60%),
    radial-gradient(760px 560px at 86% 82%, #7A2BFF26, transparent 60%),
    linear-gradient(162deg, #0b1024 0%, #0a0e1a 58%, #120a22 100%);
}
/* hand-made paper grain wash over everything */
.stApp::before {
  content:""; position:fixed; inset:0; pointer-events:none; z-index:0; opacity:.55;
  mix-blend-mode:overlay;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='180' height='180'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
  background-size:180px 180px;
}
[data-testid="stAppViewContainer"], .main { position:relative; z-index:1; }

h1, h2, h3 { font-family: 'Anton', sans-serif !important; letter-spacing: .5px; }

/* Hero banner */
.wc-hero {
  position: relative; border-radius: 22px; padding: 34px 30px;
  background: linear-gradient(125deg, #06224a 0%, #0a0e1a 45%, #2a0838 100%);
  border: 1px solid #ffffff1a; overflow: hidden; margin-bottom: 8px;
  box-shadow: 0 18px 60px #00000066;
}
.wc-hero::after {
  content: "⚽"; position: absolute; right: -10px; top: -30px;
  font-size: 190px; opacity: .07; transform: rotate(-15deg);
}
.wc-kicker {
  font-family:'Rajdhani'; font-weight:700; letter-spacing:4px; font-size:13px;
  color: var(--neon); text-transform: uppercase;
}
.wc-title {
  font-family:'Anton'; font-size: clamp(34px, 6vw, 62px); line-height:.95;
  margin: 6px 0 4px; background: linear-gradient(92deg, #fff, var(--neon) 55%, var(--neon2));
  -webkit-background-clip: text; background-clip: text; color: transparent;
}
.wc-sub { color:#aebbd6; font-size:18px; font-weight:600; }

/* Cards */
.wc-card {
  background: linear-gradient(180deg, #ffffff0d, #ffffff05);
  border: 1px solid #ffffff14; border-radius: 16px; padding: 16px 18px;
  backdrop-filter: blur(6px); margin-bottom: 12px;
}
.wc-badge {
  display:inline-block; font-family:'Anton'; font-size:13px; letter-spacing:1px;
  padding:4px 12px; border-radius:8px; color:#05121f;
  background: linear-gradient(90deg, var(--neon), var(--neon2));
}
.wc-pill {
  display:inline-block; padding:2px 10px; border-radius:999px; font-weight:700;
  font-size:12px; background:#ffffff14; border:1px solid #ffffff22; color:#cdd9f5;
}

/* Painterly bordered containers (group/match cards) — torn, brush-edged */
[data-testid="stVerticalBlockBorderWrapper"] {
  background:linear-gradient(165deg,#16203be6,#0d1426f2) !important;
  border:1px solid #ffffff1c !important;
  border-radius:22px 7px 24px 9px !important;
  box-shadow:0 14px 38px #00000059, inset 0 1px 0 #ffffff12 !important;
  position:relative;
}
[data-testid="stVerticalBlockBorderWrapper"]::before {
  content:""; position:absolute; left:0; top:8px; bottom:8px; width:7px;
  border-radius:6px;
  background:linear-gradient(180deg,var(--neon),var(--neon2) 55%,var(--magenta));
  filter:url(#paintRough); opacity:.9;
}
/* Waving, torn-edge painted flags (for big feature flags) */
.flag-wave { filter:url(#flagWave); transform:rotate(-1.6deg);
  box-shadow:0 8px 20px #0008; border-radius:3px; }

/* Buttons */
.stButton > button {
  border-radius: 12px; font-weight:700; border:1px solid var(--neon)55;
  background: linear-gradient(90deg, var(--neon), var(--neon2)); color:#04121f;
  transition: transform .08s ease, box-shadow .2s ease;
}
.stButton > button:hover { transform: translateY(-1px); box-shadow:0 8px 22px #00E5A055; }

/* Leaderboard rows */
.lb-row {
  display:flex; align-items:center; gap:14px; padding:12px 16px; border-radius:14px;
  margin-bottom:8px; background: linear-gradient(90deg,#ffffff0e,#ffffff05);
  border:1px solid #ffffff14;
}
.lb-rank { font-family:'Anton'; font-size:26px; min-width:46px; text-align:center; }
.lb-1 { background: linear-gradient(90deg,#FFD23F22,transparent); border-color:#FFD23F66; }
.lb-2 { background: linear-gradient(90deg,#C0C6D922,transparent); border-color:#C0C6D955; }
.lb-3 { background: linear-gradient(90deg,#CD7F3222,transparent); border-color:#CD7F3255; }
.lb-name { font-size:20px; font-weight:700; flex:1; }
.lb-score { font-family:'Anton'; font-size:24px; color: var(--neon); }

/* Countdown */
.cd-wrap { display:flex; gap:10px; margin-top:16px; flex-wrap:wrap; }
.cd-box {
  background:#ffffff10; border:1px solid #ffffff22; border-radius:12px;
  padding:8px 16px; min-width:74px; text-align:center;
}
.cd-num { font-family:'Anton'; font-size:30px; color:#fff; line-height:1; }
.cd-lbl { font-size:11px; letter-spacing:2px; color:#8ea0c4; text-transform:uppercase; }

/* Animated floating trophy / ball */
@keyframes floaty { 0%,100%{transform:translateY(0) rotate(0)} 50%{transform:translateY(-12px) rotate(8deg)} }
@keyframes spin { to { transform: rotate(360deg); } }
.wc-float { display:inline-block; animation: floaty 3.2s ease-in-out infinite; }
.wc-spin  { display:inline-block; animation: spin 6s linear infinite; }

/* Stadium cards */
.stad {
  position:relative; border-radius:26px 9px 26px 11px; padding:0; overflow:hidden;
  margin-bottom:16px; border:1px solid #ffffff1c; background:#0d1426;
  box-shadow:0 14px 36px #00000061; transition:transform .12s ease, box-shadow .2s ease;
}
.stad:hover { transform:translateY(-4px); box-shadow:0 20px 44px #18A0FB44; }
.stad-sky {
  height:88px; position:relative;
  background:linear-gradient(180deg,#0b2a57,#123a78 70%,#0a8f5a 70%,#0c7a4d);
}
.stad-sky::before {  /* stadium roof silhouette */
  content:""; position:absolute; left:6%; right:6%; top:18px; height:46px; border-radius:50%/70px;
  background:radial-gradient(60% 100% at 50% 0,#1b2740,#0d1426); border:2px solid #2a3a5e;
  box-shadow:inset 0 -8px 18px #000a;
}
.stad-pitch {  /* mowed-grass stripes */
  position:absolute; left:18%; right:18%; bottom:6px; height:26px; border-radius:4px;
  background:repeating-linear-gradient(90deg,#0f9a5e 0 10px,#0c854f 10px 20px);
  border:1px solid #ffffff44;
}
.stad-photo-wrap { position:relative; height:150px; overflow:hidden; }
.stad-photo { width:100%; height:150px; object-fit:cover; display:block;
  filter:saturate(1.15) contrast(1.03); }
.stad-photo-wrap::after { content:""; position:absolute; inset:0;
  background:linear-gradient(180deg, #0a0e1a00 35%, #0d1426ee); }
.stad-credit { position:absolute; bottom:4px; right:8px; z-index:2; font-size:10px;
  color:#cdd9f5cc; text-decoration:none; background:#0008; padding:1px 6px; border-radius:6px; }
.stad-flagbadge { position:absolute; left:10px; bottom:8px; z-index:2; }
.stad-body { padding:12px 16px 14px; }
.stad-name { font-family:'Anton'; font-size:19px; color:#fff; line-height:1.05; }
.stad-city { color:#9fb0d4; font-weight:600; font-size:14px; }
.stad-cap  { color:var(--neon); font-weight:700; font-size:13px; }
.stad-tag {
  position:absolute; top:10px; right:10px; z-index:2; font-family:'Anton'; font-size:11px;
  letter-spacing:1px; padding:3px 9px; border-radius:7px; color:#05121f;
  background:linear-gradient(90deg,var(--gold),#ff9d2e);
}

/* Legend cards */
.legend {
  display:flex; align-items:center; gap:12px; padding:12px 14px;
  border-radius:18px 6px 20px 8px; margin-bottom:10px; border:1px solid #ffffff1a;
  background:linear-gradient(100deg,#ffffff12,#ffffff04);
  box-shadow:0 8px 22px #0000003d; position:relative;
}
.legend::before {
  content:""; position:absolute; left:0; top:8px; bottom:8px; width:5px; border-radius:5px;
  background:linear-gradient(180deg,var(--gold),var(--magenta)); filter:url(#paintRough);
}
.legend-flag { font-size:30px; }
.legend-name { font-family:'Anton'; font-size:18px; color:#fff; line-height:1; }
.legend-honor { color:#9fb0d4; font-size:13px; font-weight:600; }
.record {
  text-align:center; padding:16px 10px; border-radius:18px 7px 20px 6px; margin-bottom:10px;
  border:1px solid #ffffff1a; background:linear-gradient(180deg,#ffffff12,#ffffff05);
  box-shadow:0 8px 22px #0000003d;
}
.record-num { font-family:'Anton'; font-size:30px;
  background:linear-gradient(90deg,var(--gold),var(--neon)); -webkit-background-clip:text;
  background-clip:text; color:transparent; }
.record-lbl { color:#aebbd6; font-size:13px; font-weight:600; }

/* Animated city-card backgrounds */
.stad.has-bg { min-height:210px; }
.stad-bg { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; z-index:0; }
.stad-shade { position:absolute; inset:0; z-index:1;
  background:linear-gradient(180deg,#0a0e1a3d 0%,#0d1426c2 58%,#0d1426f2 100%); }
.stad .stad-body { position:relative; z-index:2; }
.stad .stad-tag, .stad .stad-flagbadge { z-index:3; }

/* Animated legend figures */
.legend-anim { width:56px; height:56px; border-radius:12px; object-fit:cover;
  border:1px solid #ffffff22; box-shadow:0 3px 12px #0008; background:#0d1426; flex:0 0 auto; }

/* Match scoreboard + group ranking */
.team-block { display:flex; flex-direction:column; gap:4px; }
.team-block.home { align-items:flex-end; text-align:right; }
.team-block.away { align-items:flex-start; text-align:left; }
.team-block .tn { font-family:'Anton'; font-size:17px; line-height:1; color:#fff; }
.verdict { display:inline-block; font-family:'Anton'; letter-spacing:1px; font-size:15px;
  padding:6px 18px; border-radius:10px; box-shadow:0 6px 18px #0006; }
.verdict-wrap { text-align:center; margin-top:6px; }
.rank-team { display:flex; align-items:center; gap:9px; font-weight:700; font-size:16px; color:#fff; }
.adv-badge { font-family:'Anton'; font-size:10px; letter-spacing:.5px; padding:3px 8px;
  border-radius:6px; white-space:nowrap; }
.adv-1 { background:linear-gradient(90deg,#FFD23F,#ff9d00); color:#05121f; }
.adv-2 { background:linear-gradient(90deg,#00E5A0,#18A0FB); color:#05121f; }
.adv-3 { background:linear-gradient(90deg,#ff9d2e,#ff6a00); color:#05121f; }
.adv-out { background:#26314e; color:#9fb0d4; }
.pos-num { font-family:'Anton'; font-size:20px; color:#5f7099; min-width:22px; }

/* Compact match rows + live group tables */
.mt { display:flex; align-items:center; gap:6px; font-weight:600; font-size:13px; color:#dce6ff; }
.mt.home { justify-content:flex-end; text-align:right; }
.mt.away { justify-content:flex-start; text-align:left; }
.mt-n { line-height:1.05; }
.mt-dash { text-align:center; font-family:'Anton'; font-size:18px; color:#5f7099; }
.mini-table { margin-top:10px; display:flex; flex-direction:column; gap:5px; }
.tbl-row { display:flex; align-items:center; gap:8px;
  padding:6px 10px; border-radius:10px; background:#ffffff0c; border:1px solid #ffffff12; }
.tbl-name { flex:1; font-weight:700; font-size:14px; color:#fff; white-space:nowrap;
  overflow:hidden; text-overflow:ellipsis; }
.tbl-name small { color:#8ea0c4; font-weight:600; }
.tbl-gd { font-weight:700; color:#9fb0d4; min-width:30px; text-align:right; font-size:13px; }
.tbl-pts { font-family:'Anton'; color:var(--neon); min-width:42px; text-align:right; }
.tbl-pts small { color:#6f80a6; font-size:10px; }

/* Knockout bracket ties */
.ko-tie { display:flex; align-items:center; justify-content:space-between; gap:8px;
  font-weight:700; font-size:13.5px; color:#eaf0ff; }
.ko-side { display:flex; align-items:center; gap:6px; flex:1; min-width:0; }
.ko-side span { white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.ko-side.rt { justify-content:flex-end; text-align:right; }
.ko-side small { color:#8ea0c4; font-weight:700; font-size:11px; }
.ko-vs { font-family:'Anton'; color:#5f7099; font-size:13px; }
.champ-banner { display:flex; align-items:center; gap:16px; margin:8px 0 4px;
  padding:16px 22px; border-radius:22px 8px 22px 9px;
  background:linear-gradient(100deg,#FFD23F26,#FF2E9326);
  border:1px solid #FFD23F66; font-family:'Anton'; font-size:24px; color:#fff;
  box-shadow:0 12px 30px #0000004d; }
.champ-kick { font-family:'Rajdhani'; font-weight:700; letter-spacing:3px; font-size:12px;
  color:var(--gold); }

/* Knockout bracket tree */
.rnd-head { font-family:'Anton'; font-size:12px; letter-spacing:1px; text-align:center;
  color:#9fb0d4; margin-bottom:2px; padding-bottom:5px; border-bottom:2px solid #ffffff1a; }
/* vertically distribute each round's ties so they centre against their feeders */
[data-testid="stHorizontalBlock"]:has(.kotie) > [data-testid="stColumn"]
  > [data-testid="stVerticalBlock"] {
  height:100%; justify-content:space-around; gap:4px;
}
[data-testid="stHorizontalBlock"]:has(.kotie) [data-testid="stVerticalBlockBorderWrapper"] {
  margin:0 !important; border-radius:12px 5px 13px 6px !important;
}
[data-testid="stHorizontalBlock"]:has(.kotie) [data-testid="stVerticalBlockBorderWrapper"]::before {
  display:none;  /* drop the brush bar inside tiny bracket ties */
}
[data-testid="stHorizontalBlock"]:has(.kotie) .stButton button {
  padding:3px 8px; min-height:0; font-size:12px; font-weight:700;
  border-radius:8px 3px 9px 4px; }
.kotie { display:none; }
.kof { display:flex; align-items:center; justify-content:center; padding-top:4px; }
.kof.kwin img { box-shadow:0 0 0 2px var(--neon), 0 3px 10px #000a; border-radius:3px; }
.ko-meta { display:flex; flex-direction:column; align-items:center; gap:3px; margin-bottom:6px; }
.ko-meta-img { width:100%; height:36px; object-fit:cover; border-radius:9px 3px 10px 4px;
  box-shadow:0 2px 7px #0009; border:1px solid #ffffff1f; }
.ko-meta span { font-size:11px; font-weight:700; color:#aebbd6; text-align:center; line-height:1.25; }

/* Gallery tiles */
.gal-tile { position:relative; border-radius:22px 8px 24px 9px; overflow:hidden;
  margin-bottom:16px; border:1px solid #ffffff1c; background:#0d1426;
  box-shadow:0 14px 34px #0000004d; transition:transform .14s ease; }
.gal-tile:hover { transform:translateY(-5px); box-shadow:0 22px 44px #18A0FB33; }
.gal-img { width:100%; height:210px; object-fit:cover; display:block; }
.gal-img.port { height:300px; object-position:top center; }
.gal-noimg { height:210px; display:flex; align-items:center; justify-content:center;
  font-size:78px; background:linear-gradient(160deg,#16203b,#0d1426); }
.gal-cap { position:absolute; left:0; right:0; bottom:0; padding:30px 14px 11px;
  background:linear-gradient(180deg,transparent,#0a0e1af5); display:flex; flex-direction:column; }
.gal-cap b { font-family:'Anton'; font-size:19px; color:#fff; line-height:1.05; }
.gal-cap span { color:#aebbd6; font-size:12.5px; font-weight:600; margin-top:2px; }
.gal-flag { position:absolute; top:10px; left:10px; }

/* Animated hero background */
.wc-hero-bg { position:absolute; inset:0; width:100%; height:100%; object-fit:cover;
  z-index:0; opacity:.40; }
.wc-hero-inner { position:relative; z-index:2; }

/* Bigger, punchier text everywhere */
html { font-size: 18px; }
.stMarkdown p, .stMarkdown li { font-size: 1.05rem; }
.wc-sub { font-size:23px !important; }
.rank-team { font-size:19px !important; }
.tbl-name { font-size:17px !important; }
.tbl-gd { font-size:15px !important; }
.tbl-pts { font-size:20px !important; }
.mt { font-size:16px !important; }
.gal-cap b { font-size:25px !important; }
.gal-cap span { font-size:16px !important; }
.stad-name { font-size:22px !important; }
.stad-city { font-size:16px !important; }
.stad-cap { font-size:15px !important; }
.wc-pill { font-size:14px !important; }
.adv-badge { font-size:12px !important; }
.verdict { font-size:19px !important; }
.ko-side, .ko-side small { font-size:14px !important; }
[data-testid="stHorizontalBlock"]:has(.kotie) .stButton button { font-size:14px !important; }

/* Read-only knockout tree (All Picks) */
.rotree { display:flex; gap:10px; overflow-x:auto; padding:6px 2px; align-items:stretch; }
.rocol { display:flex; flex-direction:column; justify-content:space-around; gap:8px;
  min-width:132px; flex:1; }
.rocol-head { font-family:'Anton'; font-size:11px; letter-spacing:.5px; text-align:center;
  color:#9fb0d4; }
.rocol-head small { color:#6f80a6; font-weight:600; }
.rotie { background:#ffffff08; border:1px solid #ffffff16; border-radius:10px 4px 11px 5px;
  padding:4px; }
.rorow { display:flex; align-items:center; gap:6px; padding:3px 5px; border-radius:6px;
  font-size:12px; font-weight:600; color:#90a0c4; }
.rorow span { white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.rorow.win { background:linear-gradient(90deg,#00E5A033,transparent); color:#fff; font-weight:800; }
.rocol.champ { justify-content:center; min-width:118px; }
.rochamp { text-align:center; font-family:'Anton'; color:var(--gold); font-size:14px;
  display:flex; flex-direction:column; align-items:center; gap:5px; }

/* All-Picks read-only view */
.apk-name { font-family:'Anton'; font-size:26px; color:#fff; line-height:1; margin-bottom:6px;
  background:linear-gradient(92deg,#fff,var(--neon)); -webkit-background-clip:text;
  background-clip:text; color:transparent; }
.apk-grp { font-family:'Anton'; font-size:13px; letter-spacing:1px; color:#9fb0d4;
  margin:10px 0 4px; }
.apk-score { display:flex; align-items:center; gap:9px; padding:5px 2px;
  border-bottom:1px solid #ffffff12; }
.apk-tn { flex:1; font-weight:700; font-size:14px; color:#dce6ff; }
.apk-tn.rt { text-align:right; }
.apk-num { font-family:'Anton'; font-size:17px; color:#fff; }

/* Match meta line: date · time · city + thumbnail */
.m-meta { display:flex; align-items:center; gap:10px; margin:7px 0 3px; }
.m-meta .mthumb { width:42px; height:28px; object-fit:cover; border-radius:7px;
  box-shadow:0 2px 8px #0009; border:1px solid #ffffff22; flex:0 0 auto; }
.m-meta span { font-size:15px; font-weight:700; color:#bcc9e6; }
</style>
"""


_SVG_DEFS = """
<svg style="position:absolute;width:0;height:0;" aria-hidden="true" focusable="false">
  <defs>
    <!-- rough torn-paper / brush edge -->
    <filter id="paintRough" x="-8%" y="-8%" width="116%" height="116%">
      <feTurbulence type="fractalNoise" baseFrequency="0.014" numOctaves="2" seed="7" result="n"/>
      <feDisplacementMap in="SourceGraphic" in2="n" scale="8"
        xChannelSelector="R" yChannelSelector="G"/>
    </filter>
    <!-- animated waving cloth flag -->
    <filter id="flagWave" x="-12%" y="-12%" width="124%" height="124%">
      <feTurbulence type="fractalNoise" baseFrequency="0.012 0.026" numOctaves="2"
        seed="3" result="n">
        <animate attributeName="baseFrequency" dur="8s"
          values="0.012 0.026;0.016 0.02;0.012 0.026" repeatCount="indefinite"/>
      </feTurbulence>
      <feDisplacementMap in="SourceGraphic" in2="n" scale="13"
        xChannelSelector="R" yChannelSelector="G"/>
    </filter>
  </defs>
</svg>
"""


def inject():
    st.markdown(_SVG_DEFS + _CSS, unsafe_allow_html=True)
    _hide_admin_nav()
    _app_background()


def _hide_admin_nav():
    """Hide the Admin page from the sidebar unless the admin user is signed in."""
    from .util import secret
    admin_name = (secret("ADMIN_NAME", "eyal") or "eyal").strip().lower()
    user = st.session_state.get("participant") or {}
    is_admin = user.get("name", "").strip().lower() == admin_name
    if not is_admin:
        st.markdown(
            '<style>[data-testid="stSidebarNav"] a[href*="Admin"]{display:none!important;}</style>',
            unsafe_allow_html=True,
        )


def _app_background():
    """Full-page backdrop behind everything — a different random city each visit.

    Picks a random city image from static/cities/ (stable for the session, so it
    doesn't flicker between clicks; refresh for a new one). Falls back to
    static/background.* if no city art is present yet.
    """
    from .assets import find_asset, slugify
    from .data import load_stadiums

    cities = []
    for s in load_stadiums():
        u, _ = find_asset("cities", slugify(s["city"]))
        if u:
            cities.append(u)

    if cities:
        if st.session_state.get("_bg_city") not in cities:
            st.session_state["_bg_city"] = random.choice(cities)
        url = st.session_state["_bg_city"]
    else:
        url, _ = find_asset(".", "background")
    if not url:
        return
    st.markdown(
        f"""<style>
        .stApp::after {{
          content:""; position:fixed; inset:0; z-index:0; pointer-events:none;
          background:url('{url}') center/cover no-repeat fixed; opacity:.20;
          -webkit-mask-image:linear-gradient(180deg,#000,#0008 55%,transparent);
                  mask-image:linear-gradient(180deg,#000,#0008 55%,transparent);
        }}</style>""",
        unsafe_allow_html=True,
    )


def hero(title: str, subtitle: str, kicker: str = "FIFA World Cup 2026 · USA · Canada · Mexico",
         bg_html: str = ""):
    st.markdown(
        f'<div class="wc-hero">'
        f'{bg_html}'
        f'<div class="wc-hero-inner">'
        f'<div class="wc-kicker">{kicker}</div>'
        f'<div class="wc-title">{title}</div>'
        f'<div class="wc-sub">{subtitle}</div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )


def countdown():
    """Live ticking countdown to kickoff. Runs as a real (JS-executing) iframe."""
    try:
        _countdown_iframe()
    except Exception:
        # Degrade gracefully if the html component API is unavailable.
        st.markdown('<span class="wc-pill">⏱️ Kickoff: June 11, 2026</span>',
                    unsafe_allow_html=True)


def _countdown_iframe():
    components.html(
        f"""
<div class="cd-wrap" id="wc-cd"></div>
<style>
@import url('https://fonts.googleapis.com/css2?family=Anton&family=Rajdhani:wght@600&display=swap');
body{{margin:0;background:transparent;font-family:'Rajdhani',sans-serif;}}
.cd-wrap{{display:flex;gap:10px;flex-wrap:wrap;}}
.cd-box{{background:#ffffff10;border:1px solid #ffffff22;border-radius:12px;
  padding:8px 16px;min-width:74px;text-align:center;}}
.cd-num{{font-family:'Anton',sans-serif;font-size:30px;color:#fff;line-height:1;}}
.cd-lbl{{font-size:11px;letter-spacing:2px;color:#8ea0c4;text-transform:uppercase;}}
</style>
<script>
var t=new Date("{KICKOFF_ISO}").getTime();
function pad(n){{return String(n).padStart(2,"0");}}
function tick(){{
  var el=document.getElementById("wc-cd"); if(!el) return;
  var d=t-Date.now();
  if(d<0){{el.innerHTML='<div class="cd-box"><div class="cd-num">LIVE</div>'+
    '<div class="cd-lbl">Tournament underway</div></div>'; return;}}
  var dd=Math.floor(d/864e5),hh=Math.floor(d%864e5/36e5),
      mm=Math.floor(d%36e5/6e4),ss=Math.floor(d%6e4/1e3);
  var parts=[["DAYS",dd],["HRS",pad(hh)],["MIN",pad(mm)],["SEC",pad(ss)]];
  el.innerHTML=parts.map(function(x){{return '<div class="cd-box"><div class="cd-num">'+
    x[1]+'</div><div class="cd-lbl">'+x[0]+'</div></div>';}}).join("");
}}
tick(); setInterval(tick,1000);
</script>
""",
        height=80,
    )
