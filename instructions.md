

***

**CONTEXTO DO PROJETO:**
Estou desenvolvendo uma aplicação de **Prospecção Automatizada no LinkedIn (SDR Tool)** usando **Python**. O objetivo é permitir que usuários busquem leads no LinkedIn (via API Unipile), filtrem esses leads, enriqueçam os dados e criem campanhas de envio de mensagens (Outreach).

**STACK TECNOLÓGICA:**
1.  **Frontend:** Streamlit (Python).
2.  **Backend/Database:** Supabase (PostgreSQL + Auth).
3.  **API Externa:** Unipile API (Para automação do LinkedIn).
4.  **Estrutura:** Arquitetura flat (todos arquivos na mesma pasta raiz).

**ESTRUTURA DE DADOS (SUPABASE SQL):**
O banco de dados possui as seguintes tabelas já configuradas com RLS (Row Level Security):
```sql
-- Tabela de Credenciais da API Unipile
create table unipile_accounts (
  id uuid default uuid_generate_v4() primary key,
  user_id uuid references auth.users not null,
  account_id text not null,
  api_key text not null,
  label text,
  unique(user_id, account_id)
);

-- Tabela de Campanhas
create table campaigns (
  id uuid default uuid_generate_v4() primary key,
  user_id uuid references auth.users not null,
  unipile_account_id uuid references unipile_accounts(id),
  name text not null,
  message_template text,
  status text default 'draft',
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Tabela de Leads
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
  enrichment_data jsonb, -- Guarda dados completos do perfil/empresa
  unique(campaign_id, linkedin_public_id)
);

-- Tabela de Logs
create table message_logs (
  id uuid default uuid_generate_v4() primary key,
  lead_id uuid references leads(id) on delete cascade not null,
  campaign_id uuid references campaigns(id) not null,
  user_id uuid references auth.users not null,
  status text not null,
  error_message text
);
```

**CÓDIGO ATUAL DA APLICAÇÃO:**

Abaixo estão os 3 arquivos principais do projeto, já contendo as correções de sessão, paginação e tratamento de erros.

**Arquivo 1: `unipile_client.py` (Wrapper da API)**
```python
import requests
import time
import logging
from typing import Dict, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UnipileClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "X-API-KEY": self.api_key
        }

    def _request(self, method: str, endpoint: str, params: dict = None, json_data: dict = None, max_retries: int = 3):
        url = f"{self.base_url}{endpoint}"
        for attempt in range(max_retries):
            try:
                response = requests.request(method, url, headers=self.headers, params=params, json=json_data, timeout=30)
                if response.status_code == 429:
                    time.sleep((2 ** attempt) + 5)
                    continue
                if 200 <= response.status_code < 300:
                    return response.json()
                response.raise_for_status()
            except Exception as e:
                if attempt == max_retries - 1: raise e
                time.sleep(2)
        return None

    def search_people(self, account_id: str, criteria: Dict, limit: int = 50, cursor: str = None, api_type: str = "classic"):
        endpoint = "/api/v1/linkedin/search"
        if api_type == "classic" and limit > 50: limit = 50
        payload = {"api": api_type, "category": "people", "params": criteria}
        query_params = {"account_id": account_id, "limit": limit}
        if cursor: query_params["cursor"] = cursor
        return self._request("POST", endpoint, params=query_params, json_data=payload)

    def get_profile_details(self, account_id: str, identifier: str):
        sections = ["contact_info", "experience", "education", "about"]
        endpoint = f"/api/v1/users/{identifier}"
        params = {"account_id": account_id, "linkedin_sections": sections}
        return self._request("GET", endpoint, params=params)

    def start_chat(self, account_id: str, attendees_ids: List[str], text: str, subject: str = None):
        endpoint = "/api/v1/chats"
        payload = {"account_id": account_id, "attendees_ids": attendees_ids, "text": text}
        if subject: payload["subject"] = subject
        return self._request("POST", endpoint, json_data=payload)
```

**Arquivo 2: `db_handler.py` (Conexão Supabase com Sessão Persistente)**
```python
from supabase import create_client, Client
import streamlit as st
from typing import List, Dict

class DBHandler:
    def __init__(self, url: str, key: str):
        self.supabase: Client = create_client(url, key)
        self.user = None

    def login(self, email, password):
        try:
            response = self.supabase.auth.sign_in_with_password({"email": email, "password": password})
            self.user = response.user
            return response.session 
        except Exception as e:
            st.error(f"Erro no login: {e}")
            return None

    def set_session(self, access_token, refresh_token):
        try:
            self.supabase.auth.set_session(access_token, refresh_token)
            self.user = self.supabase.auth.get_user().user
            return True
        except: return False

    def save_unipile_account(self, account_id: str, api_key: str, label: str):
        if not self.user: raise Exception("Não autenticado.")
        data = {"user_id": self.user.id, "account_id": account_id, "api_key": api_key, "label": label}
        return self.supabase.table("unipile_accounts").upsert(data).execute()

    def get_user_accounts(self):
        return self.supabase.table("unipile_accounts").select("*").execute()

    def create_campaign(self, name: str, template: str, account_db_id: str):
        data = {"user_id": self.user.id, "unipile_account_id": account_db_id, "name": name, "message_template": template, "status": "draft"}
        return self.supabase.table("campaigns").insert(data).execute()

    def save_leads(self, campaign_id: str, leads_list: List[Dict]):
        formatted = []
        for lead in leads_list:
            formatted.append({
                "user_id": self.user.id,
                "campaign_id": campaign_id,
                "linkedin_public_id": lead.get("public_identifier"),
                "provider_id": lead.get("provider_id") or lead.get("id"),
                "full_name": lead.get("name"),
                "headline": lead.get("headline"),
                "location": lead.get("location"),
                "status": "new",
                "enrichment_data": lead.get("enrichment_data", None) 
            })
        return self.supabase.table("leads").upsert(formatted, on_conflict="campaign_id, linkedin_public_id").execute()
    
    def update_lead_status(self, lead_id: str, status: str):
        self.supabase.table("leads").update({"status": status}).eq("id", lead_id).execute()

    def log_attempt(self, campaign_id: str, lead_id: str, status: str, error_msg: str = None):
        data = {"user_id": self.user.id, "campaign_id": campaign_id, "lead_id": lead_id, "status": status, "error_message": error_msg}
        self.supabase.table("message_logs").insert(data).execute()
```

**Arquivo 3: `app.py` (Frontend Streamlit)**
```python
import streamlit as st
import pandas as pd
import time
from unipile_client import UnipileClient
from db_handler import DBHandler

st.set_page_config(page_title="LinkedIn List Builder Pro", layout="wide", page_icon="🎯")

def init_session():
    if 'search_results' not in st.session_state: st.session_state['search_results'] = []
    if 'next_cursor' not in st.session_state: st.session_state['next_cursor'] = None
    if 'search_params' not in st.session_state: st.session_state['search_params'] = {}

def clean_results(items):
    valid = []
    for item in items:
        name = item.get('name', '').lower()
        pid = item.get('public_identifier')
        if pid and "usuário do linkedin" not in name and "linkedin member" not in name:
            valid.append(item)
    return valid

# --- Sidebar ---
with st.sidebar:
    st.title("⚙️ Config")
    url = st.text_input("Supabase URL", type="password", key="sb_url")
    key = st.text_input("Supabase Key", type="password", key="sb_key")
    
    db = None
    if url and key:
        db = DBHandler(url, key)
        if 'access_token' in st.session_state:
            db.set_session(st.session_state['access_token'], st.session_state['refresh_token'])
            st.session_state['db_connected'] = True

    if db and not st.session_state.get('db_connected'):
        with st.form("login"):
            if st.form_submit_button("Login"):
                sess = db.login(st.text_input("Email", key="le"), st.text_input("Senha", type="password", key="lp"))
                if sess:
                    st.session_state['access_token'] = sess.access_token
                    st.session_state['refresh_token'] = sess.refresh_token
                    st.session_state['db_connected'] = True
                    st.rerun()

    if st.session_state.get('db_connected') and db and db.user:
        accs = db.get_user_accounts().data or []
        opts = {a['label']: a for a in accs}
        sel = st.selectbox("Conta", ["Selecione..."] + list(opts.keys()) + ["➕ Nova..."], key="acc_sel")
        
        if sel == "➕ Nova...":
            with st.form("new_acc"):
                if st.form_submit_button("Salvar") and db.save_unipile_account(st.text_input("ID", key="ni"), st.text_input("Key", key="nk"), st.text_input("Label", key="nl")):
                    st.rerun()
        elif sel != "Selecione...":
            st.session_state['current_account'] = opts[sel]

if not st.session_state.get('db_connected') or 'current_account' not in st.session_state:
    st.stop()

unipile = UnipileClient("https://api26.unipile.com:15609", st.session_state['current_account']['api_key'])
init_session()

tab1, tab2 = st.tabs(["🔍 Busca", "🚀 Campanhas"])

with tab1:
    with st.expander("Filtros", expanded=True):
        c1, c2, c3 = st.columns(3)
        title = c1.text_input("Cargo", key="st")
        loc = c1.text_input("Local", key="sl")
        kws = c2.text_input("Keywords", key="sk")
        ind = c2.text_input("Setor", key="si")
        comp = c3.text_input("Empresa", key="sc")
        api = st.radio("API", ["classic", "sales_navigator"], horizontal=True)
        
        if st.button("Buscar", key="btn_s"):
            st.session_state['search_results'] = []
            st.session_state['next_cursor'] = None
            crit = {}
            if title: crit["title"] = title
            if kws: crit["keywords"] = kws
            if loc: crit["location"] = loc
            if comp: crit["company"] = comp
            if ind: crit["industry"] = ind
            
            st.session_state['search_params'] = {"c": crit, "api": api}
            res = unipile.search_people(st.session_state['current_account']['account_id'], crit, limit=50, api_type=api)
            if res and 'items' in res:
                st.session_state['search_results'] = clean_results(res['items'])
                st.session_state['next_cursor'] = res.get('paging', {}).get('cursor')

    if st.session_state['search_results']:
        if st.session_state['next_cursor'] and st.button("Carregar +50", key="btn_m"):
            p = st.session_state['search_params']
            res = unipile.search_people(st.session_state['current_account']['account_id'], p['c'], limit=50, cursor=st.session_state['next_cursor'], api_type=p['api'])
            if res and 'items' in res:
                st.session_state['search_results'].extend(clean_results(res['items']))
                st.session_state['next_cursor'] = res.get('paging', {}).get('cursor')
                st.rerun()

        df = pd.DataFrame(st.session_state['search_results'])
        df.insert(0, "Sel", True)
        edited = st.data_editor(df[["Sel", "name", "headline", "location", "public_identifier"]], hide_index=True, key="de")
        
        sel_leads = [st.session_state['search_results'][i] for i in edited[edited["Sel"]==True].index]
        
        c1, c2 = st.columns([2,1])
        cn = c1.text_input("Nome Campanha", key="cn")
        mt = c1.text_area("Msg", "Olá {first_name}!", key="mt")
        enrich = c2.checkbox("Enriquecer", key="enr")
        
        if st.button("Salvar", key="sv"):
            camp = db.create_campaign(cn, mt, st.session_state['current_account']['id']).data[0]
            final = []
            bar = st.progress(0)
            for i, l in enumerate(sel_leads):
                if enrich:
                    try: l['enrichment_data'] = unipile.get_profile_details(st.session_state['current_account']['account_id'], l['public_identifier'])
                    except: pass
                final.append(l)
                bar.progress((i+1)/len(sel_leads))
            db.save_leads(camp['id'], final)
            st.success("Salvo!")
```

**OBJETIVO DA TAREFA:**
Analise todo o código fornecido acima. Entenda como o frontend gerencia o estado da sessão e como o backend lida com os limites da API do LinkedIn.
Apenas confirme que entendeu o contexto e a arquitetura. Aguarde minha próxima instrução para melhorias.