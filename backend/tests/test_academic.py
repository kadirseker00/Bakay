"""Tam olmayan dışa aktarım, yanlış kişi eşleştirmesi ve kaynak kaybı regresyonları."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
from unittest import TestCase

from app.ingest.academic import export, prepare


def payload():
    work = {"url": "https://publications.manas.edu.kg/yayin/123", "title": "Örnek yayın",
            "year": "2026", "journal": "Örnek dergi"}
    return {"schema_version": 1, "fetched_at": "2026-11-02", "complete": True,
            "expected_researchers": 2, "researchers": [
                {"url": "https://publications.manas.edu.kg/arastirmaci/a", "name": "Araştırmacı A",
                 "department": "Bilgisayar", "email": "a@manas.edu.kg", "publications": [deepcopy(work)]},
                {"url": "https://publications.manas.edu.kg/arastirmaci/b", "name": "Araştırmacı B",
                 "department": "Matematik", "publications": [deepcopy(work)]}]}


class AcademicTests(TestCase):
    def test_shared_work_has_one_record_and_two_authors_without_mixing_people(self):
        records = prepare(payload())
        self.assertEqual(len(records), 3)
        self.assertIn("Kurumsal e-posta: a@manas.edu.kg", records[0]["text"])
        self.assertNotIn("a@manas.edu.kg", records[1]["text"])
        self.assertIn("Araştırmacı A; Araştırmacı B", records[2]["text"])
        self.assertEqual(records[2]["meta"]["source_url"], "https://publications.manas.edu.kg/yayin/123")

    def test_partial_or_duplicate_snapshot_and_conflicting_work_are_rejected(self):
        cases = []
        data = payload(); data["complete"] = False; cases.append(data)
        data = payload(); data["researchers"].pop(); cases.append(data)
        data = payload(); data["researchers"][1] = deepcopy(data["researchers"][0]); cases.append(data)
        data = payload(); data["researchers"][1]["publications"][0]["title"] = "Başka eser"; cases.append(data)
        data = payload(); data["researchers"][0].pop("publications"); cases.append(data)
        for data in cases:
            with self.subTest(data=data), self.assertRaises(ValueError):
                prepare(data)

    def test_foreign_urls_verification_pages_and_private_email_are_rejected(self):
        for url in ("https://publications.manas.edu.kg.evil.test/arastirmaci/a",
                    "https://evil@publications.manas.edu.kg/arastirmaci/a",
                    "http://publications.manas.edu.kg/arastirmaci/a",
                    "https://publications.manas.edu.kg/dogrulama/",
                    "https://publications.manas.edu.kg/arastirmaci/a?token=private"):
            data = payload(); data["researchers"][0]["url"] = url
            with self.subTest(url=url), self.assertRaises(ValueError):
                prepare(data)
        data = payload(); data["researchers"][0]["email"] = "private@example.com"
        with self.assertRaises(ValueError):
            prepare(data)

    def test_contact_update_keeps_identity_and_export_retains_source_map(self):
        before = prepare(payload())
        data = payload(); data["researchers"][0]["email"] = "changed@manas.edu.kg"
        after = prepare(data)
        self.assertEqual(before[0]["id"], after[0]["id"])
        with tempfile.TemporaryDirectory() as folder:
            export(after, Path(folder))
            mapping = json.loads((Path(folder) / "data/sitemap-academic.json").read_text())
            self.assertEqual(len(mapping["pages"]), 3)
            self.assertEqual(mapping["pages"][0]["url"], data["researchers"][0]["url"])
            saved = Path(folder) / "data/processed/academic" / after[0]["document"]
            self.assertIn("changed@manas.edu.kg", saved.read_text())
