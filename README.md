# LinkedIn Prospect SDR Tool

Aplicacao para prospeccao automatizada no LinkedIn usando Unipile, Supabase e Streamlit. O foco e criar listas de leads, enriquecer dados e organizar campanhas de outreach.

## Para que serve
- Buscar pessoas no LinkedIn (Classic) e no Sales Navigator.
- Salvar listas de leads com deduplicacao e score simples por palavras-chave.
- Enriquecer perfis (contato, experiencia, educacao, sobre).
- Criar campanhas e registrar tentativas de envio.

## Arquitetura
- Frontend: Streamlit
- Backend/DB: Supabase (PostgreSQL + Auth + RLS)
- Integracao externa: Unipile API (LinkedIn)

## Requisitos
- Python 3.10+
- Conta Supabase (com Auth habilitado)
- Conta Unipile com LinkedIn conectado (Classic e/ou Sales Navigator)

## Instalacao
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuracao do Supabase
Crie as tabelas abaixo no SQL Editor do Supabase (ative a extensao uuid-ossp se necessario):
```sql
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
  status text default 'new',
  enrichment_data jsonb,
  unique(campaign_id, linkedin_public_id)
);

create table message_logs (
  id uuid default uuid_generate_v4() primary key,
  lead_id uuid references leads(id) on delete cascade not null,
  campaign_id uuid references campaigns(id) not null,
  user_id uuid references auth.users not null,
  status text not null,
  error_message text
);
```

## Como rodar
```bash
streamlit run projeto_linkedin/app.py
```

## Como usar
1. Abra o app e informe `Supabase URL` e `Supabase Key`.
2. Faca login com seu usuario do Supabase Auth.
3. Cadastre uma conta Unipile (Account ID, API Key, Label).
4. Use a aba de busca:
   - Classic: permite filtros simples (cargo, palavras-chave, local, empresa).
   - Sales Navigator: use palavras-chave e empresa por nome ou cole a URL do Sales Navigator.
5. Selecione leads, salve campanha e opcionalmente faca enriquecimento.

### Sales Navigator: boas praticas
- Filtros avancados do Sales Navigator usam IDs. Para evitar erro, cole a URL de busca diretamente.
- Para buscas simples, use apenas `Palavras-chave` e `Empresa`.

## Seguranca e chaves
- Nao commite chaves no repositorio.
- Este repo ignora arquivos `.env`, `secrets.toml`, `json-n8n*.json` e ambientes virtuais.
- Informe chaves pelo formulario da aplicacao ou guarde localmente.

## Estrutura do repo
```
.
- projeto_linkedin/
  - app.py
  - unipile_client.py
  - db_handler.py
  - documentacao_api/
- requirements.txt
- README.md
```

## Observacoes
- Use a API Unipile e o LinkedIn de acordo com os termos de uso.
- Se o Sales Navigator retornar vazio, confirme o payload e use URL de busca.
