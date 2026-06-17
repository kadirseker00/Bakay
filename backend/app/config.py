"""Tüm yapılandırma .env dosyasından okunur (pydantic-settings).

Tek bir `settings` nesnesi import edilir; modeller, anahtarlar ve yollar
buradan gelir. Sağlayıcı değiştirmek için sadece .env'i düzenlemek yeterli.
"""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Proje kök dizini (backend/ bir üst seviye)
ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT / ".env", env_file_encoding="utf-8", extra="ignore"
    )

    # LLM sağlayıcı seçimi: "gemini" | "ollama"
    llm_provider: str = "gemini"

    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "mistral"
    # Hız ayarları: reasoning'i kapatmak (think=false) en büyük latency kazancı
    ollama_think: bool = False
    ollama_temperature: float = 0.3
    ollama_num_ctx: int = 8192
    ollama_num_predict: int = 1024

    # Embedding
    embedding_model: str = "sentence-transformers/LaBSE"

    # Vektör deposu
    chroma_dir: str = "./data/chroma"
    collection_name: str = "ktmu_docs"

    # Retrieval
    top_k: int = 5

    # --- Ajansal akış düğümleri ---
    # Skor-tabanlı yönlendirme/yeterlilik kapısı: en yüksek skor bunun altındaysa
    # soru kapsam dışı sayılır (belge uydurulmaz). Bedava (ekstra LLM yok).
    score_threshold: float = 0.30
    # LLM-ağırlıklı düğümler (her biri ~bir LLM çağrısı = latency). Varsayılan kapalı.
    agent_route: bool = False     # LLM ile kapsam yönlendirmesi (skor kapısı güvenilmez)
    agent_rewrite: bool = False   # sorgu yeniden yazma (retrieval kalitesi)
    agent_verify: bool = False    # üretilen yanıtın dayanak doğrulaması

    # Telemetri / loglama
    log_dir: str = "./data/logs"
    db_path: str = "./data/bakay.db"

    @property
    def chroma_path(self) -> Path:
        p = Path(self.chroma_dir)
        return p if p.is_absolute() else ROOT / p

    def _resolve(self, p: str) -> Path:
        path = Path(p)
        return path if path.is_absolute() else ROOT / path

    @property
    def log_path(self) -> Path:
        return self._resolve(self.log_dir)

    @property
    def db_file(self) -> Path:
        return self._resolve(self.db_path)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
