import { BrowserRouter, Routes, Route } from "react-router-dom";
import ChatPage from "./pages/ChatPage";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>

        {/* Youth chat link */}
        <Route path="/chat" element={<ChatPage />} />

        {/* Fallback */}
        <Route
          path="*"
          element={
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
              Page not found.
            </div>
          }
        />

      </Routes>
    </BrowserRouter>
  );
}