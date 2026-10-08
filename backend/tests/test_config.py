from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.config import Settings
from app.main import app
from app.rag import pipeline


class DefaultModelTests(unittest.TestCase):
    def test_fresh_install_defaults_to_qwen(self):
        with patch.dict(os.environ, {}, clear=True):
            config = Settings(_env_file=None)
        self.assertEqual(config.llm_provider, "ollama")
        self.assertEqual(config.ollama_model, "qwen3.5:9b")
        self.assertFalse(config.ollama_think)

    def test_model_override_still_supported(self):
        with patch.dict(os.environ, {"OLLAMA_MODEL": "comparison-model"}):
            config = Settings(_env_file=None)
        self.assertEqual(config.ollama_model, "comparison-model")

    def test_sonnet_configuration_from_environment(self):
        with patch.dict(os.environ, {
            "LLM_PROVIDER": "anthropic", "ANTHROPIC_API_KEY": "test-key",
            "ANTHROPIC_MAX_TOKENS": "2048",
        }, clear=True):
            config = Settings(_env_file=None)
        self.assertEqual(config.anthropic_model, "claude-sonnet-5-5")
        self.assertEqual(config.anthropic_max_tokens, 2048)
        self.assertEqual(config.anthropic_thinking, "between_tools")
        self.assertNotIn("test-key", repr(config))

    def test_health_reports_sonnet_when_selected(self):
        with patch.object(pipeline.settings, "llm_provider", "anthropic"), \
                patch.object(pipeline.settings, "anthropic_model", "claude-sonnet-5-5"), \
                patch("app.rag.vectorstore.get_store") as store:
            store.return_value.count.return_value = 12
            response = TestClient(app).get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["llm_provider"], "anthropic")
        self.assertEqual(response.json()["llm_model"], "claude-sonnet-5-5")

    def test_health_reports_active_model(self):
        with patch("app.rag.vectorstore.get_store") as store, patch("app.rag.pipeline._model_name", return_value="qwen3.5:9b"):
            store.return_value.count.return_value = 12
            response = TestClient(app).get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["llm_model"], "qwen3.5:9b")
        self.assertEqual(response.json()["indexed_chunks"], 12)


if __name__ == "__main__":
    unittest.main()
