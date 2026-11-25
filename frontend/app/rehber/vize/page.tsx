import type { Metadata } from "next";
import { AlertTriangle, ArrowLeft, ArrowUpRight, CalendarClock, FileCheck2, MapPin, MessageCircleQuestion, Wallet } from "lucide-react";
import Logo from "../../components/Logo";
import Wordmark from "../../components/Wordmark";
import { AIDS_RESULT_URL, CHECKLISTS, PAYMENT, QUESTIONS, RULES, SOURCE, STEPS, type MapLink } from "./content";
import styles from "./guide.module.css";
import VisaAnimation from "./VisaAnimation";

export const metadata: Metadata = {
  title: "Personel vize rehberi | bak.ai",
  description: "KTMÜ çalışanları ve aile bireyleri için vize uzatma adımları: PIN, zorunlu sağlık sigortası, 086 sağlık raporu, AIDS testi ve gerekli belgeler.",
};

function Places({ places }: { places: MapLink[] }) {
  return <ul className={styles.places}>
    {places.map(place => <li key={place.label}>
      <MapPin size={15} aria-hidden="true" />
      <span>{place.label}</span>
      <span className={styles.mapLinks}>
        {place.yandex && <a href={place.yandex} target="_blank" rel="noopener noreferrer">Yandex</a>}
        {place.google && <a href={place.google} target="_blank" rel="noopener noreferrer">Google</a>}
      </span>
    </li>)}
  </ul>;
}

export default function VisaGuidePage() {
  return <div className={styles.page}>
    <header className={styles.header}>
      <a href="/" className={styles.brand} aria-label="bak.ai ana sayfa">
        <Logo size={42} /><span><strong><Wordmark /></strong></span>
      </a>
      <a href="/" className={styles.back}><ArrowLeft size={16} /> Ana sayfa</a>
    </header>

    <main className={styles.main}>
      <div className={styles.intro}>
        <span className={styles.eyebrow}>PERSONEL · VİZE · OTURUM</span>
        <h1>Çalışan ve aile vize rehberi</h1>
        <p>Türkiye’den gelen akademik ve idari personel ile aile bireyleri için vize
          uzatma işlemleri, sırasıyla. {SOURCE.regulation} tarihli yeni vize yönetmeliğiyle
          sigorta, sağlık raporu ve AIDS testi de istenmektedir.</p>
        <p className={styles.source}>Kaynak: {SOURCE.unit}, “{SOURCE.title}” · son düzenleme {SOURCE.updated}</p>
      </div>

      <div className={styles.timing} role="note">
        <CalendarClock size={22} aria-hidden="true" />
        <div>
          <strong>Vize bitiminden 40 gün önce</strong> belgeleri hazırlamaya başlayın,
          <strong> 1 ay önce</strong> başvurun. Eksik evrakla başvuru kabul edilmez.
        </div>
      </div>

      <VisaAnimation />

      <nav className={styles.jump} aria-label="Sayfa içi bağlantılar">
        <a href="#adimlar">Adımlar</a>
        <a href="#belgeler">Belge listesi</a>
        <a href="#dikkat">Dikkat edilecekler</a>
        <a href="#sor">bak.ai’ye sor</a>
      </nav>

      <section id="adimlar" aria-labelledby="steps-heading" className={styles.section}>
        <h2 id="steps-heading">Adım adım</h2>
        <ol className={styles.steps}>
          {STEPS.map(step => <li key={step.id} id={step.id} className={styles.step}>
            <span className={styles.stepNo} aria-hidden="true">{step.no}</span>
            <div className={styles.stepBody}>
              <h3>{step.title}</h3>
              {step.local && <p className={styles.local} lang="ky">{step.local}</p>}
              <p className={styles.summary}>{step.summary}</p>
              {step.cost && <p className={styles.cost}><Wallet size={15} aria-hidden="true" /> {step.cost}</p>}
              {step.where && <Places places={step.where} />}
              <ul className={styles.points}>
                {step.points.map(point => <li key={point}>{point}</li>)}
              </ul>
              {step.id === "sigorta" && <details className={styles.payment}>
                <summary>Eldik Bank ödeme bilgileri (Реквизиты)</summary>
                <dl>
                  {PAYMENT.map(row => <div key={row.label}><dt>{row.label}</dt><dd lang="ru">{row.value}</dd></div>)}
                </dl>
              </details>}
              {step.id === "aids" && <a className={styles.external} href={AIDS_RESULT_URL} target="_blank" rel="noopener noreferrer">
                Test sonucunu sorgula (ilab.med.kg) <ArrowUpRight size={14} />
              </a>}
              {step.warning && <p className={styles.warning}><AlertTriangle size={15} aria-hidden="true" /> {step.warning}</p>}
            </div>
          </li>)}
        </ol>
      </section>

      <section id="belgeler" aria-labelledby="docs-heading" className={styles.section}>
        <h2 id="docs-heading">Başvuruda gerekli belgeler</h2>
        <p className={styles.sectionNote}>Bu listedekiler dışında belge getirmeyin. İşaretler yalnız bu ekranda tutulur.</p>
        <div className={styles.checklists}>
          {CHECKLISTS.map(list => <div key={list.id} className={styles.checklist}>
            <h3><FileCheck2 size={18} aria-hidden="true" /> {list.title}</h3>
            <ul>
              {list.items.map(item => <li key={item.text}>
                <label>
                  <input type="checkbox" />
                  <span>{item.text}{item.note && <small>{item.note}</small>}</span>
                </label>
              </li>)}
            </ul>
          </div>)}
        </div>
      </section>

      <section id="dikkat" aria-labelledby="rules-heading" className={styles.section}>
        <h2 id="rules-heading">Dikkat edilecekler</h2>
        <dl className={styles.rules}>
          {RULES.map(rule => <div key={rule.title}><dt>{rule.title}</dt><dd>{rule.text}</dd></div>)}
        </dl>
      </section>

      <section id="sor" aria-labelledby="ask-heading" className={styles.ask}>
        <MessageCircleQuestion size={26} aria-hidden="true" />
        <h2 id="ask-heading">Durumunuz farklı mı? bak.ai’ye sorun</h2>
        <p>Yanıtlar bu yönergeye ve kurum belgelerine dayanır, kaynağıyla gösterilir.</p>
        <div className={styles.questions}>
          {QUESTIONS.map(question => <a key={question} href={`/?q=${encodeURIComponent(question)}`}>
            {question} <ArrowUpRight size={14} />
          </a>)}
        </div>
      </section>
    </main>

    <footer className={styles.footer}>
      Bu sayfa {SOURCE.unit} yönergesinin ({SOURCE.updated}) özetidir. Kesin bilgi ve
      yönergede yer almayan sorular için Vize Birimine ve belgeyi veren kuruma başvurun.
    </footer>
  </div>;
}
