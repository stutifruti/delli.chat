import json
import os
from pathlib import Path
from typing import Optional
from datetime import datetime, timezone

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

CONTEXT_FILE = DATA_DIR / "youth_context.json"
WORKER_PAYLOADS_DIR = DATA_DIR / "worker_payloads"
WORKER_PAYLOADS_DIR.mkdir(parents=True, exist_ok=True)


def _read_json_file(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _write_json_file(path: Path, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


async def get_youth_context(youth_id: str) -> dict:
    """
    Fetch local youth context from chatbot backend storage.
    This is completely independent from any external dashboard.
    """
    data = _read_json_file(CONTEXT_FILE)
    return data.get(youth_id, {})


async def save_youth_context(youth_id: str, context: dict) -> None:
    """
    Save or update youth context locally.
    """
    data = _read_json_file(CONTEXT_FILE)
    existing = data.get(youth_id, {})
    existing.update(context)
    data[youth_id] = existing
    _write_json_file(CONTEXT_FILE, data)


async def update_youth_session(
    youth_id: str,
    distress_level: Optional[str],
    requires_escalation: Optional[bool],
    key_themes: Optional[list],
    suggested_follow_up: Optional[str],
    tldr_notes: Optional[str] = None,
) -> None:
    context_data = _read_json_file(CONTEXT_FILE)
    existing = context_data.get(youth_id, {})

    if distress_level is not None:
        existing["urgency_label"] = distress_level

    if requires_escalation is not None:
        existing["requires_escalation"] = requires_escalation
        existing["status"] = "escalated" if requires_escalation else "active"

    if key_themes is not None:
        existing["key_themes"] = key_themes

    if suggested_follow_up is not None:
        existing["suggested_follow_up"] = suggested_follow_up

    if tldr_notes is not None:
        existing["notes"] = tldr_notes

    existing["updated_at"] = datetime.now(timezone.utc).isoformat()

    context_data[youth_id] = existing
    _write_json_file(CONTEXT_FILE, context_data)


async def save_worker_payload(youth_id: str, payload: dict) -> None:
    """
    Save the latest worker JSON as a standalone file for easy extraction.
    """
    output_path = WORKER_PAYLOADS_DIR / f"{youth_id}.json"
    _write_json_file(output_path, payload)


async def get_worker_payload(youth_id: str) -> dict:
    """
    Return the saved worker JSON file if it exists.
    """
    output_path = WORKER_PAYLOADS_DIR / f"{youth_id}.json"
    return _read_json_file(output_path)