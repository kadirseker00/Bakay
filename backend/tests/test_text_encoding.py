"""Bozuk kaynak başlığının indeks, prompt ve kullanıcıya taşınmasını önler."""
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import RLock
import unittest
from unittest.mock import Mock

from app.ingest.clean import normalize, repair_turkish_encoding
from app.ingest.titles import extract_document_title
from app.rag.pipeline import _build_context, _label_source_references
from app.rag.source_links import append_source_reading
from app.rag.vectorstore import VectorStore


BROKEN = "Kırgızistan-Tьrkiye Manas Ьniversitesi"
CORRECT = "Kırgızistan-Türkiye Manas Üniversitesi"


class TextEncodingTests(unittest.TestCase):
    def test_ingestion_repairs_name_and_preserves_rules(self):
        text = f"{BROKEN}\r\nEn az CC; 5 yıl; 1/3'ü aşamaz."
        self.assertEqual(normalize(text), f"{CORRECT}\nEn az CC; 5 yıl; 1/3'ü aşamaz.")

    def test_uppercase_suffixes_and_lowercase_are_repaired(self):
        self.assertEqual(
            repair_turkish_encoding("TЬRKİYE ЬNİVERSİTESİ; tьrkiye ьniversitesinin"),
            "TÜRKİYE ÜNİVERSİTESİ; türkiye üniversitesinin",
        )

    def test_cyrillic_languages_and_correct_turkish_are_preserved(self):
        text = f"Кыргыз-Түрк Манас университети; факультеты; июль; ОБЪЯВЛЕНИЕ; {CORRECT}"
        self.assertEqual(repair_turkish_encoding(text), text)
        self.assertEqual(repair_turkish_encoding(repair_turkish_encoding(BROKEN)), CORRECT)

    def test_pdf_metadata_title_is_repaired(self):
        import fitz

        with TemporaryDirectory() as directory:
            path = Path(directory) / "ogrenci_el_kitabi.pdf"
            with fitz.open() as document:
                document.set_metadata({"title": BROKEN + " Öğrenci El Kitabı"})
                document.new_page()
                document.save(path)
            self.assertEqual(extract_document_title(path), CORRECT + " Öğrenci El Kitabı")

    def make_store(self):
        store = VectorStore.__new__(VectorStore)
        store.collection = Mock()
        store.collection.count.return_value = 1
        store.embedder = Mock()
        store.embedder.encode_one.return_value = [1.0, 0.0]
        store._lexical = None
        store._lexical_count = -1
        store._lexical_lock = RLock()
        return store

    def test_existing_index_is_repaired_before_prompt_citation_and_source_link(self):
        store = self.make_store()
        document = "ogrenci_el_kitabi.pdf"
        store.collection.get.side_effect = [
            {"ids": ["book::0::abc"], "documents": [BROKEN + " burs bilgileri."],
             "metadatas": [{"document": document, "title": BROKEN}]},
            {"ids": ["book::0::abc"], "embeddings": [[1.0, 0.0]]},
        ]
        store.collection.query.return_value = {"ids": [["book::0::abc"]]}
        hits = store.query("burs", top_k=1)
        self.assertEqual(hits[0]["title"], CORRECT)
        self.assertIn(CORRECT, hits[0]["text"])
        self.assertIn(CORRECT, hits[0]["context_text"])
        context = _build_context(hits)
        self.assertIn(CORRECT, context)
        self.assertNotIn(BROKEN, context)
        answer = append_source_reading(_label_source_references("Bkz. [1].", hits), hits)
        self.assertIn(f"**{CORRECT}**", answer)
        self.assertNotIn(BROKEN, answer)
        self.assertEqual(hits[0]["document"], document)
        store.collection.upsert.assert_not_called()

    def test_dense_retrieval_repairs_existing_title_and_snippet(self):
        store = self.make_store()
        store.collection.query.return_value = {
            "ids": [["book::0::abc"]], "documents": [[BROKEN]],
            "metadatas": [[{"document": "book.pdf", "title": BROKEN}]],
            "distances": [[0.1]],
        }
        hit = store.query_dense("üniversite", top_k=1)[0]
        self.assertEqual(hit["title"], CORRECT)
        self.assertEqual(hit["text"], CORRECT)


if __name__ == "__main__":
    unittest.main()
