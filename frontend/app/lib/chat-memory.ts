// Tarayıcı geçmişi ile API'ye gönderilen kısa sohbet bağlamı ayrı tutulur.
export const STORAGE_KEY = "bakay_history";

export type Source = { document: string; title?: string | null; snippet: string; score: number };
export type Message = {
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
  latency_ms?: number;
  query_id?: string;
  feedback?: "up" | "down";
  error?: boolean;
};

export function buildHistory(messages: Message[]) {
  const history: { role: Message["role"]; content: string }[] = [];
  for (let index = 0; index < messages.length - 1; index += 1) {
    const user = messages[index];
    const assistant = messages[index + 1];
    // Başarısız veya yarım kalan istekler sonraki turun bağlamına girmez.
    if (user.role === "user" && assistant.role === "assistant" && !assistant.error) {
      history.push(
        { role: "user", content: user.content.slice(0, 2000) },
        { role: "assistant", content: assistant.content.slice(0, 2000) },
      );
      index += 1;
    }
  }
  return history.slice(-12);
}

function isMessage(value: unknown): value is Message {
  if (!value || typeof value !== "object") return false;
  const message = value as Message;
  return (
    (message.role === "user" || message.role === "assistant") &&
    typeof message.content === "string" && message.content.length > 0 &&
    message.content.length <= 20000 &&
    (message.sources === undefined || (Array.isArray(message.sources) && message.sources.every(
      (source) => source && typeof source.document === "string" &&
        (source.title == null || typeof source.title === "string") &&
        typeof source.snippet === "string" && typeof source.score === "number",
    ))) &&
    (message.latency_ms === undefined || typeof message.latency_ms === "number") &&
    (message.query_id === undefined || typeof message.query_id === "string") &&
    (message.feedback === undefined || message.feedback === "up" || message.feedback === "down") &&
    (message.error === undefined || typeof message.error === "boolean")
  );
}

export function restoreHistory(): Message[] {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (!saved) return [];
    const parsed: unknown = JSON.parse(saved);
    if (Array.isArray(parsed) && parsed.every(isMessage)) return parsed.slice(-100);
    localStorage.removeItem(STORAGE_KEY);
  } catch {
    // Depolama kapalı veya bozuk olduğunda sohbet yine kullanılabilir.
  }
  return [];
}

export function persistHistory(messages: Message[]): boolean {
  try {
    if (messages.length) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(messages.slice(-100)));
    } else {
      localStorage.removeItem(STORAGE_KEY);
    }
    return true;
  } catch {
    return false;
  }
}
