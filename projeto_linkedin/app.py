import json
import re
from datetime import datetime
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
    if 'total_count' not in st.session_state: st.session_state['total_count'] = None
    if 'url_base' not in st.session_state: st.session_state['url_base'] = None
    if 'url_page' not in st.session_state: st.session_state['url_page'] = None
    if 'last_search_debug' not in st.session_state: st.session_state['last_search_debug'] = None
    if 'api_logs' not in st.session_state: st.session_state['api_logs'] = []
    if 'last_request' not in st.session_state: st.session_state['last_request'] = None
    if 'last_response' not in st.session_state: st.session_state['last_response'] = None
    if 'last_response_full' not in st.session_state: st.session_state['last_response_full'] = None

def reset_search():
    st.session_state['search_results'] = []
    st.session_state['next_cursor'] = None
    st.session_state['seen_lead_keys'] = set()
    st.session_state['last_cursor'] = None
    st.session_state['total_count'] = None
    st.session_state['url_base'] = None
    st.session_state['url_page'] = None
    st.session_state['last_search_debug'] = None
    st.session_state['last_request'] = None
    st.session_state['last_response'] = None
    st.session_state['last_response_full'] = None

def log_api_event(event_type: str, payload: dict) -> None:
    logs = st.session_state.get('api_logs', [])
    entry = {
        "ts": datetime.now().isoformat(timespec="seconds"),
        "event": event_type,
    }
    entry.update(payload or {})
    logs.append(entry)
    st.session_state['api_logs'] = logs[-200:]

def log_request(action: str, payload: dict) -> None:
    log_api_event("request", {"action": action, **(payload or {})})
    st.session_state['last_request'] = payload

def compact_response(res: dict | None, max_items: int = 3) -> dict | None:
    if not res or "items" not in res:
        return res
    items = res.get("items") or []
    if len(items) <= max_items:
        return res
    compact = dict(res)
    compact["items"] = items[:max_items]
    compact["_items_truncated"] = len(items)
    return compact

def log_response(action: str, res: dict | None, status: int | None) -> None:
    items_count = len(res.get("items", []) or []) if res else 0
    paging = res.get("paging") if res else None
    cursor = res.get("cursor") if res else None
    st.session_state['last_response_full'] = res
    st.session_state['last_response'] = compact_response(res)
    log_api_event(
        "response",
        {
            "action": action,
            "status": status,
            "items_count": items_count,
            "paging": paging,
            "cursor": cursor,
        },
    )

def log_error(action: str, error: Exception) -> None:
    log_api_event("error", {"action": action, "error": str(error)})

def build_checkpoint_payload() -> dict:
    return {
        "version": 1,
        "saved_at": datetime.now().isoformat(timespec="seconds"),
        "search_params": st.session_state.get("search_params") or {},
        "next_cursor": st.session_state.get("next_cursor"),
        "last_cursor": st.session_state.get("last_cursor"),
        "total_count": st.session_state.get("total_count"),
        "url_base": st.session_state.get("url_base"),
        "url_page": st.session_state.get("url_page"),
        "last_search_debug": st.session_state.get("last_search_debug"),
        "results": st.session_state.get("search_results") or [],
        "seen_lead_keys": list(st.session_state.get("seen_lead_keys") or []),
    }

def apply_checkpoint_payload(payload: dict) -> None:
    if not isinstance(payload, dict):
        return
    st.session_state['search_params'] = payload.get("search_params") or {}
    st.session_state['search_results'] = payload.get("results") or []
    seen_keys = payload.get("seen_lead_keys") or []
    if not seen_keys and st.session_state['search_results']:
        seen_keys = [lead_key(item) for item in st.session_state['search_results'] if lead_key(item)]
    st.session_state['seen_lead_keys'] = set(seen_keys)
    cursor = payload.get("next_cursor") or payload.get("cursor")
    st.session_state['next_cursor'] = cursor
    st.session_state['last_cursor'] = payload.get("last_cursor") or cursor
    st.session_state['total_count'] = payload.get("total_count")
    st.session_state['url_base'] = payload.get("url_base")
    st.session_state['url_page'] = payload.get("url_page")
    st.session_state['last_search_debug'] = payload.get("last_search_debug")

def handle_search_response(res, criteria):
    if res and 'items' in res:
        valid = clean_results(res['items'], criteria)
        valid, st.session_state['seen_lead_keys'] = dedupe_results(
            valid,
            st.session_state['seen_lead_keys'],
        )
        st.session_state['search_results'] = valid
        paging = res.get('paging', {})
        st.session_state['last_search_debug'] = {
            "paging": paging,
            "items_count": len(res.get("items", []) or []),
            "config": res.get("config"),
        }
        config_url = (res.get("config") or {}).get("url")
        if config_url:
            st.session_state['url_base'] = strip_page_param(config_url)
            st.session_state['url_page'] = get_page_param(config_url)
        st.session_state['next_cursor'] = res.get('cursor') or paging.get('cursor')
        st.session_state['last_cursor'] = st.session_state['next_cursor']
        st.session_state['total_count'] = paging.get('total_count')
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

def parse_csv_list(value: str) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]

def build_include(values: list[str]) -> dict | None:
    if not values:
        return None
    return {"include": values}

def public_identifier_from_url(profile_url: str) -> str | None:
    if not profile_url:
        return None
    match = re.search(r"/in/([^/?#]+)", profile_url)
    if match:
        return match.group(1)
    return None

def resolve_profile_identifier(row: dict) -> str | None:
    for key in ("public_identifier", "linkedin_public_id", "provider_id", "id"):
        value = row.get(key)
        if value:
            return str(value)
    profile_url = row.get("profile_url") or row.get("public_profile_url")
    return public_identifier_from_url(profile_url) if profile_url else None

def strip_page_param(search_url: str) -> str:
    if not search_url:
        return search_url
    try:
        parsed = urlparse(search_url)
    except Exception:
        return search_url
    query = re.sub(r'(^|&)(page=\d+)', '', parsed.query).strip('&')
    return parsed._replace(query=query).geturl()

def get_page_param(search_url: str) -> int:
    if not search_url:
        return 1
    try:
        parsed = urlparse(search_url)
    except Exception:
        return 1
    match = re.search(r'(?:^|&)page=(\d+)', parsed.query)
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            return 1
    return 1

def set_page_param(search_url: str, page: int) -> str:
    if not search_url:
        return search_url
    try:
        parsed = urlparse(search_url)
    except Exception:
        return search_url
    query = re.sub(r'(^|&)(page=\d+)', '', parsed.query).strip('&')
    prefix = f"page={page}"
    query = f"{prefix}&{query}" if query else prefix
    return parsed._replace(query=query).geturl()

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

def first_name_from(value: str) -> str:
    if not value:
        return ""
    parts = str(value).strip().split()
    return parts[0] if parts else ""

def build_message_context(lead: dict) -> dict:
    full_name = lead.get("full_name") or lead.get("name") or ""
    headline = lead.get("headline") or ""
    profile_location = lead.get("profile_location") or ""
    location = lead.get("location") or profile_location
    current_title = lead.get("current_title") or ""
    companies = lead.get("companies") or ""
    if isinstance(companies, list):
        companies = ", ".join([c for c in companies if c])
    companies = companies or ""
    company = ""
    if isinstance(companies, str) and companies:
        company = companies.split(",")[0].strip()

    public_identifier = lead.get("linkedin_public_id") or lead.get("public_identifier") or ""
    provider_id = lead.get("provider_id") or lead.get("id") or ""
    profile_url = ""
    if public_identifier:
        profile_url = f"https://www.linkedin.com/in/{public_identifier}"

    context = {
        "first_name": first_name_from(full_name),
        "full_name": full_name,
        "headline": headline,
        "location": location or "",
        "profile_location": profile_location or "",
        "current_title": current_title or "",
        "companies": companies,
        "company": company,
        "company_id": lead.get("company_id") or "",
        "bio": lead.get("bio") or "",
        "public_identifier": public_identifier,
        "provider_id": provider_id,
        "profile_url": profile_url,
    }
    for key, value in lead.items():
        if key not in context:
            context[key] = value if value is not None else ""
    return context

class SafeFormatDict(dict):
    def __missing__(self, key: str) -> str:
        return ""

def render_message(template: str, lead: dict) -> str:
    context = build_message_context(lead)
    try:
        return template.format_map(SafeFormatDict(context))
    except Exception:
        return template

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
tab1, tab2, tab3, tab4 = st.tabs(
    ["🔎 Lista (Sales Navigator)", "✨ Enriquecimento", "📨 Mensagens", "📦 Payloads"]
)

with tab1:
    st.header("🔎 Lista (Sales Navigator)")
    sales_mode = st.radio(
        "Modo de Busca",
        ["URL do Sales Navigator", "Parametros"],
        horizontal=True,
        key="sales_search_mode",
    )
    with st.expander("♻️ Retomar busca (checkpoint)", expanded=False):
        st.caption("Use um checkpoint para continuar no dia seguinte. O cursor pode expirar.")
        checkpoint_upload = st.file_uploader(
            "Upload checkpoint",
            type=["json"],
            key="checkpoint_upload",
        )
        if st.button("Carregar checkpoint", key="btn_load_checkpoint"):
            if not checkpoint_upload:
                st.error("Envie um arquivo de checkpoint.")
            else:
                try:
                    payload = json.load(checkpoint_upload)
                    apply_checkpoint_payload(payload)
                    st.success("Checkpoint carregado.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao carregar checkpoint: {e}")

    sales_url = None
    criteria: dict = {}
    if sales_mode == "URL do Sales Navigator":
        st.info("Cole a URL completa do Sales Navigator para usar os filtros originais.")
        sales_url = st.text_input(
            "URL de busca do Sales Navigator",
            placeholder="https://www.linkedin.com/sales/search/people?query=(keywords:rh)",
            key="sales_search_url",
        )
    else:
        st.info("Use IDs conforme o search.md. Separe multiplos IDs por virgula.")
        col1, col2, col3 = st.columns(3)
        with col1:
            keywords = st.text_input("Palavras-chave", key="sn_keywords")
            location_ids = st.text_input("REGION IDs (include)", key="sn_region_ids")
            industry_ids = st.text_input("SALES_INDUSTRY IDs (include)", key="sn_industry_ids")
        with col2:
            company_vals = st.text_input("Company (IDs ou nomes)", key="sn_company_vals")
            role_vals = st.text_input("Job title (IDs ou texto)", key="sn_role_vals")
            function_ids = st.text_input("Department IDs (include)", key="sn_function_ids")
        with col3:
            seniority_vals = st.multiselect(
                "Seniority (include)",
                [
                    "owner/partner",
                    "cxo",
                    "vice_president",
                    "director",
                    "experienced_manager",
                    "entry_level_manager",
                    "strategic",
                    "senior",
                    "entry_level",
                    "in_training",
                ],
                key="sn_seniority",
            )
            network_vals = st.multiselect(
                "Network distance",
                [1, 2, 3, "GROUP"],
                key="sn_network",
            )
            saved_search_id = st.text_input(
                "Saved search ID (opcional)",
                help="Se informado, substitui todos os outros parametros.",
                key="sn_saved_search_id",
            )

        with st.expander("🔎 Buscar IDs de parametros (opcional)", expanded=False):
            param_type = st.selectbox(
                "Tipo de parametro",
                [
                    "REGION",
                    "SALES_INDUSTRY",
                    "COMPANY",
                    "JOB_TITLE",
                    "DEPARTMENT",
                    "SCHOOL",
                    "GROUPS",
                    "PERSONA",
                    "ACCOUNT_LISTS",
                    "LEAD_LISTS",
                    "POSTAL_CODE",
                ],
                key="param_type_select",
            )
            param_query = st.text_input("Busca por palavra-chave", key="param_query")
            if st.button("Listar parametros", key="btn_list_params"):
                try:
                    log_request(
                        "list_search_parameters",
                        {
                            "endpoint": "/api/v1/linkedin/search/parameters",
                            "params": {
                                "account_id": acc_id,
                                "type": param_type,
                                "service": "SALES_NAVIGATOR",
                                "keywords": param_query,
                            },
                        },
                    )
                    res_params = unipile.list_search_parameters(
                        acc_id,
                        parameter_type=param_type,
                        service="SALES_NAVIGATOR",
                        keywords=param_query,
                        limit=50,
                    )
                    log_response("list_search_parameters", res_params, unipile.last_status)
                    items = (res_params or {}).get("items", []) or []
                    if items:
                        st.json(items)
                    else:
                        st.info("Nenhum parametro encontrado.")
                except Exception as e:
                    log_error("list_search_parameters", e)
                    st.error(f"Erro ao listar parametros: {e}")

    sales_limit = st.radio("Resultados por página", [50, 100], horizontal=True, key="sales_page_limit")

    if st.button("🔎 Buscar no Sales Navigator", key="btn_search_sales"):
        reset_search()
        res = None

        if sales_mode == "URL do Sales Navigator":
            if not sales_url:
                st.error("Cole a URL completa do Sales Navigator.")
            else:
                cleaned_url = strip_page_param(sales_url)
                st.session_state['url_base'] = cleaned_url
                st.session_state['url_page'] = get_page_param(cleaned_url)
                st.session_state['search_params'] = {
                    "mode": "url",
                    "search_url": cleaned_url,
                    "criteria": {},
                    "api_type": "sales_navigator",
                    "limit": sales_limit,
                }
                with st.spinner("Buscando..."):
                    log_request(
                        "search_from_url",
                        {
                            "endpoint": "/api/v1/linkedin/search",
                            "params": {"account_id": acc_id, "limit": sales_limit},
                            "body": {"url": cleaned_url},
                        },
                    )
                    res = unipile.search_from_url(acc_id, cleaned_url, limit=sales_limit)
                    log_response("search_from_url", res, unipile.last_status)
        else:
            if saved_search_id:
                criteria = {"saved_search_id": saved_search_id.strip()}
            else:
                if keywords:
                    criteria["keywords"] = keywords
                location_vals = build_include(parse_csv_list(location_ids))
                if location_vals:
                    criteria["location"] = location_vals
                industry_vals = build_include(parse_csv_list(industry_ids))
                if industry_vals:
                    criteria["industry"] = industry_vals
                company_vals_list = parse_csv_list(company_vals)
                if company_vals_list:
                    criteria["company"] = {"include": company_vals_list}
                role_vals_list = parse_csv_list(role_vals)
                if role_vals_list:
                    criteria["role"] = {"include": role_vals_list}
                function_vals = build_include(parse_csv_list(function_ids))
                if function_vals:
                    criteria["function"] = function_vals
                if seniority_vals:
                    criteria["seniority"] = {"include": seniority_vals}
                if network_vals:
                    criteria["network_distance"] = network_vals

            if not criteria:
                st.error("Preencha ao menos um parametro.")
            else:
                st.session_state['search_params'] = {
                    "mode": "filters",
                    "criteria": criteria,
                    "api_type": "sales_navigator",
                    "limit": sales_limit,
                }
                with st.spinner("Buscando..."):
                    log_request(
                        "search_people",
                        {
                            "endpoint": "/api/v1/linkedin/search",
                            "params": {"account_id": acc_id, "limit": sales_limit},
                            "body": {
                                "api": "sales_navigator",
                                "category": "people",
                                **criteria,
                            },
                        },
                    )
                    res = unipile.search_people(
                        acc_id,
                        criteria,
                        limit=sales_limit,
                        api_type="sales_navigator",
                    )
                    log_response("search_people", res, unipile.last_status)

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
            p = st.session_state.get('search_params', {})
            mode = p.get("mode", "filters")
            criteria = p.get("criteria", {})
            has_cursor = st.session_state.get('next_cursor') is not None
            has_url_paging = bool(st.session_state.get('url_base'))
            if has_cursor or has_url_paging:
                if st.button(f"🔄 Buscar +{page_limit}", key="btn_more"):
                    with st.spinner("Carregando..."):
                        if has_cursor:
                            if mode == "url":
                                log_request(
                                    "search_from_url",
                                    {
                                        "endpoint": "/api/v1/linkedin/search",
                                        "params": {
                                            "account_id": acc_id,
                                            "limit": page_limit,
                                            "cursor": st.session_state['next_cursor'],
                                        },
                                        "body": {"url": p.get("search_url")},
                                    },
                                )
                                res = unipile.search_from_url(
                                    acc_id,
                                    p.get("search_url"),
                                    limit=page_limit,
                                    cursor=st.session_state['next_cursor'],
                                )
                                log_response("search_from_url", res, unipile.last_status)
                            else:
                                log_request(
                                    "search_people",
                                    {
                                        "endpoint": "/api/v1/linkedin/search",
                                        "params": {
                                            "account_id": acc_id,
                                            "limit": page_limit,
                                            "cursor": st.session_state['next_cursor'],
                                        },
                                        "body": {
                                            "api": p.get("api_type", "sales_navigator"),
                                            "category": "people",
                                            **criteria,
                                        },
                                    },
                                )
                                res = unipile.search_people(
                                    acc_id,
                                    criteria,
                                    limit=page_limit,
                                    cursor=st.session_state['next_cursor'],
                                    api_type=p.get("api_type", "classic"),
                                )
                                log_response("search_people", res, unipile.last_status)
                        else:
                            current_page = st.session_state.get('url_page') or 1
                            next_page = current_page + 1
                            next_url = set_page_param(st.session_state['url_base'], next_page)
                            log_request(
                                "search_from_url",
                                {
                                    "endpoint": "/api/v1/linkedin/search",
                                    "params": {
                                        "account_id": acc_id,
                                        "limit": page_limit,
                                    },
                                    "body": {"url": next_url},
                                },
                            )
                            res = unipile.search_from_url(
                                acc_id,
                                next_url,
                                limit=page_limit,
                            )
                            log_response("search_from_url", res, unipile.last_status)
                            st.session_state['url_page'] = next_page
                        if res and 'items' in res:
                            valid = clean_results(res['items'], criteria)
                            valid, st.session_state['seen_lead_keys'] = dedupe_results(
                                valid,
                                st.session_state['seen_lead_keys'],
                            )
                            if valid:
                                st.session_state['search_results'].extend(valid)
                            else:
                                st.warning("Sem novos resultados nessa pagina.")
                            paging = res.get('paging', {})
                            st.session_state['last_search_debug'] = {
                                "paging": paging,
                                "items_count": len(res.get("items", []) or []),
                                "config": res.get("config"),
                            }
                            config_url = (res.get("config") or {}).get("url")
                            if config_url:
                                st.session_state['url_base'] = strip_page_param(config_url)
                                st.session_state['url_page'] = get_page_param(config_url)
                            total_count = paging.get('total_count')
                            if total_count is not None:
                                st.session_state['total_count'] = total_count
                            if has_cursor:
                                new_cursor = res.get('cursor') or paging.get('cursor')
                                if not new_cursor:
                                    st.session_state['next_cursor'] = None
                                elif new_cursor == st.session_state['last_cursor']:
                                    st.warning("Cursor repetido: encerrando paginação.")
                                    st.session_state['next_cursor'] = None
                                else:
                                    st.session_state['next_cursor'] = new_cursor
                                    st.session_state['last_cursor'] = new_cursor
                            if valid:
                                st.rerun()
                        else:
                            st.session_state['next_cursor'] = None
        with c_bulk:
            p = st.session_state.get('search_params', {})
            mode = p.get("mode", "filters")
            has_cursor = st.session_state.get('next_cursor') is not None
            has_url_paging = bool(st.session_state.get('url_base'))
            if has_cursor or has_url_paging:
                current_count = len(st.session_state['search_results'])
                total_count = st.session_state.get('total_count')
                max_total = max(1000, total_count or 10000)
                default_target = min(max_total, max(page_limit * 2, current_count + page_limit))
                if total_count is not None and current_count >= total_count:
                    default_target = current_count
                daily_cap = st.number_input(
                    "Limite diario (leads)",
                    min_value=100,
                    max_value=2500,
                    value=2500,
                    step=100,
                    key="daily_cap",
                )
                fetch_all = st.checkbox(
                    "Buscar ate o fim",
                    value=False,
                    key="fetch_all_pages",
                )
                max_leads = st.number_input(
                    "Max leads",
                    min_value=page_limit,
                    max_value=max_total,
                    value=default_target,
                    step=page_limit,
                    key="max_leads",
                    disabled=fetch_all,
                )
                delay = st.number_input(
                    "Delay (s)",
                    min_value=0.0,
                    max_value=5.0,
                    value=0.5,
                    step=0.5,
                    key="page_delay",
                )
                def run_bulk_fetch(target: int | None, use_fetch_all: bool) -> None:
                    if target is not None and target <= current_count:
                        st.info("Já temos essa quantidade de leads.")
                        return
                    bar = st.progress(0)
                    status = st.empty()
                    seen_cursors = set()
                    if st.session_state['last_cursor']:
                        seen_cursors.add(st.session_state['last_cursor'])
                    no_new_pages = 0
                    use_cursor = st.session_state.get('next_cursor') is not None
                    url_base = st.session_state.get('url_base')
                    max_pages = None
                    if not use_cursor and url_base:
                        items_per_page = None
                        last_debug = st.session_state.get("last_search_debug") or {}
                        try:
                            items_per_page = int(last_debug.get("items_count") or 0)
                        except (TypeError, ValueError):
                            items_per_page = None
                        items_per_page = items_per_page or page_limit
                        if total_count:
                            max_pages = (total_count + items_per_page - 1) // items_per_page + 2
                        else:
                            max_pages = 200

                    while True:
                        if target is not None and len(st.session_state['search_results']) >= target:
                            break
                        if use_cursor:
                            if not st.session_state['next_cursor']:
                                break
                            criteria = p.get("criteria", {})
                            try:
                                if mode == "url":
                                    log_request(
                                        "search_from_url",
                                        {
                                            "endpoint": "/api/v1/linkedin/search",
                                            "params": {
                                                "account_id": acc_id,
                                                "limit": page_limit,
                                                "cursor": st.session_state['next_cursor'],
                                            },
                                            "body": {"url": p.get("search_url")},
                                        },
                                    )
                                    res = unipile.search_from_url(
                                        acc_id,
                                        p.get("search_url"),
                                        limit=page_limit,
                                        cursor=st.session_state['next_cursor'],
                                    )
                                    log_response("search_from_url", res, unipile.last_status)
                                else:
                                    log_request(
                                        "search_people",
                                        {
                                            "endpoint": "/api/v1/linkedin/search",
                                            "params": {
                                                "account_id": acc_id,
                                                "limit": page_limit,
                                                "cursor": st.session_state['next_cursor'],
                                            },
                                            "body": {
                                                "api": p.get("api_type", "sales_navigator"),
                                                "category": "people",
                                                **criteria,
                                            },
                                        },
                                    )
                                    res = unipile.search_people(
                                        acc_id,
                                        criteria,
                                        limit=page_limit,
                                        cursor=st.session_state['next_cursor'],
                                        api_type=p.get("api_type", "classic"),
                                    )
                                    log_response("search_people", res, unipile.last_status)
                            except Exception as e:
                                log_error("bulk_cursor", e)
                                st.error(f"Erro ao buscar pagina: {e}")
                                break
                        else:
                            if not url_base:
                                break
                            current_page = st.session_state.get('url_page') or 1
                            if max_pages and current_page >= max_pages:
                                st.warning("Limite de paginas atingido.")
                                break
                            next_page = current_page + 1
                            next_url = set_page_param(url_base, next_page)
                            try:
                                log_request(
                                    "search_from_url",
                                    {
                                        "endpoint": "/api/v1/linkedin/search",
                                        "params": {
                                            "account_id": acc_id,
                                            "limit": page_limit,
                                        },
                                        "body": {"url": next_url},
                                    },
                                )
                                res = unipile.search_from_url(
                                    acc_id,
                                    next_url,
                                    limit=page_limit,
                                )
                                log_response("search_from_url", res, unipile.last_status)
                            except Exception as e:
                                log_error("bulk_page", e)
                                st.error(f"Erro ao buscar pagina: {e}")
                                break
                            st.session_state['url_page'] = next_page

                        if not res or 'items' not in res:
                            break
                        paging = res.get('paging', {})
                        st.session_state['last_search_debug'] = {
                            "paging": paging,
                            "items_count": len(res.get("items", []) or []),
                            "config": res.get("config"),
                        }
                        config_url = (res.get("config") or {}).get("url")
                        if config_url:
                            st.session_state['url_base'] = strip_page_param(config_url)
                            st.session_state['url_page'] = get_page_param(config_url)
                        paging_total = paging.get('total_count')
                        if paging_total is not None:
                            st.session_state['total_count'] = paging_total
                            if use_fetch_all:
                                target = paging_total
                        criteria = p.get("criteria", {})
                        valid = clean_results(res['items'], criteria)
                        valid, st.session_state['seen_lead_keys'] = dedupe_results(
                            valid,
                            st.session_state['seen_lead_keys'],
                        )
                        if valid:
                            st.session_state['search_results'].extend(valid)
                            no_new_pages = 0
                        else:
                            no_new_pages += 1
                            status.text("Sem novos resultados nesta pagina. Continuando...")

                        new_cursor = res.get('cursor') or paging.get('cursor')
                        if use_cursor:
                            if not new_cursor:
                                st.session_state['next_cursor'] = None
                                break
                            if new_cursor in seen_cursors:
                                st.warning("Cursor repetido: encerrando paginação.")
                                st.session_state['next_cursor'] = None
                                break
                            st.session_state['next_cursor'] = new_cursor
                            st.session_state['last_cursor'] = new_cursor
                            seen_cursors.add(new_cursor)
                        elif new_cursor:
                            st.session_state['next_cursor'] = new_cursor
                            st.session_state['last_cursor'] = new_cursor

                        if not use_cursor and not res.get("items"):
                            break
                        if not use_cursor and no_new_pages >= 2:
                            st.warning("Sem novos resultados em duas paginas seguidas.")
                            break

                        progress_total = target or st.session_state.get('total_count')
                        if progress_total:
                            status.text(f"{len(st.session_state['search_results'])}/{progress_total} leads")
                            bar.progress(min(1.0, len(st.session_state['search_results']) / max(progress_total, 1)))
                        else:
                            status.text(f"{len(st.session_state['search_results'])} leads coletados")
                        if delay:
                            time.sleep(delay)
                    st.success(f"Concluído: {len(st.session_state['search_results'])} leads.")
                    st.rerun()

                c_btn_daily, c_btn_all = st.columns(2)
                with c_btn_daily:
                    if st.button("⏱ Buscar até limite diario", key="btn_more_daily"):
                        target = min(int(daily_cap), total_count or int(daily_cap))
                        if target <= current_count:
                            st.info("Já atingimos o limite diario.")
                        else:
                            run_bulk_fetch(target, use_fetch_all=False)
                with c_btn_all:
                    if st.button("⏩ Buscar todas páginas", key="btn_more_all"):
                        target = None
                        should_fetch = True
                        if fetch_all:
                            target = total_count
                            if target is not None and current_count >= target:
                                st.info("Já temos todos os resultados estimados.")
                                should_fetch = False
                        else:
                            target = int(max_leads)
                            if target <= current_count:
                                st.info("Já temos essa quantidade de leads.")
                                should_fetch = False
                        if should_fetch:
                            run_bulk_fetch(target, use_fetch_all=fetch_all)
        with c_info:
            st.markdown(f"### Lista Atual: **{len(st.session_state['search_results'])}** leads")
            total_count = st.session_state.get('total_count')
            if total_count is not None:
                st.caption(f"Total estimado pela API: {total_count}")
                if st.session_state.get('next_cursor') is None and len(st.session_state['search_results']) < total_count:
                    st.warning("A API nao retornou cursor para paginacao. Se estiver usando URL do Sales Navigator, o app tenta paginar via parametro page; caso contrario, revise filtros/conta.")
            debug = st.session_state.get("last_search_debug")
            if debug:
                with st.expander("Debug da resposta (paging/config)", expanded=False):
                    st.json(debug)
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
        st.markdown("#### 📥 Download da lista")
        dl_all = pd.DataFrame(st.session_state['search_results'])
        dl_selected = pd.DataFrame(sel_objs) if sel_objs else None
        d1, d2 = st.columns(2)
        with d1:
            if dl_selected is not None and not dl_selected.empty:
                st.download_button(
                    "Baixar selecionados",
                    data=dl_selected.to_csv(index=False).encode("utf-8"),
                    file_name="leads_selecionados.csv",
                    mime="text/csv",
                )
            else:
                st.caption("Selecione leads para baixar.")
        with d2:
            if not dl_all.empty:
                st.download_button(
                    "Baixar todos",
                    data=dl_all.to_csv(index=False).encode("utf-8"),
                    file_name="leads_todos.csv",
                    mime="text/csv",
                )

        st.divider()
        st.markdown("#### ♻️ Checkpoint")
        st.caption("Salve para retomar a busca no dia seguinte.")
        checkpoint_payload = build_checkpoint_payload()
        st.download_button(
            "Baixar checkpoint",
            data=json.dumps(checkpoint_payload, ensure_ascii=False, indent=2).encode("utf-8"),
            file_name="salesnav_checkpoint.json",
            mime="application/json",
        )
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
    source = st.radio(
        "Fonte da lista",
        ["Lista existente", "Upload CSV"],
        horizontal=True,
        key="enrich_source",
    )
    if source == "Lista existente":
        try:
            camps = db.supabase.table("campaigns").select("*").eq("user_id", db.user.id).order('created_at', desc=True).execute().data
            if not camps:
                st.info("Nenhuma lista/campanha encontrada.")
            else:
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

                    enrich_df = pd.DataFrame(leads)
                    if not enrich_df.empty:
                        enrich_df["Bio"] = enrich_df.get("bio")
                        enrich_df["Cargo"] = enrich_df.get("current_title")
                        enrich_df["Empresas"] = enrich_df.get("companies")
                        enrich_df["Empresa ID"] = enrich_df.get("company_id")
                        enrich_df["Localizacao"] = enrich_df.get("profile_location").fillna(enrich_df.get("location")) if "profile_location" in enrich_df.columns else enrich_df.get("location")
                        export_cols = ["Bio", "Cargo", "Empresas", "Empresa ID", "Localizacao"]
                        st.download_button(
                            "Baixar colunas de enriquecimento",
                            data=enrich_df[export_cols].to_csv(index=False).encode("utf-8"),
                            file_name="enriquecimento.csv",
                            mime="text/csv",
                        )
                else:
                    st.info("Nenhum lead salvo nesta lista ainda.")
        except Exception as e:
            st.error(f"Erro ao carregar campanhas: {e}")
    else:
        st.info("Suba um CSV com coluna public_identifier, linkedin_public_id, id ou profile_url.")
        upload = st.file_uploader("Upload CSV", type=["csv"], key="enrich_upload")
        if upload:
            try:
                df = pd.read_csv(upload)
            except Exception as e:
                st.error(f"Erro ao ler CSV: {e}")
                df = None
            if df is not None:
                if df.empty:
                    st.info("CSV vazio.")
                else:
                    df_view = df.copy()
                    df_view.insert(0, "Selecionar", [True] * len(df_view))
                    edited = st.data_editor(df_view, hide_index=True, height=320, key="editor_enrich_upload")
                    sel_idx = edited[edited["Selecionar"] == True].index
                    selected_rows = [df.iloc[i].to_dict() for i in sel_idx]
                    st.caption(f"Selecionados: {len(selected_rows)}")
                    if st.button("✨ Enriquecer lista", key="btn_enrich_upload"):
                        if not selected_rows:
                            st.error("Selecione linhas para enriquecer.")
                        else:
                            bar = st.progress(0)
                            status = st.empty()
                            enriched_rows = []
                            for i, row in enumerate(selected_rows):
                                identifier = resolve_profile_identifier(row)
                                out = dict(row)
                                if not identifier:
                                    out["Bio"] = ""
                                    out["Cargo"] = ""
                                    out["Empresas"] = ""
                                    out["Empresa ID"] = ""
                                    out["Localizacao"] = ""
                                    out["_enrich_error"] = "identificador ausente"
                                    enriched_rows.append(out)
                                    continue
                                lead = dict(row)
                                lead["public_identifier"] = identifier
                                status.text(f"Enriquecendo {identifier}...")
                                fields = build_enrichment_payload(unipile, acc_id, lead)
                                out["Bio"] = fields.get("bio") or ""
                                out["Cargo"] = fields.get("current_title") or ""
                                out["Empresas"] = fields.get("companies") or ""
                                out["Empresa ID"] = fields.get("company_id") or ""
                                out["Localizacao"] = fields.get("profile_location") or ""
                                enriched_rows.append(out)
                                bar.progress((i + 1) / len(selected_rows))
                            result_df = pd.DataFrame(enriched_rows)
                            st.success("Enriquecimento concluído.")
                            st.download_button(
                                "Baixar lista enriquecida",
                                data=result_df.to_csv(index=False).encode("utf-8"),
                                file_name="lista_enriquecida.csv",
                                mime="text/csv",
                            )

with tab3:
    st.header("📨 Mensagens")
    st.caption("Crie a mensagem e envie usando uma lista existente ou um CSV.")
    source = st.radio(
        "Fonte da lista",
        ["Lista existente", "Upload CSV"],
        horizontal=True,
        key="msg_source",
    )
    if source == "Lista existente":
        try:
            camps = db.supabase.table("campaigns").select("*").eq("user_id", db.user.id).order('created_at', desc=True).execute().data
            if not camps:
                st.info("Nenhuma lista/campanha encontrada.")
            else:
                sel = st.selectbox("Lista/Campanha", [c['name'] for c in camps], key="msg_campaign_sel")
                curr = next(c for c in camps if c['name'] == sel)
                leads_all = db.supabase.table("leads").select("*").eq("campaign_id", curr['id']).execute().data
                if not leads_all:
                    st.info("Nenhum lead encontrado nessa lista.")
                else:
                    only_new = st.checkbox("Somente status 'new'", value=True, key="msg_only_new")
                    leads = [l for l in leads_all if l.get("status") == "new"] if only_new else leads_all

                    if not leads:
                        st.info("Nenhum lead com status 'new'.")
                    else:
                        df = pd.DataFrame(leads)
                        if "profile_location" in df.columns:
                            df["localizacao"] = df["profile_location"].fillna(df.get("location"))
                        elif "location" in df.columns:
                            df["localizacao"] = df["location"]

                        send_scope = st.radio("Enviar para", ["Todos", "Selecionados"], horizontal=True, key="msg_send_scope")

                        if send_scope == "Selecionados":
                            default_select = [True] * len(df)
                            df.insert(0, "Selecionar", default_select)
                            cols = [
                                "Selecionar",
                                "full_name",
                                "headline",
                                "localizacao",
                                "current_title",
                                "companies",
                                "status",
                            ]
                            df_show = df[[c for c in cols if c in df.columns]]
                            column_config = {
                                "Selecionar": st.column_config.CheckboxColumn(required=True),
                                "full_name": st.column_config.TextColumn("Nome"),
                                "headline": st.column_config.TextColumn("Headline"),
                                "localizacao": st.column_config.TextColumn("Localização"),
                                "current_title": st.column_config.TextColumn("Cargo"),
                                "companies": st.column_config.TextColumn("Empresas"),
                                "status": st.column_config.TextColumn("Status"),
                            }
                            edited = st.data_editor(
                                df_show,
                                hide_index=True,
                                column_config=column_config,
                                height=320,
                                key="editor_msg",
                            )
                            sel_idx = edited[edited["Selecionar"] == True].index
                            selected_leads = [leads[i] for i in sel_idx]
                        else:
                            selected_leads = leads

                        st.caption(f"Total selecionado: {len(selected_leads)}")

                        send_mode = st.radio(
                            "Modo de envio",
                            ["Novo chat (attendee_id)", "Chat existente (chat_id)"],
                            horizontal=True,
                            key=f"msg_send_mode_{curr['id']}",
                        )
                        if send_mode == "Novo chat (attendee_id)":
                            linkedin_api = st.selectbox(
                                "LinkedIn API",
                                ["sales_navigator", "classic", "recruiter"],
                                index=0,
                                key=f"msg_linkedin_api_{curr['id']}",
                            )
                            linkedin_inmail = st.checkbox(
                                "Enviar como InMail",
                                value=False,
                                key=f"msg_inmail_{curr['id']}",
                            )
                        else:
                            linkedin_api = None
                            linkedin_inmail = None
                            has_chat_id = any(lead.get("chat_id") for lead in selected_leads)
                            if selected_leads and not has_chat_id:
                                st.warning("Nenhum lead possui chat_id; envie como novo chat ou forneça chat_id.")

                        subject = st.text_input(
                            "Assunto (opcional)",
                            value="",
                            key=f"msg_subject_{curr['id']}",
                        )

                        template_default = curr.get("message_template") or "Olá {first_name}!"
                        template = st.text_area(
                            "Mensagem",
                            value=template_default,
                            height=140,
                            key=f"msg_template_{curr['id']}",
                        )
                        c_save, c_tip = st.columns([1, 3])
                        with c_save:
                            if st.button("Salvar template", key=f"msg_save_template_{curr['id']}"):
                                db.update_campaign_template(curr["id"], template)
                                st.success("Template salvo na campanha.")
                        with c_tip:
                            sample_ctx = build_message_context(selected_leads[0]) if selected_leads else build_message_context(leads[0])
                            placeholders = " ".join([f"{{{k}}}" for k in sample_ctx.keys()])
                            st.caption(f"Campos disponiveis: {placeholders}")

                        if selected_leads:
                            with st.expander("🔍 Preview (primeiros 3)", expanded=False):
                                for lead in selected_leads[:3]:
                                    name = lead.get("full_name") or lead.get("name") or "Lead"
                                    st.markdown(f"**{name}**")
                                    st.code(render_message(template, lead))

                        delay = st.number_input(
                            "Delay entre mensagens (s)",
                            min_value=0.0,
                            max_value=10.0,
                            value=1.0,
                            step=0.5,
                            key="msg_delay",
                        )

                        if st.button("📨 Enviar mensagens", key="btn_send_messages"):
                            if not template.strip():
                                st.error("A mensagem esta vazia.")
                            elif not selected_leads:
                                st.error("Selecione pelo menos um lead.")
                            else:
                                ok = fail = skipped = 0
                                bar = st.progress(0)
                                status = st.empty()
                                for i, lead in enumerate(selected_leads):
                                    text = render_message(template, lead).strip()
                                    if not text:
                                        skipped += 1
                                        db.log_attempt(curr["id"], lead["id"], "skipped", "mensagem vazia")
                                        continue
                                    try:
                                        if send_mode == "Chat existente (chat_id)":
                                            chat_id = lead.get("chat_id")
                                            if not chat_id:
                                                skipped += 1
                                                db.log_attempt(curr["id"], lead["id"], "skipped", "chat_id ausente")
                                                continue
                                            log_request(
                                                "send_message_in_chat",
                                                {
                                                    "endpoint": f"/api/v1/chats/{chat_id}/messages",
                                                    "body": {
                                                        "account_id": acc_id,
                                                        "text": text,
                                                    },
                                                },
                                            )
                                            res = unipile.send_message_in_chat(chat_id, text, account_id=acc_id)
                                            log_response("send_message_in_chat", res, unipile.last_status)
                                        else:
                                            attendee_id = lead.get("provider_id") or lead.get("id")
                                            if not attendee_id:
                                                skipped += 1
                                                db.log_attempt(curr["id"], lead["id"], "skipped", "provider_id ausente")
                                                continue
                                            log_request(
                                                "start_chat",
                                                {
                                                    "endpoint": "/api/v1/chats",
                                                    "body": {
                                                        "account_id": acc_id,
                                                        "attendees_ids": [attendee_id],
                                                        "text": text,
                                                        "subject": subject or None,
                                                        "linkedin[api]": linkedin_api,
                                                        "linkedin[inmail]": linkedin_inmail,
                                                    },
                                                },
                                            )
                                            res = unipile.start_chat(
                                                acc_id,
                                                [attendee_id],
                                                text,
                                                subject=subject or None,
                                                linkedin_api=linkedin_api,
                                                linkedin_inmail=linkedin_inmail,
                                            )
                                            log_response("start_chat", res, unipile.last_status)
                                        db.update_lead_status(lead["id"], "sent")
                                        db.log_attempt(curr["id"], lead["id"], "sent")
                                        ok += 1
                                    except Exception as e:
                                        db.update_lead_status(lead["id"], "error")
                                        db.log_attempt(curr["id"], lead["id"], "error", str(e))
                                        fail += 1
                                    bar.progress((i + 1) / len(selected_leads))
                                    status.text(f"Enviando... {i + 1}/{len(selected_leads)}")
                                    if delay:
                                        time.sleep(delay)
                                st.success(f"Concluido. Enviadas: {ok}, Erros: {fail}, Ignoradas: {skipped}.")
        except Exception as e:
            st.error(f"Erro ao carregar listas: {e}")
    else:
        st.info("CSV precisa ter coluna provider_id/id (novo chat) ou chat_id (chat existente).")
        upload = st.file_uploader("Upload CSV", type=["csv"], key="msg_upload")
        if upload:
            try:
                df = pd.read_csv(upload)
            except Exception as e:
                st.error(f"Erro ao ler CSV: {e}")
                df = None
            if df is not None:
                if df.empty:
                    st.info("CSV vazio.")
                else:
                    send_mode = st.radio(
                        "Modo de envio",
                        ["Novo chat (attendee_id)", "Chat existente (chat_id)"],
                        horizontal=True,
                        key="msg_send_mode_upload",
                    )
                    can_send = True
                    if send_mode == "Novo chat (attendee_id)":
                        if not any(col in df.columns for col in ("provider_id", "id")):
                            st.error("CSV precisa ter coluna provider_id ou id.")
                            can_send = False
                        linkedin_api = st.selectbox(
                            "LinkedIn API",
                            ["sales_navigator", "classic", "recruiter"],
                            index=0,
                            key="msg_upload_linkedin_api",
                        )
                        linkedin_inmail = st.checkbox(
                            "Enviar como InMail",
                            value=False,
                            key="msg_upload_inmail",
                        )
                    else:
                        if "chat_id" not in df.columns:
                            st.error("CSV precisa ter coluna chat_id.")
                            can_send = False
                        linkedin_api = None
                        linkedin_inmail = None

                    if can_send:
                        send_scope = st.radio(
                            "Enviar para",
                            ["Todos", "Selecionados"],
                            horizontal=True,
                            key="msg_upload_scope",
                        )
                        df_view = df.copy()
                        selected_rows = df.to_dict(orient="records")
                        if send_scope == "Selecionados":
                            df_view.insert(0, "Selecionar", [True] * len(df_view))
                            edited = st.data_editor(df_view, hide_index=True, height=320, key="editor_msg_upload")
                            sel_idx = edited[edited["Selecionar"] == True].index
                            selected_rows = [df.iloc[i].to_dict() for i in sel_idx]

                        st.caption(f"Total selecionado: {len(selected_rows)}")
                        subject = st.text_input("Assunto (opcional)", value="", key="msg_upload_subject")
                        template = st.text_area(
                            "Mensagem",
                            value="Olá {first_name}!",
                            height=140,
                            key="msg_upload_template",
                        )
                        sample_ctx = build_message_context(selected_rows[0]) if selected_rows else {}
                        if sample_ctx:
                            placeholders = " ".join([f"{{{k}}}" for k in sample_ctx.keys()])
                            st.caption(f"Campos disponiveis: {placeholders}")

                        if selected_rows:
                            with st.expander("🔍 Preview (primeiros 3)", expanded=False):
                                for lead in selected_rows[:3]:
                                    name = lead.get("full_name") or lead.get("name") or "Lead"
                                    st.markdown(f"**{name}**")
                                    st.code(render_message(template, lead))

                        delay = st.number_input(
                            "Delay entre mensagens (s)",
                            min_value=0.0,
                            max_value=10.0,
                            value=1.0,
                            step=0.5,
                            key="msg_upload_delay",
                        )
                        if st.button("📨 Enviar mensagens", key="btn_send_messages_upload"):
                            if not template.strip():
                                st.error("A mensagem esta vazia.")
                            elif not selected_rows:
                                st.error("Selecione pelo menos um lead.")
                            else:
                                ok = fail = skipped = 0
                                bar = st.progress(0)
                                status = st.empty()
                                report = []
                                for i, lead in enumerate(selected_rows):
                                    text = render_message(template, lead).strip()
                                    row_report = dict(lead)
                                    if not text:
                                        skipped += 1
                                        row_report["_status"] = "skipped"
                                        row_report["_error"] = "mensagem vazia"
                                        report.append(row_report)
                                        continue
                                    try:
                                        if send_mode == "Chat existente (chat_id)":
                                            chat_id = lead.get("chat_id")
                                            if not chat_id:
                                                skipped += 1
                                                row_report["_status"] = "skipped"
                                                row_report["_error"] = "chat_id ausente"
                                                report.append(row_report)
                                                continue
                                            log_request(
                                                "send_message_in_chat",
                                                {
                                                    "endpoint": f"/api/v1/chats/{chat_id}/messages",
                                                    "body": {"account_id": acc_id, "text": text},
                                                },
                                            )
                                            res = unipile.send_message_in_chat(chat_id, text, account_id=acc_id)
                                            log_response("send_message_in_chat", res, unipile.last_status)
                                            if isinstance(res, dict):
                                                row_report["message_id"] = res.get("message_id")
                                        else:
                                            attendee_id = lead.get("provider_id") or lead.get("id")
                                            if not attendee_id:
                                                skipped += 1
                                                row_report["_status"] = "skipped"
                                                row_report["_error"] = "provider_id ausente"
                                                report.append(row_report)
                                                continue
                                            log_request(
                                                "start_chat",
                                                {
                                                    "endpoint": "/api/v1/chats",
                                                    "body": {
                                                        "account_id": acc_id,
                                                        "attendees_ids": [attendee_id],
                                                        "text": text,
                                                        "subject": subject or None,
                                                        "linkedin[api]": linkedin_api,
                                                        "linkedin[inmail]": linkedin_inmail,
                                                    },
                                                },
                                            )
                                            res = unipile.start_chat(
                                                acc_id,
                                                [attendee_id],
                                                text,
                                                subject=subject or None,
                                                linkedin_api=linkedin_api,
                                                linkedin_inmail=linkedin_inmail,
                                            )
                                            log_response("start_chat", res, unipile.last_status)
                                            if isinstance(res, dict):
                                                row_report["chat_id"] = res.get("chat_id")
                                                row_report["message_id"] = res.get("message_id")
                                        ok += 1
                                        row_report["_status"] = "sent"
                                    except Exception as e:
                                        fail += 1
                                        row_report["_status"] = "error"
                                        row_report["_error"] = str(e)
                                    report.append(row_report)
                                    bar.progress((i + 1) / len(selected_rows))
                                    status.text(f"Enviando... {i + 1}/{len(selected_rows)}")
                                    if delay:
                                        time.sleep(delay)
                                st.success(f"Concluido. Enviadas: {ok}, Erros: {fail}, Ignoradas: {skipped}.")
                                report_df = pd.DataFrame(report)
                                st.download_button(
                                    "Baixar relatorio de envio",
                                    data=report_df.to_csv(index=False).encode("utf-8"),
                                    file_name="relatorio_envio.csv",
                                    mime="text/csv",
                                )

with tab4:
    st.header("📦 Payloads")
    st.caption("Ultimo payload enviado e resposta recebida.")
    show_full = st.checkbox("Mostrar resposta completa", value=False, key="show_full_response")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Request")
        last_request = st.session_state.get("last_request")
        if last_request:
            st.json(last_request)
        else:
            st.info("Nenhuma requisicao registrada ainda.")
    with c2:
        st.subheader("Response")
        last_response = st.session_state.get("last_response_full") if show_full else st.session_state.get("last_response")
        if last_response:
            st.json(last_response)
        else:
            st.info("Nenhuma resposta registrada ainda.")

    with st.expander("Historico de eventos", expanded=False):
        c3, c4 = st.columns([1, 3])
        with c3:
            if st.button("Limpar logs", key="btn_clear_logs"):
                st.session_state['api_logs'] = []
                st.success("Logs limpos.")
        with c4:
            st.caption(f"Total de eventos: {len(st.session_state.get('api_logs', []))}")
        logs = st.session_state.get('api_logs', [])
        if logs:
            st.json(logs[-50:])
        else:
            st.info("Nenhum log registrado ainda.")
