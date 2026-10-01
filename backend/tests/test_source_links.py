"""Ayrıntı yönlendirmesinde gerçek kaynak eşleştirmesi ve adres sınırları."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from app.rag import source_links


class SourceReadingTests(unittest.TestCase):
    def test_recorded_source_url_is_used_and_no_page_is_invented(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "data").mkdir()
            (root / "data/sitemap.json").write_text(json.dumps({"docs": [
                {"file": "ug.pdf", "url": "https://oidb.manas.edu.kg/upload/ug.pdf"}]}))
            with patch.object(source_links, "ROOT", root):
                source_links._source_urls.cache_clear()
                result = source_links.append_source_reading("Yanıt.", [{"document": "ug.pdf", "title": "Yönetmelik"}])
                self.assertEqual(result, "Yanıt.\n\nAyrıntılar için [Yönetmelik](https://oidb.manas.edu.kg/upload/ug.pdf) belgesini okuyabilirsiniz.")
                self.assertEqual(source_links.append_source_reading(result, [{"document": "ug.pdf"}]), result)
        source_links._source_urls.cache_clear()

    def test_missing_first_source_does_not_link_an_unrelated_lower_result(self):
        with patch.object(source_links, "_source_urls", return_value={}):
            hits = [{"document": "unknown.pdf"}, {"document": "https://oidb.manas.edu.kg/other.pdf"}]
            self.assertEqual(source_links.append_source_reading("Yanıt.", hits), "Yanıt.")

    def test_unknown_answer_and_untrusted_urls_do_not_get_a_recommendation(self):
        hit = {"document": "https://oidb.manas.edu.kg/ug.pdf", "title": "Yönetmelik"}
        text = "Bu konuda elimdeki belgelerde bilgi bulamadım."
        self.assertEqual(source_links.append_source_reading(text, [hit]), text)
        for url in ["javascript:alert(1)", "https://manas.edu.kg.evil.example/a", "https://manas.edu.kg@evil.example/a"]:
            self.assertFalse(source_links._official_url(url))
