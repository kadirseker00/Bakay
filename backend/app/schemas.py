"""API istek/yanıt veri modelleri."""
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class ChatMessage(BaseModel):
    """Sohbet bağlamı; kurumsal bilgi kaynağı olarak kullanılmaz."""

    role: Literal["user", "assistant"]
    content: str = Field(..., min_length=1, max_length=2000)


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000, description="Kullanıcının Türkçe sorusu")
    top_k: int | None = Field(None, ge=1, le=8, description="Geri çağrılacak belge sayısı (1–8; varsayılan ayarlardan)")
    history: list[ChatMessage] = Field(default_factory=list, max_length=12)
    captcha_token: str | None = Field(None, max_length=2048, repr=False)

    @model_validator(mode="after")
    def validate_history(self) -> "ChatRequest":
        # Yalnızca tamamlanmış soru/yanıt çiftleri taşınır; son soru ayrı alandadır.
        if len(self.history) % 2 or any(
            message.role != ("user" if index % 2 == 0 else "assistant")
            for index, message in enumerate(self.history)
        ):
            raise ValueError("Geçmiş, kullanıcı/asistan sırasındaki tamamlanmış çiftlerden oluşmalı.")
        return self


class Source(BaseModel):
    """Yanıtın dayandığı belge parçası — açıklanabilirlik için."""
    document: str          # kaynak belge adı / URL
    title: str | None = None  # kullanıcıya gösterilecek gerçek belge başlığı
    snippet: str           # ilgili paragraf
    score: float           # benzerlik skoru


class ChatResponse(BaseModel):
    query_id: str          # geri bildirim bu id ile ilişkilendirilir
    answer: str
    sources: list[Source]
    latency_ms: int


class FeedbackRequest(BaseModel):
    query_id: str = Field(pattern="^[0-9a-f]{32}$")
    rating: str = Field(..., pattern="^(up|down)$", description="'up' | 'down'")
    comment: str | None = Field(None, max_length=2000)
    reason: Literal["outdated", "irrelevant", "incorrect", "incomplete", "sources", "other"] | None = None
    respondent_name: str | None = Field(None, max_length=120)
    correction_question: str | None = Field(None, min_length=3, max_length=2000)
    correction_answer: str | None = Field(None, min_length=1, max_length=12000)
    correction_source: str | None = Field(None, max_length=2000)

    @field_validator("respondent_name", "comment", "correction_question", "correction_answer", "correction_source", mode="before")
    @classmethod
    def trim_text(cls, value: str | None) -> str | None:
        return (value.strip() or None) if value is not None else None

    @model_validator(mode="after")
    def validate_reason(self) -> "FeedbackRequest":
        # Eski arayüzün nedensiz oylarını kabul etmeye devam et.
        if self.rating != "down" and self.reason is not None:
            raise ValueError("Neden yalnız olumsuz geri bildirimde belirtilebilir.")
        if self.reason == "other" and not self.comment:
            raise ValueError("Diğer seçeneğinde sorunu kısaca açıklayın.")
        if self.correction_answer or self.correction_question or self.correction_source:
            if self.rating != 'down' or not self.correction_answer or not self.correction_question:
                raise ValueError('Düzeltme yalnız olumsuz geri bildirimde, açık soru ve cevapla gönderilebilir.')
            if self.correction_source:
                from app.knowledge import KnowledgeSource
                KnowledgeSource(title='Önerilen kaynak', url=self.correction_source, snippet='Öneri')
        return self
