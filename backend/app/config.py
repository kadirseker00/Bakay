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

    # Embedding
    embedding_model: str = "sentence-transformers/LaBSE"

    # Vektör deposu
    chroma_dir: str = "./data/chroma"
    collection_name: str = "ktmu_docs"

    # Retrieval
    top_k: int = 5

    @property
    def chroma_path(self) -> Path:
        p = Path(self.chroma_dir)
        return p if p.is_absolute() else ROOT / p


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
