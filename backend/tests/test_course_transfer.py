"""Vektör aramasının kaçırdığı hükmün kelime aramasıyla kurtarılması."""
from __future__ import annotations

import math
import tempfile
from threading import RLock
import unittest
from unittest.mock import Mock, patch

import chromadb

from app.rag import pipeline
from app.rag.retrieval import LexicalIndex, needs_education_level, text_key
from app.rag.vectorstore import VectorStore
from app.schemas import ChatMessage


TITLE = "ÖNLİSANS VE LİSANS EĞİTİM-ÖĞRETİM YÖNETMELİĞİ (YENİ)"
ARTICLE = (
    "Ders Saydırma, Ders Muafiyeti ve İntibak\n"
    "Madde 25– (1) Üniversitenin bir önlisans ve lisans programına ilk kez kayıt yaptıran öğrenci, "
    "daha önce kaydolduğu yükseköğretim kurumundan almış ve başarmış olduğu dersleri saydırabilir. "
    "(2) Ders saydırma ve ders muafiyetleri işlemleri öğrencinin Bölüm Başkanlığına, ekinde not "
    "durum belgesi ve ders içerikleri bulunan yazılı başvurusu ile başlatılır. "
    "(3) Son 5 yıl içinde alınmış olması ve başarı notunun en az CC olması şartıyla "
    "AKTS’si ve içeriği uygun olan derslerden muaf tutulabilir."
)


class CourseTransferTests(unittest.TestCase):
    def test_degree_selection_preserves_original_question_without_rewriting(self):
        original = "başka kurumdan aldığım dersi saydırabilir miyim"
        history = [ChatMessage(role="user", content=original),
                   ChatMessage(role="assistant", content=pipeline.NEEDS_LEVEL)]
        llm = Mock()
        for question in ["Lisans için soruyorum.", "Önlisans", "Yüksek lisans için?", "Doktora"]:
            with self.subTest(question=question):
                resolved = pipeline._resolve_question(question, history, llm)
                self.assertIn(original, resolved)
                self.assertEqual(resolved.split(" için:")[0], question.split(" için")[0])
        llm.generate.assert_not_called()
        # Açık bir yeni konu eski soruyla birleştirilmez.
        question = "Lisans öğrencileri için burs şartları neler?"
        self.assertEqual(pipeline._resolve_question(question, history, llm), question)

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        store = VectorStore.__new__(VectorStore)
        store.client = chromadb.PersistentClient(path=self.directory.name)
        store.collection = store.client.get_or_create_collection(
            "course_test", metadata={"hnsw:space": "cosine"}
        )
        store.embedder = Mock()
        store.embedder.encode_one.return_value = [1.0, 0.0, 0.0]
        store.embedder.encode.side_effect = lambda texts: [[0.37, math.sqrt(1 - 0.37**2), 0.0]] * len(texts)
        store._lexical = None
        store._lexical_count = -1
        store._lexical_lock = RLock()
        self.store = store

    def add_article(self, text=ARTICLE):
        self.store.add([{"id": "article", "text": text, "document": "onlisans.pdf",
                         "meta": {"title": TITLE}}])

    def test_article_outside_dense_candidates_is_recovered_with_real_cosine(self):
        self.add_article()
        # İlk 60 vektör sonucunun hepsi yanıltıcıdır; hedef bu havuzun dışında.
        records = [{"id": f"noise-{i}", "text": f"Faaliyet raporu laboratuvar imkanları {i}",
                    "document": f"report-{i}.pdf"} for i in range(70)]
        self.store.embedder.encode.side_effect = lambda texts: [[0.6, 0.8, 0.0]] * len(texts)
        self.store.add(records)
        question = "başka kurumdan aldığım dersi saydırabilir miyim"
        self.assertNotIn("article", [hit["id"] for hit in self.store.query_dense(question, 60)])
        hits = self.store.query(question, 5)
        article = next(hit for hit in hits if hit["id"] == "article")
        self.assertEqual(article["score"], 0.37)
        self.assertEqual(article["title"], TITLE)

    def test_inflected_course_transfer_and_exemption_queries_recover_article(self):
        index = LexicalIndex([
            {"id": "article", "text": ARTICLE, "document": "onlisans.pdf", "title": TITLE},
            {"id": "noise", "text": "Yabancı dil hazırlık sınavı muafiyet işlemleri.",
             "document": "prep.pdf", "title": "Dil Hazırlığı"},
        ])
        for question in ["Dersi saydırabilir miyim?", "Lisans derslerini saydırmanın koşulları",
                         "Başka kurumdan aldığım derslerin muafiyeti"]:
            with self.subTest(question=question):
                self.assertIn("article", index.query(question, 2))

    def test_duplicate_text_prefers_standalone_regulation(self):
        self.add_article()
        self.store.add([{"id": "compilation", "text": ARTICLE.replace(" ", "  "),
                         "document": "docs_mevzuattr.pdf", "meta": {"title": "KTMÜ Mevzuatı"}}])
        hits = self.store.query("ders saydırma", 5)
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["document"], "onlisans.pdf")

    def test_explicit_degree_does_not_promote_the_other_degree(self):
        index = LexicalIndex([
            {"id": "ug", "text": ARTICLE, "document": "ug.pdf", "title": TITLE},
            {"id": "grad", "text": "Ders saydırma lisansüstü: yüksek lisans CB, doktora BB.",
             "document": "grad.pdf", "title": "Lisansüstü Eğitim Yönetmeliği"},
        ])
        for question, expected in [("Lisansta ders saydırma", "ug"),
                                   ("Yüksek lisans ders saydırma", "grad"),
                                   ("Doktorada ders saydırma", "grad")]:
            with self.subTest(question=question):
                self.assertEqual(index.fuse(question, ["ug", "grad"], ["ug", "grad"], 1), [expected])

    def test_empty_and_small_collection_do_not_request_too_many_neighbors(self):
        self.assertEqual(self.store.query("ders saydırma", 5), [])
        self.add_article()
        self.assertEqual(len(self.store.query("ders saydırma", 5)), 1)

    def test_local_upsert_refreshes_index_even_when_count_is_unchanged(self):
        self.add_article()
        self.store.query("ders saydırma")
        self.add_article("Kütüphane ödünç kitap teslimi.")
        self.store.query("kütüphane")
        self.assertEqual(self.store._lexical.query("saydırma", 5), [])

    def test_external_addition_refreshes_cached_index(self):
        self.add_article()
        self.store.query("ders saydırma")
        self.store.collection.upsert(ids=["new"], documents=["Burs başvurusu belgeleri"],
                                     metadatas=[{"document": "burs.pdf"}], embeddings=[[0.6, 0.8, 0.0]])
        self.assertIn("new", [hit["id"] for hit in self.store.query("burs başvurusu")])

    def test_deduplication_preserves_material_numbers(self):
        self.assertNotEqual(text_key("Not en az CC, sınır 1/3"), text_key("Not en az CB, sınır 1/2"))

    def test_cut_condition_is_completed_from_same_document(self):
        previous = "X" * (1000 - len("Öğreni")) + "Öğreni"
        current = "m dili ve içeriği uygun derslerin %70'i saydırılabilir."
        index = LexicalIndex([
            {"id": "grad.pdf::0::a", "text": previous, "document": "grad.pdf", "title": "Lisansüstü"},
            {"id": "grad.pdf::1::b", "text": current, "document": "grad.pdf", "title": "Lisansüstü"},
            {"id": "other.pdf::0::c", "text": "Yanlış belge", "document": "other.pdf", "title": "Başka"},
        ])
        context = index.context_for("grad.pdf::1::b")
        self.assertIn("Öğrenim dili ve içeriği uygun", context)
        self.assertNotIn("Yanlış belge", context)

    def test_conflicting_degree_rules_ask_for_scope_without_generating_conditions(self):
        hits = [
            {"document": "ug.pdf", "title": TITLE, "text": ARTICLE, "score": 0.37},
            {"document": "grad.pdf", "title": "Lisansüstü Yönetmeliği", "score": 0.4,
             "text": "Lisansüstü dersleri saydırılabilir. Yüksek lisans CB, doktora BB."},
        ]
        llm = Mock()
        with patch.object(pipeline, "get_store") as store, \
             patch.object(pipeline, "get_llm", return_value=llm), \
             patch.object(pipeline, "_log"), \
             patch.multiple(pipeline.settings, agent_route=False, agent_rewrite=False, agent_verify=False):
            store.return_value.query.return_value = hits
            response = pipeline.answer("başka kurumdan aldığım dersi saydırabilir miyim")
        self.assertTrue(response.answer.endswith(pipeline.NEEDS_LEVEL))
        self.assertIn("Madde 25", response.answer)
        self.assertIn("dersleri saydırabilir.", response.answer)
        self.assertNotIn("CB", response.answer)
        self.assertNotIn("CC", response.answer)
        self.assertEqual(response.sources[0].document, "ug.pdf")
        llm.generate.assert_not_called()
        self.assertFalse(needs_education_level("Lisansta dersi saydırabilir miyim?", hits))
        self.assertFalse(needs_education_level("Yüksek lisans ders saydırma şartları", hits))

    def test_unrelated_degree_documents_do_not_trigger_scope_question(self):
        hits = [{"title": TITLE, "text": ARTICLE},
                {"title": "Lisansüstü Yönetmeliği", "text": "Doktora azami öğrenim süresi."}]
        self.assertFalse(needs_education_level("Ders saydırmanın şartları neler?", hits))
        self.assertFalse(needs_education_level("Yurt başvuru belgeleri neler?", hits))

    def test_preanswer_skips_irrelevant_or_incomplete_provisions_and_thresholds(self):
        for text in [
            "Ders Saydırma\nMadde 25– (1) Üniversitenin bir lisans öğrencisi derslerini saydırabil",
            "Ders Saydırma\nMadde 25– (1) Lisans öğrencisi son 5 yılda aldığı derslerini saydırabilir.",
            "Devam Zorunluluğu\nMadde 28– (1) Lisans öğrencileri derslere devam etmek zorundadır.",
        ]:
            with self.subTest(text=text):
                hits = [{"title": TITLE, "text": text}]
                self.assertEqual(pipeline._scope_preanswer("ders saydırma", hits), pipeline.NEEDS_LEVEL)

    def test_preanswer_followup_keeps_question_and_ignores_quoted_facts(self):
        original = "başka kurumdan aldığım dersi saydırabilir miyim"
        preanswer = pipeline._scope_preanswer(original, [{"title": TITLE, "text": ARTICLE}])
        history = [ChatMessage(role="user", content=original),
                   ChatMessage(role="assistant", content=preanswer)]
        llm = Mock()
        resolved = pipeline._resolve_question("Lisans için soruyorum.", history, llm)
        self.assertEqual(resolved, "Lisans için: " + original)
        llm.generate.assert_not_called()


if __name__ == "__main__":
    unittest.main()
