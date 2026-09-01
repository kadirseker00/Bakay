from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from app.ingest.titles import extract_document_title, title_from_filename


class DocumentTitleTests(unittest.TestCase):
    def test_special_document_title(self) -> None:
        self.assertEqual(title_from_filename("docs_mevzuattr.pdf"), "KTMÜ Mevzuatı")

    def test_crawler_filename_is_cleaned(self) -> None:
        title = title_from_filename(
            "upload_global_Lisansustu_20egitim.pdf_ecd8a9f0.pdf"
        )
        self.assertEqual(title, "Lisansustu Egitim")

    def test_language_suffix_is_removed(self) -> None:
        self.assertEqual(
            title_from_filename("docs_2017_Idare_Faaliyet_Raporu_KG_s.pdf"),
            "2017 Idare Faaliyet Raporu",
        )

    def test_html_heading_is_preferred(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tr_faq_7_3bc18714.html"
            path.write_text(
                "<html><head><title>Öğrenci İşleri</title></head>"
                "<body><h1>Hazırlık Dil Eğitimi</h1></body></html>",
                encoding="utf-8",
            )
            self.assertEqual(extract_document_title(path), "Hazırlık Dil Eğitimi")

    def test_pdf_cover_filename_is_not_a_usable_title(self) -> None:
        import fitz

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "docs_faaliyet_raporu.pdf"
            document = fitz.open()
            document.set_metadata({"title": "tr kapak.CDR"})
            page = document.new_page()
            page.insert_text((72, 72), "2025 AKADEMIK FAALIYET RAPORU")
            document.save(path)
            document.close()
            self.assertEqual(
                extract_document_title(path), "2025 AKADEMIK FAALIYET RAPORU"
            )


if __name__ == "__main__":
    unittest.main()
