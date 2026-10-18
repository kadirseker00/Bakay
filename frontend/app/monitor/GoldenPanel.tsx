"use client";

import { useCallback, useEffect, useState } from "react";
import { Download, RefreshCw } from "lucide-react";
import type { AnswerCandidate } from "./KnowledgePanel";
import styles from "./golden.module.css";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
type Candidate = AnswerCandidate & {
  id: string; knowledge_id: string; current_question: string; original_question: string;
  original_answer: string; proposed_answer: string; proposed_source: string | null;
  history: { role: string; content: string }[]; review_status: "pending" | "approved" | "archived";
  created_at: string; revision: number;
};
const statusLabel = { pending: "İnceleme bekliyor", approved: "Onaylı", archived: "Arşiv" };

export default function GoldenPanel({ refreshKey, onReview }: { refreshKey: number; onReview: (candidate: AnswerCandidate) => void }) {
  const [items, setItems] = useState<Candidate[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [filter, setFilter] = useState("pending");
  const [search, setSearch] = useState("");
  const load = useCallback(async () => {
    setLoading(true); setError("");
    try {
      const response = await fetch(`${API}/monitor/golden`, { credentials: "include", cache: "no-store" });
      if (!response.ok) throw new Error("Düzeltmeler alınamadı. Oturumunuzu ve bağlantınızı kontrol edin.");
      setItems((await response.json()).items);
    } catch (caught) { setError(caught instanceof Error ? caught.message : "Düzeltmeler alınamadı."); }
    finally { setLoading(false); }
  }, []);
  useEffect(() => { void load(); }, [load, refreshKey]);

  const download = async () => {
    setLoading(true); setError("");
    try {
      const response = await fetch(`${API}/monitor/golden/export`, { credentials: "include", cache: "no-store" });
      if (!response.ok) throw new Error("Veri seti indirilemedi.");
      const url = URL.createObjectURL(await response.blob());
      const link = document.createElement("a"); link.href = url; link.download = "bakai-golden-development.jsonl";
      document.body.appendChild(link); link.click(); link.remove();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    } catch (caught) { setError(caught instanceof Error ? caught.message : "Veri seti indirilemedi."); }
    finally { setLoading(false); }
  };
  const approved = items.filter(item => item.review_status === "approved").length;
  const visible = items.filter(item => (filter === "all" || item.review_status === filter) &&
    [item.current_question, item.proposed_answer, item.original_question].join(" ").toLocaleLowerCase("tr").includes(search.toLocaleLowerCase("tr")));

  return <div className={styles.root}>
    <div className={styles.heading}><div><h2>Golden dataset · Düzeltmeler</h2><p>Olumsuz geri bildirimlerden gelen soru-cevap önerilerini kontrol edin.</p></div><button type="button" disabled={loading || !approved} onClick={() => void download()}><Download size={15} /> Onaylıları indir (JSONL)</button></div>
    <div className={styles.summary}><span><strong>{items.filter(item => item.review_status === "pending").length}</strong> inceleme bekleyen</span><span><strong>{approved}</strong> onaylı</span><span><strong>{items.length}</strong> düzeltme</span></div>
    <p className={styles.info}>Düzeltmeler hazır cevaplara taslak olarak eklenir. Kaynak ve geçerlilik kontrolünden sonra onaylananlar veri setine alınır. Bu kayıtlar geliştirme içindir; bağımsız test seti olarak değerlendirilmemelidir.</p>
    <div className={styles.toolbar}><input aria-label="Düzeltmelerde ara" placeholder="Soru veya düzeltme ara…" value={search} onChange={event => setSearch(event.target.value)} /><select aria-label="Düzeltme durumu" value={filter} onChange={event => setFilter(event.target.value)}><option value="pending">İnceleme bekleyen</option><option value="approved">Onaylı</option><option value="archived">Arşiv</option><option value="all">Tümü</option></select><button type="button" onClick={() => void load()} disabled={loading} aria-label="Düzeltmeleri yenile"><RefreshCw size={15} /></button></div>
    {error && <p role="alert" className={styles.error}>{error}</p>}
    <div className={styles.list}>{visible.map(item => <article key={item.id} className={styles.item}>
      <div className={styles.itemHeading}><span className={styles.badge}>{statusLabel[item.review_status]}</span><small>{new Intl.DateTimeFormat("tr-TR", { dateStyle: "medium", timeZone: "Asia/Bishkek" }).format(new Date(item.created_at))}</small></div>
      <h3>{item.current_question}</h3><div className={styles.comparison}><div><h4>Verilen yanıt</h4><p>{item.original_answer || "Yanıt kaydedilmemiş."}</p></div><div><h4>Önerilen düzeltme</h4><p>{item.proposed_answer}</p>{item.proposed_source && <a href={item.proposed_source} target="_blank" rel="noopener noreferrer">Önerilen resmî kaynak</a>}</div></div>
      <details><summary>Sorunun özgün hali ve bağlamı</summary><p>{item.original_question}</p>{item.history.map((message, index) => <p key={index}><strong>{message.role === "user" ? "Kullanıcı" : "Asistan"}:</strong> {message.content}</p>)}</details>
      {item.answer !== item.proposed_answer && <details><summary>Yöneticinin güncel cevabı · sürüm {item.revision}</summary><p>{item.answer}</p></details>}
      <button type="button" className={styles.review} onClick={() => onReview({ question: item.current_question, answer: item.answer, sources: item.sources, entryId: item.knowledge_id })}>Hazır cevapta incele</button>
    </article>)}{!visible.length && <p className={styles.empty}>{loading ? "Düzeltmeler yükleniyor…" : "Bu filtrede düzeltme yok. Kullanıcı doğru bir yanıt önerdiğinde burada görünür."}</p>}</div>
  </div>;
}
