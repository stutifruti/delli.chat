import os
from typing import Optional
from supabase import create_client, Client


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


def _get_supabase() -> Client:
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("SUPABASE_URL or SUPABASE_KEY is missing from .env")
    return create_client(SUPABASE_URL, SUPABASE_KEY)


async def get_case_id_from_username(instagram_username: str | None) -> str | None:
    """
    Resolve instagram username -> case_id from social_media_accounts.
    """
    if not instagram_username:
        return None

    try:
        supabase = _get_supabase()

        res = (
            supabase.table("social_media_accounts")
            .select("case_id")
            .eq("username", instagram_username)
            .eq("platform", "instagram")
            .maybe_single()
            .execute()
        )

        row = getattr(res, "data", None) or {}
        return row.get("case_id")
    except Exception as e:
        print(f"[dashboard_service] get_case_id_from_username error: {e}")
        return None


async def get_youth_context(youth_id: str) -> dict:
    """
    Fetch latest worker-facing context for a youth from Supabase worker_updates.
    Returns a dict shaped similarly to the old local context store.
    """
    try:
        supabase = _get_supabase()

        res = (
            supabase.table("worker_updates")
            .select("*")
            .eq("youth_id", youth_id)
            .maybe_single()
            .execute()
        )

        if not res:
            return {}

        row = getattr(res, "data", None) or {}
        if not row:
            return {}

        return {
            "urgency_label": row.get("risk_label"),
            "requires_escalation": row.get("requires_escalation", False),
            "status": "escalated" if row.get("requires_escalation") else "active",
            "key_themes": row.get("key_themes", []),
            "suggested_follow_up": row.get("suggested_follow_up", ""),
            "notes": row.get("summary_text", ""),
            "emotional_state": row.get("emotional_state", "Unknown"),
            "risk_indicators": row.get("risk_indicators", []),
            "overall_risk": row.get("overall_risk"),
            "updated_at": row.get("updated_at"),
            "instagram_username": row.get("instagram_username"),
        }
    except Exception as e:
        print(f"[dashboard_service] get_youth_context error: {e}")
        return {}


async def save_youth_context(youth_id: str, context: dict) -> None:
    """
    Optional helper to write arbitrary context fields into worker_updates.
    """
    try:
        supabase = _get_supabase()

        resolved_youth_id = youth_id
        instagram_username = context.get("instagram_username")
        if instagram_username:
            case_id = await get_case_id_from_username(instagram_username)
            if case_id:
                resolved_youth_id = case_id

        payload = {
            "youth_id": resolved_youth_id,
            "instagram_username": instagram_username,
            "risk_label": context.get("urgency_label"),
            "requires_escalation": context.get("requires_escalation", False),
            "key_themes": context.get("key_themes", []),
            "suggested_follow_up": context.get("suggested_follow_up", ""),
            "summary_text": context.get("notes", ""),
            "emotional_state": context.get("emotional_state", "Unknown"),
            "risk_indicators": context.get("risk_indicators", []),
            "overall_risk": context.get("overall_risk") or context.get("urgency_label"),
            "updated_at": context.get("updated_at"),
        }

        res = (
            supabase.table("worker_updates")
            .upsert(payload, on_conflict="youth_id")
            .execute()
        )

        print("[dashboard_service] save_youth_context response:", res)

    except Exception as e:
        print(f"[dashboard_service] save_youth_context error: {e}")


async def update_youth_session(
    youth_id: str,
    distress_level: Optional[str],
    requires_escalation: Optional[bool],
    key_themes: Optional[list],
    suggested_follow_up: Optional[str],
    instagram_username: Optional[str] = None,
    tldr_notes: Optional[str] = None,
) -> None:
    """
    Upsert latest worker-facing metadata into Supabase worker_updates.
    If instagram_username is provided, resolve its case_id and use that as youth_id.
    """
    try:
        supabase = _get_supabase()

        resolved_youth_id = youth_id
        if instagram_username:
            case_id = await get_case_id_from_username(instagram_username)
            if case_id:
                resolved_youth_id = case_id

        existing_res = (
            supabase.table("worker_updates")
            .select("*")
            .eq("youth_id", resolved_youth_id)
            .maybe_single()
            .execute()
        )

        existing = {}
        if existing_res and getattr(existing_res, "data", None):
            existing = existing_res.data

        payload = {
            "youth_id": resolved_youth_id,
            "instagram_username": (
                instagram_username
                if instagram_username is not None
                else existing.get("instagram_username")
            ),
            "risk_label": distress_level if distress_level is not None else existing.get("risk_label"),
            "requires_escalation": (
                requires_escalation
                if requires_escalation is not None
                else existing.get("requires_escalation", False)
            ),
            "key_themes": key_themes if key_themes is not None else existing.get("key_themes", []),
            "suggested_follow_up": (
                suggested_follow_up
                if suggested_follow_up is not None
                else existing.get("suggested_follow_up", "")
            ),
            "summary_text": (
                tldr_notes
                if tldr_notes is not None
                else existing.get("summary_text", "")
            ),
            "emotional_state": existing.get("emotional_state", "Unknown"),
            "risk_indicators": existing.get("risk_indicators", []),
            "overall_risk": (
                distress_level
                if distress_level is not None
                else existing.get("overall_risk") or existing.get("risk_label")
            ),
        }

        print("[dashboard_service] update_youth_session payload:", payload)

        res = (
            supabase.table("worker_updates")
            .upsert(payload, on_conflict="youth_id")
            .execute()
        )

        print("[dashboard_service] update_youth_session response:", res)

    except Exception as e:
        print(f"[dashboard_service] update_youth_session error: {e}")


async def save_worker_payload(youth_id: str, payload: dict) -> None:
    """
    Save a complete worker payload into worker_updates.
    If instagram_username is present, resolve case_id and use that as youth_id.
    """
    try:
        supabase = _get_supabase()

        risk = payload.get("risk", {})
        summary = payload.get("summary", {})
        instagram_username = payload.get("instagram_username")

        resolved_youth_id = youth_id
        if instagram_username:
            case_id = await get_case_id_from_username(instagram_username)
            if case_id:
                resolved_youth_id = case_id

        db_payload = {
            "youth_id": resolved_youth_id,
            "instagram_username": instagram_username,
            "risk_label": risk.get("label"),
            "requires_escalation": risk.get("requiresEscalation", False),
            "key_themes": risk.get("keyThemes", []),
            "suggested_follow_up": risk.get("suggestedFollowUp", ""),
            "summary_text": summary.get("text", ""),
            "emotional_state": summary.get("emotionalState", "Unknown"),
            "risk_indicators": summary.get("riskIndicators", []),
            "overall_risk": summary.get("overallRisk") or risk.get("label"),
            "updated_at": payload.get("timestamp"),
        }

        res = (
            supabase.table("worker_updates")
            .upsert(db_payload, on_conflict="youth_id")
            .execute()
        )

        print("[dashboard_service] save_worker_payload response:", res)

    except Exception as e:
        print(f"[dashboard_service] save_worker_payload error: {e}")


async def get_worker_payload(youth_id: str) -> dict:
    """
    Return latest raw worker_updates row for this youth.
    """
    try:
        supabase = _get_supabase()

        res = (
            supabase.table("worker_updates")
            .select("*")
            .eq("youth_id", youth_id)
            .maybe_single()
            .execute()
        )

        if not res:
            return {}

        return getattr(res, "data", None) or {}

    except Exception as e:
        print(f"[dashboard_service] get_worker_payload error: {e}")
        return {}