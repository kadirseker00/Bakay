"""Ölçüm hatalarını engelleyen küçük, bağımsız örnekler."""
import unittest

from evaluation.system_audit import BM25, aggregate, fuse, qrels, score


class AuditMetricsTests(unittest.TestCase):
    def test_one_hit_does_not_mean_all_evidence_found(self):
        result = score([0], [{"relevant": [0], "full_quote": [0]},
                             {"relevant": [1], "full_quote": [1]}])
        self.assertTrue(result["hit_at_5"])
        self.assertFalse(result["all_citations_at_5"])
        self.assertEqual(result["citation_recall_at_5"], .5)

    def test_mrr_and_top_five_are_distinct(self):
        result = score(list(range(10)), [{"relevant": [7], "full_quote": [7]}])
        self.assertFalse(result["hit_at_5"])
        self.assertEqual(result["mrr_at_10"], 1 / 8)

    def test_abstention_is_excluded_from_retrieval_denominator(self):
        answer = {"behavior": "answer", **score([0], [{"relevant": [0], "full_quote": [0]}])}
        abstain = {"behavior": "abstain", **score([], [])}
        self.assertEqual(aggregate([answer, abstain])["n_answer_queries"], 1)

    def test_short_common_quote_requires_same_document(self):
        labels = qrels([{"id": "q", "citations": [{"evidence_id": "u", "quote": "Evet.", "section": "s"}]}],
                       [{"text": "Evet.", "document": "a.pdf"}, {"text": "Evet.", "document": "b.pdf"}],
                       {"s": {"path": "a.pdf"}}, {"u": {"source_id": "s"}})
        self.assertEqual(labels["q"][0]["relevant"], [0])

    def test_long_verbatim_duplicate_is_not_penalized(self):
        quote = "Başvuru süresi sınavların bitiminden itibaren üç iş günüdür. " * 3
        labels = qrels([{"id": "q", "citations": [{"evidence_id": "u", "quote": quote, "section": "s"}]}],
                       [{"text": quote, "document": "a.pdf"}, {"text": quote, "document": "anthology.pdf"}],
                       {"s": {"path": "a.pdf"}}, {"u": {"source_id": "s"}})
        self.assertEqual(labels["q"][0]["full_quote"], [0, 1])

    def test_bm25_turkish_case_and_rrf(self):
        chunks = [{"text": "İTİRAZ SINAVI"}, {"text": "Kayıt işlemleri"}]
        self.assertEqual(BM25(chunks).query("itiraz sınavı"), [0])
        self.assertEqual(fuse([0, 1], [1, 2])[0], 1)


if __name__ == "__main__":
    unittest.main()
