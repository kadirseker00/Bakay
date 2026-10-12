import type { Metadata } from "next";
import { ArrowLeft, ArrowUpRight, BookOpenText, GraduationCap } from "lucide-react";
import Logo from "../components/Logo";
import { PROJECT } from "../lib/project";
import styles from "./about.module.css";

export const metadata: Metadata = {
  title: "BAKAI hakkında | İsim, BAP projesi ve geliştirici",
  description: "BAKAI adının Manas Destanı’ndaki kökeni, KTMÜ BAP projesi ve proje yürütücüsü ve geliştirici Abdulkadir Şeker hakkında.",
};

export default function AboutPage() {
  return <div className={styles.page}>
    <header className={styles.header}>
      <a href="/" className={styles.brand} aria-label="BAKAI ana sayfa">
        <Logo size={42} /><span><strong>{PROJECT.name}</strong><small>KTMÜ Bilgi Asistanı</small></span>
      </a>
      <a href="/" className={styles.back}><ArrowLeft size={16} /> Ana sayfa</a>
    </header>
    <main className={styles.main}>
      <div className={styles.intro}>
        <span className={styles.eyebrow}>İSİM · PROJE · GELİŞTİRİCİ</span>
        <h1>BAKAI hakkında</h1>
        <p>Kırgızistan-Türkiye Manas Üniversitesi’nin kurumsal belgelerinden
          yararlanarak sorulara kaynaklarıyla yanıt veren yapay zekâ destekli bilgi asistanı.</p>
      </div>
      <div className={styles.grid}>
        <section className={styles.story} aria-labelledby="name-heading">
          <BookOpenText size={28} aria-hidden="true" />
          <span className={styles.eyebrow}>ADIN HİKÂYESİ</span>
          <h2 id="name-heading">Bu isim nereden geliyor?</h2>
          <p>İsim, <strong>Manas Destanı’ndaki bilge danışman Bakay</strong> karakterinden
            esinlenir. Destandaki yol gösterici figür, üniversite bilgisine erişimi
            kolaylaştıran bir rehber fikrine ilham verir.</p>
          <p>Projenin ilk adı <strong>BAKAY</strong>, aynı zamanda
            <strong> Bütünleşik Akıllı Kurumsal Asistan Yazılımı</strong> sözlerinin
            kısaltmasıdır. BAP başvurusunda adın bu iki kökeni birlikte açıklanır.</p>
          <p>Uygulamanın ürün adı bugün <strong>BAKAI</strong> olarak kullanılır;
            adın kültürel kökeni ve projenin amacı korunur.</p>
        </section>
        <section className={styles.project} aria-labelledby="project-heading">
          <GraduationCap size={28} aria-hidden="true" />
          <span className={styles.eyebrow}>BİLİMSEL ARAŞTIRMA PROJESİ</span>
          <h2 id="project-heading">KTMÜ BAP kapsamında</h2>
          <p>BAKAI, Kırgızistan-Türkiye Manas Üniversitesi’nin
            <strong> Bilimsel Araştırma Projeleri (BAP)</strong> kapsamında yürütülen
            araştırma projesinin web uygulamasıdır.</p>
          <dl className={styles.facts}>
            <div><dt>Proje numarası</dt><dd className={styles.projectNumber}>{PROJECT.number}</dd></div>
            <div><dt>Resmî proje adı</dt><dd>{PROJECT.officialTitle}</dd></div>
          </dl>
        </section>
      </div>
      <section className={styles.author} aria-labelledby="author-heading">
        <div><span className={styles.eyebrow}>PROJE YÜRÜTÜCÜSÜ VE GELİŞTİRİCİ</span>
          <h2 id="author-heading">{PROJECT.author}</h2>
          <p>{PROJECT.institution}<br />{PROJECT.department}</p>
        </div>
        <p className={styles.authorNote}>BAKAI web uygulaması, bu BAP projesi kapsamında
          Abdulkadir Şeker tarafından geliştirilmiştir.</p>
      </section>
      <a href="/" className={styles.cta}>BAKAI’ye soru sor <ArrowUpRight size={18} /></a>
    </main>
    <footer className={styles.footer}>BAKAI · KTMÜ Bilimsel Araştırma Projesi · {PROJECT.number}</footer>
  </div>;
}
