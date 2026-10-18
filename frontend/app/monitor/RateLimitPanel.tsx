"use client";

import { useCallback, useEffect, useState } from "react";
import { Check, RefreshCw, Save } from "lucide-react";
import styles from "./rate-limits.module.css";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const fields = [
  { key: "rate_chat_per_minute", label: "IP başına / dakika", max: 1000, note: "Aynı bağlantıdan gelen sohbet istekleri" },
  { key: "rate_chat_per_hour", label: "IP başına / saat", max: 10000, note: "Son 60 dakikadaki toplam istek" },
  { key: "rate_chat_global_per_minute", label: "Sistem toplamı / dakika", max: 1000, note: "Tüm bağlantılardan gelen sohbet istekleri" },
  { key: "rate_chat_global_per_day", label: "Sistem toplamı / 24 saat", max: 100000, note: "Son 24 saatte başlatılan yanıt işlemleri" },
  { key: "rate_chat_concurrent", label: "Eşzamanlı işlem / sistem", max: 16, note: "Sistemin aynı anda yanıtladığı soru sayısı" },
  { key: "rate_chat_concurrent_per_ip", label: "Eşzamanlı işlem / IP", max: 16, note: "Aynı bağlantının kullanabileceği işlem sayısı" },
] as const;
type Key = typeof fields[number]["key"];
type Limits = Record<Key, number>;
type Draft = Record<Key, string>;
type Saved = { limits: Limits; defaults: Limits; revision: number; updated_at: string | null; updated_by: string | null };
const draftFor = (limits: Limits): Draft => Object.fromEntries(fields.map(field => [field.key, String(limits[field.key])])) as Draft;
const dateTime = (value: string) => new Intl.DateTimeFormat("tr-TR", { timeZone: "Asia/Bishkek", dateStyle: "medium", timeStyle: "short" }).format(new Date(value));

export default function RateLimitPanel({ onSaved }: { onSaved: () => void }) {
  const [saved, setSaved] = useState<Saved | null>(null);
  const [draft, setDraft] = useState<Draft | null>(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const load = useCallback(async () => {
    setLoading(true); setError(""); setNotice("");
    try {
      const response = await fetch(`${API}/monitor/rate-limits`, { credentials: "include", cache: "no-store" });
      if (!response.ok) throw new Error(response.status === 401 ? "Oturumunuz sona erdi. Yeniden giriş yapın." : "Kullanım sınırları alınamadı.");
      const data: Saved = await response.json();
      setSaved(data); setDraft(draftFor(data.limits));
    } catch (caught) { setError(caught instanceof Error ? caught.message : "Ayarlar alınamadı."); }
    finally { setLoading(false); }
  }, []);
  useEffect(() => { void load(); }, [load]);
  const dirty = saved && draft && fields.some(field => draft[field.key] !== String(saved.limits[field.key]));

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!saved || !draft) return;
    setSaving(true); setError(""); setNotice("");
    try {
      const body = { ...Object.fromEntries(fields.map(field => [field.key, Number(draft[field.key])])), revision: saved.revision };
      const response = await fetch(`${API}/monitor/rate-limits`, { method: "PUT", credentials: "include", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
      const result = await response.json();
      if (!response.ok) throw new Error(typeof result.detail === "string" ? result.detail : Array.isArray(result.detail) ? result.detail.map((entry: { msg: string }) => entry.msg.replace(/^Value error, /, "")).join(" · ") : "Ayarlar kaydedilemedi.");
      setSaved(result); setDraft(draftFor(result.limits));
      setNotice("Kullanım sınırları kaydedildi ve yeni istekler için uygulandı.");
      onSaved();
    } catch (caught) { setError(caught instanceof Error ? caught.message : "Ayarlar kaydedilemedi."); }
    finally { setSaving(false); }
  };

  return <div className={styles.root}>
    <div className={styles.heading}><div><h3>Kullanım sınırlarını düzenle</h3><p>Değişiklikler kaydedildiğinde uygulanır ve sistem yeniden başlasa da korunur.</p></div><button type="button" onClick={() => void load()} disabled={loading || saving}><RefreshCw size={14} /> Güncel ayarları yükle</button></div>
    {error && <p role="alert" className={styles.error}>{error}</p>}
    {notice && <p role="status" className={styles.success}><Check size={15} /> {notice}</p>}
    {!draft || !saved ? <p className={styles.note}>{loading ? "Kullanım sınırları yükleniyor…" : "Ayarları yeniden yükleyin."}</p> : <form onSubmit={submit}>
      <fieldset disabled={loading || saving}><div className={styles.fields}>{fields.map(field => <div key={field.key}><label htmlFor={`limit-${field.key}`}>{field.label}</label><input id={`limit-${field.key}`} type="number" inputMode="numeric" min={1} max={field.max} step={1} required value={draft[field.key]} onChange={event => { setDraft(current => current ? { ...current, [field.key]: event.target.value } : current); setNotice(""); }} aria-describedby={`limit-help-${field.key}`} /><small id={`limit-help-${field.key}`}>{field.note} · 1–{field.max.toLocaleString("tr-TR")}</small></div>)}</div>
      <p className={styles.note}>IP sınırı, üniversite veya yurt ağı gibi ortak bağlantıları paylaşan herkese birlikte uygulanır. Mevcut kullanım sayaçları sıfırlanmaz; devam eden yanıtlar tamamlanır.</p>
      <div className={styles.actions}><button type="button" onClick={() => { setDraft(draftFor(saved.defaults)); setNotice(""); setError(""); }}>Başlangıç değerlerini doldur</button><button type="submit" className={styles.primary} disabled={!dirty}><Save size={15} /> {saving ? "Kaydediliyor…" : "Sınırları kaydet"}</button></div></fieldset>
      <p className={styles.meta}>{saved.updated_at ? `Son değişiklik: ${dateTime(saved.updated_at)} · ${saved.updated_by} · Sürüm ${saved.revision}` : "Henüz panelden değişiklik yapılmadı; başlangıç değerleri uygulanıyor."}{dirty ? " · Kaydedilmemiş değişiklikler var." : ""}</p>
    </form>}
  </div>;
}
