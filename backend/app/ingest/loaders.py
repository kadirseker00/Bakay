"""Belge yükleyiciler (İP1): PDF, HTML ve düz metin.

data/raw/ içindeki dosyaları okuyup ham metne çevirir. Web scraping (Selenium/
Playwright) İP1'in ilerleyen aşamasında eklenecek; şu an indirilmiş dosyalarla
çalışıyoruz.
"""
from __future__ import annotations

from pathlib import Path


def load_pdf(path: Path) -> str:
    """PyMuPDF ile PDF metnini çıkarır."""
    import fitz  # pymupdf

    doc = fitz.open(path)
    pages = [page.get_text("text") for page in doc]
    doc.close()
    return "\n".join(pages)


def load_html(path: Path) -> str:
    """HTML'den okunabilir metni çıkarır (script/style atılır)."""
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(path.read_text(encoding="utf-8", errors="ignore"), "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    return soup.get_text(separator="\n")


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


_LOADERS = {
    ".pdf": load_pdf,
    ".html": load_html,
    ".htm": load_html,
    ".txt": load_text,
    ".md": load_text,
}


def load_file(path: Path) -> str | None:
    """Uzantıya göre uygun yükleyiciyi seçer. Desteklenmeyen tip için None."""
    loader = _LOADERS.get(path.suffix.lower())
    return loader(path) if loader else None
