"""Vurgu eklenirken hüküm metni ve bağlantıların korunması."""
import unittest

from app.rag.pipeline import _highlight_key_details


class AnswerPresentationTests(unittest.TestCase):
    def test_emphasis_preserves_thresholds_and_negations_verbatim(self):
        text = "Son 5 yıl içinde alınmış ve en az CC olmalıdır; toplam AKTS 1/3'ü aşamaz."
        result = _highlight_key_details(text)
        self.assertEqual(result.replace("**", ""), text)
        for detail in ["Son 5 yıl", "en az CC", "1/3"]:
            self.assertIn(f"**{detail}**", result)

    def test_existing_markdown_and_links_are_preserved_and_idempotent(self):
        text = "**en az CC**; [Kaynak %70](https://example.org/5/3); `5 yıl`; en az %70."
        result = _highlight_key_details(text)
        self.assertEqual(_highlight_key_details(result), result)
        self.assertIn("[Kaynak %70](https://example.org/5/3)", result)
        self.assertIn("`5 yıl`", result)
        self.assertIn("**en az %70**", result)

    def test_dates_article_numbers_and_absent_rules_are_not_emphasized(self):
        text = "Madde 25; 2026-10-01; bu konuda şart bulunamadı."
        self.assertEqual(_highlight_key_details(text), text)
