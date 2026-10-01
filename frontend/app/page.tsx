"use client";

import { useEffect, useRef, useState } from "react";
import type { LucideIcon } from "lucide-react";
import ReactMarkdown from "react-markdown";
import {
  AlertCircle,
  ArrowUp,
  BookOpenText,
  CalendarDays,
  Check,
  ChevronDown,
  Clock3,
  Compass,
  ExternalLink,
  FileCheck2,
  Files,
  Globe2,
  GraduationCap,
  LibraryBig,
  MapPin,
  Menu,
  MessageSquarePlus,
  Search,
  ShieldCheck,
  Sparkles,
  ThumbsDown,
  ThumbsUp,
  Wifi,
  WifiOff,
  X,
} from "lucide-react";
import Logo from "./components/Logo";
import { buildHistory, persistHistory, restoreHistory } from "./lib/chat-memory";
import type { Message } from "./lib/chat-memory";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
type Health = { indexed_chunks: number; llm_provider: string; embedding_model: string };
type ConnectionState = "checking" | "online" | "offline";
type Topic = { title: string; description: string; question: string; icon: LucideIcon };
type CandidateTrackId = "lisans" | "lisansustu" | "uluslararasi";
type CandidateTrack = {
  id: CandidateTrackId;
  label: string;
  title: string;
  description: string;
  icon: LucideIcon;
  questions: Topic[];
};

const EXAMPLES = [
  "Bütünleme sınavına kimler girebilir?",
  "Başarı bursu için not ortalaması kaç olmalı?",
  "Üniversiteye kayıt için hangi belgeler gerekli?",
  "Kayıt yenilemeyen öğrencinin durumu ne olur?",
  "Yatay geçiş başvuru şartları nelerdir?",
];

const TOPICS: Topic[] = [
  {
    title: "Akademik süreçler",
    description: "Sınavlar, notlandırma ve mezuniyet",
    question: "Bütünleme sınavına kimler girebilir?",
    icon: GraduationCap,
  },
  {
    title: "Kayıt ve başvuru",
    description: "Kayıt, yatay geçiş ve gerekli belgeler",
    question: "Üniversiteye kayıt için hangi belgeler gerekli?",
    icon: FileCheck2,
  },
  {
    title: "Burslar",
    description: "Başarı bursu ve değerlendirme koşulları",
    question: "Başarı bursu için not ortalaması kaç olmalı?",
    icon: Sparkles,
  },
  {
    title: "Takvim ve tarihler",
    description: "Akademik takvim ve önemli dönemler",
    question: "Kayıt yenileme tarihleri ne zaman?",
    icon: CalendarDays,
  },
];

const CANDIDATE_TRACKS: CandidateTrack[] = [
  {
    id: "lisans",
    label: "Lisans",
    title: "Lisans yolculuğunu planla",
    description:
      "Bölüm seçmeden kayıt gününe kadar ihtiyaç duyacağınız kurumsal bilgilere ulaşın.",
    icon: GraduationCap,
    questions: [
      {
        title: "Eğitim süresi ve hazırlık",
        description: "Program sürelerini ve hazırlık eğitimini öğrenin",
        question: "KTMÜ'de ön lisans ve lisans eğitimi kaç yıl sürer, hazırlık eğitimi var mıdır?",
        icon: LibraryBig,
      },
      {
        title: "Kabul yolları",
        description: "YKS ve MANAS-ÖSS ile kabul süreçlerini inceleyin",
        question:
          "Türkiye ve Kırgızistan uyruklu adaylar KTMÜ lisans programlarına YKS veya MANAS-ÖSS ile nasıl kabul edilir?",
        icon: FileCheck2,
      },
      {
        title: "Ücret ve burslar",
        description: "Eğitim ücretini ve sunulan burs türlerini inceleyin",
        question: "KTMÜ'de eğitim ücretli midir ve öğrencilere hangi burs türleri verilir?",
        icon: Sparkles,
      },
      {
        title: "Kayıt işlemleri",
        description: "Kayıt sürecinde istenen belgeleri kontrol edin",
        question: "Üniversiteye kayıt için hangi belgeler gerekmektedir?",
        icon: CalendarDays,
      },
    ],
  },
  {
    id: "lisansustu",
    label: "Lisansüstü",
    title: "Akademik hedefini ileri taşı",
    description:
      "Yüksek lisans ve doktora programlarının kabul, değerlendirme ve kayıt süreçlerini araştırın.",
    icon: BookOpenText,
    questions: [
      {
        title: "Eğitim süreleri",
        description: "Yüksek lisans ve doktora eğitim sürelerini öğrenin",
        question: "KTMÜ'de yüksek lisans ve doktora eğitimi kaç yıl sürer?",
        icon: LibraryBig,
      },
      {
        title: "Yüksek lisans koşulları",
        description: "Not ortalaması ve sınav koşullarını inceleyin",
        question:
          "KTMÜ'de yüksek lisans için gereken lisans not ortalaması ile ALES, GRE veya GMAT koşulları nelerdir?",
        icon: FileCheck2,
      },
      {
        title: "Doktora koşulları",
        description: "Not ortalaması ve yabancı dil şartlarını öğrenin",
        question:
          "KTMÜ doktora programına başvurmak için gereken not ortalaması ve yabancı dil koşulları nelerdir?",
        icon: Sparkles,
      },
      {
        title: "Öğrenci alım ilanı",
        description: "Kontenjan ve gerekli belgelerin nasıl duyurulduğunu öğrenin",
        question:
          "KTMÜ lisansüstü öğrenci alım ilanında kontenjan, başvuru koşulları ve gerekli belgeler nasıl duyurulur?",
        icon: CalendarDays,
      },
    ],
  },
  {
    id: "uluslararasi",
    label: "Uluslararası",
    title: "KTMÜ'ye gelişini hazırla",
    description:
      "Uluslararası adayların kabulden kampüs yaşamına kadar merak ettiği süreçleri tek yerde inceleyin.",
    icon: Globe2,
    questions: [
      {
        title: "TR-YÖS ile kabul",
        description: "TR-YÖS ile uluslararası kabul koşullarını öğrenin",
        question: "KTMÜ'ye TR-YÖS ile uluslararası öğrenci kabul şartları nelerdir?",
        icon: Globe2,
      },
      {
        title: "Diğer ülkelerden başvuru",
        description: "Türkiye ve Kırgızistan dışından kabul yollarını inceleyin",
        question:
          "Türkiye ve Kırgızistan dışındaki ülkelerden adaylar KTMÜ'ye hangi yollarla kabul edilir?",
        icon: FileCheck2,
      },
      {
        title: "Vize ve oturum",
        description: "Kırgızistan'a geliş ve oturum işlemlerini öğrenin",
        question:
          "Türkiye'den Kırgızistan'a gelirken vize almak gerekiyor mu? Vize ve oturum işlemleri nasıl yapılıyor?",
        icon: Sparkles,
      },
      {
        title: "Yurt başvurusu",
        description: "Öğrenci yurtlarına başvuru sürecini inceleyin",
        question: "Öğrenci yurtlarında kalabilmek için ne zaman ve nasıl başvuru yapacağım?",
        icon: MapPin,
      },
    ],
  },
];

const FAQS = [
  {
    question: "BAKAY yanıtlarını nereden buluyor?",
    answer:
      "Yanıtlar KTMÜ'nün indekslenen resmî yönetmelik, yönerge, duyuru ve kurumsal belgelerinden hazırlanır. Her yanıtta kullanılan kaynak parçalarını ayrıca görebilirsiniz.",
  },
  {
    question: "Verilen bilgi güncel değilse ne yapmalıyım?",
    answer:
      "Kaynak kartındaki belge adını ve ilgili metni kontrol edin. Tarihe bağlı kayıt, başvuru ve sınav bilgileri için üniversitenin güncel duyurusunu esas alın.",
  },
  {
    question: "Her konuda soru sorabilir miyim?",
    answer:
      "BAKAY, KTMÜ'nün kurumsal ve akademik süreçleri için tasarlanmıştır. Kaynaklarda bulunmayan veya üniversiteyle ilgisiz konularda tahminde bulunmak yerine kapsamını açıkça belirtir.",
  },
  {
    question: "Yanıtın kalitesini bildirebilir miyim?",
    answer:
      "Evet. Her yanıtın altındaki yararlı veya yararlı değil düğmeleri, sistemin değerlendirilmesine ve geliştirilmesine katkı sağlar.",
  },
];

function sourceLabel(document: string) {
  try {
    const url = new URL(document);
    const lastPart = url.pathname.split("/").filter(Boolean).pop();
    return decodeURIComponent(lastPart || url.hostname).replace(/[-_]/g, " ");
  } catch {
    return document.split("/").filter(Boolean).pop()?.replace(/[-_]/g, " ") || document;
  }
}

function Brand({ onHome }: { onHome?: () => void }) {
  return (
    <a
      className="brand"
      href="#baslangic"
      aria-label="BAKAY ana sayfa"
      onClick={(event) => {
        if (!onHome) return;
        event.preventDefault();
        onHome();
      }}
    >
      <Logo size={42} />
      <span className="brand-copy">
        <strong>BAKAY</strong>
        <span className="brand-version">v{process.env.NEXT_PUBLIC_APP_VERSION}</span>
        <small>KTMÜ Bilgi Asistanı</small>
      </span>
    </a>
  );
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [historyReady, setHistoryReady] = useState(false);
  const [historySaved, setHistorySaved] = useState(true);
  const [input, setInput] = useState("");
  const [typedPrompt, setTypedPrompt] = useState("");
  const [promptAnimationStopped, setPromptAnimationStopped] = useState(false);
  const [loading, setLoading] = useState(false);
  const [health, setHealth] = useState<Health | null>(null);
  const [connection, setConnection] = useState<ConnectionState>("checking");
  const [menuOpen, setMenuOpen] = useState(false);
  const [candidateTrack, setCandidateTrack] = useState<CandidateTrackId>("lisans");
  const latestQuestionRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const conversationHeadingRef = useRef<HTMLHeadingElement>(null);
  const requestControllerRef = useRef<AbortController | null>(null);
  const shouldFocusConversationRef = useRef(false);
  const isConversation = messages.length > 0;

  useEffect(() => {
    setMessages(restoreHistory());
    setHistoryReady(true);

    fetch(`${API_URL}/health`)
      .then((response) => {
        if (!response.ok) throw new Error("Sağlık kontrolü başarısız");
        return response.json();
      })
      .then((data: Health) => {
        setHealth(data);
        setConnection("online");
      })
      .catch(() => setConnection("offline"));
  }, []);

  useEffect(() => {
    if (historyReady) setHistorySaved(persistHistory(messages));

    if (messages.at(-1)?.role === "user") {
      requestAnimationFrame(() => {
        latestQuestionRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
      });
    }
  }, [messages, historyReady]);

  useEffect(() => {
    if (!isConversation || !shouldFocusConversationRef.current) return;

    shouldFocusConversationRef.current = false;
    requestAnimationFrame(() => conversationHeadingRef.current?.focus());
  }, [isConversation]);

  useEffect(() => {
    if (!menuOpen) return;

    const closeOnEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") setMenuOpen(false);
    };
    const closeOutsideMenu = (event: PointerEvent) => {
      const target = event.target;
      if (target instanceof Element && !target.closest(".site-nav, .menu-button")) {
        setMenuOpen(false);
      }
    };
    document.addEventListener("keydown", closeOnEscape);
    document.addEventListener("pointerdown", closeOutsideMenu);
    return () => {
      document.removeEventListener("keydown", closeOnEscape);
      document.removeEventListener("pointerdown", closeOutsideMenu);
    };
  }, [menuOpen]);

  useEffect(() => {
    return () => requestControllerRef.current?.abort();
  }, []);

  useEffect(() => {
    if (isConversation || promptAnimationStopped) {
      setTypedPrompt("");
      return;
    }

    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduceMotion) {
      setTypedPrompt(EXAMPLES[0]);
      return;
    }

    let exampleIndex = 0;
    let characterIndex = 0;
    let deleting = false;
    let timer: ReturnType<typeof setTimeout>;

    const typeNext = () => {
      const sentence = EXAMPLES[exampleIndex];
      if (!deleting) {
        characterIndex += 1;
        setTypedPrompt(sentence.slice(0, characterIndex));
        if (characterIndex === sentence.length) {
          deleting = true;
          timer = setTimeout(typeNext, 1900);
          return;
        }
        timer = setTimeout(typeNext, 42);
        return;
      }

      characterIndex -= 1;
      setTypedPrompt(sentence.slice(0, characterIndex));
      if (characterIndex === 0) {
        deleting = false;
        exampleIndex = (exampleIndex + 1) % EXAMPLES.length;
        timer = setTimeout(typeNext, 320);
        return;
      }
      timer = setTimeout(typeNext, 20);
    };

    timer = setTimeout(typeNext, 500);
    return () => clearTimeout(timer);
  }, [isConversation, promptAnimationStopped]);

  function resizeTextarea(target: HTMLTextAreaElement) {
    target.style.height = "0px";
    target.style.height = `${Math.min(target.scrollHeight, 144)}px`;
  }

  function clearHistory() {
    requestControllerRef.current?.abort();
    requestControllerRef.current = null;
    setHistorySaved(persistHistory([]));
    setMessages([]);
    setInput("");
    setLoading(false);
    setMenuOpen(false);
    requestAnimationFrame(() => {
      window.scrollTo({ top: 0, behavior: "smooth" });
      textareaRef.current?.focus();
    });
  }

  async function sendFeedback(index: number, rating: "up" | "down") {
    const message = messages[index];
    if (!message.query_id || message.feedback) return;

    setMessages((current) =>
      current.map((item, itemIndex) =>
        itemIndex === index ? { ...item, feedback: rating } : item,
      ),
    );

    try {
      await fetch(`${API_URL}/feedback`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query_id: message.query_id, rating }),
      });
    } catch {
      // Geri bildirim ana soru-cevap akışını kesintiye uğratmamalı.
    }
  }

  async function ask(question: string) {
    const cleanQuestion = question.trim();
    if (!cleanQuestion || loading || !historyReady || requestControllerRef.current) return;

    const controller = new AbortController();
    requestControllerRef.current = controller;
    shouldFocusConversationRef.current = true;
    setMenuOpen(false);
    setMessages((current) => [...current, { role: "user", content: cleanQuestion }]);
    setInput("");
    setLoading(true);
    if (textareaRef.current) textareaRef.current.style.height = "auto";

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: cleanQuestion, history: buildHistory(messages) }),
        signal: controller.signal,
      });
      if (!response.ok) throw new Error(`Sunucu hatası: ${response.status}`);
      const data = await response.json();
      if (controller.signal.aborted) return;
      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content: data.answer,
          sources: data.sources,
          latency_ms: data.latency_ms,
          query_id: data.query_id,
        },
      ]);
    } catch {
      if (controller.signal.aborted) return;
      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content:
            "Şu anda bilgi servisine ulaşamıyorum. Birkaç dakika sonra yeniden deneyebilirsiniz.",
          error: true,
        },
      ]);
    } finally {
      if (requestControllerRef.current === controller) {
        requestControllerRef.current = null;
        setLoading(false);
      }
    }
  }

  function handleCandidateTabKeyDown(
    event: React.KeyboardEvent<HTMLButtonElement>,
    currentIndex: number,
  ) {
    let nextIndex: number | null = null;
    if (event.key === "ArrowRight") {
      nextIndex = (currentIndex + 1) % CANDIDATE_TRACKS.length;
    } else if (event.key === "ArrowLeft") {
      nextIndex = (currentIndex - 1 + CANDIDATE_TRACKS.length) % CANDIDATE_TRACKS.length;
    } else if (event.key === "Home") {
      nextIndex = 0;
    } else if (event.key === "End") {
      nextIndex = CANDIDATE_TRACKS.length - 1;
    }

    if (nextIndex === null) return;
    event.preventDefault();
    const nextTrack = CANDIDATE_TRACKS[nextIndex];
    setCandidateTrack(nextTrack.id);
    requestAnimationFrame(() => {
      document.getElementById(`candidate-tab-${nextTrack.id}`)?.focus();
    });
  }

  const sourceCount = messages.reduce(
    (count, message) => count + (message.sources?.length || 0),
    0,
  );
  const latestQuestionIndex = messages.reduce(
    (latestIndex, message, index) => (message.role === "user" ? index : latestIndex),
    -1,
  );
  const activeCandidateTrack =
    CANDIDATE_TRACKS.find((track) => track.id === candidateTrack) || CANDIDATE_TRACKS[0];

  return (
    <div className={`app-shell ${isConversation ? "conversation-mode" : ""}`}>
      <header className="site-header">
        <div className="header-inner">
          <Brand onHome={isConversation ? clearHistory : undefined} />

          {!isConversation && (
            <nav
              className={`site-nav ${menuOpen ? "open" : ""}`}
              id="primary-navigation"
              aria-label="Ana menü"
            >
              <a href="#aday-ogrenci" onClick={() => setMenuOpen(false)}>
                Aday Öğrenci
              </a>
              <a href="#konular" onClick={() => setMenuOpen(false)}>
                Konular
              </a>
              <a href="#nasil-calisir" onClick={() => setMenuOpen(false)}>
                Nasıl çalışır?
              </a>
              <a href="#sss" onClick={() => setMenuOpen(false)}>
                SSS
              </a>
            </nav>
          )}

          <div className="header-actions">
            <div className={`connection ${connection}`} title="BAKAY servis durumu">
              {connection === "online" ? <Wifi size={15} /> : <WifiOff size={15} />}
              <span>
                {connection === "online"
                  ? "Sistem hazır"
                  : connection === "checking"
                    ? "Kontrol ediliyor"
                    : "Bağlantı yok"}
              </span>
            </div>
            {isConversation && (
              <button className="new-question" onClick={clearHistory}>
                <MessageSquarePlus size={17} />
                <span>Yeni sohbet</span>
              </button>
            )}
            {!isConversation && (
              <button
                className="menu-button"
                onClick={() => setMenuOpen((current) => !current)}
                aria-label={menuOpen ? "Menüyü kapat" : "Menüyü aç"}
                aria-expanded={menuOpen}
                aria-controls="primary-navigation"
              >
                {menuOpen ? <X size={22} /> : <Menu size={22} />}
              </button>
            )}
          </div>
        </div>
      </header>

      {isConversation ? (
        <main className="conversation-workspace">
          <section className="conversation-main" aria-label="BAKAY görüşmesi">
            <div className="conversation-heading">
              <div>
                <span className="section-kicker">KAYNAKLI SORU-CEVAP</span>
                <h1 ref={conversationHeadingRef} tabIndex={-1}>BAKAY ile görüşme</h1>
              </div>
              <span className="conversation-count">{messages.filter((m) => m.role === "user").length} soru</span>
            </div>

            <div className="messages" aria-live="polite">
              {messages.map((message, index) => (
                <div
                  key={`${message.role}-${index}`}
                  className={`message-row ${message.role}`}
                  ref={index === latestQuestionIndex ? latestQuestionRef : undefined}
                >
                  {message.role === "assistant" && (
                    <div className="assistant-mark" aria-hidden="true">
                      {message.error ? <AlertCircle size={19} /> : <Logo size={32} />}
                    </div>
                  )}

                  <div className={`message ${message.role} ${message.error ? "error" : ""}`}>
                    <div className="message-author">
                      {message.role === "assistant" ? (message.error ? "Sistem bildirimi" : "BAKAY") : "Siz"}
                    </div>
                    <div
                      className={`message-text ${
                        message.role === "assistant" && !message.error ? "markdown-content" : ""
                      }`}
                    >
                      {message.role === "assistant" && !message.error ? (
                        <ReactMarkdown>{message.content}</ReactMarkdown>
                      ) : (
                        message.content
                      )}
                    </div>

                    {message.sources && message.sources.length > 0 && (
                      <details className="sources" open>
                        <summary>
                          <span>
                            <LibraryBig size={17} />
                            {message.sources.length} kaynak parçası
                          </span>
                          <ChevronDown className="summary-chevron" size={18} />
                        </summary>
                        <div className="source-list">
                          {message.sources.map((source, sourceIndex) => {
                            const isLink = /^https?:\/\//.test(source.document);
                            const content = (
                              <>
                                <span className="source-index">{sourceIndex + 1}</span>
                                <span className="source-body">
                                  <strong>{source.title || sourceLabel(source.document)}</strong>
                                  <span className="source-snippet">{source.snippet}</span>
                                </span>
                                <span className="source-score">
                                  %{Math.round(source.score * 100)}
                                  {isLink && <ExternalLink size={13} />}
                                </span>
                              </>
                            );
                            return isLink ? (
                              <a
                                className="source-card"
                                href={source.document}
                                target="_blank"
                                rel="noreferrer"
                                key={`${source.document}-${sourceIndex}`}
                              >
                                {content}
                              </a>
                            ) : (
                              <div className="source-card" key={`${source.document}-${sourceIndex}`}>
                                {content}
                              </div>
                            );
                          })}
                        </div>
                      </details>
                    )}

                    {message.role === "assistant" && message.query_id && (
                      <div className="message-actions">
                        {message.latency_ms != null && (
                          <span className="latency">
                            <Clock3 size={14} />
                            {(message.latency_ms / 1000).toFixed(1)} saniye
                          </span>
                        )}
                        <span className="action-label">Bu yanıt yararlı mı?</span>
                        <button
                          className={`feedback-button ${message.feedback === "up" ? "active" : ""}`}
                          onClick={() => sendFeedback(index, "up")}
                          disabled={!!message.feedback}
                          aria-label="Yanıt yararlı"
                          title="Yararlı"
                        >
                          <ThumbsUp size={16} />
                        </button>
                        <button
                          className={`feedback-button ${message.feedback === "down" ? "active" : ""}`}
                          onClick={() => sendFeedback(index, "down")}
                          disabled={!!message.feedback}
                          aria-label="Yanıt yararlı değil"
                          title="Yararlı değil"
                        >
                          <ThumbsDown size={16} />
                        </button>
                        {message.feedback && (
                          <span className="feedback-thanks">
                            <Check size={14} /> Kaydedildi
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              ))}

              {loading && (
                <div className="message-row assistant loading-row">
                  <div className="assistant-mark">
                    <Logo size={32} />
                  </div>
                  <div className="message assistant loading-message">
                    <span className="loading-pulse" />
                    <div>
                      <strong>Resmî kaynaklar taranıyor</strong>
                      <span>En ilgili belge parçaları karşılaştırılıyor.</span>
                    </div>
                  </div>
                </div>
              )}
            </div>

            <div className="conversation-composer-wrap">
              <QuestionComposer
                input={input}
                loading={loading}
                textareaRef={textareaRef}
                onInput={setInput}
                onResize={resizeTextarea}
                onAsk={ask}
              />
              <p>
                {historySaved
                  ? "Sohbet bu tarayıcıda saklanır. Yeni sohbet, geçmişi ve konuşma bağlamını temizler."
                  : "Tarayıcı sohbeti kaydedemedi; sayfa yenilenirse geçmiş kaybolabilir."}
                {" "}BAKAY hata yapabilir; önemli kararlar için gösterilen kaynağı doğrulayın.
              </p>
            </div>
          </section>

          <aside className="conversation-aside" aria-label="Görüşme bilgileri">
            <div className="aside-section">
              <span className="aside-label">Bu görüşme</span>
              <div className="aside-metric">
                <Files size={19} />
                <span>
                  <strong>{sourceCount}</strong>
                  görüntülenen kaynak
                </span>
              </div>
            </div>
            <div className="aside-section">
              <span className="aside-label">Başka bir konu</span>
              <div className="aside-questions">
                {TOPICS.slice(0, 3).map((topic) => (
                  <button key={topic.title} onClick={() => ask(topic.question)} disabled={loading}>
                    <topic.icon size={17} />
                    <span>{topic.title}</span>
                    <ArrowUp size={14} />
                  </button>
                ))}
              </div>
            </div>
            <div className="aside-note">
              <ShieldCheck size={20} />
              <p>
                <strong>Kaynak öncelikli</strong>
                BAKAY yalnızca erişebildiği kurumsal belgelere göre yanıt verir.
              </p>
            </div>
          </aside>
        </main>
      ) : (
        <main id="baslangic">
          <section className="hero" aria-labelledby="hero-title">
            <div className="hero-inner">
              <div className="hero-kicker">
                <ShieldCheck size={17} />
                Resmî KTMÜ belgelerine dayalı
              </div>
              <h1 id="hero-title">
                <span>BAKAY</span>
                KTMÜ Kurumsal Bilgi Asistanı
              </h1>
              <p className="hero-copy">
                Yönetmelikler, burslar, kayıt ve akademik süreçler hakkında sorun.
                Yanıtı, dayandığı kaynaklarla birlikte inceleyin.
              </p>

              <div className="hero-composer">
                <QuestionComposer
                  input={input}
                  loading={loading}
                  animatedPrompt={typedPrompt}
                  onFocus={() => setPromptAnimationStopped(true)}
                  textareaRef={textareaRef}
                  onInput={setInput}
                  onResize={resizeTextarea}
                  onAsk={ask}
                />
                <div className="example-line">
                  <span>
                    <Sparkles size={15} /> Örnek:
                  </span>
                  <button onClick={() => ask(EXAMPLES[1])}>{EXAMPLES[1]}</button>
                </div>
              </div>

              <div className="hero-facts" aria-label="BAKAY özellikleri">
                <div>
                  <LibraryBig size={20} />
                  <span>
                    <strong>{health ? health.indexed_chunks.toLocaleString("tr-TR") : "23.000+"}</strong>
                    belge parçası
                  </span>
                </div>
                <div>
                  <Files size={20} />
                  <span>
                    <strong>Kaynaklı</strong>
                    doğrulanabilir yanıt
                  </span>
                </div>
                <div>
                  <ShieldCheck size={20} />
                  <span>
                    <strong>Kurumsal</strong>
                    bilgi kapsamı
                  </span>
                </div>
              </div>
            </div>
          </section>

          <section className="candidate-section" id="aday-ogrenci" aria-labelledby="candidate-title">
            <div className="section-inner candidate-layout">
              <div className="candidate-intro">
                <span className="section-kicker">ADAY ÖĞRENCİ REHBERİ</span>
                <h2 id="candidate-title">Tercihini resmî bilgilerle şekillendir.</h2>
                <p>
                  Eğitim hedefinizi seçin; BAKAY başvuru, kontenjan, burs ve kampüs
                  yaşamıyla ilgili sorularınızı üniversite belgelerinde arasın.
                </p>
                <div className="candidate-note">
                  <Compass size={21} aria-hidden="true" />
                  <span>
                    <strong>Karar desteği</strong>
                    Her yanıt, inceleyebileceğiniz kaynak parçalarıyla birlikte gelir.
                  </span>
                </div>
              </div>

              <div className="candidate-guide">
                <div className="candidate-tabs" role="tablist" aria-label="Eğitim hedefi">
                  {CANDIDATE_TRACKS.map((track, trackIndex) => (
                    <button
                      key={track.id}
                      type="button"
                      role="tab"
                      id={`candidate-tab-${track.id}`}
                      aria-selected={candidateTrack === track.id}
                      aria-controls="candidate-panel"
                      tabIndex={candidateTrack === track.id ? 0 : -1}
                      className={candidateTrack === track.id ? "active" : ""}
                      onClick={() => setCandidateTrack(track.id)}
                      onKeyDown={(event) => handleCandidateTabKeyDown(event, trackIndex)}
                    >
                      <track.icon size={18} aria-hidden="true" />
                      {track.label}
                    </button>
                  ))}
                </div>

                <div
                  className="candidate-panel"
                  role="tabpanel"
                  id="candidate-panel"
                  aria-labelledby={`candidate-tab-${activeCandidateTrack.id}`}
                >
                  <div className="candidate-panel-heading">
                    <span className="candidate-panel-icon">
                      <activeCandidateTrack.icon size={23} aria-hidden="true" />
                    </span>
                    <div>
                      <h3>{activeCandidateTrack.title}</h3>
                      <p>{activeCandidateTrack.description}</p>
                    </div>
                  </div>

                  <div className="candidate-question-grid">
                    {activeCandidateTrack.questions.map((item) => (
                      <button
                        className="candidate-question"
                        key={item.title}
                        onClick={() => ask(item.question)}
                        disabled={loading}
                      >
                        <span className="candidate-question-icon">
                          <item.icon size={19} aria-hidden="true" />
                        </span>
                        <span className="candidate-question-copy">
                          <strong>{item.title}</strong>
                          <small>{item.description}</small>
                        </span>
                        <ArrowUp size={17} aria-hidden="true" />
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </section>

          <section className="topics-section" id="konular">
            <div className="section-inner">
              <div className="section-heading">
                <div>
                  <span className="section-kicker">HIZLI BAŞLANGIÇ</span>
                  <h2>Hangi konuda bilgi arıyorsunuz?</h2>
                </div>
                <p>Sık kullanılan alanlardan birini seçerek doğrudan sorunuzu iletin.</p>
              </div>
              <div className="topic-grid">
                {TOPICS.map((topic) => (
                  <button className="topic-card" key={topic.title} onClick={() => ask(topic.question)}>
                    <span className="topic-icon">
                      <topic.icon size={22} />
                    </span>
                    <span className="topic-copy">
                      <strong>{topic.title}</strong>
                      <small>{topic.description}</small>
                    </span>
                    <ArrowUp className="topic-arrow" size={18} />
                  </button>
                ))}
              </div>
            </div>
          </section>

          <section className="method-section" id="nasil-calisir">
            <div className="section-inner method-grid">
              <div className="method-intro">
                <span className="section-kicker">GÜVENİLİR BİLGİ</span>
                <h2>Bir cevap değil, dayanağıyla birlikte bilgi.</h2>
                <p>
                  BAKAY sorunuzla ilgili resmî metinleri bulur, yanıtı bu içerikten üretir ve
                  kullandığı belge parçalarını görünür kılar.
                </p>
              </div>
              <ol className="method-steps">
                <li>
                  <span>01</span>
                  <div>
                    <strong>Soruyu anlar</strong>
                    <p>Gündelik dilde yazdığınız soruyu kurumsal bilgi alanıyla eşleştirir.</p>
                  </div>
                </li>
                <li>
                  <span>02</span>
                  <div>
                    <strong>Belgeleri tarar</strong>
                    <p>İlgili yönetmelik, yönerge ve duyuru parçalarını karşılaştırır.</p>
                  </div>
                </li>
                <li>
                  <span>03</span>
                  <div>
                    <strong>Kaynağı gösterir</strong>
                    <p>Yanıtla birlikte kullanılan metni ve eşleşme düzeyini sunar.</p>
                  </div>
                </li>
              </ol>
            </div>
          </section>

          <section className="faq-section" id="sss">
            <div className="section-inner faq-grid">
              <div className="faq-intro">
                <span className="section-kicker">SIK SORULANLAR</span>
                <h2>BAKAY hakkında merak edilenler</h2>
                <p>Bilginin kapsamı, güncelliği ve yanıtların nasıl değerlendirildiği.</p>
                <BookOpenText size={64} strokeWidth={1.2} aria-hidden="true" />
              </div>
              <div className="faq-list">
                {FAQS.map((item) => (
                  <details key={item.question}>
                    <summary>
                      <span>{item.question}</span>
                      <ChevronDown size={19} />
                    </summary>
                    <p>{item.answer}</p>
                  </details>
                ))}
              </div>
            </div>
          </section>

          <footer className="site-footer">
            <div className="section-inner footer-inner">
              <Brand />
              <p>Bütünleşik Akıllı Kurumsal Asistan Yazılımı.</p>
              <span>KTMÜ · BAP</span>
            </div>
          </footer>
        </main>
      )}
    </div>
  );
}

type QuestionComposerProps = {
  input: string;
  loading: boolean;
  animatedPrompt?: string;
  onFocus?: () => void;
  textareaRef: React.RefObject<HTMLTextAreaElement>;
  onInput: (value: string) => void;
  onResize: (target: HTMLTextAreaElement) => void;
  onAsk: (question: string) => void;
};

function QuestionComposer({
  input,
  loading,
  animatedPrompt,
  onFocus,
  textareaRef,
  onInput,
  onResize,
  onAsk,
}: QuestionComposerProps) {
  return (
    <div className="question-composer">
      <Search className="composer-search-icon" size={21} aria-hidden="true" />
      <div className="textarea-shell">
        {!input && animatedPrompt && (
          <span className="animated-placeholder" aria-hidden="true">
            {animatedPrompt}
            <span className="typing-caret" />
          </span>
        )}
        <textarea
          ref={textareaRef}
          rows={1}
          maxLength={2000}
          value={input}
          aria-label="KTMÜ hakkında sorunuzu yazın"
          placeholder={animatedPrompt ? "" : "KTMÜ hakkında sorunuzu yazın..."}
          onFocus={onFocus}
          onChange={(event) => {
            onInput(event.target.value);
            onResize(event.target);
          }}
          onKeyDown={(event) => {
            if (event.key === "Enter" && !event.shiftKey) {
              event.preventDefault();
              onAsk(input);
            }
          }}
        />
      </div>
      <button
        className="send-button"
        onClick={() => onAsk(input)}
        disabled={loading || !input.trim()}
        aria-label="Soruyu gönder"
        title="Gönder"
      >
        <ArrowUp size={21} strokeWidth={2.4} />
      </button>
    </div>
  );
}
