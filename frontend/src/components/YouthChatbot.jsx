import { useState, useRef, useEffect } from "react";

const CHATBOT_API = import.meta.env.VITE_CHATBOT_API_URL || "http://localhost:8001";

export default function YouthChatbot({ youthId, instagramUsername }) {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content: "Hey, I'm Delli 👋 I'm here to listen, no judgment. What's on your mind today?",
      workerData: null,
      id: 0,
    },
  ]);

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [loadingContext, setLoadingContext] = useState(true);
  const [youthContext, setYouthContext] = useState(null);
  const bottomRef = useRef(null);

  useEffect(() => {
    if (!youthId) return;

    fetch(`${CHATBOT_API}/api/context/${youthId}`)
      .then((r) => r.json())
      .then((data) => {
        setYouthContext(data);

        if (data.display_name) {
          setMessages([
            {
              role: "assistant",
              content: `Hey ${data.display_name} 👋 Good to see you again. I'm here to listen — what's on your mind?`,
              workerData: null,
              id: 0,
            },
          ]);
        }
      })
      .catch(() => {})
      .finally(() => setLoadingContext(false));
  }, [youthId]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const saveSession = async (workerData) => {
    if (!youthId) return;

    try {
      await fetch(`${CHATBOT_API}/api/session`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          youthId,
          instagramUsername,
          distressLevel: workerData?.distressLevel || "low",
          requiresEscalation: workerData?.requiresEscalation || false,
          keyThemes: workerData?.keyThemes || [],
          suggestedFollowUp: workerData?.suggestedFollowUp || "",
        }),
      });
    } catch {}
  };

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMsg = {
      role: "user",
      content: input.trim(),
      id: Date.now(),
    };

    const newMessages = [...messages, userMsg];
    setMessages(newMessages);
    setInput("");
    setLoading(true);

    const apiMessages = newMessages.map((m) => ({
      role: m.role,
      content: m.content,
    }));

    try {
      const response = await fetch(`${CHATBOT_API}/api/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          messages: apiMessages,
          youthId,
          instagramUsername,
          previousContext: youthContext?.notes || null,
        }),
      });

      const data = await response.json();

      const workerData = {
        distressLevel: data.distressLevel || "low",
        keyThemes: data.keyThemes || [],
        suggestedFollowUp: data.suggestedFollowUp || "",
        requiresEscalation: data.requiresEscalation || false,
      };

      const assistantMsg = {
        role: "assistant",
        content: data.reply || "Sorry, something went wrong.",
        workerData,
        id: Date.now() + 1,
      };

      setMessages((prev) => [...prev, assistantMsg]);
      await saveSession(workerData);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Eh sorry, I'm having a little trouble connecting. Try again in a bit?",
          workerData: null,
          id: Date.now() + 1,
        },
      ]);
    }

    setLoading(false);
  };

  if (loadingContext) {
    return (
      <div
        style={{
          minHeight: "100vh",
          background: "#0f1117",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <div
          style={{
            color: "#4ade80",
            fontFamily: "DM Sans, sans-serif",
            fontSize: "14px",
          }}
        >
          Loading...
        </div>
      </div>
    );
  }

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "linear-gradient(135deg, #0f1117 0%, #1a1f2e 50%, #0f1117 100%)",
        fontFamily: "'DM Sans', 'Helvetica Neue', sans-serif",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "16px",
      }}
    >
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=Syne:wght@700;800&display=swap');
        * { box-sizing: border-box; }
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-thumb { background: #2d3748; border-radius: 4px; }
        .msg-in { animation: slideIn 0.25s ease; }
        @keyframes slideIn { from { opacity:0; transform:translateY(10px); } to { opacity:1; transform:translateY(0); } }
        .pulse { animation: pulse 2s infinite; }
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }
        .send-btn:hover { transform: scale(1.05); }
        textarea:focus { outline: none; }
      `}</style>

      <div
        style={{
          width: "100%",
          maxWidth: "440px",
          background: "#13161e",
          borderRadius: "24px",
          border: "1px solid #1e2433",
          boxShadow: "0 32px 80px rgba(0,0,0,0.6)",
          overflow: "hidden",
          display: "flex",
          flexDirection: "column",
          height: "min(88vh, 780px)",
        }}
      >
        <div
          style={{
            padding: "18px 20px 16px",
            borderBottom: "1px solid #1e2433",
            display: "flex",
            alignItems: "center",
            gap: "12px",
            background: "linear-gradient(180deg, #161b27 0%, #13161e 100%)",
          }}
        >
          <div
            style={{
              width: 42,
              height: 42,
              borderRadius: "14px",
              background: "linear-gradient(135deg, #6ee7b7, #3b82f6)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: "18px",
              flexShrink: 0,
            }}
          >
            💚
          </div>

          <div style={{ flex: 1 }}>
            <div
              style={{
                fontFamily: "'Syne', sans-serif",
                fontWeight: 800,
                fontSize: "15px",
                color: "#f0f4ff",
              }}
            >
              Delli
            </div>
            <div
              style={{
                fontSize: "11px",
                color: "#4ade80",
                display: "flex",
                alignItems: "center",
                gap: "5px",
              }}
            >
              <span
                style={{
                  width: 6,
                  height: 6,
                  borderRadius: "50%",
                  background: "#4ade80",
                  display: "inline-block",
                }}
                className="pulse"
              />
              Always here for you
            </div>
          </div>
        </div>

        <div style={{ flex: 1, overflow: "auto", padding: "16px 16px 8px" }}>
          {messages.map((m) => (
            <div
              key={m.id}
              className="msg-in"
              style={{
                display: "flex",
                justifyContent: m.role === "user" ? "flex-end" : "flex-start",
                marginBottom: "10px",
              }}
            >
              {m.role === "assistant" && (
                <div
                  style={{
                    width: 28,
                    height: 28,
                    borderRadius: "10px",
                    background: "linear-gradient(135deg, #6ee7b7, #3b82f6)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: "13px",
                    marginRight: "8px",
                    flexShrink: 0,
                    alignSelf: "flex-end",
                  }}
                >
                  💚
                </div>
              )}

              <div
                style={{
                  maxWidth: "75%",
                  padding: "10px 14px",
                  borderRadius:
                    m.role === "user" ? "18px 18px 4px 18px" : "18px 18px 18px 4px",
                  background:
                    m.role === "user"
                      ? "linear-gradient(135deg, #3b82f6, #6366f1)"
                      : "#1e2433",
                  color: "#e8edf5",
                  fontSize: "13.5px",
                  lineHeight: "1.55",
                  border: m.role === "assistant" ? "1px solid #2d3748" : "none",
                  whiteSpace: "pre-wrap",
                }}
              >
                {m.content}
              </div>
            </div>
          ))}

          {loading && (
            <div
              className="msg-in"
              style={{
                display: "flex",
                alignItems: "flex-end",
                gap: "8px",
                marginBottom: "10px",
              }}
            >
              <div
                style={{
                  width: 28,
                  height: 28,
                  borderRadius: "10px",
                  background: "linear-gradient(135deg, #6ee7b7, #3b82f6)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: "13px",
                }}
              >
                💚
              </div>

              <div
                style={{
                  background: "#1e2433",
                  border: "1px solid #2d3748",
                  borderRadius: "18px 18px 18px 4px",
                  padding: "12px 16px",
                  display: "flex",
                  gap: "5px",
                  alignItems: "center",
                }}
              >
                {[0, 0.2, 0.4].map((d, i) => (
                  <div
                    key={i}
                    style={{
                      width: 6,
                      height: 6,
                      borderRadius: "50%",
                      background: "#4ade80",
                      animation: `pulse 1.2s ${d}s infinite`,
                    }}
                  />
                ))}
              </div>
            </div>
          )}

          <div ref={bottomRef} />
        </div>

        <div style={{ padding: "12px 16px 16px", borderTop: "1px solid #1e2433" }}>
          <div
            style={{
              display: "flex",
              gap: "10px",
              alignItems: "flex-end",
              background: "#1a1f2e",
              borderRadius: "16px",
              border: "1px solid #2d3748",
              padding: "8px 8px 8px 14px",
            }}
          >
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  sendMessage();
                }
              }}
              placeholder="Type here, no pressure..."
              rows={1}
              style={{
                flex: 1,
                background: "transparent",
                border: "none",
                color: "#e2e8f0",
                fontSize: "13.5px",
                resize: "none",
                fontFamily: "'DM Sans', sans-serif",
                lineHeight: "1.5",
                maxHeight: "100px",
                paddingTop: "2px",
              }}
            />
            <button
              onClick={sendMessage}
              disabled={!input.trim() || loading}
              className="send-btn"
              style={{
                width: 36,
                height: 36,
                borderRadius: "12px",
                background: input.trim()
                  ? "linear-gradient(135deg, #6ee7b7, #3b82f6)"
                  : "#2d3748",
                border: "none",
                cursor: input.trim() ? "pointer" : "default",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: "15px",
                flexShrink: 0,
                transition: "all 0.2s",
              }}
            >
              {loading ? "⏳" : "↑"}
            </button>
          </div>

          <div
            style={{
              textAlign: "center",
              fontSize: "10px",
              color: "#374151",
              marginTop: "8px",
            }}
          >
            If you're in crisis, call SOS 1-767 · IMH 6389-2222
          </div>
        </div>
      </div>
    </div>
  );
}