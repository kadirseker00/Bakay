"""Kaynak dosyalardan kullanıcıya gösterilecek belge başlığını çıkarır."""
from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import unquote


_SPECIAL_TITLES = {
    "docs_mevzuattr.pdf": "KTMÜ Mevzuatı",
}

_TITLE_TERMS = re.compile(
    r"(?i)(yönetmeliği|yönergesi|usul ve esasları|ilkeleri|kılavuzu|rehberi|"
    r"akademik takvim|stratejik plan|faaliyet raporu|kontenjan|burs|protokolü|"
    r"programı|planı|esasları|duyurusu)"
)

_GENERIC_LINES = {
    "bir üniversiteden ötesi",
    "kırgızistan-türkiye manas üniversitesi",
    "kırgızistan–türkiye manas üniversitesi",
    "ktmü mevzuatı",
    "mevzuat",
    "anlaşma",
    "tüzük",
    "yönetmelikler",
    "yönergeler",
    "usul ve esaslar",
    "ilkeler",
    "eşdeğerlik tabloları",
    "içindekiler",
}


def _clean(value: str) -> str:
    value = re.sub(r"^[^\wÇĞİÖŞÜçğıöşü]+", "", value, flags=re.UNICODE)
    return re.sub(r"\s+", " ", value).strip(" -–—_|:;,.\u00a0")


def _usable(value: str) -> bool:
    if not 4 <= len(value) <= 180:
        return False
    if value.casefold() in _GENERIC_LINES:
        return False
    if re.fullmatch(r"(?i)(sayfa\s*:?)?\s*\d+(?:\s*[/.-]\s*\d+)*", value):
        return False
    return sum(char.isalpha() for char in value) >= max(3, len(value) // 3)


def _choose_line(lines: list[str], *, require_title_term: bool = False) -> str | None:
    cleaned = [_clean(line) for line in lines]
    usable = [line for line in cleaned if _usable(line)]
    preferred = [line for line in usable if _TITLE_TERMS.search(line)]
    if require_title_term:
        return preferred[0] if preferred else None
    return (preferred or usable or [None])[0]


def title_from_filename(path: Path | str) -> str:
    """Teknik dosya adını okunabilir bir yedek başlığa dönüştürür."""
    name = Path(path).name
    if name in _SPECIAL_TITLES:
        return _SPECIAL_TITLES[name]

    name = unquote(name)
    name = re.sub(
        r"_[0-9a-f]{8}\.(?:html?|pdf|docx?|txt|md)$", "", name, flags=re.IGNORECASE
    )
    name = re.sub(r"\.(?:html?|pdf|docx?|txt|md)$", "", name, flags=re.IGNORECASE)
    name = re.sub(
        r"^(?:index\.php_|upload_global_|uploads_|docs_|tr_|kg_|ru_|en_)+",
        "",
        name,
        flags=re.IGNORECASE,
    )
    name = re.sub(
        r"(?i)(?:_(?:tr|kg|ru|en|site|s))+$",
        "",
        name,
    )
    # URL'lerdeki ``%20`` boşlukları tarama sırasında ``_20`` biçimine dönüşebiliyor.
    name = re.sub(r"(?i)(?:_|-)20(?=[a-zçğıöşü])", " ", name)
    name = re.sub(r"(?:_|-)20(?:_|-)", " ", name)
    name = re.sub(r"[_-]+", " ", name)
    name = _clean(name)
    if not name:
        return "KTMÜ Belgesi"

    title = name.title()
    replacements = {
        "Ktmu": "KTMÜ",
        "Ktmü": "KTMÜ",
        "Pdf": "PDF",
        "Tc": "T.C.",
    }
    for old, new in replacements.items():
        title = re.sub(rf"\b{re.escape(old)}\b", new, title)
    return title


def _html_title(path: Path) -> str | None:
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(path.read_text(encoding="utf-8", errors="ignore"), "html.parser")
    candidates: list[str] = []
    heading = soup.find("h1") or soup.find("h2")
    if heading:
        candidates.append(heading.get_text(" ", strip=True))
    social_title = soup.find("meta", attrs={"property": "og:title"})
    if social_title and social_title.get("content"):
        candidates.append(str(social_title["content"]))
    if soup.title:
        candidates.append(soup.title.get_text(" ", strip=True))

    for candidate in candidates:
        candidate = _clean(re.split(r"\s+[|–—]\s+", candidate, maxsplit=1)[0])
        if _usable(candidate):
            return candidate
    return None


def _pdf_title(path: Path) -> str | None:
    import fitz

    document = fitz.open(path)
    try:
        metadata_title = _clean((document.metadata or {}).get("title", ""))
        metadata_is_technical = bool(
            re.search(r"(?i)\.(?:cdr|pdf|docx?|xlsx?|pptx?)$", metadata_title)
            or "kapak" in metadata_title.casefold()
            or "_" in metadata_title
        )
        if _usable(metadata_title) and not metadata_is_technical:
            return metadata_title

        first_page = document[0].get_text("text") if document.page_count else ""
        # Tablo hücrelerini başlık sanmamak için PDF'de yalnızca başlık niteliği
        # taşıyan satırları kabul et; bulunamazsa temiz dosya adına düşülür.
        return _choose_line(
            first_page.splitlines()[:300], require_title_term=True
        )
    finally:
        document.close()


def _docx_title(path: Path) -> str | None:
    import docx

    document = docx.Document(path)
    metadata_title = _clean(document.core_properties.title or "")
    if _usable(metadata_title):
        return metadata_title
    return _choose_line([paragraph.text for paragraph in document.paragraphs[:30]])


def _text_title(path: Path) -> str | None:
    text = path.read_text(encoding="utf-8", errors="ignore")
    lines = [re.sub(r"^#{1,6}\s+", "", line) for line in text.splitlines()[:50]]
    return _choose_line(lines)


def extract_document_title(path: Path) -> str:
    """Belgenin gerçek başlığını çıkarır; bulunamazsa dosya adını temizler."""
    if path.name in _SPECIAL_TITLES:
        return _SPECIAL_TITLES[path.name]

    try:
        suffix = path.suffix.lower()
        if suffix in {".html", ".htm"}:
            title = _html_title(path)
        elif suffix == ".pdf":
            title = _pdf_title(path)
        elif suffix == ".docx":
            title = _docx_title(path)
        elif suffix in {".txt", ".md"}:
            title = _text_title(path)
        else:
            title = None
    except Exception:
        title = None

    return title or title_from_filename(path)
