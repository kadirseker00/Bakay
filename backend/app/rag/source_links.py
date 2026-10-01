"""Kaynak dosyalarının taramada kaydedilen gerçek adreslerine yönlendirme."""
from functools import lru_cache
import json
from urllib.parse import quote, urlsplit

from app.config import ROOT


def _official_url(url: str) -> bool:
    try:
        parsed = urlsplit(url)
        host = parsed.hostname or ""
        return (parsed.scheme in {"http", "https"} and not parsed.username
                and not parsed.password and (host == "manas.edu.kg" or host.endswith(".manas.edu.kg")))
    except ValueError:
        return False


@lru_cache(maxsize=1)
def _source_urls(signature: tuple) -> dict[str, str]:
    urls = {}
    for name, _ in signature:
        try:
            data = json.loads((ROOT / "data" / name).read_text(encoding="utf-8"))
            for row in [*data.get("docs", []), *data.get("pages", [])]:
                if row.get("file") and _official_url(row.get("url", "")):
                    urls[row["file"]] = row["url"]
        except (OSError, ValueError, TypeError, AttributeError):
            # Eksik/bozuk harita bir cevap üretimini engellememeli.
            continue
    return urls


def append_source_reading(text: str, hits: list[dict]) -> str:
    """İlk kaynak biliniyorsa ayrıntı bağlantısı ekler; URL veya sayfa uydurmaz."""
    if not hits or "bilgi bulamadım" in text.lower():
        return text
    hit = hits[0]
    document = hit["document"]
    if _official_url(document):
        url = document
    else:
        maps = sorted((ROOT / "data").glob("sitemap*.json"))
        try:
            signature = tuple((path.name, path.stat().st_mtime_ns) for path in maps)
        except OSError:
            return text
        url = _source_urls(signature).get(document)
    if not url:
        return text
    title = hit.get("title") or "Kaynak belge"
    title = title.replace("\\", "\\\\").replace("[", "\\[").replace("]", "\\]").replace("\n", " ")
    url = quote(url, safe=":/?=&%#@+;,-._~")
    if f"]({url})" in text:
        return text
    return text.rstrip() + f"\n\nAyrıntılar için [{title}]({url}) belgesini okuyabilirsiniz."
