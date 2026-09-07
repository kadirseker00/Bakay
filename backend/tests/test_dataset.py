from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path

from pydantic import ValidationError

from evaluation.dataset import (
    DEFAULT_DATA, Case, Dataset, Review, content_hash, digest, export_rows,
    human_approved, normalize, read_json, review_markdown, snapshot, validate,
)
from scripts.dataset import write_new


class DatasetTests(unittest.TestCase):
    def setUp(self):
        self.evidence = {
            "sources": [{"id": "test", "title": "Deneme kaynağı", "kind": "html", "url": "https://example.org/test"}],
            "units": [{"id": "test:html", "source_id": "test", "page": None,
                       "printed_page": None, "text": "Başvuru yazılı olarak yapılır.",
                       "text_sha256": digest("Başvuru yazılı olarak yapılır.")}],
        }
        self.case = Case(
            id="BAKAY-001", question="Başvuru hangi şekilde yapılır?",
            paraphrases=["Başvuru yöntemini öğrenebilir miyim?"],
            answer="Başvuruyu yazılı olarak yapmalısınız.",
            required_points=["Yazılı başvuru."], forbidden_claims=["Sözlü başvurunun yeterli olduğu."],
            citations=[{"evidence_id": "test:html", "section": "Deneme madde",
                        "quote": "Başvuru yazılı olarak yapılır."}],
            behavior="answer", category="registration", scope="Sentetik test örneği",
            group_ids=["registration"],
        )
        self.dataset = Dataset(schema_version=1, title="Sentetik test", created_on="2026-09-07",
                               truth_scope="archived_source_snapshot_not_current_policy",
                               language="tr", evidence_sha256=digest(self.evidence), cases=[self.case])

    def approve(self, case=None, reviewers=("uzman-1", "uzman-2")):
        case = case or self.case
        case.reviews = [Review(reviewer_id=name, kind="human", decision="approve",
                               reviewed_at="2026-09-07T10:00:00+06:00",
                               content_sha256=content_hash(case, self.dataset.evidence_sha256),
                               source_version_checked=True, note="Sentetik test onayı.") for name in reviewers]
        case.status = "approved"

    def test_real_packet_contains_50_unapproved_cases(self):
        dataset = Dataset.model_validate(read_json(DEFAULT_DATA / "dataset.json"))
        report = validate(dataset, read_json(DEFAULT_DATA / "evidence.json"))
        self.assertEqual(report["cases"], 50)
        self.assertEqual(report["statuses"], {"pending_review": 50})
        self.assertEqual(report["behaviors"], {"answer": 45, "clarify": 3, "abstain": 2})
        self.assertTrue(all(not case.reviews for case in dataset.cases))

    def test_published_json_schema_matches_code(self):
        self.assertEqual(read_json(DEFAULT_DATA / "schema.json"), Dataset.model_json_schema())

    def test_defaults_never_imply_gold(self):
        self.assertEqual(self.case.status, "pending_review")
        self.assertEqual(self.case.split, "unassigned")
        self.assertFalse(human_approved(self.case, self.dataset.evidence_sha256))

    def test_missing_citation_is_rejected(self):
        self.case.citations[0].evidence_id = "missing"
        with self.assertRaisesRegex(ValueError, "Kaynakta bulunmayan"):
            validate(self.dataset, self.evidence)

    def test_fabricated_quote_is_rejected(self):
        self.case.citations[0].quote = "Başvuru sözlü olarak yapılır."
        with self.assertRaisesRegex(ValueError, "Kaynakta bulunmayan"):
            validate(self.dataset, self.evidence)

    def test_changed_snapshot_is_rejected(self):
        self.evidence["sources"][0]["title"] = "Değiştirilmiş kaynak"
        with self.assertRaisesRegex(ValueError, "anlık görüntüsünün"):
            validate(self.dataset, self.evidence)

    def test_changed_text_hash_is_rejected(self):
        self.evidence["units"][0]["text"] = "Yeni dayanak metni."
        self.dataset.evidence_sha256 = digest(self.evidence)
        with self.assertRaisesRegex(ValueError, "Dayanak özeti"):
            validate(self.dataset, self.evidence)

    def test_duplicate_case_id_is_rejected(self):
        self.dataset.cases.append(self.case.model_copy(deep=True))
        with self.assertRaisesRegex(ValueError, "Yinelenen soru kimliği"):
            validate(self.dataset, self.evidence)

    def test_paraphrase_duplicate_ignores_case_and_punctuation(self):
        self.case.paraphrases.append("BAŞVURU HANGİ ŞEKİLDE YAPILIR!!!")
        with self.assertRaisesRegex(ValueError, "Yinelenen/boş soru"):
            validate(self.dataset, self.evidence)

    def test_group_cannot_cross_splits(self):
        other = self.case.model_copy(deep=True, update={"id": "BAKAY-002", "question": "Kaydı nasıl tamamlarım?",
                                   "paraphrases": ["Kayıt yöntemi nedir?"], "split": "dev"})
        self.case.split = "train"
        self.dataset.cases.append(other)
        with self.assertRaisesRegex(ValueError, "sızıntısı"):
            validate(self.dataset, self.evidence)

    def test_exposed_case_cannot_become_test(self):
        row = self.case.model_dump()
        row["split"] = "test"
        with self.assertRaisesRegex(ValidationError, "bağımsız test"):
            Case.model_validate(row)

    def test_export_revalidates_mutated_objects(self):
        self.case.split = "test"
        with self.assertRaisesRegex(ValidationError, "bağımsız test"):
            export_rows(self.dataset, self.evidence, "test", "evaluation")

    def test_source_required_except_out_of_scope_abstention(self):
        row = self.case.model_dump()
        row["citations"] = []
        with self.assertRaises(ValidationError):
            Case.model_validate(row)
        row.update(behavior="abstain", category="out_of_scope")
        self.assertFalse(Case.model_validate(row).citations)

    def test_unknown_schema_field_is_rejected(self):
        with self.assertRaises(ValidationError):
            Case.model_validate({**self.case.model_dump(), "auto_approved": True})

    def test_empty_variant_is_rejected(self):
        with self.assertRaises(ValidationError):
            Case.model_validate({**self.case.model_dump(), "paraphrases": [" "]})

    def test_pending_data_cannot_export_to_evaluation_or_lora(self):
        for split, purpose in [("dev", "evaluation"), ("train", "lora")]:
            self.case.split = split
            with self.assertRaisesRegex(ValueError, "uzman onayı"):
                export_rows(self.dataset, self.evidence, split, purpose)

    def test_empty_split_cannot_export(self):
        with self.assertRaisesRegex(ValueError, "bölümü boş"):
            export_rows(self.dataset, self.evidence, "train", "lora")

    def test_one_human_is_not_enough(self):
        self.approve(reviewers=("uzman-1",))
        with self.assertRaisesRegex(ValueError, "İki güncel insan onayı"):
            validate(self.dataset, self.evidence)

    def test_same_human_twice_is_not_enough(self):
        self.approve(reviewers=("uzman-1", "UZMAN-1"))
        self.assertFalse(human_approved(self.case, self.dataset.evidence_sha256))

    def test_ai_review_cannot_replace_human(self):
        self.approve()
        self.case.reviews[1].kind = "ai"
        self.assertFalse(human_approved(self.case, self.dataset.evidence_sha256))

    def test_source_version_check_required(self):
        self.approve()
        self.case.reviews[1].source_version_checked = False
        self.assertFalse(human_approved(self.case, self.dataset.evidence_sha256))

    def test_review_invalidated_by_answer_change(self):
        self.approve()
        self.case.answer += " Değişen cevap."
        self.assertFalse(human_approved(self.case, self.dataset.evidence_sha256))

    def test_review_invalidated_by_split_change(self):
        self.approve()
        self.case.split = "train"
        self.assertFalse(human_approved(self.case, self.dataset.evidence_sha256))

    def test_later_rejection_blocks_approval(self):
        self.approve()
        self.case.reviews.append(self.case.reviews[0].model_copy(update={"decision": "reject"}))
        self.assertFalse(human_approved(self.case, self.dataset.evidence_sha256))

    def test_approved_train_exports_grounded_lora_messages(self):
        self.case.split = "train"
        self.approve()
        rows = export_rows(self.dataset, self.evidence, "train", "lora")
        self.assertEqual(len(rows), 1)
        self.assertIn(self.case.citations[0].quote, rows[0]["messages"][1]["content"])
        self.assertIn(self.case.scope, rows[0]["messages"][1]["content"])
        self.assertEqual(rows[0]["messages"][-1]["content"], self.case.answer)

    def test_lora_never_accepts_dev_or_test(self):
        for split in ["dev", "test"]:
            with self.assertRaisesRegex(ValueError, "yalnızca train"):
                export_rows(self.dataset, self.evidence, split, "lora")

    def test_approved_dev_can_export_for_evaluation(self):
        self.case.split = "dev"
        self.approve()
        rows = export_rows(self.dataset, self.evidence, "dev", "evaluation")
        self.assertEqual(rows[0]["content_sha256"], content_hash(self.case, self.dataset.evidence_sha256))

    def test_rejected_case_cannot_export(self):
        self.case.split = "dev"
        self.approve()
        self.case.status = "rejected"
        with self.assertRaisesRegex(ValueError, "reddedilen"):
            export_rows(self.dataset, self.evidence, "dev", "evaluation")

    def test_review_packet_lists_real_status_not_fixed_zero(self):
        self.approve()
        text = review_markdown(self.dataset, self.evidence)
        self.assertIn("1/1", text)
        self.assertIn("Deneme kaynağı", text)
        self.assertIn(content_hash(self.case, self.dataset.evidence_sha256), text)

    def test_write_new_does_not_overwrite_existing_output(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "review.md"
            write_new(path, "ilk")
            with self.assertRaises(FileExistsError):
                write_new(path, "yeni")
            self.assertEqual(path.read_text(), "ilk")

    def test_snapshot_roundtrip_and_raw_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.html"
            source.write_text('<main id="content">Başvuru yazılı olarak yapılır.</main>', encoding="utf-8")
            catalog = [{"id": "test", "title": "Test", "path": "source.html", "url": "https://example.org",
                        "kind": "html", "selector": "#content"}]
            evidence = snapshot(catalog, root)
            self.dataset.evidence_sha256 = digest(evidence)
            validate(self.dataset, evidence, verify_raw=True, root=root)
            source.write_text('<main id="content">Başvuru sözlü olarak yapılır.</main>', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Ham belge değişmiş"):
                validate(self.dataset, evidence, verify_raw=True, root=root)

    def test_source_path_cannot_escape_repository(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "depo dışına"):
                snapshot([{"id": "test", "path": "../external.html", "kind": "html", "selector": "main"}], Path(directory))

    def test_pdf_page_metadata_is_checked(self):
        evidence = copy.deepcopy(self.evidence)
        evidence["sources"][0].update(kind="pdf", pages=[2], printed_page_offset=100)
        evidence["units"][0].update(id="test:p2", page=2, printed_page=103)
        self.case.citations[0].evidence_id = "test:p2"
        self.dataset.evidence_sha256 = digest(evidence)
        with self.assertRaisesRegex(ValueError, "PDF sayfa konumu"):
            validate(self.dataset, evidence)

    def test_unicode_and_whitespace_normalization(self):
        self.assertEqual(normalize(" o\u0308g\u0306renci\n  işleri "), "öğrenci işleri")


if __name__ == "__main__":
    unittest.main()
