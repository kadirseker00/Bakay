"""Tüm yapılandırma .env dosyasından okunur (pydantic-settings).

Tek bir `settings` nesnesi import edilir; modeller, anahtarlar ve yollar
buradan gelir. Sağlayıcı değiştirmek için sadece .env'i düzenlemek yeterli.
"""
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Proje kök dizini (backend/ bir üst seviye)
ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT / ".env", env_file_encoding="utf-8", extra="ignore"
    )

    # LLM sağlayıcı seçimi: "gemini" | "ollama" | "anthropic"
    llm_provider: str = "ollama"

    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"

    anthropic_api_key: str = Field(default="", repr=False)
    anthropic_model: str = "claude-sonnet-5-5"
    anthropic_max_tokens: int = Field(default=2048, ge=1)
    # Sonnet 5.5'te araçsız istekte between_tools yalnızca yanıt metni üretir.
    # Haiku 5.5 araçsız hız denemesinde disabled kullanılabilir.
    anthropic_thinking: Literal["between_tools", "adaptive", "disabled"] = "between_tools"
    anthropic_effort: Literal["low", "medium", "high"] = "high"
    anthropic_timeout: float = Field(default=120.0, gt=0)

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen3.5:9b"
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

    # İzleme panelinin sırları frontend'e veya sağlık yanıtına aktarılmaz.
    monitor_username: str = "adminbakai"
    monitor_password_hash: str = Field(default="", repr=False)
    monitor_session_secret: str = Field(default="", repr=False)
    monitor_public_url: str = ""
    monitor_show_query_details: bool = True

    # Tek worker'lı pilotun kötüye kullanım sınırları; kotalar SQLite'ta kalır.
    rate_chat_per_minute: int = Field(default=10, ge=1, le=1000)
    rate_chat_per_hour: int = Field(default=120, ge=1, le=10000)
    rate_chat_global_per_minute: int = Field(default=30, ge=1, le=1000)
    rate_chat_global_per_day: int = Field(default=1000, ge=1, le=100000)
    rate_chat_concurrent: int = Field(default=2, ge=1, le=16)
    rate_chat_concurrent_per_ip: int = Field(default=2, ge=1, le=16)
    rate_max_body_bytes: int = Field(default=131072, ge=4096, le=1048576)
    rate_body_timeout: float = Field(default=10, ge=1, le=30)

    # Bildirim ayarları; e-posta içeriğine kullanıcı sorguları eklenmez.
    alert_daily_usd: float = Field(default=1, gt=0)
    alert_disk_percent: float = Field(default=85, gt=0, le=100)
    alert_memory_percent: float = Field(default=90, gt=0, le=100)
    alert_failure_ticks: int = Field(default=3, ge=1, le=30)
    alert_recovery_ticks: int = Field(default=2, ge=1, le=30)
    alert_email_to: str = ""
    alert_email_from: str = ""
    alert_smtp_host: str = ""
    alert_smtp_port: int = Field(default=587, ge=1, le=65535)
    alert_smtp_security: Literal["starttls", "ssl"] = "starttls"
    alert_smtp_username: str = ""
    alert_smtp_password: str = Field(default="", repr=False)
    backup_status_path: str = "/var/lib/bakay/backup-status.json"

    # Yalnız şüpheli IP için Turnstile; site anahtarı açık, doğrulama sırrı özeldir.
    captcha_site_key: str = ""
    captcha_secret_key: str = Field(default="", repr=False)
    captcha_hostname: str = "bakai.manas.edu.kg"

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
