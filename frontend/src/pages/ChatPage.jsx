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
  const [instagramUsername, setInstagramUsername] = useState(directInstagramUsername || null);
  const [loading, setLoading] = useState(!directYouthId && !!token);

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

  if (loading) {
    return (
      <div
        style={{
          minHeight: "100vh",
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

  if (!youthId) {
    return (
      <div
        style={{
          minHeight: "100vh",
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