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

## Automacao (opcao 2: Edge Function + Worker)
Nesta opcao, a Edge Function faz apenas a sincronizacao de aceites e o worker Python envia as mensagens.

### 1) Edge Function (sync de aceites)
Arquivo: `supabase/functions/sync-acceptances/index.ts`

Requisitos:
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `UNIPILE_BASE_URL` (opcional)

Deploy (exemplo):
```bash
supabase functions deploy sync-acceptances
```

Execucao manual (exemplo):
```bash
curl -H "x-dry-run: true" "https://<project>.functions.supabase.co/sync-acceptances"
```

Parametros opcionais:
- `account_db_id`: limita a uma conta Unipile
- `dry_run=1`: apenas simula
- `max_leads`: limita o numero de leads avaliados

### 2) Worker Python (envio automatico)
Arquivo: `projeto_linkedin/sync_acceptances.py`

Requisitos:
- `SUPABASE_URL`
- `SUPABASE_SERVICE_KEY` (recomendado para bypass de RLS)

Enviar mensagens apenas para leads aceitos (padrao):
```bash
SUPABASE_URL="..." SUPABASE_SERVICE_KEY="..." \
python3 projeto_linkedin/sync_acceptances.py
```

Rodar sync via Python (fallback):
```bash
SUPABASE_URL="..." SUPABASE_SERVICE_KEY="..." \
python3 projeto_linkedin/sync_acceptances.py --sync --no-send
```

Variaveis de envio:
- `AUTO_MESSAGE_LIMIT` (default 50)
- `AUTO_MESSAGE_DELAY_MIN` / `AUTO_MESSAGE_DELAY_MAX`
- `AUTO_MESSAGE_LINKEDIN_API`
- `AUTO_MESSAGE_INMAIL`
- `AUTO_MESSAGE_SUBJECT`

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

## Modo BYO (cada usuario com seu Supabase)
Este app funciona no modelo BYO: cada pessoa usa o proprio projeto Supabase.

Passos resumidos:
1. No app, baixe o arquivo `supabase_schema.sql` na barra lateral.
2. Rode o SQL no SQL Editor do Supabase do usuario.
3. No app, informe `Supabase URL` e `Supabase Key` do proprio projeto.
4. Cadastre as credenciais da Unipile do usuario.

### Worker (opcional)
O worker de sincronizacao nao roda na stack compartilhada, pois depende da `SUPABASE_SERVICE_KEY` de cada usuario.
Se quiser automatizar, cada usuario deve rodar o worker no proprio ambiente com as credenciais dele:
```bash
SUPABASE_URL="..." SUPABASE_SERVICE_KEY="..." \
python3 projeto_linkedin/sync_acceptances.py --sync --send
```

#### Worker via Docker Compose
Se preferir, o usuario pode subir o worker com Docker usando o arquivo `docker-compose.worker.yml`.

Passo a passo:
1. Garanta que o usuario tenha este repositorio na maquina (com o Dockerfile).
2. (Recomendado) Copie o arquivo de exemplo e preencha as variaveis:
```bash
cp .env.worker.example .env.worker
```
3. Rode o comando abaixo no diretorio do projeto:
```bash
docker compose --env-file .env.worker -f docker-compose.worker.yml up -d --build
```

Variaveis opcionais:
- `UNIPILE_BASE_URL`
- `UNIPILE_ACCOUNT_DB_ID`
- `AUTO_MESSAGE_LIMIT`
- `AUTO_MESSAGE_DELAY_MIN`
- `AUTO_MESSAGE_DELAY_MAX`
- `AUTO_MESSAGE_LINKEDIN_API`
- `AUTO_MESSAGE_INMAIL`
- `AUTO_MESSAGE_SUBJECT`
- `WORKER_INTERVAL_SECONDS` (padrao 21600 = 6h)

Parar o worker:
```bash
docker compose -f docker-compose.worker.yml down
```

Atualizar o worker (rebuild):
```bash
docker compose -f docker-compose.worker.yml up -d --build
```

## Subir no Portainer (Traefik + BYO)
Pre-requisitos:
- Traefik rodando em modo Swarm com a rede `network_public`.
- A imagem `linkedin-prospect:latest` precisa existir no servidor do Portainer.
  - Se o Portainer roda neste servidor, rode: `docker build -t linkedin-prospect:latest .`
  - Se usa outro servidor, faça o build la ou publique a imagem em um registry.

Passo a passo (app):
1. Abra o Portainer no navegador.
2. Clique em **Stacks** -> **Add stack**.
3. Nome: `linkedin-prospect`.
4. Em **Web editor**, cole o conteudo do arquivo `docker-compose.yml`.
5. Em **Environment variables**, adicione:
   - `LINKEDIN_PROSPECT_HOST` = seu dominio (ex: `app.seudominio.com`)
6. Clique em **Deploy the stack**.
7. Acesse `https://seu-dominio` no navegador.

Passo a passo (worker por usuario, opcional):
1. **Stacks** -> **Add stack**.
2. Nome: `linkedin-worker-cliente`.
3. Em **Web editor**, cole o conteudo do arquivo `docker-compose.worker.yml`.
4. Em **Environment variables**, preencha:
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_KEY`
   - (Opcional) demais variaveis de automacao.
5. Clique em **Deploy the stack**.

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
