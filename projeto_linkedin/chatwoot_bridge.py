import os
import sqlite3
from typing import Any, Dict, Optional, Tuple

import requests
from fastapi import FastAPI, Header, HTTPException, Request


CHATWOOT_URL = os.getenv("CHATWOOT_URL", "").rstrip("/")
CHATWOOT_ACCOUNT_ID = os.getenv("CHATWOOT_ACCOUNT_ID", "")
CHATWOOT_INBOX_ID = os.getenv("CHATWOOT_INBOX_ID", "")
CHATWOOT_API_TOKEN = os.getenv("CHATWOOT_API_TOKEN", "")
WEBHOOK_SECRET = os.getenv("UNIPILE_WEBHOOK_SECRET", "")
DB_PATH = os.getenv("CHATWOOT_BRIDGE_DB", "data/chatwoot_bridge.db")


app = FastAPI(title="Unipile -> Chatwoot Bridge")


def ensure_db() -> None:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_map (
                provider_chat_id TEXT PRIMARY KEY,
                conversation_id INTEGER NOT NULL,
                contact_id INTEGER NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS message_dedupe (
                provider_message_id TEXT PRIMARY KEY,
                processed_at TEXT NOT NULL
            )
            """
        )


ensure_db()


def chatwoot_headers() -> Dict[str, str]:
    if not CHATWOOT_API_TOKEN:
        raise HTTPException(status_code=500, detail="Chatwoot token missing")
    return {
        "api_access_token": CHATWOOT_API_TOKEN,
        "Content-Type": "application/json",
    }


def get_mapping(provider_chat_id: str) -> Optional[Tuple[int, int]]:
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            "SELECT conversation_id, contact_id FROM chat_map WHERE provider_chat_id = ?",
            (provider_chat_id,),
        ).fetchone()
    if row:
        return int(row[0]), int(row[1])
    return None


def save_mapping(provider_chat_id: str, conversation_id: int, contact_id: int) -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO chat_map (provider_chat_id, conversation_id, contact_id, updated_at)
            VALUES (?, ?, ?, datetime('now'))
            """,
            (provider_chat_id, conversation_id, contact_id),
        )


def is_duplicate(provider_message_id: Optional[str]) -> bool:
    if not provider_message_id:
        return False
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            "SELECT 1 FROM message_dedupe WHERE provider_message_id = ?",
            (provider_message_id,),
        ).fetchone()
        if row:
            return True
        conn.execute(
            "INSERT INTO message_dedupe (provider_message_id, processed_at) VALUES (?, datetime('now'))",
            (provider_message_id,),
        )
    return False


def search_contact(identifier: str) -> Optional[Dict[str, Any]]:
    if not CHATWOOT_URL:
        raise HTTPException(status_code=500, detail="Chatwoot URL missing")
    params = {"q": identifier}
    url = f"{CHATWOOT_URL}/api/v1/accounts/{CHATWOOT_ACCOUNT_ID}/contacts/search"
    resp = requests.get(url, params=params, headers=chatwoot_headers(), timeout=20)
    resp.raise_for_status()
    payload = resp.json().get("payload", [])
    for item in payload:
        if item.get("identifier") == identifier:
            return item
    return payload[0] if payload else None


def create_contact(name: str, identifier: str, profile_url: Optional[str]) -> Dict[str, Any]:
    url = f"{CHATWOOT_URL}/api/v1/accounts/{CHATWOOT_ACCOUNT_ID}/contacts"
    custom_attrs = {"provider": "linkedin"}
    if profile_url:
        custom_attrs["profile_url"] = profile_url
    payload = {
        "inbox_id": int(CHATWOOT_INBOX_ID),
        "name": name,
        "identifier": identifier,
        "custom_attributes": custom_attrs,
    }
    resp = requests.post(url, json=payload, headers=chatwoot_headers(), timeout=20)
    resp.raise_for_status()
    return resp.json()


def create_conversation(contact_id: int, source_id: str) -> Dict[str, Any]:
    url = f"{CHATWOOT_URL}/api/v1/accounts/{CHATWOOT_ACCOUNT_ID}/conversations"
    payload = {
        "inbox_id": int(CHATWOOT_INBOX_ID),
        "source_id": source_id,
        "contact_id": contact_id,
        "custom_attributes": {"provider": "linkedin"},
    }
    resp = requests.post(url, json=payload, headers=chatwoot_headers(), timeout=20)
    resp.raise_for_status()
    return resp.json()


def send_incoming_message(conversation_id: int, content: str) -> Dict[str, Any]:
    url = f"{CHATWOOT_URL}/api/v1/accounts/{CHATWOOT_ACCOUNT_ID}/conversations/{conversation_id}/messages"
    payload = {"content": content, "message_type": "incoming"}
    resp = requests.post(url, json=payload, headers=chatwoot_headers(), timeout=20)
    resp.raise_for_status()
    return resp.json()


def normalize_payload(payload: Any) -> Dict[str, Any]:
    if isinstance(payload, list) and payload:
        payload = payload[0]
    if isinstance(payload, dict) and "body" in payload:
        return payload["body"]
    if isinstance(payload, dict):
        return payload
    return {}


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/webhooks/unipile")
async def unipile_webhook(
    request: Request,
    x_webhook_secret: Optional[str] = Header(default=None),
) -> Dict[str, str]:
    if WEBHOOK_SECRET and x_webhook_secret != WEBHOOK_SECRET:
        raise HTTPException(status_code=401, detail="Invalid webhook secret")

    raw = await request.json()
    body = normalize_payload(raw)
    if not body or body.get("event") != "message_received":
        return {"status": "ignored"}
    if body.get("is_sender") is True:
        return {"status": "ignored"}

    provider_chat_id = body.get("provider_chat_id") or body.get("chat_id")
    if not provider_chat_id:
        raise HTTPException(status_code=400, detail="Missing provider_chat_id")

    provider_message_id = body.get("provider_message_id") or body.get("message_id")
    if is_duplicate(provider_message_id):
        return {"status": "duplicate"}

    sender = body.get("sender") or {}
    name = sender.get("attendee_name") or "LinkedIn Lead"
    identifier = (
        sender.get("attendee_provider_id")
        or sender.get("attendee_profile_url")
        or sender.get("attendee_public_identifier")
        or sender.get("attendee_specifics", {}).get("member_urn")
        or name
    )
    profile_url = sender.get("attendee_profile_url")
    message = body.get("message") or ""

    mapping = get_mapping(provider_chat_id)
    if mapping:
        conversation_id, contact_id = mapping
    else:
        contact = search_contact(identifier)
        if not contact:
            contact = create_contact(name, identifier, profile_url)
        contact_id = int(contact.get("id"))
        conv = create_conversation(contact_id, provider_chat_id)
        conversation_id = int(conv.get("id"))
        save_mapping(provider_chat_id, conversation_id, contact_id)

    if message:
        send_incoming_message(conversation_id, message)

    return {"status": "ok"}
