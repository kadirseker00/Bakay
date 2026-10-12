"use client";

import Script from "next/script";
import { useEffect, useRef, useState } from "react";
import styles from "./security-challenge.module.css";

type Turnstile = {
  render: (element: HTMLElement, options: Record<string, unknown>) => string;
  remove: (id: string) => void;
};
declare global { interface Window { turnstile?: Turnstile } }

export default function SecurityChallenge({ siteKey, onSubmit, onCancel }: {
  siteKey: string; onSubmit: (token: string) => void; onCancel: () => void;
}) {
  const dialog = useRef<HTMLDialogElement>(null);
  const target = useRef<HTMLDivElement>(null);
  const [ready, setReady] = useState(false);
  const [token, setToken] = useState("");
  const [error, setError] = useState("");
  useEffect(() => { dialog.current?.showModal(); }, []);
  useEffect(() => {
    if (!ready || !target.current || !window.turnstile) return;
    const id = window.turnstile.render(target.current, {
      sitekey: siteKey, action: "bakai_chat", language: "tr", size: "flexible",
      callback: (value: string) => { setToken(value); setError(""); },
      "expired-callback": () => { setToken(""); setError("Doğrulamanın süresi doldu. Yeniden doğrulayın."); },
      "error-callback": () => { setToken(""); setError("Doğrulama yüklenemedi. Bağlantınızı kontrol edip tekrar deneyin."); },
    });
    return () => window.turnstile?.remove(id);
  }, [ready, siteKey]);
  return <dialog ref={dialog} className={styles.dialog} aria-labelledby="challenge-title" onCancel={event => { event.preventDefault(); onCancel(); }}>
    <h2 id="challenge-title">Kısa bir güvenlik kontrolü</h2>
    <p>Bu bağlantıdan kısa sürede çok sayıda istek geldi. Sorunuzu yanıtlamadan önce doğrulamayı tamamlayın.</p>
    <Script src="https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit" strategy="afterInteractive" onReady={() => setReady(true)} onError={() => setError("Doğrulama yüklenemedi. Biraz sonra yeniden deneyin.")} />
    <div ref={target} className={styles.widget} />
    {error && <p role="alert">{error}</p>}
    <div className={styles.buttons}><button type="button" onClick={onCancel}>Vazgeç</button><button type="button" disabled={!token} onClick={() => onSubmit(token)}>Doğrula ve soruyu gönder</button></div>
    <small>Doğrulama Cloudflare Turnstile ile yapılır. Kullanım sınırları geçerliliğini korur.</small>
  </dialog>;
}
