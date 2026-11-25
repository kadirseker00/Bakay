"use client";

// Vize sürecini 60 saniyede anlatan sayfa içi animasyon. Zamanlayıcı JS'te,
// sahne içi hareketler CSS'te; duraklatınca ikisi birlikte durur. Ekran dışında
// ve "hareketi azalt" tercihinde kendiliğinden oynamaz.

import { useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import {
  Baby, BookUser, Building2, CalendarClock, CircleCheck, CircleX, Clock, FileText, Fingerprint,
  Heart, Hospital, Landmark, Languages, MessageCircle, Pause, Play, QrCode, RotateCcw, School,
  ShieldCheck, Smartphone, Stamp, Stethoscope, TestTube,
} from "lucide-react";
import styles from "./animation.module.css";

type Scene = { id: string; label: string; duration: number; caption: string };

const SCENES: Scene[] = [
  { id: "basla", label: "Başla", duration: 6, caption: "Vizen bitmeden 40 gün önce hazırlığa başla." },
  { id: "ceviri", label: "Çeviri", duration: 9, caption: "1 · Önce çeviriler: pasaport ve evlilik cüzdanı, noter onaylı Kırgızca." },
  { id: "pin", label: "PIN", duration: 7, caption: "2 · Pasaport çevirisiyle ЦОН’dan PIN al. Çocuğa PIN, okula gidecekse." },
  { id: "sigorta", label: "Sigorta", duration: 10, caption: "3 · Sigorta: 1840 som, yalnız Eldik Bank’tan. Dekontla Vize Birimine." },
  { id: "rapor", label: "086", duration: 8, caption: "4 · 086 sağlık raporu: 2 No’lu Poliklinik, oda 304." },
  { id: "aids", label: "AIDS", duration: 8, caption: "5 · AIDS testi: kan alımı hafta içi 12.00’ye kadar." },
  { id: "basvuru", label: "Başvuru", duration: 12, caption: "6 · Belgeler telefonda, ücret QR ile. Vize bitiminden 1 ay önce başvur." },
];

const STARTS = SCENES.reduce<number[]>((acc, scene, i) => [...acc, i === 0 ? 0 : acc[i - 1] + SCENES[i - 1].duration], []);
const TOTAL = SCENES.reduce((sum, scene) => sum + scene.duration, 0);

// Belge çantasına düşen belgeler: hangi saniyede "alınmış" sayılır.
const BAG = [
  { id: "ceviri", label: "Çeviriler", icon: Languages, at: STARTS[1] + 7 },
  { id: "pin", label: "PIN", icon: Fingerprint, at: STARTS[2] + 5 },
  { id: "police", label: "Poliçe", icon: ShieldCheck, at: STARTS[3] + 8.5 },
  { id: "rapor", label: "086", icon: Stethoscope, at: STARTS[4] + 6 },
  { id: "aids", label: "AIDS", icon: TestTube, at: STARTS[5] + 6.5 },
];

function sceneAt(time: number) {
  let index = SCENES.length - 1;
  for (let i = 0; i < SCENES.length; i++) {
    if (time < STARTS[i] + SCENES[i].duration) { index = i; break; }
  }
  return index;
}

function Item({ delay, children, className = "" }: { delay: number; children: ReactNode; className?: string }) {
  return <div className={`${styles.pop} ${className}`} style={{ animationDelay: `${delay}s` }}>{children}</div>;
}

function SceneStart() {
  return <div className={styles.sceneCenter}>
    <Item delay={0.2} className={styles.calendar}>
      <CalendarClock size={30} />
      <span className={styles.countdown} aria-hidden="true">
        <span>60</span><span>50</span><span>40</span>
      </span>
      <small>gün kala</small>
    </Item>
    <Item delay={2.6} className={styles.headline}>Vize uzatma 6 adımda</Item>
    <Item delay={3.4} className={styles.subline}>Sıra önemli: bir adım bir sonrakinin şartı.</Item>
  </div>;
}

function SceneTranslate() {
  return <div className={styles.sceneRow}>
    <div className={styles.docsColumn}>
      <Item delay={0.3} className={styles.doc}><BookUser size={22} /> Pasaport</Item>
      <Item delay={1.0} className={styles.doc}><Heart size={22} /> Evlilik cüzdanı <em>eş için</em></Item>
      <Item delay={1.7} className={styles.doc}><Baby size={22} /> Nüfus cüzdanı <em>çocuk için</em></Item>
    </div>
    <Item delay={2.6} className={styles.arrow}>→</Item>
    <div className={styles.notary}>
      <Item delay={3.0} className={styles.place}><Languages size={26} /><strong>Noter + Kırgızca tercüme</strong><small>Cal · Şeroy içinde</small></Item>
      <div className={styles.stamp} style={{ animationDelay: "4.6s" }}><Stamp size={20} /> ONAYLI</div>
    </div>
  </div>;
}

function ScenePin() {
  return <div className={styles.sceneRow}>
    <Item delay={0.3} className={styles.doc}><Languages size={22} /> Pasaport çevirisi</Item>
    <Item delay={1.1} className={styles.arrow}>→</Item>
    <Item delay={1.5} className={styles.place}><Building2 size={26} /><strong>ЦОН · Nüfus Dairesi</strong><small>Jumabeka 121 · Nikâh Dairesi 2. kat</small></Item>
    <Item delay={3.0} className={styles.arrow}>→</Item>
    <div className={styles.pinColumn}>
      <Item delay={3.4} className={styles.pin}>
        <Fingerprint size={22} />
        <span className={styles.digits}>{"1234 5678".split("").map((d, i) => <span key={i} style={{ animationDelay: `${3.6 + i * 0.12}s` }}>{d}</span>)}</span>
      </Item>
      <Item delay={4.8} className={styles.note}><School size={16} /> Çocuk: okula gidecekse</Item>
    </div>
  </div>;
}

function SceneInsurance() {
  return <div className={styles.sceneRow}>
    <div className={styles.compare}>
      <Item delay={0.3} className={`${styles.option} ${styles.good}`}><Landmark size={22} /><span><strong>Eldik Bank</strong><small>1840 som</small></span><CircleCheck size={22} /></Item>
      <Item delay={1.4} className={`${styles.option} ${styles.bad}`}><Landmark size={22} /><span><strong>Başka banka</strong><small>12000 som</small></span><CircleX size={22} /></Item>
    </div>
    <Item delay={3.4} className={styles.arrow}>→</Item>
    <Item delay={3.9} className={styles.place}><FileText size={26} /><strong>Dekont + pasaport</strong><small>Vize Birimi · sigorta masası</small></Item>
    <Item delay={5.6} className={styles.arrow}>→</Item>
    <Item delay={6.1} className={styles.doc}><ShieldCheck size={22} /> Poliçe <em>3 gün içinde</em></Item>
  </div>;
}

function SceneReport() {
  return <div className={styles.sceneRow}>
    <Item delay={0.3} className={styles.place}><Hospital size={26} /><strong>2 No’lu Poliklinik</strong><small>Abdraimov 25/1 · oda 304</small></Item>
    <Item delay={1.6} className={styles.arrow}>→</Item>
    <div className={styles.docsColumn}>
      <Item delay={2.0} className={styles.doc}><Stethoscope size={22} /> 086 raporu <em>“nöl 86 spravka”</em></Item>
      <Item delay={3.4} className={`${styles.option} ${styles.bad} ${styles.small}`}><span><strong>Özel hastane</strong></span><CircleX size={18} /></Item>
      <Item delay={4.0} className={`${styles.option} ${styles.bad} ${styles.small}`}><span><strong>Türkiye’den rapor</strong></span><CircleX size={18} /></Item>
    </div>
  </div>;
}

function SceneAids() {
  return <div className={styles.sceneRow}>
    <div className={styles.docsColumn}>
      <Item delay={0.3} className={styles.place}><TestTube size={24} /><strong>Logvinenko 8</strong><small>sonuç ertesi gün online</small></Item>
      <Item delay={1.0} className={styles.place}><TestTube size={24} /><strong>Toktogul 62</strong><small>hızlı, sonuç elden</small></Item>
    </div>
    <Item delay={2.0} className={styles.clock}><Clock size={26} /><span>12.00</span><small>hafta içi kan alımı</small></Item>
    <Item delay={3.6} className={styles.arrow}>→</Item>
    <Item delay={4.0} className={styles.doc}><TestTube size={22} /> Sonuç <em>ekran görüntüsü veya PDF</em></Item>
  </div>;
}

function SceneApply() {
  const chats = ["Sigorta poliçesi", "086 raporu (önlü arkalı)", "AIDS test sonucu"];
  return <div className={styles.sceneRow}>
    <div className={styles.phone}>
      <div className={styles.phoneTop}><MessageCircle size={14} /> Vize Birimi</div>
      {chats.map((chat, i) => <div key={chat} className={styles.bubble} style={{ animationDelay: `${0.6 + i * 0.9}s` }}>{chat} ✓✓</div>)}
      <div className={`${styles.bubble} ${styles.qr}`} style={{ animationDelay: "3.6s" }}><QrCode size={16} /> Vize ücreti · QR</div>
    </div>
    <div className={styles.docsColumn}>
      <Item delay={5.0} className={styles.place}><Smartphone size={24} /><strong>Telefon yeter</strong><small>Çıktı, asıl belge getirme</small></Item>
      <Item delay={6.4} className={`${styles.option} ${styles.good}`}><CalendarClock size={22} /><span><strong>Bitişten 1 ay önce</strong><small>başvur</small></span><CircleCheck size={22} /></Item>
      <Item delay={7.8} className={`${styles.option} ${styles.bad}`}><FileText size={22} /><span><strong>Eksik evrak</strong><small>kabul edilmez</small></span><CircleX size={22} /></Item>
    </div>
  </div>;
}

const RENDER: Record<string, () => JSX.Element> = {
  basla: SceneStart, ceviri: SceneTranslate, pin: ScenePin, sigorta: SceneInsurance,
  rapor: SceneReport, aids: SceneAids, basvuru: SceneApply,
};

export default function VisaAnimation() {
  const [elapsed, setElapsed] = useState(0); // döngüler dahil toplam saniye
  const [playing, setPlaying] = useState(true);
  const [inView, setInView] = useState(false);
  const [seek, setSeek] = useState(0);
  const rootRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) setPlaying(false);
    const node = rootRef.current;
    if (!node) return;
    const observer = new IntersectionObserver(([entry]) => setInView(entry.isIntersecting), { threshold: 0.35 });
    observer.observe(node);
    return () => observer.disconnect();
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

    <div className={styles.screen} aria-hidden="true">
      <div key={`${loop}-${index}-${seek}`} className={styles.scene}><Render /></div>
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
          <span className={styles.fill} style={{ width: i < index ? "100%" : i === index ? `${((time - STARTS[i]) / item.duration) * 100}%` : "0%" }} />
          <span className={styles.tick}>{item.label}</span>
        </button>)}
      </div>
      <button type="button" onClick={restart} aria-label="Baştan oynat"><RotateCcw size={16} /></button>
      <span className={styles.time}>{`0:${String(Math.floor(time)).padStart(2, "0")}`} / 1:00</span>
    </div>
  </div>;
}
