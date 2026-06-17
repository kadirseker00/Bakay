"use client";

import { useRef, useState, useEffect } from "react";

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

const STORAGE_KEY = "bakay_history";

const EXAMPLES = [
  "Bütünleme sınavına kimler girebilir?",
  "Başarı bursu için not ortalaması kaç olmalı?",
  "Kayıt yenilemeyen öğrenci ne olur?",
];

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  // Sohbet geçmişini tarayıcıda sakla (yeniden yüklemede korunur)
  useEffect(() => {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      try {
        setMessages(JSON.parse(saved));
      } catch {}
    }
  }, []);

  useEffect(() => {
    if (messages.length) localStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  function clearHistory() {
    localStorage.removeItem(STORAGE_KEY);
    setMessages([]);
  }

  async function sendFeedback(idx: number, rating: "up" | "down") {
    const msg = messages[idx];
    if (!msg.query_id) return;
    setMessages((m) =>
      m.map((x, i) => (i === idx ? { ...x, feedback: rating } : x))
    );
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
    } catch (e) {
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          content:
            "⚠ Sunucuya ulaşılamadı. Backend çalışıyor mu? (uvicorn app.main:app)",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <header className="header">
        <div className="header-row">
          <div>
            <h1>🗿 BAKAY</h1>
            <div className="sub">
              KTMÜ resmi belgelerine dayalı, kaynak gösteren kurumsal asistan
            </div>
          </div>
          {messages.length > 0 && (
            <button className="clear" onClick={clearHistory} title="Geçmişi temizle">
              🗑 Temizle
            </button>
          )}
        </div>
      </header>

      <div className="messages">
        {messages.length === 0 && (
          <div className="empty">
            Üniversite yönetmelikleri, burslar, kayıt ve sınavlar hakkında
            soru sorun.
            <div className="examples">
              {EXAMPLES.map((ex) => (
                <button key={ex} className="example" onClick={() => ask(ex)}>
                  {ex}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((m, i) => (
          <div key={i} className={`row ${m.role}`}>
            <div className={`bubble ${m.role}`}>
              {m.content}
              {m.sources && m.sources.length > 0 && (
                <details className="sources">
                  <summary>📄 {m.sources.length} kaynak</summary>
                  {m.sources.map((s, j) => (
                    <div key={j} className="source">
                      <span className="score">{(s.score * 100).toFixed(0)}%</span>
                      <span className="doc">[{j + 1}] {s.document}</span>
                      <div>{s.snippet}…</div>
                    </div>
                  ))}
                </details>
              )}
              {m.role === "assistant" && m.query_id && (
                <div className="actions">
                  {m.latency_ms != null && (
                    <span className="meta">{(m.latency_ms / 1000).toFixed(1)} sn</span>
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
                  {m.feedback && <span className="meta">geri bildirim alındı, teşekkürler</span>}
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="row assistant">
            <div className="bubble assistant dots">
              <span>●</span> <span>●</span> <span>●</span>
            </div>
          </div>
        )}
        <div ref={endRef} />
      </div>

      <div className="composer">
        <textarea
          rows={1}
          value={input}
          placeholder="Sorunuzu yazın…"
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              ask(input);
            }
          }}
        />
        <button onClick={() => ask(input)} disabled={loading || !input.trim()}>
          Sor
        </button>
      </div>
    </div>
  );
}
