import json
import secrets
from pathlib import Path
from datetime import datetime, timezone

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

TOKENS_FILE = DATA_DIR / "chat_tokens.json"


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


async def create_chat_token(youth_id: str) -> dict:
    data = _read_json_file(TOKENS_FILE)

    token = secrets.token_urlsafe(16)

    data[token] = {
        "youthId": youth_id,
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "isActive": True,
    }

    _write_json_file(TOKENS_FILE, data)

    return {
        "token": token,
        "youthId": youth_id,
    }


async def resolve_chat_token(token: str) -> dict:
    data = _read_json_file(TOKENS_FILE)
    record = data.get(token)

    if not record or not record.get("isActive"):
        return {}

    return record


async def deactivate_chat_token(token: str) -> bool:
    data = _read_json_file(TOKENS_FILE)
    if token not in data:
        return False

    data[token]["isActive"] = False
    _write_json_file(TOKENS_FILE, data)
    return True