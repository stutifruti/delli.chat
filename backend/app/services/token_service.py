import os
import secrets
from datetime import datetime, timezone
from supabase import create_client, Client


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL", "http://localhost:5173")


def _get_supabase() -> Client:
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("SUPABASE_URL or SUPABASE_KEY is missing from .env")
    return create_client(SUPABASE_URL, SUPABASE_KEY)


async def create_chat_token(youth_id: str) -> dict:
    """
    Create a new secure token for a youth and store it in Supabase chat_links.
    """
    try:
        supabase = _get_supabase()

        token = secrets.token_urlsafe(16)
        chat_url = f"{FRONTEND_BASE_URL}/chat?token={token}"

        payload = {
            "youth_id": youth_id,
            "token": token,
            "chat_url": chat_url,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        supabase.table("chat_links").insert(payload).execute()

        return {
            "token": token,
            "youthId": youth_id,
            "chatUrl": chat_url,
        }
    except Exception as e:
        print(f"[token_service] create_chat_token error: {e}")
        return {}


async def resolve_chat_token(token: str) -> dict:
    """
    Resolve a public token to the internal youth_id.
    """
    try:
        supabase = _get_supabase()

        res = (
            supabase.table("chat_links")
            .select("*")
            .eq("token", token)
            .eq("is_active", True)
            .maybe_single()
            .execute()
        )

        row = res.data or {}
        if not row:
            return {}

        return {
            "youthId": row.get("youth_id"),
            "token": row.get("token"),
            "chatUrl": row.get("chat_url"),
            "isActive": row.get("is_active", False),
            "createdAt": row.get("created_at"),
        }
    except Exception as e:
        print(f"[token_service] resolve_chat_token error: {e}")
        return {}


async def deactivate_chat_token(token: str) -> bool:
    """
    Deactivate an existing token so the chat link no longer works.
    """
    try:
        supabase = _get_supabase()

        supabase.table("chat_links").update(
            {"is_active": False}
        ).eq("token", token).execute()

        return True
    except Exception as e:
        print(f"[token_service] deactivate_chat_token error: {e}")
        return False