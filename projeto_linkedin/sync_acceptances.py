import argparse
import os
import random
import time
from typing import Iterable

from supabase import create_client

from unipile_client import UnipileClient
from message_utils import render_message


DEFAULT_UNIPILE_BASE_URL = "https://api26.unipile.com:15609"
DEFAULT_TEMPLATE = "Ola {first_name}!"


def parse_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}


def clamp(value: int, min_value: int, max_value: int) -> int:
    return max(min_value, min(value, max_value))


def iter_invite_sent(
    unipile: UnipileClient,
    account_id: str,
    limit: int,
) -> Iterable[dict]:
    cursor = None
    seen = set()
    while True:
        res = unipile.list_invitations_sent(account_id, limit=limit, cursor=cursor) or {}
        items = res.get("items") or []
        for item in items:
            yield item
        cursor = res.get("cursor") or (res.get("paging") or {}).get("cursor")
        if not cursor or cursor in seen:
            break
        seen.add(cursor)


def iter_relations(
    unipile: UnipileClient,
    account_id: str,
    limit: int,
) -> Iterable[dict]:
    cursor = None
    seen = set()
    while True:
        res = unipile.list_relations(account_id, limit=limit, cursor=cursor) or {}
        items = res.get("items") or []
        for item in items:
            yield item
        cursor = res.get("cursor") or (res.get("paging") or {}).get("cursor")
        if not cursor or cursor in seen:
            break
        seen.add(cursor)


def build_pending_sets(items: Iterable[dict]) -> tuple[set[str], set[str]]:
    pending_public_ids: set[str] = set()
    pending_member_ids: set[str] = set()
    for item in items:
        public_id = item.get("invited_user_public_id")
        member_id = item.get("invited_user_id")
        if public_id:
            pending_public_ids.add(str(public_id))
        if member_id:
            pending_member_ids.add(str(member_id))
    return pending_public_ids, pending_member_ids


def build_relation_sets(items: Iterable[dict]) -> tuple[set[str], set[str]]:
    relation_public_ids: set[str] = set()
    relation_member_ids: set[str] = set()
    for item in items:
        public_id = item.get("public_identifier")
        member_id = item.get("member_id")
        if public_id:
            relation_public_ids.add(str(public_id))
        if member_id:
            relation_member_ids.add(str(member_id))
    return relation_public_ids, relation_member_ids


def lead_is_accepted(
    lead: dict,
    relation_public_ids: set[str],
    relation_member_ids: set[str],
    pending_public_ids: set[str],
    pending_member_ids: set[str],
) -> bool:
    public_id = lead.get("linkedin_public_id") or lead.get("public_identifier")
    member_id = lead.get("provider_id") or lead.get("id")
    public_id = str(public_id) if public_id else None
    member_id = str(member_id) if member_id else None

    in_relations = (
        (public_id and public_id in relation_public_ids)
        or (member_id and member_id in relation_member_ids)
    )
    in_pending = (
        (public_id and public_id in pending_public_ids)
        or (member_id and member_id in pending_member_ids)
    )
    return in_relations and not in_pending


def run() -> None:
    parser = argparse.ArgumentParser(description="Sync invite acceptances and send automatic messages.")
    parser.add_argument("--supabase-url", default=os.getenv("SUPABASE_URL"))
    parser.add_argument(
        "--supabase-key",
        default=os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY"),
    )
    parser.add_argument("--unipile-base-url", default=os.getenv("UNIPILE_BASE_URL", DEFAULT_UNIPILE_BASE_URL))
    parser.add_argument("--account-db-id", default=os.getenv("UNIPILE_ACCOUNT_DB_ID"))
    parser.add_argument("--dry-run", action="store_true", help="Do not write updates or send messages.")
    parser.add_argument("--sync", action="store_true", help="Update acceptance status before sending.")
    parser.add_argument(
        "--send",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Send messages for accepted leads.",
    )
    parser.add_argument("--sync-only", action="store_true", help="Deprecated: same as --sync --no-send.")
    parser.add_argument("--max-messages", type=int, default=int(os.getenv("AUTO_MESSAGE_LIMIT", "50")))
    parser.add_argument("--delay-min", type=float, default=float(os.getenv("AUTO_MESSAGE_DELAY_MIN", "1.0")))
    parser.add_argument("--delay-max", type=float, default=float(os.getenv("AUTO_MESSAGE_DELAY_MAX", "3.0")))
    parser.add_argument("--linkedin-api", default=os.getenv("AUTO_MESSAGE_LINKEDIN_API", "sales_navigator"))
    parser.add_argument(
        "--linkedin-inmail",
        action="store_true",
        default=parse_bool(os.getenv("AUTO_MESSAGE_INMAIL"), False),
    )
    parser.add_argument("--message-subject", default=os.getenv("AUTO_MESSAGE_SUBJECT") or None)
    args = parser.parse_args()

    if not args.supabase_url or not args.supabase_key:
        raise SystemExit("Missing SUPABASE_URL or SUPABASE_SERVICE_KEY/SUPABASE_KEY.")

    do_sync = args.sync or args.sync_only
    do_send = args.send and not args.sync_only
    if not do_sync and not do_send:
        print("Nothing to do. Use --sync and/or --send.")
        return

    supabase = create_client(args.supabase_url, args.supabase_key)
    accounts_query = supabase.table("unipile_accounts").select("id,user_id,account_id,api_key,label")
    if args.account_db_id:
        accounts_query = accounts_query.eq("id", args.account_db_id)
    accounts = accounts_query.execute().data or []
    if not accounts:
        print("No Unipile accounts found.")
        return

    max_messages = max(0, args.max_messages)
    delay_min = max(0.0, args.delay_min)
    delay_max = max(delay_min, args.delay_max)
    total_messages_sent = 0

    for account in accounts:
        account_db_id = account.get("id")
        account_id = account.get("account_id")
        api_key = account.get("api_key")
        label = account.get("label") or account_id
        if not account_id or not api_key:
            print(f"[{label}] Skipping account with missing credentials.")
            continue

        unipile = UnipileClient(args.unipile_base_url, api_key)
        pending_public_ids: set[str] = set()
        pending_member_ids: set[str] = set()
        relation_public_ids: set[str] = set()
        relation_member_ids: set[str] = set()
        if do_sync:
            pending_items = iter_invite_sent(unipile, account_id, limit=100)
            pending_public_ids, pending_member_ids = build_pending_sets(pending_items)
            relation_items = iter_relations(unipile, account_id, limit=1000)
            relation_public_ids, relation_member_ids = build_relation_sets(relation_items)

        campaigns = (
            supabase.table("campaigns")
            .select("id,user_id,message_template,unipile_account_id")
            .eq("unipile_account_id", account_db_id)
            .execute()
            .data
            or []
        )
        print(
            f"[{label}] campaigns={len(campaigns)} pending={len(pending_public_ids)} relations={len(relation_public_ids)}"
        )
        for campaign in campaigns:
            campaign_id = campaign.get("id")
            user_id = campaign.get("user_id")
            template = campaign.get("message_template") or DEFAULT_TEMPLATE
            if not campaign_id:
                continue
            lead_query = supabase.table("leads").select("*").eq("campaign_id", campaign_id)
            if do_sync:
                lead_query = lead_query.in_("invitation_status", ["sent", "accepted"])
            else:
                lead_query = lead_query.eq("invitation_status", "accepted")
            leads = lead_query.execute().data or []
            accepted_updates: list[dict] = []
            accepted_leads: list[dict] = []
            for lead in leads:
                status = lead.get("invitation_status")
                if status == "sent" and do_sync:
                    if lead_is_accepted(
                        lead,
                        relation_public_ids,
                        relation_member_ids,
                        pending_public_ids,
                        pending_member_ids,
                    ):
                        accepted_updates.append(lead)
                        accepted_leads.append(lead)
                elif status == "accepted":
                    accepted_leads.append(lead)

            if do_sync and accepted_updates and not args.dry_run:
                for lead in accepted_updates:
                    supabase.table("leads").update(
                        {"invitation_status": "accepted", "invitation_error": None}
                    ).eq("id", lead["id"]).execute()

            if not do_send:
                continue

            if not accepted_leads:
                continue

            sent_logs = (
                supabase.table("message_logs")
                .select("lead_id")
                .eq("campaign_id", campaign_id)
                .in_("status", ["sent", "auto_sent"])
                .execute()
                .data
                or []
            )
            already_sent_ids = {row.get("lead_id") for row in sent_logs if row.get("lead_id")}

            for lead in accepted_leads:
                if total_messages_sent >= max_messages and max_messages > 0:
                    break
                lead_id = lead.get("id")
                if lead_id in already_sent_ids:
                    continue
                if lead.get("status") == "sent":
                    continue
                attendee_id = lead.get("provider_id") or lead.get("id")
                if not attendee_id:
                    continue
                text = render_message(template, lead).strip()
                if not text:
                    continue

                if args.dry_run:
                    total_messages_sent += 1
                    continue

                try:
                    unipile.start_chat(
                        account_id,
                        [str(attendee_id)],
                        text,
                        subject=args.message_subject,
                        linkedin_api=args.linkedin_api,
                        linkedin_inmail=args.linkedin_inmail,
                    )
                    supabase.table("leads").update({"status": "sent"}).eq("id", lead_id).execute()
                    supabase.table("message_logs").insert(
                        {
                            "user_id": user_id,
                            "campaign_id": campaign_id,
                            "lead_id": lead_id,
                            "status": "auto_sent",
                            "error_message": None,
                        }
                    ).execute()
                    total_messages_sent += 1
                except Exception as exc:
                    if not args.dry_run:
                        supabase.table("leads").update({"status": "error"}).eq("id", lead_id).execute()
                        supabase.table("message_logs").insert(
                            {
                                "user_id": user_id,
                                "campaign_id": campaign_id,
                                "lead_id": lead_id,
                                "status": "auto_error",
                                "error_message": str(exc),
                            }
                        ).execute()

                if delay_max > 0:
                    time.sleep(random.uniform(delay_min, delay_max))

    print(f"Done. messages_sent={total_messages_sent}")


if __name__ == "__main__":
    run()
