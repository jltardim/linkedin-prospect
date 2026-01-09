# LinkedIn Prospect SDR Tool

Aplicacao para prospeccao no LinkedIn usando Unipile, Supabase e Streamlit. O fluxo principal e: criar uma lista via Sales Navigator, salvar, enriquecer, convidar e enviar mensagens.

## O que este app faz
- Busca pessoas no Sales Navigator por parametros com IDs oficiais.
- Extrai parametros de uma URL do Sales Navigator para preencher os campos de busca.
- Pagina resultados com cursor e permite buscar em lote.
- Salva listas em campanhas, com deduplicacao.
- Enriquecimento leve (Bio, Cargo, Empresas, Empresa ID, Localizacao, Emails, Phones, Adresses, Socials).
- Envio de convites com agendamento e limite diario.
- Envio de mensagens por novo chat (attendee_id) ou chat existente (chat_id).
- Aba de payloads para auditar request/response.

## Estrategia completa de prospeccao (recomendada)
1. Defina o ICP e filtros do Sales Navigator.
2. Cole a URL do Sales Navigator e extraia os parametros (apenas para preencher os campos).
3. Ajuste os filtros e busque por parametros oficiais (REGION, SALES_INDUSTRY, JOB_TITLE, etc).
4. Deduplicate e salve a lista em campanha.
5. Enriqueca apenas o necessario antes de convidar.
6. Envie convites com limite diario e intervalo entre envios.
7. Monitore aceites e envie mensagens apenas para conexoes.
8. Reavalie respostas e otimize o copy e o targeting.

## Estrategia para identificar aceites e enviar mensagens
Nao existe webhook de aceite. A forma mais confiavel e cruzar:
- Pendentes: `/api/v1/users/invite/sent`
- Conexoes: `/api/v1/users/relations`

Regra pratica:
- Aceitou = aparece em relations e nao aparece mais em invite/sent
- Pendente = aparece em invite/sent
- Desconhecido/ignorado = nao aparece em nenhum

Recomendacao operacional:
- Rodar uma sincronizacao 2-4x ao dia.
- Persistir `invited_user_public_id` e/ou `invited_user_id` no lead.
- Usar `public_identifier` ou `member_id` para o join.
- Enviar mensagem automatica somente para leads marcados como aceitos.
Nota: essa sincronizacao precisa ser implementada via job/worker; o app atual nao faz isso sozinho.

## Arquitetura
- Frontend: Streamlit
- Backend/DB: Supabase (PostgreSQL + Auth + RLS)
- Integracao externa: Unipile API (LinkedIn)

## Requisitos
- Python 3.10+
- Conta Supabase com Auth habilitado
- Conta Unipile com LinkedIn conectado (Sales Navigator recomendado)

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
```

## Como rodar
```bash
streamlit run projeto_linkedin/app.py
```

## Como usar (passo a passo)
1. Abra o app e informe `Supabase URL` e `Supabase Key`.
2. Faca login com seu usuario do Supabase Auth.
3. Cadastre uma conta Unipile (Account ID, API Key, Label).
4. Aba **Lista (Sales Navigator)**:
   - Cole a URL no expander "Extrair parametros da URL" e clique em "Extrair parametros".
   - Revise os campos preenchidos e ajuste os filtros.
   - Informe IDs (REGION, SALES_INDUSTRY, JOB_TITLE, etc).
   - Use o expander de parametros para listar IDs.
   - Use o botao de busca em lote para coletar mais paginas.
   - Baixe a lista ou salve como campanha.
5. Aba **Enriquecimento**:
   - Escolha uma lista existente ou envie um CSV.
   - O app retorna Bio, Cargo, Empresas, Empresa ID, Localizacao, Emails, Phones, Adresses, Socials.
6. Aba **Convites**:
   - Lista existente ou CSV.
   - Configure agendamento com limite de 50 convites/dia.
   - Defina mensagem opcional (max 300) e envie os convites do dia.
7. Aba **Mensagens**:
   - Lista existente ou CSV.
   - Escolha o modo: Novo chat (attendee_id) ou Chat existente (chat_id).
   - Defina o template e envie com delay entre mensagens.
8. Aba **Payloads**:
   - Veja o payload enviado e a resposta recebida.

## Paginacao e limites
- Sales Navigator tem limite de 100 itens por pagina.
- O cursor pode expirar; use o checkpoint para retomar no dia seguinte.
- O LinkedIn aplica limites dinamicos de envio (influencia por conta, rede e tipo de mensagem).
- Quando estourar limites, a API retorna erros como `errors/limit_exceeded`.

## Checkpoint (retomar no dia seguinte)
Na aba de lista:
- Baixe o checkpoint com a lista e o cursor.
- No dia seguinte, faca upload e clique em "Carregar checkpoint".

## Formato de CSV
**Enriquecimento (upload):**
- Colunas aceitas: `public_identifier`, `linkedin_public_id`, `id`, `profile_url`.

**Mensagens (upload):**
- Novo chat: `provider_id` ou `id`
- Chat existente: `chat_id`

**Convites (upload):**
- `provider_id` ou `id`
- opcional: `user_email`

## Script de paginacao (opcional)
Arquivo: `linkedin_salesnav_pagination.py`

Variaveis de ambiente:
- `UNIPILE_TOKEN`
- `UNIPILE_ACCOUNT_ID`
- `UNIPILE_BASE_URL` (opcional)

Exemplo:
```bash
export UNIPILE_TOKEN="..."
export UNIPILE_ACCOUNT_ID="..."
python linkedin_salesnav_pagination.py
```

## Seguranca e chaves
- Nao commite chaves no repositorio.
- `.env`, `.streamlit/secrets.toml` e `json-n8n*.json` estao ignorados no `.gitignore`.
- Use variaveis de ambiente ou o formulario do app.

## Problemas comuns
- **"Apenas perfis inacessiveis encontrados"**: confira o payload enviado na aba Payloads e valide os parametros.
- **URL nao preencheu os campos**: valide se a URL e do Sales Navigator e se o campo `query` existe.
- **Sem cursor**: revise filtros/conta.
- **Mensagem nao enviada**: verifique se o attendee_id ou chat_id esta presente e se a conta tem permissao.
- **Convite nao enviado**: confirme provider_id e limites do LinkedIn; mensagens de convite tem limite de 300 caracteres.

## Observacoes legais
Use a API Unipile e o LinkedIn de acordo com os termos de uso. Evite automacoes agressivas.
