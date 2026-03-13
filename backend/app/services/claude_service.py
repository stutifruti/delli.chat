import google.generativeai as genai
import os
import json

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-3-flash-preview")

SYSTEM_PROMPT = """You are a warm, non-judgmental support companion called "Delli" for a youth outreach platform in Singapore called VOX. You talk to young people (aged 13–21) who may be experiencing emotional distress.

Your role:
- Be a compassionate, safe space for youths to express themselves
- Use casual, friendly language appropriate for Singaporean youth
- ALWAYS validate feelings before offering perspective
- If there is risk of self-harm or suicide, respond supportively and encourage immediate real-world help

Respond ONLY with valid JSON, no markdown, no backticks.

Schema:
{
  "reply": "string",
  "distressLevel": "low|moderate|high|critical",
  "keyThemes": ["string"],
  "suggestedFollowUp": "string",
  "requiresEscalation": true
}
"""

async def chat(messages: list, youth_id: str = None, previous_context: str = None) -> dict:
    system = SYSTEM_PROMPT
    if previous_context:
        system += f"\n\nPREVIOUS WORKER NOTES:\n{previous_context}"

    history = []
    for m in messages[:-1]:
        history.append({
            "role": "user" if m["role"] == "user" else "model",
            "parts": [m["content"]]
        })

    chat_session = model.start_chat(history=history)
    last_message = messages[-1]["content"]

    response = chat_session.send_message(f"{system}\n\nUSER MESSAGE:\n{last_message}")
    raw = response.text.strip()

    try:
        parsed = json.loads(raw)
        return {
            "reply": parsed.get("reply", ""),
            "distressLevel": parsed.get("distressLevel", "low"),
            "keyThemes": parsed.get("keyThemes", []),
            "suggestedFollowUp": parsed.get("suggestedFollowUp", ""),
            "requiresEscalation": parsed.get("requiresEscalation", False),
        }
    except json.JSONDecodeError:
        return {
            "reply": raw,
            "distressLevel": "low",
            "keyThemes": [],
            "suggestedFollowUp": "",
            "requiresEscalation": False,
        }


async def generate_tldr(conversation_text: str) -> dict:
    prompt = f"""Summarise this for the next youth worker. Respond ONLY with valid JSON, no backticks:
{{"summary":"...","emotionalState":"...","riskIndicators":["..."],"suggestedFollowUp":"...","overallRisk":"low|moderate|high|critical"}}

CONVERSATION:
{conversation_text}"""

    response = model.generate_content(prompt)
    raw = response.text.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {
            "summary": raw,
            "emotionalState": "Unknown",
            "riskIndicators": [],
            "suggestedFollowUp": "Review manually.",
            "overallRisk": "low"
        }