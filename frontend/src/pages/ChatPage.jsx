import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import YouthChatbot from "../components/YouthChatbot";

const CHATBOT_API = import.meta.env.VITE_CHATBOT_API_URL || "http://localhost:8001";

export default function ChatPage() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token");
  const directYouthId = searchParams.get("id");
  const directInstagramUsername = searchParams.get("username");

  const [youthId, setYouthId] = useState(directYouthId || null);
  const [instagramUsername, setInstagramUsername] = useState(
    directInstagramUsername || null
  );
  const [loading, setLoading] = useState(!directYouthId && !!token);

  const [usernameInput, setUsernameInput] = useState("");
  const [lookupLoading, setLookupLoading] = useState(false);
  const [lookupError, setLookupError] = useState("");
  const [linkMessage, setLinkMessage] = useState("");

  useEffect(() => {
    if (directYouthId) return;
    if (!token) return;

    fetch(`${CHATBOT_API}/api/links/resolve/${token}`)
      .then((r) => r.json())
      .then((data) => {
        if (data.ok && data.youthId) {
          setYouthId(data.youthId);
          setInstagramUsername(data.instagramUsername || null);
        }
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [token, directYouthId]);

  const handleUsernameSubmit = async () => {
    const clean = usernameInput.trim().replace(/^@/, "");
    if (!clean) return;

    setLookupLoading(true);
    setLookupError("");
    setLinkMessage("");

    try {
      const response = await fetch(
        `${CHATBOT_API}/api/links/get-or-create-by-username`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            instagramUsername: clean,
          }),
        }
      );

      const data = await response.json();

      if (!data.ok) {
        setLookupError(data.error || "Could not find your username in the system.");
        return;
      }

      setLinkMessage(
        data.existing
          ? "We found your existing chat link. Please keep using the same one."
          : "Your chat link has been created. Please save it and keep using the same link."
      );

      window.location.href = data.chatUrl;
    } catch {
      setLookupError("Something went wrong. Please try again.");
    } finally {
      setLookupLoading(false);
    }
  };

  if (loading) {
    return (
      <div
        style={{
          minHeight: "100vh",
          width: "100%",
          background: "#0f1117",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          color: "#94a3b8",
          fontFamily: "DM Sans, sans-serif",
        }}
      >
        Loading chat...
      </div>
    );
  }

  if (!youthId && !token) {
    return (
      <div
        style={{
          minHeight: "100vh",
          width: "100%",
          background:
            "linear-gradient(135deg, #0f1117 0%, #1a1f2e 50%, #0f1117 100%)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          padding: "16px",
          fontFamily: "'DM Sans', 'Helvetica Neue', sans-serif",
        }}
      >
        <div
          style={{
            width: "100%",
            maxWidth: "420px",
            background: "#13161e",
            borderRadius: "24px",
            border: "1px solid #1e2433",
            boxShadow: "0 32px 80px rgba(0,0,0,0.6)",
            padding: "28px 24px",
            textAlign: "center",
          }}
        >
          <div style={{ fontSize: "34px", marginBottom: "12px" }}>💚</div>

          <div
            style={{
              fontFamily: "'Syne', sans-serif",
              fontWeight: 800,
              fontSize: "22px",
              color: "#f0f4ff",
              marginBottom: "10px",
            }}
          >
            Welcome to Delli
          </div>

          <div
            style={{
              fontSize: "13px",
              color: "#94a3b8",
              lineHeight: "1.6",
              marginBottom: "18px",
            }}
          >
            Enter your Instagram username to continue. If you already have a chat
            link, we’ll bring it back. If not, we’ll create one for you.
          </div>

          <div
            style={{
              display: "flex",
              flexDirection: "column",
              gap: "12px",
              width: "100%",
            }}
          >
            <input
              value={usernameInput}
              onChange={(e) => setUsernameInput(e.target.value)}
              placeholder="@yourusername"
              onKeyDown={(e) => {
                if (e.key === "Enter") handleUsernameSubmit();
              }}
              style={{
                width: "100%",
                boxSizing: "border-box",
                display: "block",
                background: "#1a1f2e",
                border: "1px solid #2d3748",
                borderRadius: "14px",
                color: "#e2e8f0",
                fontSize: "14px",
                padding: "14px 16px",
                outline: "none",
              }}
            />

            <button
              onClick={handleUsernameSubmit}
              disabled={lookupLoading || !usernameInput.trim()}
              style={{
                width: "100%",
                boxSizing: "border-box",
                display: "block",
                padding: "12px",
                background: usernameInput.trim()
                  ? "linear-gradient(135deg, #6ee7b7, #3b82f6)"
                  : "#2d3748",
                border: "none",
                borderRadius: "14px",
                color: "#0f1117",
                fontWeight: 700,
                fontSize: "14px",
                cursor: usernameInput.trim() ? "pointer" : "default",
              }}
            >
              {lookupLoading ? "Checking..." : "Continue"}
            </button>
          </div>

          {lookupError && (
            <div
              style={{
                marginTop: "14px",
                fontSize: "12px",
                color: "#fca5a5",
              }}
            >
              {lookupError}
            </div>
          )}

          {linkMessage && (
            <div
              style={{
                marginTop: "14px",
                fontSize: "12px",
                color: "#86efac",
              }}
            >
              {linkMessage}
            </div>
          )}

          <div
            style={{
              marginTop: "18px",
              fontSize: "11px",
              color: "#64748b",
              lineHeight: "1.5",
            }}
          >
            Please keep your chat link safe and reuse the same one.
          </div>
        </div>
      </div>
    );
  }

  if (!youthId) {
    return (
      <div
        style={{
          minHeight: "100vh",
          width: "100%",
          background: "#0f1117",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          color: "#94a3b8",
          fontFamily: "DM Sans, sans-serif",
          flexDirection: "column",
          gap: "12px",
        }}
      >
        <div style={{ fontSize: "32px" }}>💚</div>
        <div>Invalid or expired link.</div>
      </div>
    );
  }

  return (
    <YouthChatbot
      youthId={youthId}
      instagramUsername={instagramUsername}
    />
  );
}