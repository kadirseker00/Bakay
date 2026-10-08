"""Claude bağlantısı: gerçek istek biçimi, metin ayrımı ve hata davranışı."""
from __future__ import annotations

import json
import unittest
from unittest.mock import patch

import httpx

from app.config import Settings
from app.rag import llm


class AnthropicLLMTests(unittest.TestCase):
    def setUp(self):
        self.config = Settings(_env_file=None, anthropic_api_key="test-key")
        self.message = {
            "type": "message", "id": "msg_test", "model": "claude-sonnet-5-5",
            "content": [{"type": "text", "text": "Kaynaklı yanıt."}],
            "stop_reason": "end_turn", "usage": {"input_tokens": 100, "output_tokens": 20},
        }

    def make_client(self, handler):
        with patch.object(llm, "settings", self.config):
            client = llm.AnthropicLLM()
        headers = client.http.headers
        client.http.close()
        client.http = httpx.Client(
            base_url="https://api.anthropic.com", headers=headers,
            transport=httpx.MockTransport(handler),
        )
        self.addCleanup(client.http.close)
        return client

    def test_sonnet_request_preserves_prompt_and_supported_settings(self):
        requests = []

        def handler(request):
            requests.append(request)
            return httpx.Response(200, json=self.message, headers={"request-id": "req_test"})

        client = self.make_client(handler)
        result = client.generate_result("Sabit kaynaklar\nTürkçe soru?")
        request = requests[0]
        payload = json.loads(request.content)
        self.assertEqual(str(request.url), "https://api.anthropic.com/v1/messages")
        self.assertEqual(request.headers["x-api-key"], "test-key")
        self.assertEqual(request.headers["anthropic-version"], "2023-06-01")
        self.assertEqual(payload["messages"], [{"role": "user", "content": "Sabit kaynaklar\nTürkçe soru?"}])
        self.assertEqual(payload["thinking"], {"type": "between_tools"})
        self.assertEqual(payload["output_config"], {"effort": "high"})
        self.assertEqual(payload["max_tokens"], 2048)
        self.assertTrue({"temperature", "top_p", "top_k", "tools", "cache_control"}.isdisjoint(payload))
        self.assertEqual(result["request_id"], "req_test")
        self.assertEqual(result["usage"]["output_tokens"], 20)

    def test_hidden_thinking_and_tool_blocks_are_not_user_text(self):
        self.message["content"] = [
            {"type": "thinking", "thinking": "Gizli muhakeme"},
            {"type": "text", "text": "Birinci."},
            {"type": "tool_use", "name": "deneme", "input": {}},
            {"type": "text", "text": "İkinci."},
        ]
        client = self.make_client(lambda _: httpx.Response(200, json=self.message))
        self.assertEqual(client.generate("Soru"), "Birinci.\nİkinci.")

    def test_empty_response_keeps_billed_usage_but_generate_fails(self):
        self.message["content"] = []
        self.message["stop_reason"] = "max_tokens"
        client = self.make_client(lambda _: httpx.Response(200, json=self.message))
        result = client.generate_result("Soru")
        self.assertEqual(result["response"], "")
        self.assertEqual(result["usage"]["output_tokens"], 20)
        with self.assertRaisesRegex(RuntimeError, "max_tokens"):
            client.generate("Soru")

    def test_api_error_is_not_retried_or_returned_as_an_answer(self):
        requests = []

        def handler(request):
            requests.append(request)
            return httpx.Response(429, json={"type": "error", "error": {"type": "rate_limit_error"}})

        client = self.make_client(handler)
        with self.assertRaises(httpx.HTTPStatusError):
            client.generate("Soru")
        self.assertEqual(len(requests), 1)

    def test_missing_key_fails_before_http_client_creation(self):
        self.config.anthropic_api_key = ""
        with patch.object(llm, "settings", self.config), patch.object(llm.httpx, "Client") as factory:
            with self.assertRaisesRegex(RuntimeError, "ANTHROPIC_API_KEY"):
                llm.AnthropicLLM()
        factory.assert_not_called()

    def test_provider_factory_selects_claude(self):
        self.config.llm_provider = "Anthropic"
        with patch.object(llm, "settings", self.config), patch.object(llm, "AnthropicLLM") as factory:
            llm.get_llm.cache_clear()
            self.addCleanup(llm.get_llm.cache_clear)
            self.assertIs(llm.get_llm(), factory.return_value)
        factory.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
