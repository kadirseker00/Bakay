// Animasyonun ana karakteri: belge çantalı, kravatlı, gözlüklü sevimli hoca.
// Özgün, düz SVG. Yolda ve iş başında yürüdüğü yöne (sağa) dönük profilden
// görünür; yalnız bir iş bittiğinde ("done", "happy") önden izleyiciye döner.
// Kollar omuzdan, bacaklar kalçadan bağlı; dirsek ve diz ayrı eklem.

import type { CSSProperties } from "react";
import styles from "./animation.module.css";

export type Pose = "idle" | "walk" | "give" | "show" | "phone" | "wait" | "tired" | "hidden" | "done" | "happy";
export type Face = "smile" | "neutral" | "frown" | "wow" | "tired" | "sleep";
export type Prop = "passport" | "docs" | "card" | "cash" | "receipt" | "phone" | "paper086" | null;

const SKIN = "#f6cfae";
const SKIN_SHADE = "#eab48f";
const HAIR = "#4a3426";
const INK = "#2a2522";
const FRAME = "#2a3550";
const BLUSH = "#f49a8a";

// Profil pozları: [yakın üst kol, yakın ön kol, uzak üst kol, uzak ön kol, yakın uyluk, uzak uyluk].
// Sağa bakan karakterde negatif açı uzvu öne çevirir.
const SIDE: Record<Exclude<Pose, "done" | "happy">, number[]> = {
  idle: [4, -10, -4, -10, -3, 4],
  walk: [0, -15, 0, -15, 0, 0],
  give: [-76, -14, -3, -10, -3, 4],
  show: [-140, -14, 4, -10, -3, 4],
  phone: [-24, -102, 0, -10, -3, 4],
  wait: [6, -12, -4, -10, -3, 4],
  tired: [-116, -80, 8, -4, -6, 6],
  hidden: [4, -10, -4, -10, -3, 4],
};

// Önden pozlar: [sol üst kol, sol ön kol, sağ üst kol, sağ ön kol].
const FRONT: Record<"done" | "happy", number[]> = {
  done: [10, -4, -58, -66],
  happy: [150, 12, -150, -12],
};

const rot = (deg: number, x: number, y: number): CSSProperties => ({ transform: `rotate(${deg}deg)`, transformOrigin: `${x}px ${y}px` });

function HandProp({ kind }: { kind: Exclude<Prop, null> }) {
  // Elin merkezi (0,0); öğeler el etrafına çizilir.
  switch (kind) {
    case "passport":
      return <g>
        <rect x="-4" y="-10" width="15" height="20" rx="2" fill="#1f6b3a" stroke="#14502b" />
        <circle cx="3.5" cy="-2" r="3.4" fill="none" stroke="#d9b44a" strokeWidth="1.2" />
        <rect x="-1" y="4" width="9" height="1.4" fill="#d9b44a" />
      </g>;
    case "docs":
      return <g>
        <rect x="0" y="-15" width="17" height="22" rx="1.5" fill="#fffdf7" stroke="#9fb0ac" />
        <path d="M3 -9h11M3 -5h11M3 -1h7" stroke="#9fb0ac" strokeWidth="1.2" />
        <rect x="-5" y="-7" width="13" height="17" rx="2" fill="#a8323a" />
        <rect x="-8" y="-4" width="13" height="17" rx="2" fill="#1f6b3a" stroke="#14502b" />
        <circle cx="-1.5" cy="3" r="2.6" fill="none" stroke="#d9b44a" strokeWidth="1" />
      </g>;
    case "card":
      return <g>
        <rect x="-4" y="-9" width="27" height="16" rx="2.5" fill="#fffdf7" stroke="#087b72" strokeWidth="1.4" />
        <text x="9.5" y="2.5" fontSize="7.5" textAnchor="middle" fill="#087b72" fontWeight="800">ПИН</text>
      </g>;
    case "cash":
      return <g>
        <rect x="-4" y="-7" width="26" height="13" rx="1.5" fill="#86c97f" stroke="#4d8f47" />
        <text x="9" y="2.5" fontSize="6.5" textAnchor="middle" fill="#24521f" fontWeight="800">1840</text>
      </g>;
    case "receipt":
    case "paper086":
      return <g>
        <rect x="-3" y="-16" width="19" height="25" rx="1.5" fill="#fffdf7" stroke="#9fb0ac" />
        <text x="6.5" y="-6" fontSize="6.2" textAnchor="middle" fill="#087b72" fontWeight="800">{kind === "receipt" ? "DEKONT" : "086"}</text>
        <path d="M0 -1h13M0 3h13" stroke="#9fb0ac" strokeWidth="1.2" />
      </g>;
    case "phone":
      return <g>
        <rect x="-5" y="-15" width="14" height="24" rx="3" fill="#17202a" />
        <rect x="-3.4" y="-12.4" width="10.8" height="18.4" rx="1.2" fill="#7fd6c4" />
        <path d="M-1 -5l2.2 2.2 4-4.4" stroke="#08332f" strokeWidth="1.5" fill="none" />
      </g>;
  }
}

function Briefcase({ x }: { x: number }) {
  return <g>
    <path d={`M${x - 5} 106v-4.5h10v4.5`} stroke="#5e3b1a" strokeWidth="2.4" fill="none" />
    <rect x={x - 14} y="105" width="28" height="20" rx="4" fill="#9a6532" />
    <rect x={x - 14} y="112.5" width="28" height="2.2" fill="#7a4d22" />
    <rect x={x - 2} y="111.5" width="4" height="4" rx="1" fill="#e2bd55" />
  </g>;
}

// Omuz (sx, 70) → dirsek (sx, 86) → el (sx, 102).
function Arm({ sx, upper, fore, sleeve, skin, prop, briefcase, armClass, foreClass }: {
  sx: number; upper: number; fore: number; sleeve: string; skin: string; prop?: Prop; briefcase?: boolean; armClass: string; foreClass: string;
}) {
  const upright = rot(-(upper + fore), sx, 102);
  return <g className={armClass} style={rot(upper, sx, 70)}>
    <rect x={sx - 5} y="65" width="10" height="24" rx="5" fill={sleeve} />
    <g className={foreClass} style={rot(fore, sx, 86)}>
      <rect x={sx - 4.5} y="83" width="9" height="18" rx="4.5" fill={sleeve} />
      <circle cx={sx} cy="102" r="5.2" fill={skin} />
      {prop && <g style={upright}><g transform={`translate(${sx} 102)`}><HandProp kind={prop} /></g></g>}
      {briefcase && <g style={upright}><Briefcase x={sx} /></g>}
    </g>
  </g>;
}

// Kalça (hx, 114) → diz (hx, 134) → ayak.
function Leg({ hx, thigh, cloth, toe, legClass, shinClass }: { hx: number; thigh: number; cloth: string; toe: number; legClass: string; shinClass: string }) {
  return <g className={legClass} style={rot(thigh, hx, 114)}>
    <rect x={hx - 5.5} y="110" width="11" height="27" rx="5.5" fill={cloth} />
    <g className={shinClass} style={rot(0, hx, 134)}>
      <rect x={hx - 5} y="132" width="10" height="28" rx="5" fill={cloth} />
      <path d={toe > 0
        ? `M${hx - 6} 168 L${hx - 6} 163 Q${hx - 6} 158 ${hx} 158 L${hx + toe - 6} 158 Q${hx + toe} 159 ${hx + toe} 164 L${hx + toe} 168 Z`
        : `M${hx + 6} 168 L${hx + 6} 163 Q${hx + 6} 158 ${hx} 158 L${hx + toe + 6} 158 Q${hx + toe} 159 ${hx + toe} 164 L${hx + toe} 168 Z`} fill="#1a1d24" />
    </g>
  </g>;
}

function SideFace({ face }: { face: Face }) {
  return <g>
    <path d="M57 39.5 L46 40.5" stroke={FRAME} strokeWidth="1.6" />
    {face === "tired" ? <path d="M60.5 40.5 q3.5 2.4 7 0" stroke={INK} strokeWidth="1.8" fill="none" strokeLinecap="round" />
      : face === "sleep" ? <path d="M60.5 39.5 q3.5 2.6 7 0" stroke={INK} strokeWidth="1.8" fill="none" strokeLinecap="round" />
      : <><ellipse cx="64" cy="39.5" rx="3.6" ry="4.6" fill={INK} /><circle cx="65.4" cy="37.6" r="1.4" fill="#fff" /></>}
    <circle cx="64" cy="39.5" r="7.4" fill="rgba(255,255,255,.22)" stroke={FRAME} strokeWidth="1.8" />
    {face === "frown"
      ? <path d="M58.5 28.5 l9 3" stroke={HAIR} strokeWidth="2" strokeLinecap="round" />
      : <path d={face === "wow" ? "M59 27.5 q4.5-2.6 9 0" : face === "tired" || face === "sleep" ? "M59 30.5 q4.5 1.2 9 2" : "M59 29.5 q4.5-2.4 9 0"} stroke={HAIR} strokeWidth="2" fill="none" strokeLinecap="round" />}
    <ellipse cx="62" cy="50" rx="4.2" ry="2.6" fill={BLUSH} opacity=".6" />
    <circle cx="74.6" cy="44" r="2.6" fill={SKIN_SHADE} />
    {face === "smile" && <path d="M64.5 52.5 Q68.5 56 72 51.5" stroke="#8a3d2b" strokeWidth="1.9" fill="none" strokeLinecap="round" />}
    {face === "neutral" && <path d="M65 53 H71" stroke="#8a3d2b" strokeWidth="1.9" strokeLinecap="round" />}
    {face === "frown" && <path d="M64.5 55 Q68.5 51.5 72 54.5" stroke="#8a3d2b" strokeWidth="1.9" fill="none" strokeLinecap="round" />}
    {face === "wow" && <ellipse cx="69" cy="53.5" rx="2" ry="2.7" fill="#8a3d2b" />}
    {face === "tired" && <ellipse cx="69" cy="53.5" rx="2.4" ry="1.7" fill="#8a3d2b" />}
    {face === "sleep" && <path d="M66 53.5 H70" stroke="#8a3d2b" strokeWidth="1.6" strokeLinecap="round" />}
  </g>;
}

function SideView({ pose, face, prop, isTired }: { pose: keyof typeof SIDE; face: Face; prop: Prop; isTired: boolean }) {
  const [nearUpper, nearFore, farUpper, farFore, nearThigh, farThigh] = SIDE[pose];
  return <g className={styles.body}>
    <Arm sx={47} upper={farUpper} fore={farFore} sleeve="#0b5f57" skin={SKIN_SHADE} briefcase armClass={styles.armFar} foreClass={styles.foreFar} />
    <Leg hx={50} thigh={farThigh} cloth="#1b2638" toe={19} legClass={styles.legFar} shinClass={styles.shinFar} />
    <Leg hx={50} thigh={nearThigh} cloth="#2b3f5a" toe={19} legClass={styles.legNear} shinClass={styles.shinNear} />
    <path d="M38 77 Q38 62 50 61 Q62 61 63 75 L64 113 Q51 118 37 113 Z" fill="#119184" />
    <path d="M55 62 L62 64.5 L58.5 73 Z" fill="#fffdf7" />
    <path d="M58.6 63.4 L62.2 63.6 L61.6 67.2 L59 67 Z" fill="#b8344a" />
    <path d="M59 67 L61.6 67.2 L63 88 L60.6 92 L58.6 88 Z" fill="#d6455a" />
    <path d="M58 74 L59 113" stroke="#0b6f66" strokeWidth="1.4" />
    <g className={styles.head}>
      <circle cx="52" cy="38" r="23" fill={SKIN} />
      <path d="M30 45 Q26 14 52 14 Q75 14 75.5 34 Q68 26 58 27 Q53 28 52 34 Q47 30 42 37 L40.5 53 Q32 53 30 45 Z" fill={HAIR} />
      <path d="M49 15.5 q3 -11 11 -9 q-6.5 2.4 -6.5 9.5 Z" fill={HAIR} />
      <ellipse cx="44" cy="42.5" rx="3.6" ry="4.6" fill={SKIN_SHADE} />
      <SideFace face={isTired && face !== "sleep" ? "tired" : face} />
      {isTired && <g className={styles.sweat}>
        <path d="M77 22 q2.8 4.2 0 6.4 q-2.8-2.2 0-6.4Z" fill="#7cc8f0" />
        <path d="M33 24 q2.4 3.6 0 5.4 q-2.4-1.8 0-5.4Z" fill="#7cc8f0" />
      </g>}
    </g>
    <Arm sx={53} upper={nearUpper} fore={nearFore} sleeve="#14a291" skin={SKIN} prop={prop} armClass={styles.armNear} foreClass={styles.foreNear} />
  </g>;
}

function FrontView({ pose, prop }: { pose: "done" | "happy"; prop: Prop }) {
  const [leftUpper, leftFore, rightUpper, rightFore] = FRONT[pose];
  return <g className={styles.body}>
    <Leg hx={44} thigh={2} cloth="#2b3f5a" toe={-15} legClass={styles.limb} shinClass={styles.limb} />
    <Leg hx={56} thigh={-2} cloth="#2b3f5a" toe={15} legClass={styles.limb} shinClass={styles.limb} />
    <Arm sx={35} upper={leftUpper} fore={leftFore} sleeve="#14a291" skin={SKIN} briefcase armClass={styles.limb} foreClass={styles.limb} />
    <Arm sx={65} upper={rightUpper} fore={rightFore} sleeve="#14a291" skin={SKIN} prop={prop} armClass={styles.limb} foreClass={styles.limb} />
    <path d="M35 77 Q35 62 50 61 Q65 62 65 77 L66 113 Q50 118 34 113 Z" fill="#119184" />
    <path d="M44.5 61.5 L50 72 L55.5 61.5 Z" fill="#fffdf7" />
    <path d="M47.6 62.4 H52.4 L51.5 67 H48.5 Z" fill="#b8344a" />
    <path d="M48.5 67 H51.5 L54 88 L50 93 L46 88 Z" fill="#d6455a" />
    <g className={styles.head}>
      <ellipse cx="27.5" cy="42" rx="3.6" ry="4.8" fill={SKIN_SHADE} />
      <ellipse cx="72.5" cy="42" rx="3.6" ry="4.8" fill={SKIN_SHADE} />
      <circle cx="50" cy="38" r="23" fill={SKIN} />
      <path d="M27.5 43 Q24 13 50 14 Q76 13 72.5 43 Q70 29 60 26.5 Q50 33 39 27 Q30 30 27.5 43 Z" fill={HAIR} />
      <path d="M47 15 q3 -11 11 -9 q-6.5 2.4 -6.5 9.5 Z" fill={HAIR} />
      <ellipse cx="42" cy="40" rx="3.4" ry="4.4" fill={INK} /><circle cx="43.2" cy="38.2" r="1.3" fill="#fff" />
      <ellipse cx="58" cy="40" rx="3.4" ry="4.4" fill={INK} /><circle cx="59.2" cy="38.2" r="1.3" fill="#fff" />
      <circle cx="42" cy="40" r="7.2" fill="rgba(255,255,255,.22)" stroke={FRAME} strokeWidth="1.8" />
      <circle cx="58" cy="40" r="7.2" fill="rgba(255,255,255,.22)" stroke={FRAME} strokeWidth="1.8" />
      <path d="M49.2 40 h1.6" stroke={FRAME} strokeWidth="1.8" />
      <path d="M36 29.5 q5-2.6 10 0 M54 29.5 q5-2.6 10 0" stroke={HAIR} strokeWidth="2" fill="none" strokeLinecap="round" />
      <ellipse cx="36" cy="50" rx="4.2" ry="2.6" fill={BLUSH} opacity=".6" />
      <ellipse cx="64" cy="50" rx="4.2" ry="2.6" fill={BLUSH} opacity=".6" />
      {pose === "happy"
        ? <path d="M43.5 50.5 Q50 60 56.5 50.5 Z" fill="#8a3d2b" />
        : <path d="M44.5 51 Q50 56 55.5 51" stroke="#8a3d2b" strokeWidth="2" fill="none" strokeLinecap="round" />}
    </g>
  </g>;
}

export default function Hoca({ pose, face = "smile", prop = null, tired = false }: { pose: Pose; face?: Face; prop?: Prop; tired?: boolean }) {
  const front = pose === "done" || pose === "happy";
  const isTired = !front && (pose === "tired" || tired);
  const motion = pose === "walk" ? styles.walking : pose === "happy" ? styles.jumping
    : pose === "wait" ? styles.waiting : pose === "tired" ? styles.tiredPose : "";

  return <svg viewBox="0 0 100 180" className={`${styles.hoca} ${motion} ${isTired ? styles.slow : ""}`} aria-hidden="true">
    <ellipse cx="51" cy="172" rx="22" ry="4" fill="rgba(0,0,0,.22)" />
    {front
      ? <FrontView pose={pose} prop={prop} />
      : <SideView pose={pose as keyof typeof SIDE} face={face} prop={prop} isTired={isTired} />}
  </svg>;
}
