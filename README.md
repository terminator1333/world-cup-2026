# 🏆 World Cup 2026 Prediction Pool

<img width="1600" height="893" alt="mexico-city" src="https://github.com/user-attachments/assets/5a3f7820-ac50-435f-aef5-a9fb96a3c57c" />



A vibrant, FIFA-game-styled Streamlit app where you and your friends predict the
2026 FIFA World Cup (USA · Canada · Mexico, June 11 – July 19, 2026) and compete
on a live, auto-scored leaderboard. No local server to babysit — it runs on
**Streamlit Community Cloud** with a free **Supabase** database holding everyone's picks.

## Two separate games
The app runs **two independent competitions, each with its own leaderboard**:

1. **🏆 Full Tournament** *(season-long)* — predict, all optional, per person:
   - **🥇 Group standings** — order all 12 groups 1st → 4th
   - **⚽ Match results** — outcome (+ optional scoreline) for any group game
   - **🥉 3rd-place race** — which 8 third-placed teams sneak into the Round of 32
   - **🏆 Knockout bracket** — your run to the champion + Golden Boot & awards
2. **🥊 Knockout Pool** *(separate ranking)* — once the group stage is over and the
   32 are known, predict the **real** Round-of-32 bracket (actual qualifiers, fixed
   FIFA slotting) tie-by-tie to the champion. It does **not** affect your
   full-tournament score and locks at the **first knockout game**
   (`KO_LOCK_DATETIME`, default 2026-06-28 19:00 UTC).

Points are awarded automatically (tunable in `lib/scoring.py` / `lib/data.py`) and
everyone's picks are revealed on the **All Picks** page. The real bracket and final
group tables live in `data/knockout_bracket.json` and `data/real_results.json`;
an Admin button one-click-loads the real group results so the full-tournament board
goes live.

<img width="1600" height="893" alt="vancouver" src="https://github.com/user-attachments/assets/b43bfed4-61b3-43a0-8002-f06f717ae6a5" />

## Run locally
```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```
With no Supabase keys configured it uses a local `.localdb.json` store so you can
click through everything immediately. (Picks won't be shared between people in
this mode — that needs Supabase, below.)

## Deploy so friends can play (free)

### 1. Supabase (shared storage)
1. Create a free project at [supabase.com](https://supabase.com).
2. Open **SQL Editor**, paste `supabase_schema.sql`, click **Run**.
3. In **Project Settings → API**, copy the **Project URL** and an **API key**
   (the `service_role` key is fine — it stays server-side in Streamlit).

### 2. Streamlit Community Cloud (hosting)
1. Push this folder to a GitHub repo.
2. At [share.streamlit.io](https://share.streamlit.io), **New app** → pick the repo,
   main file `streamlit_app.py`.
3. In **App → Settings → Secrets**, paste (see `.streamlit/secrets.toml.example`):
   ```toml
   SUPABASE_URL = "https://YOUR-PROJECT.supabase.co"
   SUPABASE_KEY = "your-key"
   ADMIN_PIN = "pick-a-secret"
   LOCK_DATETIME = "2026-06-11T11:00:00"
   ```
4. Deploy and share the URL. Friends register with a name + PIN and start picking.

## Running the pool
- Share the app URL; everyone registers (name + PIN edits only their own card).
- Picks **lock** at `LOCK_DATETIME` (first kickoff). After that, **All Picks** reveals everyone.
- As matches finish, open **🔐 Admin** (the `ADMIN_PIN`), enter results, and the
  **📊 Leaderboard** updates instantly.

## Notes
- Group compositions are the real Dec 2025 final-draw results. Match **dates/venues**
  are scheduled approximations within the official window — edit `lib/data.py` to
  match the official fixture list exactly if you like.
- Uses country **flags** (via [flagcdn.com](https://flagcdn.com)) and national colours
  rather than copyrighted federation crests.
  
  <img width="1600" height="893" alt="atlanta" src="https://github.com/user-attachments/assets/af86e0c2-9bfb-4df3-82f1-0f23d187b2b1" />


- **City photos** are license-clean: by default the *Cities & Legends* page pulls free
  Creative-Commons images from [Openverse](https://openverse.org) (credited on each card).
  For sharper skylines, add a free `UNSPLASH_ACCESS_KEY` (see `secrets.toml.example`) —
  get one at [unsplash.com/developers](https://unsplash.com/developers). If a source is
  unreachable it falls back to a free placeholder so cards never break.


  <img width="2816" height="1536" alt="pele" src="https://github.com/user-attachments/assets/d65edefc-cc04-4e2a-ae8f-8941a928a5b5" />


