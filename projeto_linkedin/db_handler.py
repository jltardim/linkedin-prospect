from supabase import create_client, Client
import streamlit as st
from datetime import datetime
from typing import List, Dict, Optional, Any

class DBHandler:
    def __init__(self, url: str, key: str):
        self.supabase: Client = create_client(url, key)
        self.user = None

    def login(self, email, password):
        """Faz login e retorna a sessão completa (Tokens)."""
        try:
            response = self.supabase.auth.sign_in_with_password({"email": email, "password": password})
            self.user = response.user
            # Retornamos a sessão para salvar no Streamlit
            return response.session 
        except Exception as e:
            st.error(f"Erro no login: {e}")
            return None

    def set_session(self, access_token, refresh_token):
        """Restaura a sessão (Crachá) sem precisar digitar senha de novo."""
        try:
            self.supabase.auth.set_session(access_token, refresh_token)
            # Atualiza o usuário atual baseado no token
            self.user = self.supabase.auth.get_user().user
            return True
        except Exception as e:
            st.error(f"Sessão expirada: {e}")
            return False

    def save_unipile_account(self, account_id: str, api_key: str, label: str):
        """Salva uma nova credencial Unipile."""
        if not self.user:
            raise Exception("Usuário não autenticado.")
            
        data = {
            "user_id": self.user.id,
            "account_id": account_id,
            "api_key": api_key,
            "label": label
        }
        return self.supabase.table("unipile_accounts").upsert(data).execute()

    def get_user_accounts(self):
        return self.supabase.table("unipile_accounts").select("*").execute()

    def create_campaign(self, name: str, template: str, account_db_id: str):
        data = {
            "user_id": self.user.id,
            "unipile_account_id": account_db_id,
            "name": name,
            "message_template": template,
            "status": "draft"
        }
        return self.supabase.table("campaigns").insert(data).execute()

    def update_campaign_template(self, campaign_id: str, template: str):
        return self.supabase.table("campaigns").update({"message_template": template}).eq("id", campaign_id).execute()

    def save_leads(self, campaign_id: str, leads_list: List[Dict]):
        formatted_leads = []
        for lead in leads_list:
            formatted_leads.append({
                "user_id": self.user.id,
                "campaign_id": campaign_id,
                "linkedin_public_id": lead.get("public_identifier"),
                "provider_id": lead.get("provider_id") or lead.get("id"),
                "full_name": lead.get("name"),
                "headline": lead.get("headline"),
                "location": lead.get("location"),
                "profile_location": lead.get("profile_location"),
                "current_title": lead.get("current_title"),
                "companies": lead.get("companies"),
                "company_id": lead.get("company_id"),
                "bio": lead.get("bio"),
                "status": "new",
                "enrichment_data": lead.get("enrichment_data", None) 
            })
        
        return self.supabase.table("leads").upsert(formatted_leads, on_conflict="campaign_id, linkedin_public_id").execute()

    def update_lead_enrichment(self, lead_id: str, fields: Dict):
        if not fields:
            return None
        return self.supabase.table("leads").update(fields).eq("id", lead_id).execute()

    def get_pending_leads(self, campaign_id: str):
        return self.supabase.table("leads")\
            .select("*")\
            .eq("campaign_id", campaign_id)\
            .eq("status", "new")\
            .execute()

    def update_lead_status(self, lead_id: str, status: str):
        self.supabase.table("leads").update({"status": status}).eq("id", lead_id).execute()

    def update_lead_invitation(
        self,
        lead_id: str,
        status: str,
        invitation_id: str | None = None,
        error_msg: str | None = None,
    ):
        data: Dict[str, Any] = {"invitation_status": status}
        if invitation_id:
            data["invitation_id"] = invitation_id
        if error_msg is not None:
            data["invitation_error"] = error_msg
        if status == "sent":
            data["invited_at"] = datetime.utcnow().isoformat()
        return self.supabase.table("leads").update(data).eq("id", lead_id).execute()

    def log_attempt(self, campaign_id: str, lead_id: str, status: str, error_msg: str = None):
        data = {
            "user_id": self.user.id,
            "campaign_id": campaign_id,
            "lead_id": lead_id,
            "status": status,
            "error_message": error_msg
        }
        self.supabase.table("message_logs").insert(data).execute()
