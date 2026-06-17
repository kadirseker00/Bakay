"use client";

import { useRef, useState, useEffect } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type Source = { document: string; snippet: string; score: number };
type Message = {
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
  latency_ms?: number;
};

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

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

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
        <h1>🗿 BAKAY</h1>
        <div className="sub">
          KTMÜ resmi belgelerine dayalı, kaynak gösteren kurumsal asistan
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
              {m.latency_ms != null && (
                <div className="meta">{(m.latency_ms / 1000).toFixed(1)} sn</div>
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
