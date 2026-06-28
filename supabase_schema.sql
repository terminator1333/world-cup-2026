-- World Cup 2026 Prediction Pool — Supabase schema.
-- Paste this whole file into the Supabase SQL Editor and click "Run".

create extension if not exists pgcrypto;

-- Players in the pool.
create table if not exists participants (
  id         uuid primary key default gen_random_uuid(),
  name       text unique not null,
  pin_hash   text not null,
  created_at timestamptz default now()
);

-- One row per (player, category). payload is flexible JSON.
-- category in ('group_order','per_game','third_place','knockout','scorers',
--              'awards','ko_pool')   -- 'ko_pool' = the separate Round-of-32 game
create table if not exists predictions (
  id             uuid primary key default gen_random_uuid(),
  participant_id uuid references participants(id) on delete cascade,
  category       text not null,
  payload        jsonb not null default '{}',
  updated_at     timestamptz default now(),
  unique (participant_id, category)
);

-- Admin-entered actual results. category + key identify what the result is for.
create table if not exists results (
  id         uuid primary key default gen_random_uuid(),
  category   text not null,
  key        text not null,
  actual     jsonb,
  updated_at timestamptz default now(),
  unique (category, key)
);

-- This app talks to Supabase only from the Streamlit server (the key never
-- reaches a browser). Keep RLS off for simplicity, OR enable it and add
-- permissive policies if you prefer:
--
--   alter table participants enable row level security;
--   alter table predictions  enable row level security;
--   alter table results       enable row level security;
--   create policy "all" on participants for all using (true) with check (true);
--   create policy "all" on predictions  for all using (true) with check (true);
--   create policy "all" on results       for all using (true) with check (true);
