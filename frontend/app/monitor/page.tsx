"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { Activity, ArrowUpRight, BarChart3, CheckCircle2, ChevronRight, Clock3, Coins, Database, ExternalLink, HardDrive, LayoutDashboard, LockKeyhole, LogOut, MessageSquare, RefreshCw, Server, ShieldCheck, ThumbsUp, X } from "lucide-react";
import ReactMarkdown from "react-markdown";
import styles from "./monitor.module.css";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
type Check = { ok: boolean; status: number | null; latency_ms: number; indexed_chunks?: number };
type Query = { id: string; ts: string; question?: string; model: string; n_sources: number; total_ms: number; retrieval_ms: number; generation_ms: number; cost_usd: number | null; llm_calls: number };
type Detail = Query & { answer: string; sources: { title?: string; document: string; snippet: string; score: number }[]; calls: { model: string; status: string; input_tokens: number | null; output_tokens: number | null; cost_usd: number | null; latency_ms: number; error_type: string | null }[] };
type Metrics = {
  generated_at: string; days: number; version: string; active_model: string; embedding_model: string; backend_uptime_seconds: number; details_enabled: boolean;
  summary: { queries: number; requests: number; errors: number; server_errors: number; median_ms: number | null; p95_ms: number | null; avg_retrieval_ms: number | null; avg_generation_ms: number | null; sourced_queries: number; feedback: { up?: number; down?: number }; probe_availability_percent: number | null; probe_count: number };
  cost: { estimated_usd: number; input_tokens: number; output_tokens: number; cache_tokens: number; priced_calls: number; unknown_calls: number; unmetered_queries: number; metering_since: string; pricing_url: string; by_model: { model: string; calls: number; priced_calls: number; cost_usd: number | null }[] };
  resources: { memory_total_bytes: number | null; memory_used_bytes: number | null; disk_total_bytes: number; disk_used_bytes: number; disk_free_bytes: number; load_1m: number; cpu_count: number };
  sample: { checked_at: string; checks: Record<string, Check> } | null;
  daily: { date: string; queries: number; errors: number; cost_usd: number }[];
  recent_queries: Query[]; recent_errors: { ts: string; path: string; status: number }[];
};
const number = (value: number) => new Intl.NumberFormat("tr-TR").format(value);
const money = (value: number | null) => value == null ? "Bilinmiyor" : new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", minimumFractionDigits: value < 1 ? 6 : 2, maximumFractionDigits: value < 1 ? 6 : 2 }).format(value);
const duration = (value: number | null) => value == null ? "—" : `${(value / 1000).toLocaleString("tr-TR", { maximumFractionDigits: 1 })} sn`;
const dateTime = (value: string) => new Intl.DateTimeFormat("tr-TR", { timeZone: "Asia/Bishkek", day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" }).format(new Date(value));
const modelName = (value: string) => value.replace("claude-haiku-5-5", "Haiku 5.5").replace("claude-sonnet-5-5", "Sonnet 5.5");
const gb = (value: number | null) => value == null ? "—" : `${(value / 1024 ** 3).toFixed(1)} GB`;

function DailyChart({ rows }: { rows: Metrics["daily"] }) {
  const max = Math.max(1, ...rows.map(row => row.queries));
  const width = 840, gap = 8, cell = width / Math.max(rows.length, 1);
  return <div className={styles.chart}><svg viewBox="0 0 860 170" role="img" aria-label="Günlük sorgu sayıları">
    {[0, 0.5, 1].map(level => <line key={level} x1="10" x2="850" y1={130 - level * 110} y2={130 - level * 110} stroke="#e8eeec" strokeDasharray="4 5" />)}
    {rows.map((row, index) => <g key={row.date}><title>{row.date}: {row.queries} sorgu, {row.errors} hata</title><rect x={10 + index * cell + gap / 2} y={130 - (row.queries / max) * 110} width={Math.max(2, cell - gap)} height={Math.max(2, (row.queries / max) * 110)} fill={index === rows.length - 1 ? "#087b72" : "#98c9bf"} rx="4" />{(rows.length <= 7 || index % 5 === 0 || index === rows.length - 1) && <text x={10 + index * cell + cell / 2} y="158" textAnchor="middle" fill="#6c7f79" fontSize="13">{row.date.slice(8)}.{row.date.slice(5, 7)}</text>}</g>)}
  </svg></div>;
}

function MetricCard({ label, value, note, icon }: { label: string; value: string; note: string; icon: React.ReactNode }) {
  return <article className={styles.card}><div className={styles.cardTop}><span>{label}</span><span className={styles.metricIcon}>{icon}</span></div><strong>{value}</strong><p>{note}</p></article>;
}

export default function MonitorPage() {
  const [data, setData] = useState<Metrics | null>(null);
  const [auth, setAuth] = useState<boolean | null>(null);
  const [days, setDays] = useState(7);
  const [username, setUsername] = useState("adminbakai");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [detail, setDetail] = useState<Detail | null>(null);
  const [detailLoading, setDetailLoading] = useState("");
  const dialog = useRef<HTMLDialogElement>(null);

  const refresh = useCallback(async (signal?: AbortSignal) => {
    setLoading(true);
    try {
      const response = await fetch(`${API}/monitor/metrics?days=${days}`, { credentials: "include", cache: "no-store", signal });
      if (response.status === 401 || response.status === 503) {
        setAuth(false); setData(null); setDetail(null);
        if (response.status === 503) setError("Panelin giriş ayarları henüz tamamlanmadı.");
        return;
      }
      if (!response.ok) throw new Error("İzleme verisi alınamadı.");
      setData(await response.json()); setAuth(true); setError("");
    } catch (caught) {
      if (!signal?.aborted) { setError(caught instanceof Error ? caught.message : "Bağlantı kurulamadı."); setAuth(current => current ?? false); }
    } finally { if (!signal?.aborted) setLoading(false); }
  }, [days]);

  useEffect(() => {
    const controller = new AbortController();
    void refresh(controller.signal);
    const timer = setInterval(() => { if (!document.hidden && auth) void refresh(controller.signal); }, 15000);
    return () => { controller.abort(); clearInterval(timer); };
  }, [refresh, auth]);

  useEffect(() => { if (detail && dialog.current && !dialog.current.open) dialog.current.showModal(); }, [detail]);

  const login = async (event: React.FormEvent) => {
    event.preventDefault(); setLoading(true); setError("");
    try {
      const response = await fetch(`${API}/monitor/login`, { method: "POST", credentials: "include", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ username, password }) });
      if (!response.ok) { const body = await response.json(); throw new Error(typeof body.detail === "string" ? body.detail : "Giriş yapılamadı."); }
      await refresh();
    } catch (caught) { setError(caught instanceof Error ? caught.message : "Giriş yapılamadı."); }
    finally { setPassword(""); setLoading(false); }
  };
  const logout = async () => {
    try {
      const response = await fetch(`${API}/monitor/logout`, { method: "POST", credentials: "include" });
      if (!response.ok) throw new Error();
      setData(null); setAuth(false); setDetail(null); setError("");
    } catch { setError("Çıkış yapılamadı. Yeniden deneyin."); }
  };
  const showDetail = async (id: string) => {
    setDetailLoading(id);
    try {
      const response = await fetch(`${API}/monitor/queries/${id}`, { credentials: "include", cache: "no-store" });
      if (response.status === 401) { setAuth(false); setData(null); return; }
      if (!response.ok) throw new Error();
      setDetail(await response.json());
    } catch { setError("Sorgu ayrıntısı alınamadı."); }
    finally { setDetailLoading(""); }
  };
  const closeDetail = () => { dialog.current?.close(); setDetail(null); };

  if (!auth || !data) return <main className={styles.loginShell}><a href="/" className={styles.loginBrand}><img src="/logo.png" alt="" /><span>BAKAY<small>YÖNETİM VE İZLEME</small></span></a><section className={styles.loginCard}><span className={styles.lock}><LockKeyhole size={26} /></span><h1>Sistemin nabzını tutun.</h1><p>Kullanım, yanıt kalitesi ve API maliyetleri tek yerde. Devam etmek için yönetici hesabınızla giriş yapın.</p>{error && <div className={styles.error} role="alert">{error}</div>}<form onSubmit={login}><label htmlFor="monitor-user">Kullanıcı adı</label><input id="monitor-user" autoComplete="username" value={username} onChange={event => setUsername(event.target.value)} required /><label htmlFor="monitor-pass">Parola</label><input id="monitor-pass" type="password" autoComplete="current-password" value={password} onChange={event => setPassword(event.target.value)} required /><button type="submit" disabled={loading || !password || !username}>{loading ? "Bağlanıyor…" : "Panele giriş yap"}<ArrowUpRight size={18} /></button></form><div className={styles.loginFoot}><ShieldCheck size={15} /> Yalnız yetkili yöneticiler için</div></section><p className={styles.copyright}>Kırgızistan-Türkiye Manas Üniversitesi</p></main>;

  const summary = data.summary;
  const resource = data.resources;
  const fresh = data.sample && Date.now() - new Date(data.sample.checked_at).getTime() < 150000;
  const checks = data.sample?.checks || {};
  const healthy = fresh && Object.values(checks).length > 0 && Object.values(checks).every(check => check.ok);
  const sourcePercent = summary.queries ? Math.round(summary.sourced_queries * 100 / summary.queries) : null;
  const errorPercent = summary.requests ? (summary.errors * 100 / summary.requests).toFixed(1) : "0";
  const latencyTotal = (summary.avg_retrieval_ms || 0) + (summary.avg_generation_ms || 0);
  const memoryPercent = resource.memory_total_bytes && resource.memory_used_bytes != null ? resource.memory_used_bytes * 100 / resource.memory_total_bytes : null;
  const diskPercent = resource.disk_used_bytes * 100 / resource.disk_total_bytes;

  return <div className={styles.shell}>
    <aside className={styles.sidebar}><a href="/" className={styles.brand}><img src="/logo.png" alt="" /><span>BAKAY<small>Yönetim paneli</small></span></a><div className={styles.sideLabel}>İZLEME</div><nav aria-label="İzleme bölümleri"><a href="#overview"><LayoutDashboard size={18} /> Genel bakış</a><a href="#cost"><Coins size={18} /> API maliyetleri</a><a href="#queries"><MessageSquare size={18} /> Sorgular</a><a href="#system"><Server size={18} /> Sistem sağlığı</a></nav><div className={styles.sideBottom}><span className={styles.environment}>CANLI ORTAM</span><p>KTMÜ · BAKAY v{data.version}</p><a href="/" target="_blank" rel="noopener noreferrer">Uygulamayı aç <ExternalLink size={14} /></a></div></aside>
    <div className={styles.main}><header className={styles.header}><div className={styles.breadcrumb}>Yönetim <ChevronRight size={13} /> İzleme</div><div className={styles.headerActions}><span className={`${styles.liveStatus} ${healthy ? styles.good : styles.warn}`}><i />{healthy ? "Sistem çalışıyor" : fresh ? "Kontrol gerekli" : "Ölçüm bekleniyor"}</span><button onClick={logout} className={styles.iconButton} aria-label="Çıkış yap"><LogOut size={18} /></button></div></header>
      <main className={styles.content}><section id="overview" className={styles.heading}><div><span className={styles.eyebrow}>OPERASYON GÖRÜNÜMÜ</span><h1>Genel bakış</h1><p>BAKAY’ın kullanımını, yanıtlarını ve çalışma durumunu takip edin.</p></div><div className={styles.controls}><label className={styles.srOnly} htmlFor="monitor-period">İzleme dönemi</label><select id="monitor-period" value={days} onChange={event => setDays(Number(event.target.value))}><option value="1">Bugün</option><option value="7">Son 7 gün</option><option value="30">Son 30 gün</option></select><button onClick={() => void refresh()} disabled={loading} className={styles.refresh}><RefreshCw size={16} className={loading ? styles.spin : ""} /> Yenile</button></div></section>
      {error && <div role="alert" className={styles.error}>{error} Son başarılı ölçüm gösteriliyor.</div>}
      <div className={styles.metaLine}><span><Activity size={14} /> {modelName(data.active_model)} <b>·</b> LaBSE</span><span>{loading ? "Yenileniyor…" : `Son güncelleme ${dateTime(data.generated_at)}`} · Bişkek</span></div>
      <section className={styles.metrics} aria-label="Özet metrikler"><MetricCard label="Toplam sorgu" value={number(summary.queries)} note={`${number(summary.sourced_queries)} kaynaklı yanıt`} icon={<MessageSquare size={18} />} /><MetricCard label="Ortanca yanıt süresi" value={duration(summary.median_ms)} note={`%95 sınırı: ${duration(summary.p95_ms)}`} icon={<Clock3 size={18} />} /><MetricCard label="Tahmini API maliyeti" value={data.cost.priced_calls ? money(data.cost.estimated_usd) : "—"} note={`${number(data.cost.priced_calls)} sayaçlı çağrı · USD`} icon={<Coins size={18} />} /><MetricCard label="HTTP hata oranı" value={`%${errorPercent}`} note={`${summary.errors} hata / ${summary.requests} istek`} icon={<Activity size={18} />} /></section>
      <div className={styles.twoColumns}><section className={styles.panel}><div className={styles.panelTitle}><div><h2>Sorgu hacmi</h2><p>Günlük kullanım · Bişkek saati</p></div><BarChart3 size={20} /></div><DailyChart rows={data.daily} /><div className={styles.chartFoot}><span><i /> Kaydedilen sorgular</span><span>{number(summary.queries)} toplam</span></div></section><section className={styles.panel}><div className={styles.panelTitle}><div><h2>Yanıtın yolculuğu</h2><p>Ortalama erişim ve üretim süreleri</p></div><Clock3 size={20} /></div><div className={styles.latencyValue}>{duration(latencyTotal || null)}<small>toplam iki aşama</small></div><div className={styles.stacked}><span style={{ width: `${latencyTotal ? (summary.avg_retrieval_ms || 0) * 100 / latencyTotal : 0}%` }} /><span style={{ flex: 1 }} /></div><div className={styles.latencyLegend}><div><i /><span>Kaynak erişimi</span><strong>{duration(summary.avg_retrieval_ms)}</strong></div><div><i /><span>LLM üretimi</span><strong>{duration(summary.avg_generation_ms)}</strong></div></div><div className={styles.quality}><span>Kaynak gösteren yanıtlar <strong>{sourcePercent == null ? "—" : `%${sourcePercent}`}</strong></span><span><ThumbsUp size={14} /> {summary.feedback.up || 0} olumlu · {summary.feedback.down || 0} olumsuz</span></div></section></div>
      <section id="cost" className={styles.panel}><div className={styles.panelTitle}><div><span className={styles.eyebrow}>TOKEN SAYAÇLARI</span><h2>API maliyetleri</h2><p>Gerçek kullanım sayaçları × standart API tarifesi</p></div><span className={styles.tag}>TAHMİNİ · USD</span></div><div className={styles.costGrid}><div><span>Kaydedilen maliyet</span><strong>{data.cost.priced_calls ? money(data.cost.estimated_usd) : "—"}</strong><small>{data.cost.priced_calls} fiyatlanmış API çağrısı</small></div><div><span>Giriş tokenları</span><strong>{number(data.cost.input_tokens)}</strong><small>Önbellek dışında</small></div><div><span>Çıkış tokenları</span><strong>{number(data.cost.output_tokens)}</strong><small>Düşünme tokenları dahil</small></div><div><span>Önbellek tokenları</span><strong>{number(data.cost.cache_tokens)}</strong><small>Okuma ve yazma</small></div></div>{data.cost.by_model.length > 0 && <div className={styles.modelCosts}>{data.cost.by_model.map(row => <div key={row.model}><span><Database size={15} /> {modelName(row.model)}</span><span>{row.calls} çağrı · {row.priced_calls} fiyatlanmış</span><strong>{money(row.cost_usd)}</strong></div>)}</div>}<p className={styles.notice}>Sayaç başlangıcı: {dateTime(data.cost.metering_since)}. {data.cost.unmetered_queries} eski sorgunun ve {data.cost.unknown_calls} sayaçsız çağrının maliyeti bilinmiyor. Tutar, fatura veya kalan kredi bakiyesi değildir; vergi ve kurumsal indirimleri içermez. <a href={data.cost.pricing_url} target="_blank" rel="noopener noreferrer">Tarifeyi incele <ExternalLink size={12} /></a></p></section>
      <section id="queries" className={styles.panel}><div className={styles.panelTitle}><div><h2>Son sorgular</h2><p>Seçilen dönemdeki son 20 kayıt · ayrıntı için sorguyu açın</p></div><MessageSquare size={20} /></div><div className={styles.tableWrap}><table><thead><tr><th>SORGU</th><th>ZAMAN</th><th>MODEL</th><th>SÜRE</th><th>KAYNAK</th><th>MALİYET</th></tr></thead><tbody>{data.recent_queries.map(query => <tr key={query.id}><td>{data.details_enabled ? <button className={styles.queryButton} disabled={detailLoading === query.id} onClick={() => void showDetail(query.id)}>{query.question}<ArrowUpRight size={14} /></button> : "Ayrıntılar kapalı"}</td><td>{dateTime(query.ts)}</td><td><span className={styles.modelTag}>{modelName(query.model)}</span></td><td>{duration(query.total_ms)}</td><td>{query.n_sources}</td><td>{money(query.cost_usd)}</td></tr>)}</tbody></table>{!data.recent_queries.length && <div className={styles.empty}>Bu dönemde henüz sorgu kaydı yok.</div>}</div></section>
      <section id="system" className={styles.panel}><div className={styles.panelTitle}><div><h2>Sistem sağlığı</h2><p>Dakika başına bağımsız ölçüm · son 31 günlük sağlık geçmişi</p></div><span className={styles.tag}>{data.sample ? dateTime(data.sample.checked_at) : "Henüz ölçülmedi"}</span></div><div className={styles.healthGrid}>{[["backend", "Bilgi servisi"], ["frontend", "Web arayüzü"], ["https", "HTTPS erişimi"]].map(([key, label]) => <div className={styles.healthItem} key={key}><span>{label}</span><strong className={fresh && checks[key]?.ok ? styles.successText : styles.warningText}>{fresh ? checks[key]?.ok ? <><CheckCircle2 size={16} /> Çalışıyor</> : "Kontrol gerekli" : "Ölçüm bekleniyor"}</strong><small>{checks[key] ? `${checks[key].status ?? "Bağlantı yok"} · ${checks[key].latency_ms} ms` : "—"}</small></div>)}</div><div className={styles.resources}><div><label><Server size={16} /> RAM <strong>{gb(resource.memory_used_bytes)} / {gb(resource.memory_total_bytes)}</strong></label><div className={styles.gauge}><span className={memoryPercent != null && memoryPercent > 90 ? styles.gaugeWarning : ""} style={{ width: `${memoryPercent ?? 0}%` }} /></div></div><div><label><HardDrive size={16} /> Disk <strong>{gb(resource.disk_free_bytes)} boş</strong></label><div className={styles.gauge}><span className={diskPercent > 85 ? styles.gaugeWarning : ""} style={{ width: `${diskPercent}%` }} /></div></div></div><div className={styles.systemFoot}><span>1 dk sistem yükü: <strong>{resource.load_1m}</strong> / {resource.cpu_count} çekirdek</span><span>Ölçümlerde erişim: <strong>{summary.probe_availability_percent == null ? "—" : `%${summary.probe_availability_percent}`}</strong> · {summary.probe_count} yoklama</span></div>{summary.errors > 0 && <div className={styles.errorList}><h3>Son HTTP hataları</h3>{data.recent_errors.map((row, index) => <p key={`${row.ts}-${index}`}><span>{dateTime(row.ts)}</span><code>{row.path}</code><strong>HTTP {row.status}</strong></p>)}</div>}</section>
      <footer className={styles.footer}><span>BAKAY · KTMÜ Kurumsal Bilgi Asistanı</span><span>15 sn otomatik yenileme · Yalnız yönetici erişimi</span></footer>
      </main></div>
    <dialog ref={dialog} className={styles.dialog} aria-label="Sorgu ayrıntısı" onCancel={() => setDetail(null)} onClose={() => setDetail(null)}>{detail && <><div className={styles.dialogHeader}><span className={styles.eyebrow}>SORGU AYRINTISI</span><button onClick={closeDetail} className={styles.iconButton} aria-label="Ayrıntıyı kapat"><X size={20} /></button></div><h2>{detail.question}</h2><div className={styles.detailMeta}><span>{dateTime(detail.ts)}</span><span>{modelName(detail.model)}</span><span>{duration(detail.total_ms)}</span><span>{money(detail.cost_usd)}</span></div><article className={styles.answer}><ReactMarkdown components={{ a: props => <a {...props} target="_blank" rel="noopener noreferrer" /> }}>{detail.answer}</ReactMarkdown></article><h3>Kaynaklar</h3><div className={styles.detailSources}>{detail.sources.map((source, index) => <article key={index}><strong>{index + 1}. {source.title || source.document}</strong><p>{source.snippet}</p><small>Eşleşme: %{Math.round(source.score * 100)}</small></article>)}</div><h3>API çağrıları</h3>{detail.calls.length ? detail.calls.map((call, index) => <div className={styles.call} key={index}><strong>{modelName(call.model)} · {call.status === "ok" ? "Tamamlandı" : call.error_type || "Hata"}</strong><span>{call.input_tokens == null ? "—" : number(call.input_tokens)} giriş / {call.output_tokens == null ? "—" : number(call.output_tokens)} çıkış · {duration(call.latency_ms)} · {money(call.cost_usd)}</span></div>) : <p className={styles.notice}>{detail.cost_usd == null ? "Bu eski sorguda API token sayacı kaydedilmemiş." : "Bu sorguda API çağrısı yapılmamış."}</p>}</>}</dialog>
  </div>;
}
