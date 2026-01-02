import requests
import time
import logging
from typing import Dict, List, Optional, Union

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
                    wait_time = (2 ** attempt) + 5
                    logger.warning(f"⚠️ Rate limit. Aguardando {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                
                if 200 <= response.status_code < 300:
                    return response.json()
                
                response.raise_for_status()
            except Exception as e:
                if attempt == max_retries - 1: raise e
                time.sleep(2)
        return None

    def search_people(self, account_id: str, criteria: Dict, limit: int = 50, cursor: str = None, api_type: str = "classic"):
        """Busca pessoas com suporte a paginação."""
        endpoint = "/api/v1/linkedin/search"

        if api_type == "classic" and limit > 50:
            limit = 50
        elif api_type == "sales_navigator" and limit > 100:
            limit = 100

        safe_criteria = criteria or {}
        if api_type == "sales_navigator":
            payload = {
                "api": api_type,
                "category": "people",
                **safe_criteria,
            }
        else:
            payload = {
                "api": api_type,
                "category": "people",
                "params": safe_criteria,
            }

        query_params = {"account_id": account_id, "limit": limit}
        if cursor:
            query_params["cursor"] = cursor

        return self._request("POST", endpoint, params=query_params, json_data=payload)

    def search_from_url(self, account_id: str, search_url: str, limit: int = 50, cursor: str = None):
        """Busca pessoas a partir de uma URL do LinkedIn."""
        if not search_url:
            return None
        endpoint = "/api/v1/linkedin/search"
        cleaned_url = search_url.strip()
        query_params = {"account_id": account_id, "limit": limit}
        if cursor:
            query_params["cursor"] = cursor

        payloads = [
            {"url": cleaned_url},
            {"search_from_url": cleaned_url},
        ]
        last_error = None
        for payload in payloads:
            try:
                return self._request("POST", endpoint, params=query_params, json_data=payload)
            except requests.exceptions.HTTPError as exc:
                last_error = exc
                if exc.response is None or exc.response.status_code != 400:
                    raise
        if last_error:
            raise last_error
        return None

    def get_profile_details(self, account_id: str, identifier: str, sections: Union[List[str], str, None] = None):
        """Busca dados completos do perfil (Enriquecimento)."""
        # Pede seções estratégicas para não pesar tanto mas trazer contatos
        if sections is None:
            sections = ["contact_info", "experience", "education", "about"]
        endpoint = f"/api/v1/users/{identifier}"
        params = {"account_id": account_id, "linkedin_sections": sections}
        return self._request("GET", endpoint, params=params)

    def get_company_details(self, account_id: str, company_id: str):
        """Busca dados da empresa."""
        if not company_id: return None
        endpoint = f"/api/v1/linkedin/company/{company_id}"
        params = {"account_id": account_id}
        try:
            return self._request("GET", endpoint, params=params)
        except:
            return None # Se falhar empresa, não trava o fluxo

    def get_user_posts(self, account_id: str, identifier: str, limit: int = 3):
        """Busca posts recentes do usuário."""
        endpoint = f"/api/v1/users/{identifier}/posts"
        params = {"account_id": account_id, "limit": limit}
        return self._request("GET", endpoint, params=params)

    def start_chat(self, account_id: str, attendees_ids: List[str], text: str, subject: str = None):
        endpoint = "/api/v1/chats"
        payload = {"account_id": account_id, "attendees_ids": attendees_ids, "text": text}
        if subject: payload["subject"] = subject
        return self._request("POST", endpoint, json_data=payload)
