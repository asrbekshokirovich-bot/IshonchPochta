-- Ishonch Pochta — shipments table schema.
-- Run in the Supabase SQL Editor for project dhqzairyxzoppskzpzxr.
--
-- NOTE: a previous `shipments` table exists with a different schema
-- (column `tracking_number` instead of `tracking_code`, missing
-- `package_type`, `notes`, `updated_at`). It is empty. The line below
-- drops it so the table matches the schema the frontend expects.
-- If the table has data you want to keep, remove the DROP and migrate
-- by hand instead.
drop table if exists shipments cascade;

create table if not exists shipments (
  id             bigint generated always as identity primary key,
  tracking_code  text unique not null,
  sender_name    text,
  sender_phone   text,
  sender_city    text,
  receiver_name  text,
  receiver_phone text,
  receiver_city  text,
  weight_kg      numeric(6,2) default 0,
  package_type   text default 'Standart',
  status         text default 'accepted',
  notes          text,
  created_at     timestamptz default now(),
  updated_at     timestamptz default now()
);

alter table shipments enable row level security;

drop policy if exists "Public read"   on shipments;
drop policy if exists "Public insert" on shipments;
drop policy if exists "Public update" on shipments;
drop policy if exists "Public delete" on shipments;

create policy "Public read"   on shipments for select using (true);
create policy "Public insert" on shipments for insert with check (true);
create policy "Public update" on shipments for update using (true);
create policy "Public delete" on shipments for delete using (true);
