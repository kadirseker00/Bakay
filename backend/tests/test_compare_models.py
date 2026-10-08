"""API deneyi: bağlam bütünlüğü, ücretli tekrarlar ve ölçüm özeti."""
from __future__ import annotations

import json
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path
from unittest.mock import patch

import httpx

from scripts import compare_models as compare


class SonnetComparisonTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.snapshot = self.root / "snapshot.json"
        self.cases = [{"id": ident, "question": "Soru?", "prompt": f"Kaynak {ident}",
                       "prompt_sha256": compare.digest(f"Kaynak {ident}"),
                       "hits": [{"title": "Mevzuat"}]} for ident in ("q1", "q2")]
        compare.save_json(self.snapshot, {"cases": self.cases})
        self.args = Namespace(snapshot=self.snapshot, output=self.root,
                              model="claude-sonnet-5-5", label="sonnet")
        self.result = {
            "response": "Yanıt [1].", "stop_reason": "end_turn", "model": "claude-sonnet-5-5",
            "usage": {"input_tokens": 5000, "output_tokens": 1000},
            "message_id": "msg_test", "request_id": "req_test",
        }

    def test_exact_usage_price_and_cache_rates(self):
        self.assertEqual(compare.sonnet_cost(self.result["usage"], "claude-sonnet-5-5"), 0.02)
        self.assertEqual(compare.sonnet_cost({
            "cache_creation_input_tokens": 2000,
            "cache_creation": {"ephemeral_1h_input_tokens": 1000},
            "cache_read_input_tokens": 1000,
        }, "claude-sonnet-5-5"), 0.0066)
        self.assertIsNone(compare.sonnet_cost(self.result["usage"], "unknown"))

    def test_modified_prompt_is_rejected_before_paid_request(self):
        self.cases[0]["prompt"] = "Değişmiş kaynak"
        compare.save_json(self.snapshot, {"cases": self.cases})
        with patch("app.rag.llm.AnthropicLLM") as factory:
            with self.assertRaisesRegex(SystemExit, "girdisi değiştirilmiş"):
                compare.run_anthropic(self.args)
        factory.assert_not_called()

    def test_resume_skips_completed_requests_and_rejects_changed_contract(self):
        with patch("app.rag.llm.AnthropicLLM") as factory:
            factory.return_value.generate_result.return_value = self.result
            compare.run_anthropic(self.args)
            factory.return_value.generate_result.assert_any_call("Kaynak q1")
            self.assertEqual(factory.return_value.generate_result.call_count, 2)
            factory.reset_mock()
            compare.run_anthropic(self.args)
            factory.assert_not_called()
            with patch.object(compare.settings, "anthropic_effort", "low"):
                with self.assertRaisesRegex(SystemExit, "ayarları farklı"):
                    compare.run_anthropic(self.args)
            factory.assert_not_called()

    def test_api_failure_stops_and_resume_retries_only_failed_question(self):
        response = httpx.Response(401, request=httpx.Request("POST", "https://api.anthropic.com/v1/messages"))
        with patch("app.rag.llm.AnthropicLLM") as factory:
            factory.return_value.generate_result.side_effect = [
                self.result, httpx.HTTPStatusError("Yetkisiz", request=response.request, response=response),
            ]
            with self.assertRaisesRegex(SystemExit, "API hatası"):
                compare.run_anthropic(self.args)
            factory.return_value.generate_result.side_effect = None
            factory.return_value.generate_result.return_value = self.result
            factory.return_value.generate_result.reset_mock()
            compare.run_anthropic(self.args)
            factory.return_value.generate_result.assert_called_once_with("Kaynak q2")

    def test_summary_reports_api_tokens_cost_and_truncation_without_ollama_speed(self):
        with patch("app.rag.llm.AnthropicLLM") as factory:
            factory.return_value.generate_result.side_effect = [
                {**self.result, "response": "", "stop_reason": "max_tokens"}, self.result,
            ]
            compare.run_anthropic(self.args)
        output = self.root / "metrics.json"
        compare.summarize(Namespace(snapshot=self.snapshot, results=[self.root / "sonnet.answers.jsonl"],
                                    reviews=[], output=output))
        model = compare.read_json(output)["models"]["claude-sonnet-5-5"]
        self.assertEqual(model["empty_answers"], 1)
        self.assertEqual(model["truncated"], 1)
        self.assertEqual(model["billed_input_tokens"], 10000)
        self.assertEqual(model["billed_output_tokens"], 2000)
        self.assertEqual(model["estimated_cost_usd"], 0.04)
        self.assertIsNone(model["mean_tokens_per_second"])
        self.assertTrue(output.with_name("answers.md").exists())


if __name__ == "__main__":
    unittest.main()
