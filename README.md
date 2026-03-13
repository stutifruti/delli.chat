# delli.chat
Chatbot for delli.cate

This repository contains the backend service for the **Delli AI youth support chatbot**.

The backend is responsible for:

* Handling chatbot conversations
* Running AI analysis on messages
* Generating **risk scores and summaries**
* Storing worker-facing insights in **Supabase**
* Generating **unique chat links** for youths
* Providing APIs for the **worker dashboard**

The dashboard frontend lives in a **separate repository** and communicates with this backend via HTTP APIs.

---

# Architecture Overview

```
Youth
   ↓
Chat Link
   ↓
Frontend Chat UI
   ↓
Chatbot Backend (this repo)
   ↓
Gemini AI analysis
   ↓
Supabase database
   ↓
Worker Dashboard
```

The backend performs the AI analysis and stores results that the worker dashboard can display.

---

# Prerequisites

Make sure you have:

* Python **3.10+**
* `pip`
* Access to **Supabase credentials**
* A **Gemini API key**

---

# 1. Clone the Repository

```bash
git clone <repo-url>
cd backend
```

---

# 2. Install Dependencies

Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# 3. Environment Variables

Create a `.env` file inside the **backend folder**.

Example:

```
# Gemini AI
GEMINI_API_KEY=your_gemini_api_key_here

# Supabase
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=sb_secret_xxxxxxxxxxxxxx

# Frontend URL (used for generating chat links)
FRONTEND_BASE_URL=http://localhost:5173
```

Explanation:

| Variable          | Purpose                                    |
| ----------------- | ------------------------------------------ |
| GEMINI_API_KEY    | Used for chatbot responses and AI analysis |
| SUPABASE_URL      | Supabase project URL                       |
| SUPABASE_KEY      | Supabase secret key (backend access)       |
| FRONTEND_BASE_URL | Base URL for generating youth chat links   |

⚠️ Do **not commit `.env` files** to Git.

---

# 4. Run the Backend Server

From the backend folder run:

```bash
uvicorn app.main:app --port 8001 --reload
```

The API will start at:

```
http://localhost:8001
```

You can test if it is running:

```
http://localhost:8001/health
```

Expected response:

```
{"ok": true}
```

---

# 5. Key API Endpoints

## Generate Chat Link

Workers can generate a unique chat link for a youth.

```
POST /api/links/create
```

Request:

```json
{
  "youthId": "test123"
}
```

Response:

```json
{
  "ok": true,
  "youthId": "test123",
  "token": "abc123xyz",
  "chatUrl": "http://localhost:5173/chat?token=abc123xyz"
}
```

The `chatUrl` should be sent to the youth.

---

## Resolve Chat Token

When the youth opens the link, the frontend resolves the token:

```
GET /api/links/resolve/{token}
```

This returns the internal `youthId`.

---

## Chat Endpoint

Used by the chatbot frontend.

```
POST /api/chat
```

Processes messages and generates the AI response.

---

## Save Worker Metadata

```
POST /api/session
```

Stores:

* risk level
* escalation flag
* key themes
* suggested follow-up

This data is saved to Supabase.

---

## Worker Dashboard Data

Workers can retrieve AI insights using:

```
GET /api/worker-json/{youthId}
```

Example response:

```json
{
  "youthId": "test123",
  "risk": {
    "label": "moderate",
    "requiresEscalation": false,
    "keyThemes": ["bullying", "self-esteem"]
  },
  "summary": {
    "text": "...",
    "emotionalState": "stressed"
  }
}
```

The worker dashboard can display this data in a UI.

---

# 6. Supabase Tables

The backend interacts with two main tables.

## chat_links

Stores generated chat tokens.

Columns:

* `id`
* `youth_id`
* `token`
* `chat_url`
* `created_at`

---

## worker_updates

Stores AI insights for workers.

Columns:

* `id`
* `youth_id`
* `risk_label`
* `requires_escalation`
* `key_themes`
* `suggested_follow_up`
* `summary_text`
* `emotional_state`
* `risk_indicators`
* `overall_risk`
* `updated_at`

---

# 7. Dashboard Integration (Separate Repo)

The dashboard does **not need this codebase**.

It simply calls the chatbot backend APIs.

### Generate a Chat Link

Dashboard calls:

```
POST http://localhost:8001/api/links/create
```

The returned `chatUrl` can be displayed or copied for the worker to send to the youth.

---

### Display AI Risk Insights

Dashboard can either:

Option A — read directly from Supabase:

```
worker_updates table
```

Option B — call the backend API:

```
GET http://localhost:8001/api/worker-json/{youthId}
```

Recommended UI display:

* Risk level badge (Low / Moderate / High / Critical)
* Escalation warning
* Key themes tags
* Suggested follow-up
* Summary text

---

# 8. Local Development Setup

Typical local setup:

| Service            | Port  |
| ------------------ | ----- |
| Dashboard frontend | 5173  |
| Chatbot backend    | 8001  |
| Supabase           | Cloud |

---

# 9. Quick Test

Generate a test link:

```bash
curl -X POST http://localhost:8001/api/links/create \
-H "Content-Type: application/json" \
-d '{"youthId":"test123"}'
```

Open the returned `chatUrl` and send a message.

Then check the **worker_updates** table in Supabase to confirm the risk analysis was stored.

