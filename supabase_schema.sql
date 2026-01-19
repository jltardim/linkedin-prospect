create extension if not exists "uuid-ossp";

create table unipile_accounts (
  id uuid default uuid_generate_v4() primary key,
  user_id uuid references auth.users not null,
  account_id text not null,
  api_key text not null,
  label text,
  unique(user_id, account_id)
);

create table campaigns (
  id uuid default uuid_generate_v4() primary key,
  user_id uuid references auth.users not null,
  unipile_account_id uuid references unipile_accounts(id),
  name text not null,
  message_template text,
  status text default 'draft',
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

create table leads (
  id uuid default uuid_generate_v4() primary key,
  campaign_id uuid references campaigns(id) on delete cascade not null,
  user_id uuid references auth.users not null,
  linkedin_public_id text,
  provider_id text,
  full_name text,
  headline text,
  location text,
  profile_location text,
  current_title text,
  companies text,
  company_id text,
  bio text,
  emails text,
  phones text,
  adresses text,
  socials text,
  invitation_status text,
  invitation_id text,
  invited_at timestamp with time zone,
  invitation_error text,
  status text default 'new',
  enrichment_data jsonb,
  unique(campaign_id, linkedin_public_id)
);

create table invite_schedules (
  id uuid default uuid_generate_v4() primary key,
  user_id uuid references auth.users not null,
  campaign_id uuid references campaigns(id) on delete cascade,
  lead_id uuid references leads(id) on delete cascade,
  provider_id text not null,
  user_email text,
  full_name text,
  scheduled_date date not null,
  status text default 'scheduled',
  message text,
  invitation_id text,
  error_message text,
  source text default 'campaign',
  batch_id uuid,
  batch_label text,
  metadata jsonb,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  sent_at timestamp with time zone
);

create index invite_schedules_user_date_idx on invite_schedules(user_id, scheduled_date);
create index invite_schedules_campaign_idx on invite_schedules(campaign_id);
create unique index invite_schedules_unique_idx on invite_schedules(user_id, provider_id, scheduled_date);

create table message_logs (
  id uuid default uuid_generate_v4() primary key,
  lead_id uuid references leads(id) on delete cascade not null,
  campaign_id uuid references campaigns(id) not null,
  user_id uuid references auth.users not null,
  status text not null,
  error_message text
);
