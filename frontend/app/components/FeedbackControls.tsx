"use client";

import { useRef, useState } from "react";
import { Check, Clock3, ThumbsDown, ThumbsUp } from "lucide-react";
import { FEEDBACK_REASONS } from "../lib/feedback";
import type { FeedbackInput, FeedbackReason } from "../lib/feedback";
import styles from "./feedback-controls.module.css";

type Props = {
  queryId: string;
  rating?: "up" | "down";
  latencyMs?: number;
  onSubmit: (input: FeedbackInput) => Promise<void>;
};

export default function FeedbackControls({ queryId, rating, latencyMs, onSubmit }: Props) {
  const [open, setOpen] = useState(false);
  const [reason, setReason] = useState<FeedbackReason | "">("");
  const [name, setName] = useState("");
  const [comment, setComment] = useState("");
  const [pending, setPending] = useState(false);
  const [error, setError] = useState("");
  const sending = useRef(false);
  const downButton = useRef<HTMLButtonElement>(null);
  const formId = `feedback-${queryId}`;

  async function submit(input: FeedbackInput) {
    if (sending.current || rating) return;
    sending.current = true;
    setPending(true);
    setError("");
    try {
      await onSubmit(input);
      setOpen(false);
      setName("");
      setComment("");
    } catch (failure) {
      setError(failure instanceof Error ? failure.message : "Geri bildirim kaydedilemedi. Yeniden deneyin.");
    } finally {
      sending.current = false;
      setPending(false);
    }
  }

  function close() {
    setOpen(false);
    setError("");
    downButton.current?.focus();
  }

  return <>
    <div className="message-actions">
      {latencyMs != null && <span className="latency"><Clock3 size={14} />{(latencyMs / 1000).toFixed(1)} saniye</span>}
      <span className="action-label">Bu yanıt yararlı mı?</span>
      <button type="button" className={`feedback-button ${rating === "up" ? "active" : ""}`}
        onClick={() => void submit({ rating: "up" })} disabled={!!rating || pending}
        aria-label="Yanıt yararlı" title="Yararlı"><ThumbsUp size={16} /></button>
      <button ref={downButton} type="button" className={`feedback-button ${rating === "down" || open ? "active" : ""}`}
        onClick={() => { setOpen(!open); setError(""); }} disabled={!!rating || pending}
        aria-label="Yanıt yararlı değil" aria-expanded={open && !rating} aria-controls={formId}
        title="Yararlı değil"><ThumbsDown size={16} /></button>
      {rating && <span className="feedback-thanks" role="status"><Check size={14} /> Kaydedildi</span>}
      {pending && <span role="status">Gönderiliyor…</span>}
    </div>
    {open && !rating && <form id={formId} className={styles.form} aria-label="Olumsuz geri bildirim"
      aria-busy={pending} onSubmit={(event) => {
        event.preventDefault();
        if (reason && (reason !== "other" || comment.trim())) {
          void submit({ rating: "down", reason, respondent_name: name.trim() || undefined,
            comment: comment.trim() || undefined });
        }
      }} onKeyDown={(event) => {
        if (event.key === "Escape" && !pending) { event.preventDefault(); close(); }
      }}>
      <fieldset disabled={pending}>
        <legend>Yanıtla ilgili sorun neydi?</legend>
        <div className={styles.reasons}>
          {(Object.entries(FEEDBACK_REASONS) as [FeedbackReason, string][]).map(([value, label], index) =>
            <label key={value} className={reason === value ? styles.selected : ""}>
              <input type="radio" name={`${formId}-reason`} value={value} required autoFocus={index === 0}
                checked={reason === value} onChange={() => setReason(value)} />{label}
            </label>)}
        </div>
        <label className={styles.nameLabel} htmlFor={`${formId}-comment`}>Açıklamanız <span>({reason === "other" ? "zorunlu" : "isteğe bağlı"})</span></label>
        <textarea className={styles.comment} id={`${formId}-comment`} rows={3} maxLength={2000}
          required={reason === "other"} value={comment} onChange={(event) => setComment(event.target.value)}
          placeholder="Sorunu kendi cümlelerinizle anlatabilirsiniz" />
        <label className={styles.nameLabel} htmlFor={`${formId}-name`}>Adınız soyadınız <span>(isteğe bağlı)</span></label>
        <input className={styles.name} id={`${formId}-name`} type="text" autoComplete="name" maxLength={120}
          value={name} onChange={(event) => setName(event.target.value)} placeholder="İsterseniz yazabilirsiniz"
          aria-describedby={`${formId}-hint`} />
        <p id={`${formId}-hint`} className={styles.hint}>Bu alanı boş bırakarak da gönderebilirsiniz. Geri bildiriminiz yöneticiler tarafından görülebilir.</p>
        <div className={styles.actions}>
          <button type="button" onClick={close}>Vazgeç</button>
          <button type="submit" disabled={!reason || pending || (reason === "other" && !comment.trim())}>{pending ? "Gönderiliyor…" : "Geri bildirimi gönder"}</button>
        </div>
      </fieldset>
    </form>}
    {error && <p className={styles.error} role="alert">{error}</p>}
  </>;
}
