import re
from urllib.parse import urlparse, parse_qs
import streamlit as st
import pandas as pd
import time
from unipile_client import UnipileClient
from db_handler import DBHandler

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="LinkedIn List Builder Pro", layout="wide", page_icon="🎯")

# --- FUNÇÕES AUXILIARES ---
def init_session_state():
    if 'search_results' not in st.session_state: st.session_state['search_results'] = []
    if 'next_cursor' not in st.session_state: st.session_state['next_cursor'] = None
    if 'search_params' not in st.session_state: st.session_state['search_params'] = {}
    if 'seen_lead_keys' not in st.session_state: st.session_state['seen_lead_keys'] = set()
    if 'last_cursor' not in st.session_state: st.session_state['last_cursor'] = None

def reset_search():
    st.session_state['search_results'] = []
    st.session_state['next_cursor'] = None
    st.session_state['seen_lead_keys'] = set()
    st.session_state['last_cursor'] = None

def handle_search_response(res, criteria):
    if res and 'items' in res:
        valid = clean_results(res['items'], criteria)
        valid, st.session_state['seen_lead_keys'] = dedupe_results(
            valid,
            st.session_state['seen_lead_keys'],
        )
        st.session_state['search_results'] = valid
        st.session_state['next_cursor'] = res.get('paging', {}).get('cursor')
        st.session_state['last_cursor'] = st.session_state['next_cursor']
        if not valid:
            st.warning("Apenas perfis inacessíveis encontrados.")
    elif res is not None:
        st.warning("Nenhum resultado.")

def clean_results(items, criteria=None):
    results = items or []
    if criteria:
        return tag_results(results, criteria)
    return results

def lead_key(item: dict) -> str | None:
    for field in ("public_identifier", "provider_id", "id", "public_profile_url", "profile_url"):
        value = item.get(field)
        if value:
            return f"{field}:{value}"
    fallback = "|".join(
        str(item.get(field, "") or "")
        for field in ("name", "headline", "location")
    ).strip()
    if fallback:
        return f"fallback:{fallback}"
    return None

def dedupe_results(items: list, seen_keys: set) -> tuple[list, set]:
    unique = []
    for item in items:
        if not isinstance(item, dict):
            continue
        key = lead_key(item)
        if key and key in seen_keys:
            continue
        if key:
            seen_keys.add(key)
        unique.append(item)
    return unique, seen_keys

HR_SYNONYMS = [
    "RH",
    "HR",
    "\"Recursos Humanos\"",
    "\"Human Resources\"",
    "\"People Ops\"",
    "\"People Operations\"",
    "\"People & Culture\"",
    "\"Talent Acquisition\"",
    "\"Recruitment\"",
]

def expand_hr_query(value: str) -> str:
    if not value:
        return value
    stripped = value.strip()
    raw = stripped.strip('"').strip("'")
    if raw.lower() in {"rh", "hr"}:
        return " OR ".join(HR_SYNONYMS)
    return value

def apply_term_expansions(criteria: dict) -> dict:
    if not criteria:
        return criteria
    expanded = dict(criteria)
    for key in ("title", "keywords"):
        if key in expanded and isinstance(expanded[key], str):
            expanded[key] = expand_hr_query(expanded[key])
    return expanded

def split_or_terms(value: str) -> list:
    if not value:
        return []
    parts = re.split(r"\s+OR\s+", value, flags=re.IGNORECASE)
    return [p.strip() for p in parts if p and p.strip()]

def normalize_term(term: str) -> str:
    return term.strip().strip('"').strip("'").lower()

def build_match_terms(criteria: dict) -> list:
    if not criteria:
        return []
    terms = []
    for key in ("title", "keywords"):
        value = criteria.get(key)
        if not value or not isinstance(value, str):
            continue
        raw = value.strip().strip('"').strip("'")
        if raw.lower() in {"rh", "hr"}:
            terms.extend(HR_SYNONYMS)
        else:
            terms.extend(split_or_terms(value))
    normalized = []
    for term in terms:
        cleaned = normalize_term(term)
        if cleaned:
            normalized.append(cleaned)
    return list(dict.fromkeys(normalized))

def tag_results(items: list, criteria: dict) -> list:
    terms = build_match_terms(criteria)
    tagged = []
    for item in items:
        if not isinstance(item, dict):
            continue
        haystack = " ".join(
            str(item.get(field, "") or "")
            for field in ("headline", "name", "summary")
        ).lower()
        matched = [t for t in terms if t in haystack]
        tagged_item = item.copy()
        if terms:
            tagged_item["match_score"] = len(matched)
            tagged_item["is_relevant"] = bool(matched)
        else:
            tagged_item["match_score"] = 0
            tagged_item["is_relevant"] = True
        tagged.append(tagged_item)
    return tagged

def criteria_from_search_url(search_url: str) -> dict:
    if not search_url:
        return {}
    try:
        parsed = urlparse(search_url)
    except Exception:
        return {}
    params = parse_qs(parsed.query)
    keywords = params.get("keywords", [""])[0]
    criteria = {}
    if keywords:
        criteria["keywords"] = keywords
    return criteria

def extract_company_name(exp: dict) -> str | None:
    company = exp.get("company") or exp.get("company_name")
    if isinstance(company, dict):
        return company.get("name") or company.get("company") or company.get("public_identifier")
    return company

def extract_company_id(exp: dict) -> str | None:
    company_id = exp.get("company_id") or exp.get("companyId")
    if company_id:
        return company_id
    company = exp.get("company")
    if isinstance(company, dict):
        return company.get("id") or company.get("company_id") or company.get("public_identifier") or company.get("urn")
    return None

def extract_title(exp: dict) -> str | None:
    return exp.get("position") or exp.get("title") or exp.get("role")

def is_current_experience(exp: dict) -> bool:
    for key in ("end_date", "endDate", "ended_at", "ends_at", "end", "end_at", "end_year"):
        if exp.get(key):
            return False
    period = exp.get("time_period") or exp.get("date") or exp.get("dates")
    if isinstance(period, dict):
        end = period.get("end_date") or period.get("end") or period.get("to")
        if end:
            return False
    return True

def pick_current_experience(experiences: list) -> dict:
    for exp in experiences:
        if isinstance(exp, dict) and is_current_experience(exp):
            return exp
    for exp in experiences:
        if isinstance(exp, dict):
            return exp
    return {}

def extract_profile_fields(profile_data: dict) -> dict:
    if not isinstance(profile_data, dict):
        return {}
    bio = profile_data.get("summary") or profile_data.get("about") or profile_data.get("bio")
    location = profile_data.get("location")
    if isinstance(location, dict):
        location = location.get("name") or location.get("text")

    experiences = (
        profile_data.get("experiences")
        or profile_data.get("work_experience")
        or profile_data.get("experience")
    )
    companies = []
    current_title = None
    company_id = None
    if isinstance(experiences, list) and experiences:
        current_exp = pick_current_experience(experiences)
        current_title = extract_title(current_exp)
        company_id = extract_company_id(current_exp)
        for exp in experiences:
            if not isinstance(exp, dict):
                continue
            name = extract_company_name(exp)
            if name:
                companies.append(name)
    companies_text = ", ".join(dict.fromkeys([c for c in companies if c]))
    return {
        "bio": bio,
        "current_title": current_title,
        "companies": companies_text or None,
        "company_id": company_id,
        "profile_location": location,
    }

def build_enrichment_payload(unipile: UnipileClient, account_id: str, lead: dict) -> dict:
    identifier = lead.get("public_identifier") or lead.get("provider_id") or lead.get("id")
    if not identifier:
        return {}
    try:
        profile = unipile.get_profile_details(
            account_id,
            identifier,
            sections=["experience", "about"],
        )
    except Exception:
        profile = None
    fields = extract_profile_fields(profile or {})
    return fields

# --- SIDEBAR (CONFIG & LOGIN) ---
with st.sidebar:
    st.title("⚙️ Configurações")
    sb_url = st.text_input("Supabase URL", type="password", key="sb_url_input")
    sb_key = st.text_input("Supabase Key", type="password", key="sb_key_input")
    
    db = None
    if sb_url and sb_key:
        try:
            db = DBHandler(sb_url, sb_key)
            
            # --- CORREÇÃO DE SESSÃO ---
            # Se temos o token salvo, restauramos a sessão real
            if 'access_token' in st.session_state:
                db.set_session(
                    st.session_state['access_token'], 
                    st.session_state['refresh_token']
                )
                st.session_state['db_connected'] = True
            # --------------------------
            
        except Exception as e:
            st.error(f"Erro Conexão: {e}")

    # FORMULÁRIO DE LOGIN
    if db and not st.session_state.get('db_connected'):
        st.info("🔐 Login Supabase")
        with st.form("login_form"):
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Senha", type="password", key="login_pass")
            if st.form_submit_button("Conectar"):
                session = db.login(email, password)
                if session:
                    # Salva os tokens para não perder o login no reload
                    st.session_state['access_token'] = session.access_token
                    st.session_state['refresh_token'] = session.refresh_token
                    st.session_state['db_connected'] = True
                    st.success("Conectado!")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("Falha no login.")

    st.divider()

    # GERENCIAMENTO DE CONTAS LINKEDIN
    if st.session_state.get('db_connected') and db and db.user:
        st.subheader("👤 Conta LinkedIn")
        try:
            # Pega contas
            accs_resp = db.get_user_accounts()
            accs = accs_resp.data if accs_resp.data else []
            
            opts = {a['label']: a for a in accs}
            options_list = ["Selecione..."] + list(opts.keys()) + ["➕ Nova..."]
            
            sel = st.selectbox("Conta Ativa", options_list, key="acc_select")
            
            # ADICIONAR NOVA CONTA
            if sel == "➕ Nova...":
                with st.form("new_acc_form"):
                    st.caption("Adicionar Credenciais Unipile")
                    new_id = st.text_input("Account ID", key="new_acc_id")
                    new_key = st.text_input("API Key", key="new_api_key")
                    new_lbl = st.text_input("Nome (Label)", key="new_label")
                    
                    if st.form_submit_button("Salvar Conta"):
                        try:
                            db.save_unipile_account(new_id, new_key, new_lbl)
                            st.success("Conta salva com sucesso!")
                            time.sleep(1)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao salvar: {e}")
                            
            elif sel != "Selecione...":
                st.session_state['current_account'] = opts[sel]
                st.success(f"Conectado: {sel} ✅")
        except Exception as e:
            st.error(f"Erro ao carregar contas: {e}")

# --- RESTO DO APP ---
if not st.session_state.get('db_connected') or 'current_account' not in st.session_state:
    st.warning("👈 Configure o sistema na barra lateral.")
    st.stop()

unipile = UnipileClient("https://api26.unipile.com:15609", st.session_state['current_account']['api_key'])
acc_id = st.session_state['current_account']['account_id']
init_session_state()

st.title("🎯 LinkedIn List Builder Pro")
tab1, tab2 = st.tabs(["🔎 Construir Lista", "🚀 Campanhas"])

with tab1:
    search_tabs = st.tabs(["🔎 Classic", "💼 Sales Navigator"])
    with search_tabs[0]:
        with st.expander("🟦 LinkedIn Classic", expanded=True):
            classic_mode = st.radio("Modo de Busca", ["Filtros", "URL do LinkedIn"], horizontal=True, key="classic_search_mode")
            classic_url = None
            title = keywords = location = industry = company = school = None

            if classic_mode == "URL do LinkedIn":
                st.info("Cole uma URL completa do LinkedIn Search para usar os filtros originais.")
                classic_url = st.text_input(
                    "URL de busca do LinkedIn",
                    placeholder="https://www.linkedin.com/search/results/people/?keywords=RH",
                    key="classic_search_url",
                )
            else:
                st.info("💡 Dica: Use aspas para termos exatos. Ex: `\"Gerente de RH\"`")
                col1, col2, col3 = st.columns(3)
                with col1:
                    title = st.text_input("Cargo (Title)", placeholder="Ex: \"Gerente de RH\" OR \"Diretor\"", key="s_title")
                    location = st.text_input("Localização", placeholder="Ex: Brasil", key="s_loc")
                with col2:
                    keywords = st.text_input("Palavras-chave", placeholder="Ex: Tech, Startup", key="s_kw")
                    industry = st.text_input("Setor", placeholder="Ex: Human Resources", key="s_ind")
                with col3:
                    company = st.text_input("Empresa", placeholder="Ex: Google", key="s_comp")
                    school = st.text_input("Escola", key="s_school")

            classic_limit = st.radio("Resultados por página", [50], horizontal=True, key="classic_page_limit")
            st.caption("Classic: máximo de 50 por página.")

            if st.button("🔎 Buscar no LinkedIn (Classic)", key="btn_search_classic"):
                reset_search()
                criteria = {}
                res = None

                if classic_mode == "URL do LinkedIn":
                    if not classic_url:
                        st.error("Cole a URL completa da busca no LinkedIn.")
                    else:
                        criteria = apply_term_expansions(criteria_from_search_url(classic_url))
                        st.session_state['search_params'] = {
                            "mode": "url",
                            "search_url": classic_url,
                            "criteria": criteria,
                            "api_type": "classic",
                            "limit": classic_limit,
                        }
                        with st.spinner("Buscando..."):
                            res = unipile.search_from_url(acc_id, classic_url, limit=classic_limit)
                else:
                    if not title and not keywords and not company:
                        st.error("Preencha Cargo, Palavra-chave ou Empresa.")
                    else:
                        if title: criteria["title"] = title
                        if keywords: criteria["keywords"] = keywords
                        if location: criteria["location"] = location
                        if company: criteria["company"] = company
                        if industry: criteria["industry"] = industry
                        if school: criteria["school"] = school

                        criteria = apply_term_expansions(criteria)
                        st.session_state['search_params'] = {
                            "mode": "filters",
                            "criteria": criteria,
                            "api_type": "classic",
                            "limit": classic_limit,
                        }

                        with st.spinner("Buscando..."):
                            res = unipile.search_people(acc_id, criteria, limit=classic_limit, api_type="classic")

                handle_search_response(res, criteria)

    with search_tabs[1]:
        with st.expander("🟧 Sales Navigator", expanded=True):
            sales_mode = st.radio("Modo de Busca", ["Palavras-chave", "URL do Sales Navigator"], horizontal=True, key="sales_search_mode")
            sales_url = None
            sn_keywords = sn_company = None

            if sales_mode == "URL do Sales Navigator":
                st.info("Cole uma URL completa do Sales Navigator para usar filtros avançados.")
                sales_url = st.text_input(
                    "URL de busca do Sales Navigator",
                    placeholder="https://www.linkedin.com/sales/search/people?query=(keywords:rh)",
                    key="sales_search_url",
                )
            else:
                st.info("⚠️ Filtros avançados (localização, setor, senioridade) exigem IDs. Use a URL do Sales Navigator.")
                sn_keywords = st.text_input("Palavras-chave", placeholder="Ex: RH, Head of People", key="sn_keywords")
                sn_company = st.text_input("Empresa (nome)", placeholder="Ex: Google, Nubank", key="sn_company")

            sales_limit = st.radio("Resultados por página", [50, 100], horizontal=True, key="sales_page_limit")

            if st.button("🔎 Buscar no Sales Navigator", key="btn_search_sales"):
                reset_search()
                criteria = {}
                res = None

                if sales_mode == "URL do Sales Navigator":
                    if not sales_url:
                        st.error("Cole a URL completa do Sales Navigator.")
                    else:
                        st.session_state['search_params'] = {
                            "mode": "url",
                            "search_url": sales_url,
                            "criteria": criteria,
                            "api_type": "sales_navigator",
                            "limit": sales_limit,
                        }
                        with st.spinner("Buscando..."):
                            res = unipile.search_from_url(acc_id, sales_url, limit=sales_limit)
                else:
                    if not sn_keywords and not sn_company:
                        st.error("Preencha Palavras-chave ou Empresa.")
                    else:
                        if sn_keywords:
                            criteria["keywords"] = sn_keywords
                        if sn_company:
                            companies = [c.strip() for c in sn_company.split(",") if c.strip()]
                            if companies:
                                criteria["company"] = {"include": companies}

                        criteria = apply_term_expansions(criteria)
                        st.session_state['search_params'] = {
                            "mode": "filters",
                            "criteria": criteria,
                            "api_type": "sales_navigator",
                            "limit": sales_limit,
                        }

                        with st.spinner("Buscando..."):
                            res = unipile.search_people(
                                acc_id,
                                criteria,
                                limit=sales_limit,
                                api_type="sales_navigator",
                            )

                handle_search_response(res, criteria)

    if st.session_state['search_results']:
        st.divider()
        page_limit = st.session_state.get('search_params', {}).get('limit', 50)
        try:
            page_limit = int(page_limit)
        except (TypeError, ValueError):
            page_limit = 50
        if page_limit not in (50, 100):
            page_limit = 50
        c_btn, c_bulk, c_info = st.columns([1, 1.6, 3.4])
        with c_btn:
            if st.session_state['next_cursor']:
                if st.button(f"🔄 Buscar +{page_limit}", key="btn_more"):
                    with st.spinner("Carregando..."):
                        p = st.session_state['search_params']
                        # Tentativa simples de carregar mais
                        mode = p.get("mode", "filters")
                        criteria = p.get("criteria", {})
                        if mode == "url":
                            res = unipile.search_from_url(
                                acc_id,
                                p.get("search_url"),
                                limit=page_limit,
                                cursor=st.session_state['next_cursor'],
                            )
                        else:
                            res = unipile.search_people(
                                acc_id,
                                criteria,
                                limit=page_limit,
                                cursor=st.session_state['next_cursor'],
                                api_type=p.get("api_type", "classic"),
                            )
                        if res and 'items' in res:
                            valid = clean_results(res['items'], criteria)
                            valid, st.session_state['seen_lead_keys'] = dedupe_results(
                                valid,
                                st.session_state['seen_lead_keys'],
                            )
                            if not valid:
                                st.warning("Sem novos resultados nessa página.")
                                st.session_state['next_cursor'] = None
                            else:
                                st.session_state['search_results'].extend(valid)
                                new_cursor = res.get('paging', {}).get('cursor')
                                if new_cursor == st.session_state['last_cursor']:
                                    st.warning("Cursor repetido: encerrando paginação.")
                                    st.session_state['next_cursor'] = None
                                else:
                                    st.session_state['next_cursor'] = new_cursor
                                    st.session_state['last_cursor'] = new_cursor
                                st.rerun()
                        else:
                            st.session_state['next_cursor'] = None
        with c_bulk:
            if st.session_state['next_cursor']:
                current_count = len(st.session_state['search_results'])
                default_target = min(1000, max(page_limit * 2, current_count + page_limit))
                max_leads = st.number_input(
                    "Max leads",
                    min_value=page_limit,
                    max_value=1000,
                    value=default_target,
                    step=page_limit,
                    key="max_leads",
                )
                delay = st.number_input(
                    "Delay (s)",
                    min_value=0.0,
                    max_value=5.0,
                    value=0.5,
                    step=0.5,
                    key="page_delay",
                )
                if st.button("⏩ Buscar todas páginas", key="btn_more_all"):
                    target = int(max_leads)
                    if target <= current_count:
                        st.info("Já temos essa quantidade de leads.")
                    else:
                        bar = st.progress(0)
                        status = st.empty()
                        while st.session_state['next_cursor'] and len(st.session_state['search_results']) < target:
                            p = st.session_state['search_params']
                            mode = p.get("mode", "filters")
                            criteria = p.get("criteria", {})
                            if mode == "url":
                                res = unipile.search_from_url(
                                    acc_id,
                                    p.get("search_url"),
                                    limit=page_limit,
                                    cursor=st.session_state['next_cursor'],
                                )
                            else:
                                res = unipile.search_people(
                                    acc_id,
                                    criteria,
                                    limit=page_limit,
                                    cursor=st.session_state['next_cursor'],
                                    api_type=p.get("api_type", "classic"),
                                )
                            if not res or 'items' not in res:
                                break
                            valid = clean_results(res['items'], criteria)
                            valid, st.session_state['seen_lead_keys'] = dedupe_results(
                                valid,
                                st.session_state['seen_lead_keys'],
                            )
                            if not valid:
                                st.warning("Sem novos resultados nessa página.")
                                st.session_state['next_cursor'] = None
                                break
                            st.session_state['search_results'].extend(valid)
                            new_cursor = res.get('paging', {}).get('cursor')
                            if new_cursor == st.session_state['last_cursor']:
                                st.warning("Cursor repetido: encerrando paginação.")
                                st.session_state['next_cursor'] = None
                                break
                            st.session_state['next_cursor'] = new_cursor
                            st.session_state['last_cursor'] = new_cursor
                            status.text(f"{len(st.session_state['search_results'])}/{target} leads")
                            bar.progress(min(1.0, len(st.session_state['search_results']) / target))
                            if delay:
                                time.sleep(delay)
                        st.success(f"Concluído: {len(st.session_state['search_results'])} leads.")
                        st.rerun()
        with c_info:
            st.markdown(f"### Lista Atual: **{len(st.session_state['search_results'])}** leads")
            relevant_count = sum(
                1 for item in st.session_state['search_results']
                if item.get("is_relevant", True)
            )
            st.caption(f"Relevantes pelo filtro: {relevant_count}")

        df = pd.DataFrame(st.session_state['search_results'])
        profile_loc = df["profile_location"] if "profile_location" in df.columns else None
        base_loc = df["location"] if "location" in df.columns else None
        if profile_loc is not None and base_loc is not None:
            df["localizacao"] = profile_loc.fillna(base_loc)
        elif profile_loc is not None:
            df["localizacao"] = profile_loc
        elif base_loc is not None:
            df["localizacao"] = base_loc
        default_select = df["is_relevant"] if "is_relevant" in df.columns else True
        df.insert(0, "Selecionar", default_select)
        cols = [
            "Selecionar",
            "match_score",
            "distance",
            "name",
            "headline",
            "localizacao",
            "current_title",
            "companies",
            "company_id",
            "bio",
            "public_identifier",
        ]
        df_show = df[[c for c in cols if c in df.columns]]
        
        column_config = {
            "Selecionar": st.column_config.CheckboxColumn(required=True),
            "match_score": st.column_config.NumberColumn("Score", help="Quantos termos do filtro aparecem no headline/nome"),
            "distance": st.column_config.TextColumn("Grau"),
            "localizacao": st.column_config.TextColumn("Localização"),
            "current_title": st.column_config.TextColumn("Cargo"),
            "companies": st.column_config.TextColumn("Empresas"),
            "company_id": st.column_config.TextColumn("Empresa ID"),
            "bio": st.column_config.TextColumn("Bio"),
        }
        edited = st.data_editor(df_show, hide_index=True, column_config=column_config, height=400, key="editor_leads")
        
        sel_idx = edited[edited["Selecionar"] == True].index
        sel_objs = [st.session_state['search_results'][i] for i in sel_idx]

        st.divider()
        with st.container():
            c_enrich_btn, c_enrich_info = st.columns([1, 3])
            with c_enrich_btn:
                if st.button("✨ Enriquecer Selecionados", key="btn_enrich_inline"):
                    if not sel_objs:
                        st.error("Selecione leads para enriquecer.")
                    else:
                        bar = st.progress(0)
                        st_text = st.empty()
                        for i, lead in enumerate(sel_objs):
                            st_text.text(f"Enriquecendo {lead.get('name')}...")
                            fields = build_enrichment_payload(unipile, acc_id, lead)
                            if fields:
                                lead.update(fields)
                            bar.progress((i + 1) / len(sel_objs))
                        st.success("Enriquecimento concluído.")
                        st.rerun()
            with c_enrich_info:
                st.caption("Preenche Bio, Cargo, Empresas, Empresa ID e Localização antes de salvar.")

        st.divider()
        with st.container():
            st.markdown("#### 💾 Salvar Selecionados")
            c1, c2 = st.columns([2, 1])
            with c1:
                cp_name = st.text_input("Nome Campanha", f"Lista {len(sel_objs)} Leads", key="cp_name")
                msg_t = st.text_area("Template (opcional)", "", key="msg_t")
            with c2:
                st.info("Etapa 1: salvar lista básica. Enriquecimento vem depois.")
            
            if st.button(f"🚀 Importar", key="btn_imp"):
                if not sel_objs: st.error("Selecione leads!")
                else:
                    bar = st.progress(0)
                    st_text = st.empty()
                    try:
                        c_resp = db.create_campaign(cp_name, msg_t, st.session_state['current_account']['id'])
                        if c_resp.data:
                            cid = c_resp.data[0]['id']
                            final = []
                            for i, l in enumerate(sel_objs):
                                pl = l.copy()
                                st_text.text(f"Salvando {l.get('name')}...")
                                final.append(pl)
                                bar.progress((i+1)/len(sel_objs))
                            
                            db.save_leads(cid, final)
                            st.success("Salvo com sucesso!")
                    except Exception as e:
                        st.error(f"Erro: {e}")

with tab2:
    st.header("✨ Enriquecimento")
    try:
        camps = db.supabase.table("campaigns").select("*").eq("user_id", db.user.id).order('created_at', desc=True).execute().data
        if camps:
            sel = st.selectbox("Lista/Campanha", [c['name'] for c in camps])
            curr = next(c for c in camps if c['name'] == sel)
            leads = db.supabase.table("leads").select("*").eq("campaign_id", curr['id']).execute().data
            st.metric("Total", len(leads))
            if leads:
                df = pd.DataFrame(leads)
                if "bio" in df.columns:
                    default_select = df["bio"].isna() | (df["bio"] == "")
                else:
                    default_select = [True] * len(df)
                df.insert(0, "Selecionar", default_select)
                profile_loc = df["profile_location"] if "profile_location" in df.columns else None
                base_loc = df["location"] if "location" in df.columns else None
                if profile_loc is not None and base_loc is not None:
                    df["localizacao"] = profile_loc.fillna(base_loc)
                elif profile_loc is not None:
                    df["localizacao"] = profile_loc
                elif base_loc is not None:
                    df["localizacao"] = base_loc
                cols = [
                    "Selecionar",
                    "full_name",
                    "headline",
                    "localizacao",
                    "current_title",
                    "companies",
                    "company_id",
                    "bio",
                    "linkedin_public_id",
                ]
                df_show = df[[c for c in cols if c in df.columns]]
                column_config = {
                    "Selecionar": st.column_config.CheckboxColumn(required=True),
                    "full_name": st.column_config.TextColumn("Nome"),
                    "headline": st.column_config.TextColumn("Headline"),
                    "localizacao": st.column_config.TextColumn("Localização"),
                    "current_title": st.column_config.TextColumn("Cargo"),
                    "companies": st.column_config.TextColumn("Empresas"),
                    "company_id": st.column_config.TextColumn("Empresa ID"),
                    "bio": st.column_config.TextColumn("Bio"),
                }
                edited = st.data_editor(df_show, hide_index=True, column_config=column_config, height=400, key="editor_enrich")
                sel_idx = edited[edited["Selecionar"] == True].index
                sel_leads = [leads[i] for i in sel_idx]

                if st.button("✨ Enriquecer Selecionados", key="btn_enrich"):
                    if not sel_leads:
                        st.error("Selecione leads para enriquecer.")
                    else:
                        bar = st.progress(0)
                        st_text = st.empty()
                        for i, lead in enumerate(sel_leads):
                            st_text.text(f"Enriquecendo {lead.get('full_name')}...")
                            fields = build_enrichment_payload(unipile, acc_id, lead)
                            try:
                                db.update_lead_enrichment(lead["id"], fields)
                            except Exception as e:
                                st.error(f"Erro ao enriquecer {lead.get('full_name')}: {e}")
                            bar.progress((i + 1) / len(sel_leads))
                        st.success("Enriquecimento concluído.")
                        st.rerun()
            else:
                st.info("Nenhum lead salvo nesta lista ainda.")
    except Exception as e:
        st.error(f"Erro ao carregar campanhas: {e}")
