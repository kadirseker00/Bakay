"""Uyarlama verisinde dayanak bütünlüğü ve değerlendirme sızıntısı kontrolleri."""
import copy
import unittest
from unittest.mock import Mock

from evaluation.dataset import DEFAULT_DATA, Dataset, digest, read_json
from evaluation.domainrag import (TASKS, build_bundle, citation_ranks, context_hits,
                                 fixed_prompt, retrieval_summary, validate_bundle)
from scripts.compare_models import digest as prompt_digest
from scripts.domainrag import select


class DomainRAGTests(unittest.TestCase):
    def setUp(self):
        self.dataset = Dataset.model_validate(read_json(DEFAULT_DATA / "dataset.json"))
        self.evidence = read_json(DEFAULT_DATA / "evidence.json")
        self.rows, self.manifest, self.corpus = build_bundle(self.dataset, self.evidence)

    def test_bundle_covers_axes_and_preserves_draft_status_and_sources(self):
        result = validate_bundle(self.rows, self.manifest, self.corpus, self.dataset, self.evidence)
        self.assertEqual(result["cases"], 106)
        self.assertEqual(set(result["tasks"]), set(TASKS))
        for row in self.rows:
            self.assertEqual(row["metadata"]["purpose"], "evaluation_draft_only")
            self.assertEqual(row["metadata"]["status"], "pending_review")
            if not row["metadata"]["history"]:
                self.assertEqual(row["metadata"]["query"], row["question"])
            for ref in row["metadata"]["positive_reference"]:
                for citation in ref["quotes"]:
                    self.assertIn(citation["quote"], ref["contents"])

    def test_resealed_reference_answer_change_still_invalidates_bundle(self):
        self.rows[0]["golden_answers"] = ["Kaynakta olmayan kesin hüküm."]
        self.manifest["rows_sha256"] = digest(self.rows)
        with self.assertRaises(ValueError):
            validate_bundle(self.rows, self.manifest, self.corpus, self.dataset, self.evidence)

    def test_evidence_or_label_change_requires_rebuild(self):
        for field, value in [("status", "approved"), ("split", "train")]:
            rows = copy.deepcopy(self.rows)
            rows[0]["metadata"][field] = value
            with self.assertRaises(ValueError):
                validate_bundle(rows, self.manifest, self.corpus, self.dataset, self.evidence)
        self.corpus[0]["contents"] = "Değiştirilmiş kaynak"
        with self.assertRaises(ValueError):
            validate_bundle(self.rows, self.manifest, self.corpus, self.dataset, self.evidence)

    def test_conversation_uses_user_topic_and_never_reference_answer_as_prompt(self):
        row = copy.deepcopy(select(self.rows, "DTR-CONV-001")[0])
        row["golden_answers"] = ["CEVAP_SIZINTISI"]
        row["metadata"]["required_points"] = ["BEKLENTI_SIZINTISI"]
        row["metadata"]["query"] = "HEDEF_SORU_SIZINTISI"
        llm = Mock()
        query, hits, prompt = fixed_prompt(row, self.corpus, llm)
        self.assertIn("saydırabilir", query)
        self.assertTrue(query.startswith("Lisans için:"))
        for leaked in ["CEVAP_SIZINTISI", "BEKLENTI_SIZINTISI", "HEDEF_SORU_SIZINTISI",
                       "Tüm dersleriniz hiçbir şart olmadan otomatik sayılır."]:
            self.assertNotIn(leaked, prompt)
        llm.generate.assert_not_called()
        self.assertEqual(len(hits), 1)
        self.assertEqual(len(prompt_digest(prompt)), 64)

    def test_distractors_precede_positive_context_without_becoming_references(self):
        row = select(self.rows, "DTR-NOISE-001")[0]
        hits = context_hits(row, self.corpus)
        self.assertEqual(hits[0]["id"], "pg:p13")
        self.assertEqual({ref["id"] for ref in row["metadata"]["positive_reference"]}, {"ug:p7"})
        self.assertEqual(hits[-1]["id"], "ug:p7")

    def test_short_quote_in_wrong_document_is_not_relevant(self):
        quote = "Kaynakta kısa ama aynı ifade bulunur."
        row = {"metadata": {"positive_reference": [{"document": "dogru.pdf", "quotes": [{"quote": quote}]}]}}
        hits = [{"document": "yanlis.pdf", "text": quote}, {"document": "dogru.pdf", "text": quote}]
        self.assertEqual(citation_ranks(row, hits), [2])

    def test_abstention_and_missing_quotes_do_not_inflate_retrieval_success(self):
        result = retrieval_summary([{"behavior": "answer", "ranks": [1, None]},
                                    {"behavior": "abstain", "ranks": [1]},
                                    {"behavior": "answer", "ranks": [11]}])
        self.assertEqual(result["n_answer_queries"], 2)
        self.assertEqual(result["any_citation_at_5"], 1)
        self.assertEqual(result["all_citations_at_5"], 0)
        self.assertEqual(result["mrr_at_10"], .5)

    def test_unknown_scenario_is_not_silently_skipped(self):
        with self.assertRaises(ValueError):
            select(self.rows, "DTR-NOISE-999")

    def test_training_and_private_holdout_are_not_relabelled_as_development(self):
        for split, exposure in [("train", "development_exposed"), ("test", "private_holdout")]:
            dataset = self.dataset.model_copy(deep=True)
            # Aynı kural ailesine bağlı kayıtları birlikte bölümle.
            for case in dataset.cases:
                case.split, case.exposure = split, exposure
            with self.assertRaisesRegex(ValueError, "saklı test"):
                build_bundle(dataset, self.evidence)
