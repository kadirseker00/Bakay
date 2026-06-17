"use client";

import { useRef, useState, useEffect } from "react";
import Logo from "./components/Logo";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type Source = { document: string; snippet: string; score: number };
type Message = {
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
  latency_ms?: number;
  query_id?: string;
  feedback?: "up" | "down";
};
type Health = { indexed_chunks: number; llm_provider: string; embedding_model: string };

const STORAGE_KEY = "bakay_history";

const EXAMPLES = [
  "Bütünleme sınavına kimler girebilir?",
  "Başarı bursu için not ortalaması kaç olmalı?",
  "Üniversiteye kayıt için hangi belgeler gerekli?",
  "Kayıt yenilemeyen öğrenci ne olur?",
];

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [health, setHealth] = useState<Health | null>(null);
  const [menuOpen, setMenuOpen] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      try {
        setMessages(JSON.parse(saved));
      } catch {}
    }
    fetch(`${API_URL}/health`)
      .then((r) => r.json())
      .then(setHealth)
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (messages.length) localStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  function clearHistory() {
    localStorage.removeItem(STORAGE_KEY);
    setMessages([]);
    setMenuOpen(false);
  }

  async function sendFeedback(idx: number, rating: "up" | "down") {
    const msg = messages[idx];
    if (!msg.query_id) return;
    setMessages((m) => m.map((x, i) => (i === idx ? { ...x, feedback: rating } : x)));
    try {
      await fetch(`${API_URL}/feedback`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query_id: msg.query_id, rating }),
      });
    } catch {}
  }

  async function ask(question: string) {
    if (!question.trim() || loading) return;
    setMenuOpen(false);
    setMessages((m) => [...m, { role: "user", content: question }]);
    setInput("");
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      if (!res.ok) throw new Error(`Sunucu hatası: ${res.status}`);
      const data = await res.json();
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          content: data.answer,
          sources: data.sources,
          latency_ms: data.latency_ms,
          query_id: data.query_id,
        },
      ]);
    } catch {
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          content: "⚠ Sunucuya ulaşılamadı. Backend çalışıyor mu? (uvicorn app.main:app)",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="layout">
      {/* ---------- Yan menü ---------- */}
      <aside className={`sidebar ${menuOpen ? "open" : ""}`}>
        <div className="brand">
          <Logo size={42} />
          <div className="brand-text">
            <div className="brand-name">BAKAY</div>
            <div className="brand-sub">Akıllı Kurumsal Asistan</div>
          </div>
        </div>

        <button className="new-chat" onClick={clearHistory}>
          <span>＋</span> Yeni sohbet
        </button>

        <div className="nav-label">Örnek sorular</div>
        <nav className="nav">
          {EXAMPLES.map((ex) => (
            <button key={ex} className="nav-item" onClick={() => ask(ex)}>
              {ex}
            </button>
          ))}
        </nav>

        <div className="sidebar-foot">
          <div className="status">
            <span className={`dot ${health ? "on" : "off"}`} />
            {health ? "Bağlı" : "Bağlantı yok"}
          </div>
          {health && (
            <div className="foot-meta">
              <div>{health.indexed_chunks} belge parçası indeksli</div>
              <div className="muted">Model: {health.llm_provider}</div>
            </div>
          )}
          <div className="foot-org">Kırgızistan-Türkiye Manas Üniversitesi · BAP</div>
        </div>
      </aside>

      {menuOpen && <div className="backdrop" onClick={() => setMenuOpen(false)} />}

      {/* ---------- Ana alan ---------- */}
      <main className="main">
        <header className="topbar">
          <button className="hamburger" onClick={() => setMenuOpen(true)} aria-label="Menü">
            ☰
          </button>
          <div className="topbar-title">
            <Logo size={26} />
            <span>BAKAY</span>
          </div>
        </header>

        <div className="messages">
          {messages.length === 0 && (
            <div className="welcome">
              <Logo size={64} />
              <h2>Merhaba, ben BAKAY 👋</h2>
              <p>
                KTMÜ’nün resmi belgelerine dayanarak yönetmelikler, burslar, kayıt
                ve sınavlar hakkındaki sorularınızı <strong>kaynak göstererek</strong>{" "}
                yanıtlarım.
              </p>
              <div className="welcome-examples">
                {EXAMPLES.slice(0, 3).map((ex) => (
                  <button key={ex} className="chip" onClick={() => ask(ex)}>
                    {ex}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((m, i) => (
            <div key={i} className={`row ${m.role}`}>
              {m.role === "assistant" && (
                <div className="avatar">
                  <Logo size={30} />
                </div>
              )}
              <div className={`bubble ${m.role}`}>
                <div className="bubble-text">{m.content}</div>
                {m.sources && m.sources.length > 0 && (
                  <details className="sources">
                    <summary>📄 {m.sources.length} kaynak belge</summary>
                    {m.sources.map((s, j) => (
                      <div key={j} className="source">
                        <div className="source-head">
                          <span className="doc">[{j + 1}] {s.document}</span>
                          <span className="score">%{(s.score * 100).toFixed(0)} benzerlik</span>
                        </div>
                        <div className="snippet">{s.snippet}…</div>
                      </div>
                    ))}
                  </details>
                )}
                {m.role === "assistant" && m.query_id && (
                  <div className="actions">
                    {m.latency_ms != null && (
                      <span className="meta">⏱ {(m.latency_ms / 1000).toFixed(1)} sn</span>
                    )}
                    <button
                      className={`fb ${m.feedback === "up" ? "active" : ""}`}
                      onClick={() => sendFeedback(i, "up")}
                      disabled={!!m.feedback}
                      title="Yararlı"
                    >
                      👍
                    </button>
                    <button
                      className={`fb ${m.feedback === "down" ? "active" : ""}`}
                      onClick={() => sendFeedback(i, "down")}
                      disabled={!!m.feedback}
                      title="Yararlı değil"
                    >
                      👎
                    </button>
                    {m.feedback && <span className="meta">teşekkürler 🙏</span>}
                  </div>
                )}
              </div>
            </div>
          ))}

          {loading && (
            <div className="row assistant">
              <div className="avatar">
                <Logo size={30} />
              </div>
              <div className="bubble assistant dots">
                <span>●</span> <span>●</span> <span>●</span>
              </div>
            </div>
          )}
          <div ref={endRef} />
        </div>

        <div className="composer-wrap">
          <div className="composer">
            <textarea
              rows={1}
              value={input}
              placeholder="KTMÜ hakkında bir soru sorun…"
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  ask(input);
                }
              }}
            />
            <button className="send" onClick={() => ask(input)} disabled={loading || !input.trim()}>
              ➤
            </button>
          </div>
          <div className="disclaimer">
            BAKAY resmi belgelere dayanır; önemli kararlarda kaynağı teyit edin.
          </div>
        </div>
      </main>
    </div>
  );
}
