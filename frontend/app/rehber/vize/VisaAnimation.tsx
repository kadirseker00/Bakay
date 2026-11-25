"use client";

// Vize sürecini 60 saniyede, sevimli bir hoca karakterinin yolculuğu olarak
// anlatan sayfa içi animasyon. Sahneler karlı Tanrı Dağları önünde, 600×340
// birimlik bir tuvalde çizilir ve kutuya göre ölçeklenir. Zaman JS'te tutulur;
// karakterin konumu ve pozu her karede sahne senaryosundan hesaplanır.
// Ekran dışında ve "hareketi azalt" tercihinde kendiliğinden oynamaz.
// Kullanıcı istekleri: docs/rehber/animasyon-istekleri.md

import { useEffect, useMemo, useRef, useState, type CSSProperties, type ReactNode } from "react";
import { CircleCheck, Fingerprint, Languages, MessageCircle, Pause, Play, QrCode, RotateCcw, ShieldCheck, Stethoscope, TestTube } from "lucide-react";
import Hoca, { type Face, type Pose, type Prop } from "./Hoca";
import styles from "./animation.module.css";

const CANVAS_W = 600;
const CANVAS_H = 340;

type Beat = { t: number; x: number; pose: Pose; face?: Face; prop?: Prop; say?: string; flip?: boolean; tired?: boolean };
type Scene = { id: string; label: string; duration: number; caption: string };

const SCENES: Scene[] = [
  { id: "basla", label: "Başla", duration: 7, caption: "Manas’a hoş geldin! Vizen bitmeden 40 gün önce hazırlığa başla." },
  { id: "ceviri", label: "Çeviri", duration: 8, caption: "1 · Önce çeviriler: pasaport, evlilik ve nüfus cüzdanı noter onaylı Kırgızcaya çevrilir." },
  { id: "pin", label: "ПИН", duration: 8, caption: "2 · Pasaport çevirisiyle ЦОН’da sıraya gir ve PIN numaranı al." },
  { id: "sigorta", label: "Sigorta", duration: 9, caption: "3 · Sigortayı yalnız Eldik Bank’ta 1840 som öde; dekontu Vize Birimine götür." },
  { id: "rapor", label: "086", duration: 7, caption: "4 · 086 sağlık raporunu 2 No’lu Poliklinikte, 304 numaralı odadan al." },
  { id: "aids", label: "AIDS", duration: 11, caption: "5 · AIDS testi: kan alımı hafta içi 12.00’ye kadar, sonuç ertesi gün. Ekran görüntüsü veya PDF olur." },
  { id: "basvuru", label: "Başvuru", duration: 10, caption: "6 · Belgeleri telefondan gönder, ücreti QR ile öde. Vize bitiminden 1 ay önce başvur." },
];

const STARTS = SCENES.reduce<number[]>((acc, _scene, i) => [...acc, i === 0 ? 0 : acc[i - 1] + SCENES[i - 1].duration], []);
const TOTAL = SCENES.reduce((sum, scene) => sum + scene.duration, 0);

// Belge çantasına düşen belgeler: hangi saniyede "alınmış" sayılır.
const BAG = [
  { id: "ceviri", label: "Çeviriler", icon: Languages, at: STARTS[1] + 5.0 },
  { id: "pin", label: "PIN", icon: Fingerprint, at: STARTS[2] + 6.0 },
  { id: "police", label: "Poliçe", icon: ShieldCheck, at: STARTS[3] + 7.2 },
  { id: "rapor", label: "086", icon: Stethoscope, at: STARTS[4] + 4.3 },
  { id: "aids", label: "AIDS", icon: TestTube, at: STARTS[5] + 9.6 },
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
    <div className={state.flip ? styles.flip : undefined}>
      <Hoca pose={state.pose} face={state.face} prop={state.prop ?? null} tired={state.tired} />
    </div>
  </div>;
}

function Show({ when, className = "", style, children }: { when: boolean; className?: string; style?: CSSProperties; children: ReactNode }) {
  return <div className={`${styles.appear} ${when ? styles.shown : ""} ${className}`} style={style}>{children}</div>;
}

// Kısa, anlamlı bilgi notu.
function Note({ when, tone, left, top, z, wide = false, children }: { when: boolean; tone?: "bad" | "good"; left: number; top: number; z?: number; wide?: boolean; children: ReactNode }) {
  const toneClass = tone === "bad" ? styles.noteBad : tone === "good" ? styles.noteGood : "";
  return <Show when={when} className={`${styles.note} ${toneClass} ${wide ? styles.noteWide : ""}`} style={{ left, top, zIndex: z }}>{children}</Show>;
}

// Kuyruktaki ve gişedeki insanlar: farklı ten, saç ve kıyafetler.
type Look = { skin: string; shirt: string; hair: "short" | "long" | "cap" | "scarf" | "curly"; hairColor: string };

const LOOKS: Record<string, Look> = {
  a: { skin: "#8d5a3b", shirt: "#c0563a", hair: "short", hairColor: "#1b1410" },
  b: { skin: "#c68e63", shirt: "#3f7d4f", hair: "scarf", hairColor: "#6a4c93" },
  c: { skin: "#f1d0b5", shirt: "#4a6fa5", hair: "long", hairColor: "#c79a4b" },
  d: { skin: "#5e3b28", shirt: "#d19a2a", hair: "curly", hairColor: "#140e0b" },
  e: { skin: "#e3b88f", shirt: "#7a5aa8", hair: "cap", hairColor: "#2b6cb0" },
  f: { skin: "#d9a77f", shirt: "#8a6b2e", hair: "short", hairColor: "#2c211b" },
  g: { skin: "#b97f57", shirt: "#5b7f3a", hair: "long", hairColor: "#20160f" },
};

function Person({ x, look, gone = false }: { x: number; look: Look; gone?: boolean }) {
  return <svg viewBox="0 0 60 150" className={styles.person} style={{ left: x - 32, opacity: gone ? 0 : 1 }} aria-hidden="true">
    <ellipse cx="30" cy="146" rx="18" ry="3.5" fill="rgba(0,0,0,.22)" />
    <rect x="17" y="96" width="11" height="48" rx="5" fill="#1d2b40" />
    <rect x="32" y="96" width="11" height="48" rx="5" fill="#26384f" />
    {look.hair === "scarf" && <path d="M10 112 Q8 40 30 8 Q52 40 50 112 Z" fill={look.hairColor} />}
    <rect x="14" y="44" width="32" height="62" rx="14" fill={look.shirt} />
    {look.hair === "long" && <path d="M14 30 Q14 8 30 9 Q46 8 46 30 L47 58 L41 58 L41 30 L19 30 L19 58 L13 58 Z" fill={look.hairColor} />}
    {look.hair === "scarf"
      ? <><circle cx="30" cy="28" r="17" fill={look.hairColor} /><ellipse cx="30" cy="30" rx="10.5" ry="12" fill={look.skin} /></>
      : <circle cx="30" cy="27" r="15" fill={look.skin} />}
    {look.hair === "short" && <path d="M15 26 Q15 10 30 11 Q45 10 45 24 Q38 18 30 18 Q21 18 15 26Z" fill={look.hairColor} />}
    {look.hair === "long" && <path d="M15 27 Q15 10 30 11 Q45 10 45 27 Q38 17 30 18 Q22 17 15 27Z" fill={look.hairColor} />}
    {look.hair === "curly" && <path d="M14 26 q-2-8 4-12 q2-7 9-6 q4-4 9 0 q8-1 9 7 q5 4 2 11 q-6-6-16-6 q-11 0-17 6Z" fill={look.hairColor} />}
    {look.hair === "cap" && <><path d="M15 23 Q15 9 30 9 Q45 9 45 23 Z" fill={look.hairColor} /><rect x="28" y="20" width="22" height="4" rx="2" fill={look.hairColor} /></>}
    <circle cx="25" cy="29" r="1.7" fill="#1d2b40" />
    <circle cx="35" cy="29" r="1.7" fill="#1d2b40" />
    <path d="M26 35 Q30 38 34 35" stroke="#5a2b1f" strokeWidth="1.5" fill="none" strokeLinecap="round" />
  </svg>;
}

// Tabela: üstte Türkçe ad, altında Kırgızca (Kiril) ad, en altta küçük adres.
function Building({ left, width, height = 260, tone, name, local, address, signTone, logo = false, className, children }: {
  left: number; width: number; height?: number; tone: string; name: ReactNode; local: string; address?: string; signTone: string; logo?: boolean; className?: string; children?: ReactNode;
}) {
  return <div className={`${styles.building} ${className ?? ""}`} style={{ left, width, height, background: tone }}>
    <div className={`${styles.sign} ${logo ? styles.signLogo : ""}`} style={{ background: signTone }}>
      {/* KTMÜ resmî logosu (manas.edu.kg logo PDF'inden kırpıldı). */}
      {/* eslint-disable-next-line @next/next/no-img-element */}
      {logo && <img src="/ktmu-logo.png" alt="" width={40} height={40} className={styles.logo} />}
      <span>
        <strong>{name}</strong>
        <em lang="ky">{local}</em>
        {address && <small>{address}</small>}
      </span>
    </div>
    {children}
  </div>;
}

// Gökyüzü, karlı Tanrı Dağları (Ala-Too), yeşil tepeler ve yol.
function Backdrop() {
  return <>
    <svg className={styles.backdrop} viewBox="0 0 600 300" preserveAspectRatio="none" aria-hidden="true">
      <defs>
        <linearGradient id="vizeSky" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#7fc3d9" />
          <stop offset=".65" stopColor="#c4e6ec" />
          <stop offset="1" stopColor="#e3f2ec" />
        </linearGradient>
      </defs>
      <rect width="600" height="300" fill="url(#vizeSky)" />
      <path d="M0 300 L0 175 L45 150 L80 162 L120 112 L160 150 L195 132 L240 82 L282 136 L312 122 L355 88 L398 140 L432 124 L472 92 L512 142 L550 118 L582 136 L600 128 L600 300 Z" fill="#6f95ab" />
      <g fill="#fbfdff">
        <path d="M104 132 L120 112 L136 134 L128 129 L121 137 L113 128 Z" />
        <path d="M219 108 L240 82 L262 110 L253 104 L245 113 L237 103 L228 112 Z" />
        <path d="M336 112 L355 88 L376 114 L367 108 L359 117 L351 107 L343 115 Z" />
        <path d="M454 115 L472 92 L491 117 L483 111 L475 119 L468 110 L460 117 Z" />
        <path d="M538 130 L550 118 L563 131 L556 128 L550 134 L544 128 Z" />
        <path d="M184 140 L195 132 L206 141 L199 139 L194 144 Z" />
      </g>
      <path d="M0 300 L0 222 L70 200 L135 216 L205 192 L275 214 L345 196 L415 218 L485 198 L555 214 L600 204 L600 300 Z" fill="#5f9473" />
      <path d="M0 300 L0 246 L90 234 L180 248 L270 236 L360 250 L450 238 L540 250 L600 242 L600 300 Z" fill="#4e8262" />
    </svg>
    <div className={styles.ground} aria-hidden="true" />
  </>;
}

const SPARK_ANGLES = Array.from({ length: 12 }, (_, i) => i * 30);

function Fireworks({ bursts }: { bursts: { x: number; y: number; color: string; delay: number }[] }) {
  return <div className={styles.fireworks} aria-hidden="true">
    {bursts.map((burst, b) => <div key={b} className={styles.burst} style={{ left: burst.x, top: burst.y, "--c": burst.color, "--d": `${burst.delay}s` } as CSSProperties}>
      <b />
      {SPARK_ANGLES.map(angle => <i key={angle} style={{ "--a": `${angle}deg` } as CSSProperties} />)}
    </div>)}
  </div>;
}

const STARS = [[40, 30], [150, 20], [230, 55], [300, 24], [380, 46], [450, 18], [520, 40], [575, 22], [120, 80], [500, 85]];

// ——— Sahneler ———

function SceneStart({ t }: { t: number }) {
  const days = t < 4.4 ? 60 : t < 4.8 ? 50 : 40;
  return <>
    <Building left={286} width={300} tone="#f3eee4" className={styles.campus} logo signTone="#2e2a7f"
      name="Manas Üniversitesi" local="Кыргыз-Түрк «Манас» университети" address="Cengiz Aytmatov Kampüsü · Cal, Bişkek">
      <div className={`${styles.campusDoor} ${t >= 3.0 && t < 4.0 ? styles.doorLit : ""}`} />
    </Building>
    <Show when={t >= 4.0} className={styles.calendar} style={{ left: 22, top: 18 }}>
      <span className={styles.calendarTop}>VİZE BİTİMİNE</span>
      <span className={`${styles.calendarDays} ${days === 40 ? styles.alarm : ""}`} key={days}>{days}</span>
      <span className={styles.calendarBottom}>gün kaldı</span>
    </Show>
    <Actor t={t} beats={[
      { t: 0, x: -60, pose: "walk", face: "smile" },
      { t: 2.4, x: 437, pose: "idle", face: "smile", say: "Merhaba Manas!" },
      { t: 3.0, x: 437, pose: "hidden" },
      { t: 4.0, x: 437, pose: "phone", face: "neutral", prop: "phone" },
      { t: 4.8, x: 437, pose: "phone", face: "wow", prop: "phone", say: "40 gün kaldı!" },
      { t: 5.6, x: 437, pose: "show", face: "smile", prop: "passport", say: "Önce çeviriler." },
      { t: 6.3, x: 437, pose: "walk", face: "smile", prop: "passport" },
      { t: 7.3, x: 660, pose: "walk", prop: "passport" },
    ]} />
  </>;
}

function SceneTranslate({ t }: { t: number }) {
  const docs = [
    { at: 2.4, label: "Pasaport", tone: "#1f6b3a" },
    { at: 2.9, label: "Evlilik c.", tone: "#a8323a" },
    { at: 3.4, label: "Nüfus c.", tone: "#2d5aa0" },
  ];
  return <>
    <Building left={320} width={260} tone="#e8eee9" name="Noter ve Tercüme" local="Нотариус жана котормо" address="Şeroy içi · Cal, Bişkek" signTone="#27356f">
      <div className={styles.counter} style={{ left: 22, width: 128 }}><Person x={64} look={LOOKS.f} /></div>
      <div className={styles.door} style={{ left: 180 }} />
    </Building>
    <div className={styles.desk}>
      {docs.map(doc => <Show key={doc.label} when={t >= doc.at && t < 5.0} className={styles.miniDoc} style={{ background: doc.tone }}>{doc.label}</Show>)}
    </div>
    <Show when={t >= 4.0 && t < 6.0} className={styles.stamp}>ONAYLI · КОТОРМО</Show>
    <Note when={t >= 3.4} left={18} top={16}>Eşin evlilik cüzdanı, çocuğun nüfus cüzdanı da çevrilir.</Note>
    <Actor t={t} beats={[
      { t: 0, x: -60, pose: "walk", face: "smile", prop: "passport" },
      { t: 2.0, x: 285, pose: "give", face: "smile", prop: "docs", say: "Üç belge, Kırgızca lütfen." },
      { t: 5.0, x: 285, pose: "done", prop: "docs", say: "Çeviriler tamam!" },
      { t: 6.4, x: 285, pose: "walk", face: "smile", prop: "docs" },
      { t: 8.0, x: 640, pose: "walk", prop: "docs" },
    ]} />
  </>;
}

function ScenePin({ t }: { t: number }) {
  const slots = [520, 470, 420, 370];
  const advanced = t >= 4.4 ? 3 : t >= 3.2 ? 2 : t >= 2.0 ? 1 : 0;
  const queue = [LOOKS.g, LOOKS.c, LOOKS.f];
  return <>
    <Building left={300} width={290} tone="#ece9e2" name="Nüfus Dairesi (ЦОН)" local="Калкты тейлөө борбору" address="Jumabek 121 · Nikâh Dairesi 2. kat" signTone="#087b72">
      <div className={`${styles.ticket} ${advanced === 3 ? styles.mine : ""}`} key={advanced}>ПИН{String(31 + advanced).padStart(3, "0")}</div>
      <div className={styles.counter} style={{ left: 180, width: 90 }} />
    </Building>
    {queue.map((look, i) => {
      const slot = i - advanced;
      return <Person key={i} x={slot < 0 ? 560 : slots[slot]} look={look} gone={slot < 0} />;
    })}
    <Note when={t >= 6.2} left={18} top={16}>Çocuk için PIN yalnızca okula gidecekse gereklidir.</Note>
    <Actor t={t} beats={[
      { t: 0, x: -60, pose: "walk", face: "neutral", prop: "docs" },
      { t: 1.6, x: 370, pose: "wait", face: "neutral", prop: "docs", say: "Sıram ПИН034." },
      { t: 2.0, x: 370, pose: "walk", face: "neutral", prop: "docs" },
      { t: 2.5, x: 420, pose: "wait", face: "neutral", prop: "docs" },
      { t: 3.2, x: 420, pose: "walk", face: "neutral", prop: "docs" },
      { t: 3.7, x: 470, pose: "wait", face: "neutral", prop: "docs" },
      { t: 4.4, x: 470, pose: "walk", face: "smile", prop: "docs" },
      { t: 4.9, x: 520, pose: "give", face: "smile", prop: "docs" },
      { t: 6.0, x: 520, pose: "done", prop: "card", say: "PIN hazır!" },
    ]} />
  </>;
}

function SceneInsurance({ t }: { t: number }) {
  return <>
    <Building left={40} width={200} tone="#dfe3e2" name="Başka banka" local="Башка банк" signTone="#6b7a77">
      <div className={styles.door} style={{ left: 80 }} />
    </Building>
    <Building left={320} width={260} tone="#e6efe7" name="Eldik Bank" local="Элдик Банк" address="Cal-23 mikrorayon, 101" signTone="#2e7d4f">
      <div className={styles.door} style={{ left: 95 }} />
    </Building>
    <Note when={t >= 1.7 && t < 5.6} tone="bad" left={24} top={12}>Başka bankada ödeme 12 000 som olur.</Note>
    <Note when={t >= 4.5 && t < 5.6} tone="good" left={330} top={12}>Eldik Bank’ta ödeme 1840 som.</Note>
    <Note when={t >= 5.8} left={150} top={12}>Dekontu Vize Birimine götür; poliçe 3 günde çıkar.</Note>
    <Actor t={t} beats={[
      { t: 0, x: -60, pose: "walk", face: "smile", prop: "cash" },
      { t: 1.5, x: 285, pose: "idle", face: "wow", flip: true, say: "12 000 som mu?!" },
      { t: 2.5, x: 285, pose: "idle", face: "frown", flip: true, say: "Yalnız Eldik Bank!" },
      { t: 3.3, x: 285, pose: "walk", face: "smile", prop: "cash" },
      { t: 4.3, x: 440, pose: "give", face: "smile", prop: "cash" },
      { t: 5.3, x: 440, pose: "done", prop: "receipt", say: "Dekont tamam." },
      { t: 6.6, x: 440, pose: "phone", face: "smile", prop: "phone" },
      { t: 7.4, x: 440, pose: "done", prop: "phone", say: "Poliçe geldi!" },
    ]} />
  </>;
}

function SceneReport({ t }: { t: number }) {
  return <>
    <Building left={250} width={320} tone="#eef0f4" name="2 No’lu Poliklinik" local="№2 Үй-бүлөлүк медицина борбору" address="İşembay Abdraimov 25/1" signTone="#3d5a99">
      <div className={`${styles.door} ${t >= 2.6 && t < 4.2 ? styles.doorLit : ""}`} style={{ left: 130 }}><span>304</span></div>
      <div className={styles.cross}>+</div>
    </Building>
    <Note when={t >= 4.8} tone="bad" left={18} top={16}>Özel hastane raporu kabul edilmez.</Note>
    <Note when={t >= 5.4} tone="bad" left={18} top={62}>Türkiye’den alınan rapor da geçmez.</Note>
    <Actor t={t} beats={[
      { t: 0, x: -60, pose: "walk", face: "smile" },
      { t: 2.0, x: 412, pose: "idle", face: "smile", say: "Oda 304." },
      { t: 2.6, x: 412, pose: "hidden" },
      { t: 4.2, x: 412, pose: "done", prop: "paper086", say: "086 raporu alındı!" },
    ]} />
  </>;
}

function SceneAids({ t }: { t: number }) {
  // Dışarıda uluslararası kuyruk; saat 11.20'den 12.00'ye doğru ilerler.
  const minutes = 20 + Math.min(38, t * 7);
  const slots = [382, 332, 282, 232];
  const advanced = [2.0, 2.8, 3.6, 4.4].filter(at => t >= at).length;
  const queue = [LOOKS.d, LOOKS.b, LOOKS.e, LOOKS.a];
  const hellos = [
    { at: 0.5, x: 382, text: "Salam!" },
    { at: 0.9, x: 282, text: "Hello!" },
    { at: 1.3, x: 332, text: "Привет!" },
  ];
  const night = t >= 7.4 && t < 8.8;
  return <>
    <Building left={330} width={252} tone="#f0ebe4" name="AIDS Test Merkezi" local="АИВ көзөмөлдөө борбору" address="Logvinenko 8 · Toktogul 62" signTone="#a8323a">
      <div className={`${styles.door} ${t >= 5.3 && t < 6.3 ? styles.doorLit : ""}`} style={{ left: 70 }} />
      <div className={styles.clock}>
        <svg viewBox="0 0 60 60" aria-hidden="true">
          <circle cx="30" cy="30" r="27" fill="#fffdf7" stroke="#27356f" strokeWidth="3" />
          <line x1="30" y1="30" x2="30" y2="13" stroke="#27356f" strokeWidth="3" strokeLinecap="round" style={{ transform: `rotate(${330 + minutes * 0.5}deg)`, transformOrigin: "30px 30px" }} />
          <line x1="30" y1="30" x2="30" y2="8" stroke="#e56845" strokeWidth="2" strokeLinecap="round" style={{ transform: `rotate(${minutes * 6}deg)`, transformOrigin: "30px 30px" }} />
        </svg>
        <small>Kan alımı 12.00’ye kadar</small>
      </div>
    </Building>
    {queue.map((look, i) => {
      const slot = i - advanced;
      return <Person key={i} x={slot < 0 ? 427 : slots[slot]} look={look} gone={slot < 0} />;
    })}
    {hellos.map(hello => <Show key={hello.text} when={t >= hello.at && t < 2.0} className={styles.hello} style={{ left: hello.x - 28, top: 116 }}>{hello.text}</Show>)}
    <div className={`${styles.night} ${night ? styles.nightOn : ""}`} aria-hidden="true">
      <span className={styles.moon} />
      {STARS.map(([x, y]) => <i key={`${x}-${y}`} style={{ left: x, top: y }} />)}
    </div>
    <Note when={t >= 7.6} left={190} top={18} z={7}>Sonuç ertesi gün çıkar.</Note>
    <Actor t={t} beats={[
      { t: 0, x: -60, pose: "walk", face: "neutral" },
      { t: 1.4, x: 182, pose: "wait", face: "neutral", say: "Uzun bir sıra…" },
      { t: 2.0, x: 182, pose: "walk", face: "neutral" },
      { t: 2.4, x: 232, pose: "wait", face: "neutral" },
      { t: 2.8, x: 232, pose: "walk", face: "neutral" },
      { t: 3.2, x: 282, pose: "wait", face: "neutral" },
      { t: 3.6, x: 282, pose: "walk", face: "neutral" },
      { t: 4.0, x: 332, pose: "wait", face: "neutral" },
      { t: 4.4, x: 332, pose: "walk", face: "neutral" },
      { t: 4.8, x: 382, pose: "wait", face: "wow", say: "12.00’den önce yetiştim!" },
      { t: 5.3, x: 427, pose: "hidden" },
      { t: 6.3, x: 382, pose: "tired", say: "Uff, yoruldum…" },
      { t: 7.4, x: 382, pose: "idle", face: "sleep", say: "Zzz…" },
      { t: 8.9, x: 382, pose: "phone", face: "smile", prop: "phone" },
      { t: 9.6, x: 382, pose: "done", prop: "phone", say: "Sonuç geldi!" },
    ]} />
  </>;
}

function SceneApply({ t }: { t: number }) {
  const chats = [
    { at: 2.0, label: "Sigorta poliçesi" },
    { at: 2.6, label: "086 raporu" },
    { at: 3.2, label: "AIDS sonucu" },
  ];
  return <>
    <Fireworks bursts={t >= 4.8 ? [
      { x: 90, y: 70, color: "#f2b544", delay: 0 },
      { x: 250, y: 48, color: "#e56845", delay: 0.4 },
      { x: 380, y: 80, color: "#2bb673", delay: 0.8 },
      { x: 520, y: 44, color: "#d14d9b", delay: 0.6 },
      { x: 170, y: 120, color: "#3a7bd5", delay: 1.1 },
      { x: 330, y: 30, color: "#f2b544", delay: 1.3 },
    ] : []} />
    <Building left={402} width={185} tone="#e4f1ee" logo name="Vize Birimi" local="Виза бөлүмү" address="KTMÜ · Aytmatov Kampüsü" signTone="#075f59">
      <div className={styles.counter} style={{ left: 26, width: 120 }}>
        <Show when={t >= 4.4} className={styles.bigCheck}><CircleCheck size={40} /></Show>
      </div>
    </Building>
    <div className={`${styles.chat} ${t >= 6.0 ? styles.chatGone : ""}`}>
      <div className={styles.chatTop}><MessageCircle size={13} /> Vize Birimi</div>
      {chats.map(chat => <Show key={chat.label} when={t >= chat.at} className={styles.bubble}>{chat.label} ✓✓</Show>)}
      <Show when={t >= 3.8} className={`${styles.bubble} ${styles.qr}`}><QrCode size={13} /> Vize ücreti · QR</Show>
    </div>
    <Note when={t >= 6.4} tone="good" left={18} top={12} wide>Vize bitiminden 1 ay önce başvur.</Note>
    <Note when={t >= 7.4} tone="bad" left={18} top={54} wide>Eksik evrakla başvuru kabul edilmez.</Note>
    <Actor t={t} beats={[
      { t: 0, x: -60, pose: "walk", face: "smile", prop: "phone", tired: true },
      { t: 1.6, x: 160, pose: "phone", face: "smile", prop: "phone" },
      { t: 4.8, x: 160, pose: "happy", prop: "phone", say: "Başvuru tamam!" },
      { t: 6.3, x: 160, pose: "happy", prop: "phone" },
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
      <div className={styles.canvas} style={{ width: CANVAS_W, height: CANVAS_H, transform: `translateX(-50%) scale(${scale})` }}>
        <Backdrop />
        <div key={`${loop}-${index}-${seek}`} className={styles.sceneLayer}><Render t={local} /></div>
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
