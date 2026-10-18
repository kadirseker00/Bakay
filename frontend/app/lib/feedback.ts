export const FEEDBACK_REASONS = {
  outdated: "Bilgi güncel değil",
  irrelevant: "İlgisiz yanıt",
  incorrect: "Yanlış cevap",
  incomplete: "Eksik yanıt",
  sources: "Kaynak hatalı veya yetersiz",
  other: "Diğer",
} as const;

export type FeedbackReason = keyof typeof FEEDBACK_REASONS;
export type FeedbackInput = {
  rating: "up" | "down";
  reason?: FeedbackReason;
  respondent_name?: string;
  comment?: string;
};
