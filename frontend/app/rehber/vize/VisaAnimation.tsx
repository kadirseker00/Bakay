"use client";

// Vize sürecini 60 saniyede, bir hoca karakterinin yolculuğu olarak anlatan
// sayfa içi animasyon. Sahneler 600×340 birimlik bir tuvalde çizilir ve kutuya
// göre ölçeklenir. Zaman JS'te tutulur; karakterin konumu ve pozu her karede
// sahne senaryosundan hesaplanır. Ekran dışında ve "hareketi azalt"
// tercihinde kendiliğinden oynamaz.

import { useEffect, useMemo, useRef, useState, type CSSProperties, type ReactNode } from "react";
import { CircleCheck, CircleX, Fingerprint, Languages, MessageCircle, Pause, Play, QrCode, RotateCcw, ShieldCheck, Stethoscope, TestTube } from "lucide-react";
import Hoca, { type Face, type Pose, type Prop } from "./Hoca";
import styles from "./animation.module.css";

const CANVAS_W = 600;
const CANVAS_H = 340;

type Beat = { t: number; x: number; pose: Pose; face?: Face; prop?: Prop; say?: string; flip?: boolean };
type Scene = { id: string; label: string; duration: number; caption: string };

const SCENES: Scene[] = [
  { id: "basla", label: "Başla", duration: 6, caption: "Vizen bitmeden 40 gün önce hazırlığa başla." },
  { id: "ceviri", label: "Çeviri", duration: 9, caption: "1 · Önce çeviriler: pasaport, evlilik ve nüfus cüzdanı, noter onaylı Kırgızca." },
  { id: "pin", label: "PIN", duration: 8, caption: "2 · Pasaport çevirisiyle ЦОН’da sıraya gir, PIN al. Çocuğa PIN, okula gidecekse." },
  { id: "sigorta", label: "Sigorta", duration: 10, caption: "3 · Sigorta 1840 som, yalnız Eldik Bank’ta. Dekontla Vize Birimine; poliçe 3 günde." },
  { id: "rapor", label: "086", duration: 8, caption: "4 · 086 sağlık raporu: 2 No’lu Poliklinik, oda 304. Özel hastane geçmez." },
  { id: "aids", label: "AIDS", duration: 8, caption: "5 · AIDS testi: kan alımı hafta içi 12.00’ye kadar. Sonuç ekran görüntüsü veya PDF." },
  { id: "basvuru", label: "Başvuru", duration: 11, caption: "6 · Belgeler telefondan, ücret QR ile. Vize bitiminden 1 ay önce başvur." },
];

const STARTS = SCENES.reduce<number[]>((acc, _scene, i) => [...acc, i === 0 ? 0 : acc[i - 1] + SCENES[i - 1].duration], []);
const TOTAL = SCENES.reduce((sum, scene) => sum + scene.duration, 0);

// Belge çantasına düşen belgeler: hangi saniyede "alınmış" sayılır.
const BAG = [
  { id: "ceviri", label: "Çeviriler", icon: Languages, at: STARTS[1] + 5.8 },
  { id: "pin", label: "PIN", icon: Fingerprint, at: STARTS[2] + 6.0 },
  { id: "police", label: "Poliçe", icon: ShieldCheck, at: STARTS[3] + 8.0 },
  { id: "rapor", label: "086", icon: Stethoscope, at: STARTS[4] + 4.4 },
  { id: "aids", label: "AIDS", icon: TestTube, at: STARTS[5] + 4.8 },
];

function sceneAt(time: number) {
  for (let i = 0; i < SCENES.length; i++) if (time < STARTS[i] + SCENES[i].duration) return i;
  return SCENES.length - 1;
}

// Senaryodan anlık karakter durumu: "walk" vuruşunda bir sonraki konuma yürür.
function actorAt(beats: Beat[], t: number) {
  let i = 0;
  while (i < beats.length - 1 && beats[i + 1].t <= t) i++;
  const beat = beats[i];
  const next = beats[i + 1];
  let x = beat.x;
  if (beat.pose === "walk" && next && t >= beat.t) {
    const k = Math.min(1, (t - beat.t) / (next.t - beat.t));
    x = beat.x + (next.x - beat.x) * k;
  }
  return { ...beat, x, say: t >= beat.t ? beat.say : undefined };
}

function Actor({ beats, t }: { beats: Beat[]; t: number }) {
  const state = actorAt(beats, t);
  return <div className={styles.actor} style={{ left: state.x - 50, opacity: state.pose === "hidden" ? 0 : 1 }}>
    {state.say && <span className={styles.say} key={state.say}>{state.say}</span>}
    <div className={state.flip ? styles.flip : undefined}><Hoca pose={state.pose} face={state.face} prop={state.prop ?? null} /></div>
  </div>;
}

function Show({ when, className = "", style, children }: { when: boolean; className?: string; style?: CSSProperties; children: ReactNode }) {
  return <div className={`${styles.appear} ${when ? styles.shown : ""} ${className}`} style={style}>{children}</div>;
}

function Person({ x, color, gone = false }: { x: number; color: string; gone?: boolean }) {
  return <svg viewBox="0 0 60 150" className={styles.person} style={{ left: x - 32, opacity: gone ? 0 : 1 }} aria-hidden="true">
    <ellipse cx="30" cy="146" rx="18" ry="3.5" fill="rgba(0,0,0,.22)" />
    <rect x="14" y="44" width="32" height="62" rx="14" fill={color} />
    <rect x="17" y="96" width="11" height="48" rx="5" fill="#1d2b40" />
    <rect x="32" y="96" width="11" height="48" rx="5" fill="#26384f" />
    <circle cx="30" cy="27" r="15" fill="#d9a77f" />
    <path d="M15 26 Q15 10 30 11 Q45 10 45 24 Q38 18 30 18 Q21 18 15 26Z" fill="#2c211b" />
  </svg>;
}

function Building({ left, width, height, tone, sign, sub, signTone, children }: {
  left: number; width: number; height: number; tone: string; sign: string; sub?: string; signTone: string; children?: ReactNode;
}) {
  return <div className={styles.building} style={{ left, width, height, background: tone }}>
    <div className={styles.sign} style={{ background: signTone }}><strong>{sign}</strong>{sub && <small>{sub}</small>}</div>
    {children}
  </div>;
}

function Ground({ mountains = true }: { mountains?: boolean }) {
  return <>
    {mountains && <div className={styles.mountains} aria-hidden="true" />}
    <div className={styles.ground} aria-hidden="true" />
  </>;
}

// ——— Sahneler ———

function SceneStart({ t }: { t: number }) {
  const days = t < 1.1 ? 60 : t < 2.1 ? 50 : 40;
  return <>
    <div className={styles.room} />
    <div className={styles.calendar}>
      <span className={styles.calendarTop}>VİZE BİTİMİNE</span>
      <span className={`${styles.calendarDays} ${days === 40 ? styles.alarm : ""}`} key={days}>{days}</span>
      <span className={styles.calendarBottom}>gün</span>
    </div>
    <Ground mountains={false} />
    <Actor t={t} beats={[
      { t: 0, x: 190, pose: "idle", face: "neutral" },
      { t: 2.3, x: 190, pose: "idle", face: "wow", say: "40 gün kaldı!" },
      { t: 3.4, x: 190, pose: "show", face: "smile", prop: "passport", say: "Yeşil pasaport hazır." },
      { t: 4.6, x: 190, pose: "walk", face: "smile", prop: "passport" },
      { t: 6.2, x: 660, pose: "walk", prop: "passport" },
    ]} />
  </>;
}

function SceneTranslate({ t }: { t: number }) {
  const docs = [
    { at: 2.5, label: "Pasaport", tone: "#1f6b3a" },
    { at: 3.0, label: "Evlilik c.", tone: "#a8323a" },
    { at: 3.5, label: "Nüfus c.", tone: "#2d5aa0" },
  ];
  return <>
    <Building left={320} width={260} height={230} tone="#e8eee9" sign="НОТАРИУС · КОТОРМО" sub="Noter + tercüme · Şeroy, Cal" signTone="#27356f">
      <div className={styles.counter} style={{ left: 22, width: 128 }}><Person x={64} color="#7a6aa8" /></div>
      <div className={styles.door} style={{ left: 180 }} />
    </Building>
    <div className={styles.desk}>
      {docs.map(doc => <Show key={doc.label} when={t >= doc.at && t < 5.6} className={styles.miniDoc} style={{ background: doc.tone }}>{doc.label}</Show>)}
    </div>
    <Show when={t >= 4.4 && t < 6.6} className={styles.stamp}>ONAYLI · КОТОРМО</Show>
    <Ground />
    <Actor t={t} beats={[
      { t: 0, x: -60, pose: "walk", face: "smile", prop: "passport" },
      { t: 2.0, x: 285, pose: "give", face: "smile", prop: "docs", say: "Üç belge, Kırgızca lütfen." },
      { t: 5.6, x: 285, pose: "show", face: "smile", prop: "docs", say: "Çeviriler tamam!" },
      { t: 7.0, x: 285, pose: "walk", face: "smile", prop: "docs" },
      { t: 9.0, x: 660, pose: "walk", prop: "docs" },
    ]} />
  </>;
}

function ScenePin({ t }: { t: number }) {
  const slots = [520, 470, 420, 370];
  const advanced = t >= 4.4 ? 3 : t >= 3.2 ? 2 : t >= 2.0 ? 1 : 0;
  const queue = ["#b0623f", "#5b7f3a", "#8a6b2e"];
  return <>
    <Building left={300} width={290} height={235} tone="#ece9e2" sign="ЦОН" sub="Nüfus Dairesi · Jumabeka 121" signTone="#087b72">
      {advanced < 3 && <div className={styles.ticket}>№ {45 + advanced}</div>}
      <div className={styles.counter} style={{ left: 180, width: 90 }} />
    </Building>
    {queue.map((color, i) => {
      const slot = i - advanced;
      return <Person key={color} x={slot < 0 ? 560 : slots[slot]} color={color} gone={slot < 0} />;
    })}
    <Show when={t >= 6.2} className={styles.chip} style={{ left: 20, top: 24 }}>Çocuk: PIN okula gidecekse</Show>
    <Ground />
    <Actor t={t} beats={[
      { t: 0, x: -60, pose: "walk", face: "neutral", prop: "docs" },
      { t: 1.6, x: 370, pose: "wait", face: "neutral", prop: "docs", say: "Sıradayım…" },
      { t: 2.0, x: 370, pose: "walk", face: "neutral", prop: "docs" },
      { t: 2.5, x: 420, pose: "wait", face: "neutral", prop: "docs" },
      { t: 3.2, x: 420, pose: "walk", face: "neutral", prop: "docs" },
      { t: 3.7, x: 470, pose: "wait", face: "neutral", prop: "docs" },
      { t: 4.4, x: 470, pose: "walk", face: "smile", prop: "docs" },
      { t: 4.9, x: 520, pose: "give", face: "smile", prop: "docs", say: "PIN başvurusu." },
      { t: 6.0, x: 520, pose: "happy", face: "smile", prop: "card", say: "PIN hazır!" },
      { t: 7.2, x: 520, pose: "idle", face: "smile", prop: "card" },
    ]} />
  </>;
}

function SceneInsurance({ t }: { t: number }) {
  return <>
    <Building left={40} width={200} height={240} tone="#dfe3e2" sign="BAŞKA BANKA" signTone="#6b7a77">
      <div className={styles.door} style={{ left: 80 }} />
    </Building>
    <Building left={320} width={260} height={240} tone="#e6efe7" sign="ELDIK BANK" sub="Jal-23 mikrorayon, 101" signTone="#2e7d4f">
      <div className={styles.door} style={{ left: 95 }} />
    </Building>
    <Show when={t >= 1.8} className={`${styles.tag} ${styles.tagBad}`} style={{ left: 70, top: 182 }}><CircleX size={16} /> 12 000 som</Show>
    <Show when={t >= 5.0} className={`${styles.tag} ${styles.tagGood}`} style={{ left: 494, top: 165 }}><CircleCheck size={16} /> 1840 som</Show>
    <Show when={t >= 6.6} className={styles.chip} style={{ left: 330, top: 24 }}>Dekont → Vize Birimi · 3 gün</Show>
    <Ground />
    <Actor t={t} beats={[
      { t: 0, x: -60, pose: "walk", face: "smile", prop: "cash" },
      { t: 1.5, x: 285, pose: "idle", face: "wow", flip: true, say: "12 000 som mu?!" },
      { t: 2.6, x: 285, pose: "idle", face: "frown", flip: true, say: "Yalnız Eldik Bank!" },
      { t: 3.6, x: 285, pose: "walk", face: "smile", prop: "cash" },
      { t: 4.6, x: 440, pose: "give", face: "smile", prop: "cash" },
      { t: 5.8, x: 440, pose: "show", face: "smile", prop: "receipt", say: "Dekont tamam." },
      { t: 7.4, x: 440, pose: "phone", face: "smile", prop: "phone", say: "Poliçe telefonda." },
    ]} />
  </>;
}

function SceneReport({ t }: { t: number }) {
  return <>
    <Building left={250} width={320} height={235} tone="#eef0f4" sign="ПОЛИКЛИНИКА №2" sub="Abdraimov 25/1" signTone="#3d5a99">
      <div className={`${styles.door} ${t >= 2.6 && t < 4.4 ? styles.doorLit : ""}`} style={{ left: 130 }}><span>304</span></div>
      <div className={styles.cross}>+</div>
    </Building>
    <Show when={t >= 5.2} className={`${styles.tag} ${styles.tagBad}`} style={{ left: 18, top: 28 }}><CircleX size={16} /> Özel hastane</Show>
    <Show when={t >= 5.8} className={`${styles.tag} ${styles.tagBad}`} style={{ left: 18, top: 70 }}><CircleX size={16} /> Türkiye’den rapor</Show>
    <Ground />
    <Actor t={t} beats={[
      { t: 0, x: -60, pose: "walk", face: "smile" },
      { t: 2.0, x: 412, pose: "idle", face: "smile", say: "Oda 304." },
      { t: 2.6, x: 412, pose: "hidden" },
      { t: 4.4, x: 412, pose: "happy", face: "smile", prop: "paper086", say: "086 raporu alındı!" },
      { t: 5.6, x: 412, pose: "show", face: "smile", prop: "paper086" },
    ]} />
  </>;
}

function SceneAids({ t }: { t: number }) {
  // Saat 11.15'ten başlayıp içerideyken 11.50'ye ilerler.
  const minutes = 15 + Math.min(35, Math.max(0, t - 1) * 10);
  return <>
    <Building left={240} width={330} height={235} tone="#f0ebe4" sign="TEST MERKEZİ" sub="Logvinenko 8 · Toktogul 62" signTone="#a8323a">
      <div className={`${styles.door} ${t >= 2.6 && t < 4.2 ? styles.doorLit : ""}`} style={{ left: 95 }} />
      <div className={styles.clock}>
        <svg viewBox="0 0 60 60" aria-hidden="true">
          <circle cx="30" cy="30" r="27" fill="#fffdf7" stroke="#27356f" strokeWidth="3" />
          <line x1="30" y1="30" x2="30" y2="13" stroke="#27356f" strokeWidth="3" strokeLinecap="round" style={{ transform: `rotate(${330 + minutes * 0.5}deg)`, transformOrigin: "30px 30px" }} />
          <line x1="30" y1="30" x2="30" y2="8" stroke="#e56845" strokeWidth="2" strokeLinecap="round" style={{ transform: `rotate(${minutes * 6}deg)`, transformOrigin: "30px 30px" }} />
        </svg>
        <small>12.00’ye kadar</small>
      </div>
    </Building>
    <Ground />
    <Actor t={t} beats={[
      { t: 0, x: -60, pose: "walk", face: "neutral" },
      { t: 1.8, x: 350, pose: "idle", face: "wow", say: "12.00’den önce!" },
      { t: 2.6, x: 350, pose: "hidden" },
      { t: 4.2, x: 350, pose: "phone", face: "smile", prop: "phone", say: "Sonuç: görüntü veya PDF" },
    ]} />
  </>;
}

function SceneApply({ t }: { t: number }) {
  const chats = [
    { at: 1.4, label: "Sigorta poliçesi" },
    { at: 2.1, label: "086 raporu" },
    { at: 2.8, label: "AIDS sonucu" },
  ];
  return <>
    <Building left={412} width={175} height={240} tone="#e4f1ee" sign="VİZE BİRİMİ" sub="KTMÜ" signTone="#075f59">
      <div className={styles.counter} style={{ left: 26, width: 120 }}>
        <Show when={t >= 4.4} className={styles.bigCheck}><CircleCheck size={40} /></Show>
      </div>
    </Building>
    <div className={styles.chat}>
      <div className={styles.chatTop}><MessageCircle size={13} /> Vize Birimi</div>
      {chats.map(chat => <Show key={chat.label} when={t >= chat.at} className={styles.bubble}>{chat.label} ✓✓</Show>)}
      <Show when={t >= 3.5} className={`${styles.bubble} ${styles.qr}`}><QrCode size={13} /> Vize ücreti · QR</Show>
    </div>
    <Show when={t >= 6.4} className={`${styles.tag} ${styles.tagGood}`} style={{ left: 18, top: 24 }}><CircleCheck size={16} /> Bitişten 1 ay önce başvur</Show>
    <Show when={t >= 7.4} className={`${styles.tag} ${styles.tagBad}`} style={{ left: 18, top: 66 }}><CircleX size={16} /> Eksik evrak kabul edilmez</Show>
    <Ground />
    <Actor t={t} beats={[
      { t: 0, x: -60, pose: "walk", face: "smile", prop: "phone" },
      { t: 1.0, x: 185, pose: "phone", face: "smile", prop: "phone" },
      { t: 4.6, x: 185, pose: "happy", face: "smile", prop: "phone", say: "Başvuru tamam!" },
      { t: 6.2, x: 185, pose: "idle", face: "smile", prop: "phone" },
    ]} />
  </>;
}

const RENDER: Record<string, (props: { t: number }) => JSX.Element> = {
  basla: SceneStart, ceviri: SceneTranslate, pin: ScenePin, sigorta: SceneInsurance,
  rapor: SceneReport, aids: SceneAids, basvuru: SceneApply,
};

export default function VisaAnimation() {
  const [elapsed, setElapsed] = useState(0); // döngüler dahil toplam saniye
  const [playing, setPlaying] = useState(true);
  const [inView, setInView] = useState(false);
  const [seek, setSeek] = useState(0);
  const [scale, setScale] = useState(1);
  const rootRef = useRef<HTMLDivElement>(null);
  const screenRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) setPlaying(false);
    const node = rootRef.current;
    const screen = screenRef.current;
    if (!node || !screen) return;
    const observer = new IntersectionObserver(([entry]) => setInView(entry.isIntersecting), { threshold: 0.35 });
    observer.observe(node);
    const resize = new ResizeObserver(([entry]) => setScale(Math.min(1.3, entry.contentRect.width / CANVAS_W)));
    resize.observe(screen);
    return () => { observer.disconnect(); resize.disconnect(); };
  }, []);

  const running = playing && inView;

  useEffect(() => {
    if (!running) return;
    let last = performance.now();
    let frame = requestAnimationFrame(function tick(now) {
      setElapsed(value => value + Math.min(0.1, (now - last) / 1000));
      last = now;
      frame = requestAnimationFrame(tick);
    });
    return () => cancelAnimationFrame(frame);
  }, [running]);

  const loop = Math.floor(elapsed / TOTAL);
  const time = elapsed - loop * TOTAL;
  const index = sceneAt(time);
  const scene = SCENES[index];
  const local = time - STARTS[index];
  const Render = RENDER[scene.id];
  const bag = useMemo(() => BAG.map(item => ({ ...item, has: time >= item.at })), [time]);

  function jump(to: number) {
    setElapsed(loop * TOTAL + STARTS[to]);
    setSeek(value => value + 1);
    setPlaying(true);
  }

  function restart() {
    setElapsed(0);
    setSeek(value => value + 1);
    setPlaying(true);
  }

  return <div ref={rootRef} className={`${styles.stage} ${running ? "" : styles.paused}`} role="region" aria-label="Vize sürecinin 60 saniyelik animasyonu">
    <div className={styles.rail} aria-hidden="true">
      {SCENES.slice(1).map((item, i) => <span key={item.id} className={i + 1 < index ? styles.done : i + 1 === index ? styles.current : ""}>{i + 1}</span>)}
    </div>

    <div ref={screenRef} className={styles.screen} style={{ height: CANVAS_H * scale }} aria-hidden="true">
      <div key={`${loop}-${index}-${seek}`} className={styles.canvas} style={{ width: CANVAS_W, height: CANVAS_H, transform: `translateX(-50%) scale(${scale})` }}>
        <Render t={local} />
      </div>
    </div>

    <p className={styles.caption} key={`c-${loop}-${index}-${seek}`}>{scene.caption}</p>

    <div className={styles.bag} aria-hidden="true">
      <span className={styles.bagLabel}>Belge çantası</span>
      {bag.map(item => { const Icon = item.icon; return <span key={item.id} className={item.has ? styles.has : ""}><Icon size={14} /> {item.label}</span>; })}
    </div>

    <div className={styles.controls}>
      <button type="button" onClick={() => setPlaying(value => !value)} aria-label={playing ? "Duraklat" : "Oynat"}>
        {playing ? <Pause size={16} /> : <Play size={16} />}
      </button>
      <div className={styles.timeline}>
        {SCENES.map((item, i) => <button key={item.id} type="button" onClick={() => jump(i)}
          className={i === index ? styles.active : ""} style={{ flexGrow: item.duration }}
          aria-label={`${item.label} sahnesine git`} aria-current={i === index ? "step" : undefined}>
          <span className={styles.fill} style={{ width: i < index ? "100%" : i === index ? `${(local / item.duration) * 100}%` : "0%" }} />
          <span className={styles.tick}>{item.label}</span>
        </button>)}
      </div>
      <button type="button" onClick={restart} aria-label="Baştan oynat"><RotateCcw size={16} /></button>
      <span className={styles.time}>{`0:${String(Math.floor(time)).padStart(2, "0")}`} / 1:00</span>
    </div>
  </div>;
}
