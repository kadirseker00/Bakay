"""API istek/yanıt veri modelleri."""
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, description="Kullanıcının Türkçe sorusu")
    top_k: int | None = Field(None, description="Geri çağrılacak belge sayısı (varsayılan ayarlardan)")


class Source(BaseModel):
    """Yanıtın dayandığı belge parçası — açıklanabilirlik için."""
    document: str          # kaynak belge adı / URL
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
