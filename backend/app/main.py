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
    get_or_create_chat_link_by_username,
)

app = FastAPI(title="Delli Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    messages: list
    youthId: str
    instagramUsername: Optional[str] = None
    previousContext: Optional[str] = None


class TldrRequest(BaseModel):
    conversation: str
    youthId: str
    instagramUsername: Optional[str] = None


class SessionData(BaseModel):
    youthId: str
    distressLevel: str
    requiresEscalation: bool
    keyThemes: Optional[list] = []
    suggestedFollowUp: Optional[str] = ""
    instagramUsername: Optional[str] = None


class CreateLinkRequest(BaseModel):
    youthId: str
    instagramUsername: Optional[str] = None


class UsernameLookupRequest(BaseModel):
    instagramUsername: str


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/api/context/{youth_id}")
async def get_context(youth_id: str):
    data = await get_youth_context(youth_id)
    return data


@app.get("/api/session/{youth_id}")
async def get_session(youth_id: str):
    data = await get_youth_context(youth_id)

    return {
        "distressLevel": data.get("urgency_label", "low"),
        "requiresEscalation": data.get("requires_escalation", False),
        "keyThemes": data.get("key_themes", []),
        "suggestedFollowUp": data.get("suggested_follow_up", ""),
        "notes": data.get("notes"),
        "instagramUsername": data.get("instagram_username"),
    }


@app.post("/api/chat")
async def chat_route(body: ChatRequest):
    result = await chat(
        messages=body.messages,
        youth_id=body.youthId,
        previous_context=body.previousContext,
    )
    return result


@app.post("/api/session")
async def save_session(body: SessionData):
    await update_youth_session(
        youth_id=body.youthId,
        distress_level=body.distressLevel,
        requires_escalation=body.requiresEscalation,
        key_themes=body.keyThemes,
        suggested_follow_up=body.suggestedFollowUp,
        instagram_username=body.instagramUsername,
    )

    return {"ok": True}


@app.post("/api/tldr")
async def tldr_route(body: TldrRequest):
    summary = await generate_tldr(body.conversation)

    await update_youth_session(
        youth_id=body.youthId,
        distress_level=None,
        requires_escalation=None,
        key_themes=None,
        suggested_follow_up=None,
        instagram_username=body.instagramUsername,
        tldr_notes=summary.get("summary") if isinstance(summary, dict) else str(summary),
    )

    return {"summary": summary}


@app.get("/api/worker-json/{youth_id}")
async def get_worker_json(youth_id: str):
    context = await get_youth_context(youth_id)
    return build_worker_payload(youth_id, context)


@app.post("/api/links/create")
async def create_link(body: CreateLinkRequest):
    record = await create_chat_token(body.youthId, body.instagramUsername)

    if not record or "token" not in record:
        return {
            "ok": False,
            "error": "Failed to create chat link"
        }

    return {
        "ok": True,
        "youthId": record["youthId"],
        "instagramUsername": record.get("instagramUsername"),
        "token": record["token"],
        "chatUrl": record["chatUrl"],
    }


@app.post("/api/links/get-or-create-by-username")
async def get_or_create_link_by_username(body: UsernameLookupRequest):
    return await get_or_create_chat_link_by_username(body.instagramUsername)


@app.get("/api/links/resolve/{token}")
async def resolve_link(token: str):
    record = await resolve_chat_token(token)

    if not record:
        return {"ok": False}

    return {
        "ok": True,
        "youthId": record["youthId"],
        "instagramUsername": record.get("instagramUsername"),
    }


@app.post("/api/links/deactivate/{token}")
async def deactivate_link(token: str):
    ok = await deactivate_chat_token(token)
    return {"ok": ok}