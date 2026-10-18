import type { Source } from "./chat-memory";

export type ChatProgress = { stage: string; title: string; detail: string };
type ChatResult = { answer: string; sources: Source[]; latency_ms: number; query_id: string };
export class ChatStreamError extends Error {}

// Ağ paketleri bir bildirimin veya Türkçe karakterin ortasında bölünebilir.
export async function readChatResponse(
  response: Response,
  onProgress: (progress: ChatProgress) => void,
): Promise<ChatResult> {
  if (!response.headers.get("content-type")?.includes("text/event-stream")) {
    return response.json();
  }
  if (!response.body) throw new ChatStreamError("Yanıt alınamadı. Lütfen yeniden deneyin.");
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  try {
    while (true) {
      const { value, done } = await reader.read();
      buffer += decoder.decode(value, { stream: !done });
      let boundary: number;
      while ((boundary = buffer.indexOf("\n\n")) >= 0) {
        const block = buffer.slice(0, boundary);
        buffer = buffer.slice(boundary + 2);
        const lines = block.split("\n");
        const event = lines.find((line) => line.startsWith("event:"))?.slice(6).trim();
        const payload = lines.filter((line) => line.startsWith("data:"))
          .map((line) => line.slice(5).trimStart()).join("\n");
        if (!payload) continue;
        const data = JSON.parse(payload);
        if (event === "status") onProgress(data);
        if (event === "result") return data;
        if (event === "error") throw new ChatStreamError(data.detail || "Yanıt hazırlanamadı.");
      }
      if (done) throw new ChatStreamError("Bağlantı yanıt tamamlanmadan kesildi. Lütfen yeniden deneyin.");
    }
  } finally {
    await reader.cancel().catch(() => {});
    reader.releaseLock();
  }
}
