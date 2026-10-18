"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { BookOpen, CheckCircle2, ExternalLink, FilePlus2, Plus, RefreshCw, Search, X } from "lucide-react";
import ReactMarkdown from "react-markdown";
import styles from "./knowledge.module.css";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
type Source = { title: string; url: string; snippet: string };
export type AnswerCandidate = { question: string; answer: string; sources: Source[]; entryId?: string };
type Status = "draft" | "published" | "archived";
type Entry = AnswerCandidate & { id: string; variants: string[]; status: Status; reviewed_on: string | null; valid_until: string | null; revision: number; expired: boolean; approved_by: string | null; approved_at: string | null; updated_by: string; hits: number };
type Editor = AnswerCandidate & { id?: string; variants: string; reviewed_on: string; valid_until: string; revision?: number; status: Status };
const blankSource = (): Source => ({ title: "", url: "", snippet: "" });
const blank = (): Editor => ({ question: "", answer: "", variants: "", sources: [blankSource()], reviewed_on: "", valid_until: "", status: "draft" });
const statusName = (entry: Entry) => entry.status === "published" ? entry.expired ? "Süresi doldu" : "Yayında" : entry.status === "archived" ? "Arşiv" : "Taslak";

async function request(path: string, init?: RequestInit) {
  const response = await fetch(`${API}/monitor/knowledge${path}`, { credentials: "include", cache: "no-store", ...init });
  const body = await response.json();
  if (!response.ok) {
    if (response.status === 401) throw new Error("Oturumunuz sona erdi. Sayfayı yenileyip giriş yapın.");
    throw new Error(typeof body.detail === "string" ? body.detail : Array.isArray(body.detail) ? body.detail.map((item: { msg: string }) => item.msg.replace(/^Value error, /, "")).join(" · ") : "İşlem tamamlanamadı.");
  }
  return body;
}

export default function KnowledgePanel({ candidate, onSaved }: { candidate: AnswerCandidate | null; onSaved?: () => void }) {
  const [items, setItems] = useState<Entry[]>([]);
  const [editor, setEditor] = useState<Editor | null>(null);
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState("all");
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [preview, setPreview] = useState(false);
  const form = useRef<HTMLFormElement>(null);
  const load = useCallback(async () => {
    setLoading(true);
    try { setItems((await request("")).items); setError(""); }
    catch (caught) { setError(caught instanceof Error ? caught.message : "Cevaplar alınamadı."); }
    finally { setLoading(false); }
  }, []);
  useEffect(() => { void load(); }, [load]);
  useEffect(() => {
    let cancelled = false;
    if (candidate?.entryId) {
      void request("").then(data => {
        if (cancelled) return;
        const entry = (data.items as Entry[]).find(item => item.id === candidate.entryId);
        if (!entry) throw new Error("Düzeltme taslağı bulunamadı.");
        setItems(data.items); open(entry);
        setNotice("Kullanıcının düzeltme taslağı açıldı. Soruyu, cevabı ve kaynaklarını kontrol edin.");
      }).catch(caught => { if (!cancelled) setError(caught instanceof Error ? caught.message : "Taslak açılamadı."); });
    } else if (candidate) { setEditor({ ...blank(), ...candidate, sources: candidate.sources.length ? candidate.sources : [blankSource()] }); setPreview(false); setNotice("Sorgu taslağa alındı. Cevabı ve kaynaklarını kontrol ederek kaydedin."); }
    return () => { cancelled = true; };
  }, [candidate]);

  const update = (change: Partial<Editor>) => setEditor(current => current ? { ...current, ...change } : current);
  const open = (entry: Entry) => {
    setEditor({ ...entry, variants: entry.variants.join("\n"), reviewed_on: entry.reviewed_on || "", valid_until: entry.valid_until || "", sources: entry.sources.length ? entry.sources : [blankSource()] });
    setPreview(false); setError(""); setNotice("");
  };
  const sourceChange = (index: number, change: Partial<Source>) => {
    if (editor) update({ sources: editor.sources.map((source, i) => i === index ? { ...source, ...change } : source) });
  };
  const save = async (status: Status) => {
    if (!editor || !form.current?.reportValidity()) return;
    setSaving(true); setError(""); setNotice("");
    try {
      const body = { question: editor.question, answer: editor.answer,
        variants: editor.variants.split("\n").map(value => value.trim()).filter(Boolean),
        sources: editor.sources.filter(source => source.title.trim() || source.url.trim() || source.snippet.trim()),
        status, reviewed_on: editor.reviewed_on || null, valid_until: editor.valid_until || null, revision: editor.revision };
      const result: Entry = await request(editor.id ? `/${editor.id}` : "", { method: editor.id ? "PUT" : "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
      setItems(current => [result, ...current.filter(item => item.id !== result.id)]);
      open(result);
      onSaved?.();
      setNotice(status === "published" ? "Cevap onaylandı ve yayımlandı. Eşleşen yeni sorular doğrudan cevaplanacak." : status === "archived" ? "Cevap arşivlendi; doğrudan cevaplarda kullanılmayacak." : "Taslak kaydedildi; doğrudan cevaplarda kullanılmayacak.");
    } catch (caught) { setError(caught instanceof Error ? caught.message : "Cevap kaydedilemedi."); }
    finally { setSaving(false); }
  };
  const seed = async () => {
    setSaving(true); setError("");
    try { setItems((await request("/examples", { method: "POST" })).items); setNotice("Altı örnek kaynaklı taslak olarak eklendi. Mevcut düzenlemeler korundu; yayın için her cevabı kontrol edip onaylayın."); }
    catch (caught) { setError(caught instanceof Error ? caught.message : "Örnekler eklenemedi."); }
    finally { setSaving(false); }
  };
  const visible = items.filter(item => (filter === "all" || (filter === "expired" ? item.status === "published" && item.expired : item.status === filter && !(filter === "published" && item.expired))) && [item.question, ...item.variants, item.answer].join(" ").toLocaleLowerCase("tr").includes(search.toLocaleLowerCase("tr")));
  const active = items.filter(item => item.status === "published" && !item.expired);

  return <div className={styles.root}>
    <div className={styles.header}><div><span className={styles.eyebrow}>KURUMSAL BİLGİ BANKASI</span><h2><BookOpen size={20} /> Hazır cevaplar</h2><p>Sık gelen soruları kaynaklarıyla onaylayın, aynı soru yeniden geldiğinde cevabı doğrudan sunun.</p></div><button type="button" onClick={() => { setEditor(blank()); setPreview(false); setError(""); setNotice(""); }} disabled={saving}><Plus size={16} /> Yeni cevap</button></div>
    <div className={styles.summary}><span><strong>{active.length}</strong> yayında</span><span><strong>{items.filter(item => item.status === "draft").length}</strong> taslak</span><span><strong>{items.filter(item => item.status === "published" && item.expired).length}</strong> süresi dolan</span><span><strong>{items.reduce((sum, item) => sum + item.hits, 0)}</strong> doğrudan cevap</span></div>
    <p className={styles.info}>Yalnız onaylı ve geçerliliği süren cevaplar kullanılır. Soru, kayıtlı soruyla veya eklediğiniz varyantlardan biriyle eşleşmelidir. Konuşmanın devam soruları kaynak aramasıyla cevaplanır.</p>
    <div className={styles.toolbar}><label className={styles.search}><Search size={16} /><input aria-label="Hazır cevaplarda ara" placeholder="Soru veya cevap ara…" value={search} onChange={event => setSearch(event.target.value)} /></label><select aria-label="Cevap durumu" value={filter} onChange={event => setFilter(event.target.value)}><option value="all">Tüm cevaplar</option><option value="published">Yayında</option><option value="draft">Taslak</option><option value="expired">Süresi doldu</option><option value="archived">Arşiv</option></select><button type="button" onClick={() => void load()} disabled={loading || saving} aria-label="Hazır cevapları yenile"><RefreshCw size={15} /></button><button type="button" onClick={() => void seed()} disabled={saving || loading}><FilePlus2 size={15} /> 6 örneği ekle</button></div>
    {error && <p className={styles.error} role="alert">{error}</p>}
    {notice && <p className={styles.notice} role="status">{notice}</p>}
    <div className={`${styles.workspace} ${editor ? styles.editing : ""}`}><div className={styles.list} aria-label="Hazır cevap listesi">{visible.map(item => <button type="button" key={item.id} onClick={() => open(item)} disabled={saving} className={`${styles.item} ${editor?.id === item.id ? styles.selected : ""}`}><span className={`${styles.badge} ${item.status === "published" && !item.expired ? styles.published : ""}`}>{statusName(item)}</span><strong>{item.question}</strong><small>{item.variants.length} varyant · {item.hits} doğrudan cevap{item.valid_until && ` · ${item.valid_until} tarihine kadar`}</small></button>)}{!visible.length && <p className={styles.empty}>{loading ? "Cevaplar yükleniyor…" : items.length ? "Bu filtreye uygun cevap yok." : "İlk cevabı oluşturun veya altı örneği taslak olarak ekleyin."}</p>}</div>
      {editor && <form ref={form} className={styles.editor} onSubmit={event => { event.preventDefault(); void save("draft"); }}><div className={styles.editorHeading}><h3>{editor.id ? "Cevabı düzenle" : "Yeni cevap"}</h3><button type="button" onClick={() => setEditor(null)} disabled={saving} aria-label="Cevap düzenleyiciyi kapat"><X size={18} /></button></div>
        <fieldset disabled={saving}><label htmlFor="knowledge-question">Soru</label><input id="knowledge-question" value={editor.question} onChange={event => update({ question: event.target.value })} required minLength={3} maxLength={2000} />
        <label htmlFor="knowledge-variants">Aynı anlama gelen sorular <small>Her satıra bir varyant</small></label><textarea id="knowledge-variants" value={editor.variants} onChange={event => update({ variants: event.target.value })} rows={3} placeholder="Farklı düzey veya başvuru türlerini ayrı cevap olarak ekleyin." />
        <div className={styles.answerLabel}><label htmlFor="knowledge-answer">Cevap</label><button type="button" onClick={() => setPreview(value => !value)}>{preview ? "Metni düzenle" : "Önizle"}</button></div>
        {preview ? <article className={styles.preview}><ReactMarkdown components={{ a: props => <a {...props} target="_blank" rel="noopener noreferrer" /> }}>{editor.answer || "Henüz cevap yazılmadı."}</ReactMarkdown></article> : <textarea id="knowledge-answer" value={editor.answer} onChange={event => update({ answer: event.target.value })} rows={10} maxLength={12000} placeholder="Kapsamı ve koşulları açıkça yazın. Markdown kullanabilirsiniz." />}
        <div className={styles.sourceHeading}><h4>Kaynaklar</h4><button type="button" disabled={editor.sources.length >= 8} onClick={() => update({ sources: [...editor.sources, blankSource()] })}><Plus size={14} /> Kaynak ekle</button></div>
        {editor.sources.map((source, index) => <div key={index} className={styles.source}><div className={styles.sourceTop}><strong>Kaynak {index + 1}</strong>{/^https?:\/\//.test(source.url) && <a href={source.url} target="_blank" rel="noopener noreferrer">Kaynağı aç <ExternalLink size={12} /></a>}<button type="button" aria-label={`Kaynak ${index + 1} kaldır`} onClick={() => update({ sources: editor.sources.filter((_, i) => i !== index) })}><X size={14} /></button></div><label htmlFor={`knowledge-source-title-${index}`}>Belge başlığı</label><input id={`knowledge-source-title-${index}`} value={source.title} onChange={event => sourceChange(index, { title: event.target.value })} maxLength={300} /><label htmlFor={`knowledge-source-url-${index}`}>Resmî kaynak bağlantısı</label><input id={`knowledge-source-url-${index}`} type="url" value={source.url} onChange={event => sourceChange(index, { url: event.target.value })} maxLength={2000} placeholder="https://…manas.edu.kg/…" /><label htmlFor={`knowledge-source-snippet-${index}`}>İlgili madde veya kaynak özeti</label><textarea id={`knowledge-source-snippet-${index}`} value={source.snippet} onChange={event => sourceChange(index, { snippet: event.target.value })} rows={3} maxLength={2000} /></div>)}
        <div className={styles.dates}><div><label htmlFor="knowledge-reviewed">Kaynak kontrol tarihi</label><input id="knowledge-reviewed" type="date" value={editor.reviewed_on} onChange={event => update({ reviewed_on: event.target.value })} /></div><div><label htmlFor="knowledge-expires">Geçerlilik sonu <small>Bişkek saati</small></label><input id="knowledge-expires" type="date" value={editor.valid_until} onChange={event => update({ valid_until: event.target.value })} /></div></div>
        {editor.id && <p className={styles.info}>Sürüm {editor.revision} · {items.find(item => item.id === editor.id)?.approved_by ? `Son onay: ${items.find(item => item.id === editor.id)?.approved_by}` : "Henüz onaylanmadı"}. Değişiklikleri taslak kaydetmek cevabı yayından kaldırır.</p>}
        <p className={styles.approval}>“Onayla ve yayımla” ile cevabı kaynaklara göre kontrol ettiğinizi onaylarsınız. Geçerlilik süresi bitince cevap otomatik olarak kullanımdan çıkar.</p>
        <div className={styles.actions}><button type="submit">Taslak kaydet</button>{editor.id && <button type="button" onClick={() => void save("archived")}>Arşivle</button>}<button type="button" className={styles.primary} onClick={() => void save("published")}><CheckCircle2 size={16} /> {saving ? "Kaydediliyor…" : "Onayla ve yayımla"}</button></div></fieldset>
      </form>}
    </div>
  </div>;
}
