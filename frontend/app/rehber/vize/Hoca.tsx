// Animasyonun ana karakteri: elinde belge çantası olan hoca. Özgün, düz SVG.
// Pozlar kol/bacak açılarıyla, yürüme ve sevinme CSS animasyonuyla verilir.

import styles from "./animation.module.css";

export type Pose = "idle" | "walk" | "give" | "show" | "phone" | "happy" | "wait" | "hidden";
export type Face = "smile" | "neutral" | "frown" | "wow";
export type Prop = "passport" | "docs" | "card" | "cash" | "receipt" | "phone" | "paper086" | null;

const FRONT_ARM: Record<Pose, number> = { idle: 6, walk: 0, give: -80, show: -150, phone: -140, happy: -165, wait: 10, hidden: 0 };
const BACK_ARM: Record<Pose, number> = { idle: -4, walk: 0, give: -4, show: 6, phone: 4, happy: 160, wait: -4, hidden: 0 };

function HandProp({ kind }: { kind: Exclude<Prop, null> }) {
  switch (kind) {
    case "passport":
      return <g>
        <rect x="46" y="103" width="15" height="20" rx="2" fill="#1f6b3a" stroke="#14502b" />
        <circle cx="53.5" cy="111" r="3.4" fill="none" stroke="#d9b44a" strokeWidth="1.2" />
        <rect x="49" y="117" width="9" height="1.4" fill="#d9b44a" />
      </g>;
    case "docs":
      return <g>
        <rect x="50" y="98" width="17" height="22" rx="1.5" fill="#fffdf7" stroke="#9fb0ac" />
        <path d="M53 104h11M53 108h11M53 112h7" stroke="#9fb0ac" strokeWidth="1.2" />
        <rect x="44" y="106" width="13" height="17" rx="2" fill="#a8323a" />
        <rect x="41" y="109" width="13" height="17" rx="2" fill="#1f6b3a" stroke="#14502b" />
        <circle cx="47.5" cy="116" r="2.6" fill="none" stroke="#d9b44a" strokeWidth="1" />
      </g>;
    case "card":
      return <g>
        <rect x="45" y="103" width="26" height="16" rx="2.5" fill="#fffdf7" stroke="#087b72" strokeWidth="1.4" />
        <text x="58" y="114.5" fontSize="7.5" textAnchor="middle" fill="#087b72" fontWeight="800">PIN</text>
      </g>;
    case "cash":
      return <g>
        <rect x="44" y="104" width="26" height="13" rx="1.5" fill="#86c97f" stroke="#4d8f47" />
        <text x="57" y="113.5" fontSize="6.5" textAnchor="middle" fill="#24521f" fontWeight="800">1840</text>
      </g>;
    case "receipt":
    case "paper086":
      return <g>
        <rect x="47" y="96" width="19" height="25" rx="1.5" fill="#fffdf7" stroke="#9fb0ac" />
        <text x="56.5" y="106" fontSize="6.2" textAnchor="middle" fill="#087b72" fontWeight="800">{kind === "receipt" ? "DEKONT" : "086"}</text>
        <path d="M50 111h13M50 115h13" stroke="#9fb0ac" strokeWidth="1.2" />
      </g>;
    case "phone":
      return <g>
        <rect x="46" y="97" width="14" height="24" rx="3" fill="#17202a" />
        <rect x="47.6" y="99.6" width="10.8" height="18.4" rx="1.2" fill="#7fd6c4" />
        <path d="M50 107l2.2 2.2 4-4.4" stroke="#08332f" strokeWidth="1.5" fill="none" />
      </g>;
  }
}

export default function Hoca({ pose, face = "smile", prop = null }: { pose: Pose; face?: Face; prop?: Prop }) {
  const front = FRONT_ARM[pose];
  const back = BACK_ARM[pose];
  const motion = pose === "walk" ? styles.walking : pose === "happy" ? styles.jumping : pose === "wait" ? styles.waiting : "";
  const browY = face === "frown" ? 33.5 : face === "wow" ? 31 : 32.5;

  return <svg viewBox="0 0 100 180" className={`${styles.hoca} ${motion}`} aria-hidden="true">
    <ellipse cx="50" cy="174" rx="24" ry="4" fill="rgba(0,0,0,.28)" />
    <g className={styles.body}>
      <g className={styles.armBack} style={{ transform: `rotate(${back}deg)` }}>
        <rect x="43" y="64" width="12" height="44" rx="6" fill="#0b5f57" />
        <circle cx="49" cy="110" r="5" fill="#e9b892" />
        <path d="M44 113v-4.5h10v4.5" stroke="#5e3b1a" strokeWidth="2.4" fill="none" />
        <rect x="35" y="112" width="28" height="20" rx="3" fill="#8a5a2b" />
        <rect x="35" y="119.5" width="28" height="2.2" fill="#6e4520" />
        <rect x="47" y="118.5" width="4" height="4" rx="1" fill="#d9b44a" />
      </g>
      <g className={styles.legBack}>
        <rect x="40" y="110" width="11" height="56" rx="5" fill="#1d2b40" />
        <rect x="35" y="162" width="18" height="8" rx="4" fill="#0f141a" />
      </g>
      <g className={styles.legFront}>
        <rect x="50" y="110" width="11" height="56" rx="5" fill="#26384f" />
        <rect x="50" y="162" width="18" height="8" rx="4" fill="#0f141a" />
      </g>
      <path d="M33 71 Q33 60 44 59 L56 59 Q67 60 67 71 L66 117 L34 117 Z" fill="#0f7a70" />
      <path d="M45 59 L50 73 L55 59 Z" fill="#fffdf7" />
      <path d="M50 73 L50 117" stroke="#0b5f57" strokeWidth="1.4" />
      <rect x="46" y="50" width="8" height="10" fill="#e2ae87" />
      <g className={styles.head}>
        <circle cx="50" cy="38" r="17" fill="#f0c4a0" />
        <path d="M33 38 Q32 18 50 19 Q68 18 67 36 Q62 27 50 28 Q40 28 33 38Z" fill="#3b2a20" />
        <circle cx="44" cy="40" r="5" fill="rgba(255,255,255,.25)" stroke="#1d2b40" strokeWidth="1.6" />
        <circle cx="57" cy="40" r="5" fill="rgba(255,255,255,.25)" stroke="#1d2b40" strokeWidth="1.6" />
        <path d="M49 40h3" stroke="#1d2b40" strokeWidth="1.6" />
        <circle cx="44.5" cy="40.5" r="1.4" fill="#1d2b40" />
        <circle cx="57.5" cy="40.5" r="1.4" fill="#1d2b40" />
        {face === "frown"
          ? <path d={`M40 ${browY - 1.5}l7 2.5M61 ${browY - 1.5}l-7 2.5`} stroke="#3b2a20" strokeWidth="1.8" strokeLinecap="round" />
          : <path d={`M40 ${browY}q4-2 7 0M54 ${browY}q4-2 7 0`} stroke="#3b2a20" strokeWidth="1.8" fill="none" strokeLinecap="round" />}
        {face === "smile" && <path d="M45 48 Q50.5 53 56 48" stroke="#8a3d2b" strokeWidth="1.8" fill="none" strokeLinecap="round" />}
        {face === "neutral" && <path d="M46 49.5 H55" stroke="#8a3d2b" strokeWidth="1.8" strokeLinecap="round" />}
        {face === "frown" && <path d="M45 51 Q50.5 46.5 56 51" stroke="#8a3d2b" strokeWidth="1.8" fill="none" strokeLinecap="round" />}
        {face === "wow" && <ellipse cx="50.5" cy="49.5" rx="2.4" ry="3" fill="#8a3d2b" />}
      </g>
      <g className={styles.armFront} style={{ transform: `rotate(${front}deg)` }}>
        <rect x="45" y="64" width="12" height="44" rx="6" fill="#119184" />
        <circle cx="51" cy="110" r="5" fill="#f0c4a0" />
        {prop && <g style={{ transform: `rotate(${-front}deg)`, transformOrigin: "51px 110px" }}><HandProp kind={prop} /></g>}
      </g>
    </g>
  </svg>;
}
