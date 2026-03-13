import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

from app.services.claude_service import chat, generate_tldr
from app.services.dashboard_service import get_youth_context, update_youth_session
from app.services.worker_payload_service import build_worker_payload
from app.services.token_service import (
    create_chat_token,
    resolve_chat_token,
    deactivate_chat_token,
)

app = FastAPI(title="Delli Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request models ─────────────────────────────────────────────

class ChatRequest(BaseModel):
    messages: list
    youthId: str
    previousContext: Optional[str] = None


class TldrRequest(BaseModel):
    conversation: str
    youthId: str


class SessionData(BaseModel):
    youthId: str
    distressLevel: str
    requiresEscalation: bool
    keyThemes: Optional[list] = []
    suggestedFollowUp: Optional[str] = ""


class CreateLinkRequest(BaseModel):
    youthId: str


# ── Basic health check ─────────────────────────────────────────

@app.get("/health")
def health():
    return {"ok": True}


# ── Fetch youth context ────────────────────────────────────────

@app.get("/api/context/{youth_id}")
async def get_context(youth_id: str):
    """Fetch youth profile/context for Delli."""
    data = await get_youth_context(youth_id)
    return data


# ── Optional: expose latest session state ──────────────────────

@app.get("/api/session/{youth_id}")
async def get_session(youth_id: str):
    """Expose latest saved session state for external dashboards."""
    data = await get_youth_context(youth_id)

    return {
        "distressLevel": data.get("urgency_label", "low"),
        "requiresEscalation": data.get("requires_escalation", False),
        "keyThemes": data.get("key_themes", []),
        "suggestedFollowUp": data.get("suggested_follow_up", ""),
        "notes": data.get("notes"),
    }


# ── Chat endpoint (youth-facing) ───────────────────────────────

@app.post("/api/chat")
async def chat_route(body: ChatRequest):
    """Generate youth-facing chatbot reply plus worker metadata."""
    result = await chat(
        messages=body.messages,
        youth_id=body.youthId,
        previous_context=body.previousContext,
    )
    return result


# ── Save worker session metadata ───────────────────────────────

@app.post("/api/session")
async def save_session(body: SessionData):
    """Save latest worker-facing metadata."""
    await update_youth_session(
        youth_id=body.youthId,
        distress_level=body.distressLevel,
        requires_escalation=body.requiresEscalation,
        key_themes=body.keyThemes,
        suggested_follow_up=body.suggestedFollowUp,
    )

    return {"ok": True}


# ── Generate TLDR summary ──────────────────────────────────────

@app.post("/api/tldr")
async def tldr_route(body: TldrRequest):
    """Generate TLDR summary and save it for worker/dashboard use."""
    summary = await generate_tldr(body.conversation)

    await update_youth_session(
        youth_id=body.youthId,
        distress_level=None,
        requires_escalation=None,
        key_themes=None,
        suggested_follow_up=None,
        tldr_notes=summary.get("summary") if isinstance(summary, dict) else str(summary),
    )

    return {"summary": summary}


# ── Worker JSON endpoint ───────────────────────────────────────

@app.get("/api/worker-json/{youth_id}")
async def get_worker_json(youth_id: str):
    """
    Return a clean structured JSON payload for the worker dashboard.
    """
    context = await get_youth_context(youth_id)
    return build_worker_payload(youth_id, context)


# ── Unique chat link/token routes ──────────────────────────────

@app.post("/api/links/create")
async def create_link(body: CreateLinkRequest):
    """
    Create a unique token-based chat link for a youth.
    """
    record = await create_chat_token(body.youthId)

    if not record or "token" not in record:
        return {
            "ok": False,
            "error": "Failed to create chat link"
        }

    return {
        "ok": True,
        "youthId": record["youthId"],
        "token": record["token"],
        "chatUrl": record["chatUrl"],
    }


@app.get("/api/links/resolve/{token}")
async def resolve_link(token: str):
    """
    Resolve a public chat token to its internal youthId.
    """
    record = await resolve_chat_token(token)

    if not record:
        return {"ok": False}

    return {
        "ok": True,
        "youthId": record["youthId"],
    }


@app.post("/api/links/deactivate/{token}")
async def deactivate_link(token: str):
    """
    Deactivate a token so the chat link stops working.
    """
    ok = await deactivate_chat_token(token)
    return {"ok": ok}