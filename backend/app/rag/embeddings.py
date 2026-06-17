"""Pluggable embedding sağlayıcı.

Şu an sentence-transformers kullanır (LaBSE varsayılan). İP2'de farklı modeller
(BERTurk, multilingual-e5, XLM-R, Instructor) sadece .env'deki EMBEDDING_MODEL
değeri değiştirilerek karşılaştırılabilir.
"""
from __future__ import annotations

from functools import lru_cache

from app.config import settings


class Embedder:
    """sentence-transformers tabanlı embedding sarmalayıcı."""

    def __init__(self, model_name: str):
        # Ağır bağımlılık — sadece gerektiğinde yüklenir.
        from sentence_transformers import SentenceTransformer

        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    def encode(self, texts: list[str]) -> list[list[float]]:
        """Metin listesini vektör listesine çevirir (normalize edilmiş)."""
        vecs = self.model.encode(
            texts, normalize_embeddings=True, show_progress_bar=False
        )
        return vecs.tolist()

    def encode_one(self, text: str) -> list[float]:
        return self.encode([text])[0]


@lru_cache
def get_embedder() -> Embedder:
    """Tek bir model örneği (cache'li) döndürür."""
    return Embedder(settings.embedding_model)
