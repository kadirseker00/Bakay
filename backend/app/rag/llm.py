"""Pluggable LLM sağlayıcı.

LLM_PROVIDER ayarına göre Gemini/Claude API veya Ollama (yerel GPU) kullanır.
İP4'te Mistral/Llama/Qwen2 karşılaştırması için yeni sağlayıcılar buraya eklenir;
pipeline kodu değişmez.
"""
from __future__ import annotations

from functools import lru_cache
import time
from typing import Protocol

import httpx

from app.config import settings
from app import monitoring


class LLM(Protocol):
    def generate(self, prompt: str, *, system: str | None = None) -> str: ...


class AnthropicLLM:
    """Claude Messages API; ücretli denemede metin ve kullanım ayrı saklanır."""

    def __init__(self, model: str | None = None):
        if not settings.anthropic_api_key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY tanımlı değil. Proje kökündeki .env dosyasına ekleyin."
            )
        self.model = model or settings.anthropic_model
        self.max_tokens = settings.anthropic_max_tokens
        self.thinking = settings.anthropic_thinking
        self.effort = settings.anthropic_effort
        self.http = httpx.Client(
            base_url="https://api.anthropic.com",
            headers={
                "x-api-key": settings.anthropic_api_key,
                "anthropic-version": "2023-06-01",
            },
            timeout=settings.anthropic_timeout,
        )

    def generate_result(self, prompt: str, *, system: str | None = None) -> dict:
        started = time.perf_counter()
        try:
            result = self._generate_result(prompt, system=system)
        except Exception as error:
            code = f"HTTP_{error.response.status_code}" if isinstance(error, httpx.HTTPStatusError) else type(error).__name__
            monitoring.record_llm_call(self.model, "error", int((time.perf_counter() - started) * 1000),
                                       error_type=code)
            raise
        monitoring.record_llm_call(result['model'], "ok", int((time.perf_counter() - started) * 1000),
                                   usage=result['usage'])
        return result

    def _generate_result(self, prompt: str, *, system: str | None = None) -> dict:
        """Güvenilir talimatları kullanıcı verisinden ayrı gönder."""
        payload = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "messages": [{"role": "user", "content": prompt}],
            "thinking": {"type": self.thinking},
            "output_config": {"effort": self.effort},
            # Sonnet 5.5 özel sıcaklık/top_p/top_k değerlerini kabul etmez.
        }
        if system is not None:
            payload["system"] = system
        response = self.http.post("/v1/messages", json=payload)
        response.raise_for_status()
        message = response.json()
        if message.get("type") != "message" or not isinstance(message.get("content"), list):
            raise RuntimeError("Claude API geçerli bir mesaj döndürmedi.")
        text = "\n".join(
            block["text"] for block in message["content"]
            if block.get("type") == "text" and isinstance(block.get("text"), str)
        ).strip()
        return {
            "response": text,
            "model": message.get("model", self.model),
            "stop_reason": message.get("stop_reason"),
            "usage": message.get("usage", {}),
            "message_id": message.get("id"),
            "request_id": response.headers.get("request-id"),
        }

    def generate(self, prompt: str, *, system: str | None = None) -> str:
        result = self.generate_result(prompt, system=system)
        if not result["response"]:
            raise RuntimeError(
                f"Claude API yanıt metni boş (bitiş: {result['stop_reason']})."
            )
        return result["response"]


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

    def generate(self, prompt: str, *, system: str | None = None) -> str:
        options = {"config": {"system_instruction": system}} if system is not None else {}
        resp = self.client.models.generate_content(
            model=self.model, contents=prompt, **options
        )
        return (resp.text or "").strip()


class OllamaLLM:
    """Yerel GPU'da çalışan modeller (Mistral, Llama-3, Qwen2...) için Ollama."""

    def __init__(self):
        import httpx

        self.base_url = settings.ollama_base_url.rstrip("/")
        self.model = settings.ollama_model
        self.http = httpx.Client(timeout=120)

    def generate(self, prompt: str, *, system: str | None = None) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            # think=false → reasoning modellerinde <think> üretimini atlar (hız).
            # Model desteklemiyorsa Ollama bunu yok sayar.
            "think": settings.ollama_think,
            "options": {
                "temperature": settings.ollama_temperature,
                "num_ctx": settings.ollama_num_ctx,
                "num_predict": settings.ollama_num_predict,
            },
        }
        if system is not None:
            payload["system"] = system
        resp = self.http.post(f"{self.base_url}/api/generate", json=payload)
        resp.raise_for_status()
        return resp.json().get("response", "").strip()


@lru_cache
def get_llm() -> LLM:
    provider = settings.llm_provider.lower()
    if provider == "anthropic":
        return AnthropicLLM()
    if provider == "gemini":
        return GeminiLLM()
    if provider == "ollama":
        return OllamaLLM()
    raise ValueError(f"Bilinmeyen LLM_PROVIDER: {provider!r} (gemini|ollama|anthropic)")
