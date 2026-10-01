"""API istek/yanıt veri modelleri."""
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class ChatMessage(BaseModel):
    """Sohbet bağlamı; kurumsal bilgi kaynağı olarak kullanılmaz."""

    role: Literal["user", "assistant"]
    content: str = Field(..., min_length=1, max_length=2000)


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000, description="Kullanıcının Türkçe sorusu")
    top_k: int | None = Field(None, description="Geri çağrılacak belge sayısı (varsayılan ayarlardan)")
    history: list[ChatMessage] = Field(default_factory=list, max_length=12)

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
    query_id: str
    rating: str = Field(..., pattern="^(up|down)$", description="'up' | 'down'")
    comment: str | None = None
