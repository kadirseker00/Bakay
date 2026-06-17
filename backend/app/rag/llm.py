"""Pluggable LLM sağlayıcı.

LLM_PROVIDER ayarına göre Gemini API (bulut) veya Ollama (yerel GPU) kullanır.
İP4'te Mistral/Llama/Qwen2 karşılaştırması için yeni sağlayıcılar buraya eklenir;
pipeline kodu değişmez.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Protocol

from app.config import settings


class LLM(Protocol):
    def generate(self, prompt: str) -> str: ...


class GeminiLLM:
    """Google Gemini API (GPU gerektirmez — hızlı başlangıç)."""

    def __init__(self):
        if not settings.gemini_api_key:
            raise RuntimeError(
                "GEMINI_API_KEY tanımlı değil. .env dosyasına ekleyin "
                "veya LLM_PROVIDER=ollama yapın."
            )
        from google import genai

        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model = settings.gemini_model

    def generate(self, prompt: str) -> str:
        resp = self.client.models.generate_content(
            model=self.model, contents=prompt
        )
        return (resp.text or "").strip()


class OllamaLLM:
    """Yerel GPU'da çalışan modeller (Mistral, Llama-3, Qwen2...) için Ollama."""

    def __init__(self):
        import httpx

        self.base_url = settings.ollama_base_url.rstrip("/")
        self.model = settings.ollama_model
        self.http = httpx.Client(timeout=120)

    def generate(self, prompt: str) -> str:
        resp = self.http.post(
            f"{self.base_url}/api/generate",
            json={"model": self.model, "prompt": prompt, "stream": False},
        )
        resp.raise_for_status()
        return resp.json().get("response", "").strip()


@lru_cache
def get_llm() -> LLM:
    provider = settings.llm_provider.lower()
    if provider == "gemini":
        return GeminiLLM()
    if provider == "ollama":
        return OllamaLLM()
    raise ValueError(f"Bilinmeyen LLM_PROVIDER: {provider!r} (gemini|ollama)")
