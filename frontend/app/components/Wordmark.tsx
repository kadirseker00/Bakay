import styles from "./Wordmark.module.css";

/** Mevcut simgeye eşlik eden, kullanıcının seçtiği bak.ai yazımı. */
export default function Wordmark() {
  return <span className={styles.wordmark}>bak<span className={styles.dot}>.</span><span className={styles.ai}>ai</span></span>;
}
