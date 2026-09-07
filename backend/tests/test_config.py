from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.config import Settings
from app.main import app


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

    def test_health_reports_active_model(self):
        with patch("app.rag.vectorstore.get_store") as store, patch("app.rag.pipeline._model_name", return_value="qwen3.5:9b"):
            store.return_value.count.return_value = 12
            response = TestClient(app).get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["llm_model"], "qwen3.5:9b")
        self.assertEqual(response.json()["indexed_chunks"], 12)


if __name__ == "__main__":
    unittest.main()
