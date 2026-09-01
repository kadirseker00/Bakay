from __future__ import annotations

import unittest

from app.rag.pipeline import _label_source_references


class SourceReferenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.hits = [
            {"title": "KTMÜ Mevzuatı"},
            {"title": "Akademik Takvim"},
        ]

    def test_numbered_document_and_filename_are_replaced(self) -> None:
        text = "**[1] numaralı belge** (docs_mevzuattr.pdf) açıklıyor."
        self.assertEqual(
            _label_source_references(text, self.hits),
            "**KTMÜ Mevzuatı** açıklıyor.",
        )

    def test_title_followed_by_document_word_is_replaced(self) -> None:
        text = "Bilgi [1] numaralı KTMÜ Mevzuatı belgesinde yer alıyor."
        self.assertEqual(
            _label_source_references(text, self.hits),
            "Bilgi **KTMÜ Mevzuatı** adlı kaynakta yer alıyor.",
        )

    def test_plain_citations_are_replaced(self) -> None:
        text = "Tarihler [2]'de; koşullar [1] belge içinde yer alıyor."
        self.assertEqual(
            _label_source_references(text, self.hits),
            "Tarihler **Akademik Takvim**'de; koşullar **KTMÜ Mevzuatı** içinde yer alıyor.",
        )

    def test_repeated_title_after_citation_is_removed(self) -> None:
        text = "Bilgi (**[1]** KTMÜ Mevzuatı) içinde açıklanıyor."
        self.assertEqual(
            _label_source_references(text, self.hits),
            "Bilgi (**KTMÜ Mevzuatı**) içinde açıklanıyor.",
        )

    def test_adjacent_references_to_same_source_are_merged(self) -> None:
        text = "Koşullar ([1] ve [1]ler) içinde açıklanıyor."
        self.assertEqual(
            _label_source_references(text, self.hits),
            "Koşullar (**KTMÜ Mevzuatı**) içinde açıklanıyor.",
        )


if __name__ == "__main__":
    unittest.main()
