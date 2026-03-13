from datetime import datetime, timezone


def build_worker_payload(youth_id: str, context: dict) -> dict:
    return {
        "youthId": youth_id,
        "timestamp": context.get("updated_at") or datetime.now(timezone.utc).isoformat(),
        "risk": {
            "label": context.get("urgency_label", "low"),
            "requiresEscalation": context.get("requires_escalation", False),
            "keyThemes": context.get("key_themes", []),
            "suggestedFollowUp": context.get("suggested_follow_up", ""),
        },
        "summary": {
            "text": context.get("notes", ""),
            "emotionalState": context.get("emotional_state", "Unknown"),
            "riskIndicators": context.get("risk_indicators", []),
            "overallRisk": context.get("urgency_label", "low"),
        }
    }