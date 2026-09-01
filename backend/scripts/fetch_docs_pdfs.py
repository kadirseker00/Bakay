"""KTMÜ mevzuat/doküman sayfasındaki tüm PDF'leri data/raw/web/ altına indirir.

Çalıştırma: backend/ içinden  .venv/bin/python scripts/fetch_docs_pdfs.py
"""
from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from urllib.parse import quote, unquote, urljoin
from urllib.request import Request, urlopen

BASE = "https://manas.edu.kg"
PAGE = f"{BASE}/tr/about_manas/docs"
RAW_WEB = Path(__file__).resolve().parents[2] / "data" / "raw" / "web"
UA = {"User-Agent": "Mozilla/5.0 (BAKAY ingest bot; KTMU BAP)"}


def safe_name(url: str) -> str:
    """URL yolundan dosya sistemi için güvenli, ASCII bir ad üretir."""
    path = unquote(url.split("://")[-1])
    path = path.split("/", 1)[1] if "/" in path else path
    stem = unicodedata.normalize("NFKD", path)
    stem = stem.encode("ascii", "ignore").decode("ascii")
    stem = re.sub(r"[^A-Za-z0-9.]+", "_", stem).strip("_")
    return stem or "belge.pdf"


def main() -> None:
    RAW_WEB.mkdir(parents=True, exist_ok=True)
    html = urlopen(Request(PAGE, headers=UA), timeout=60).read().decode("utf-8", "ignore")
    hrefs = sorted(set(re.findall(r'href="([^"]+\.pdf[^"]*)"', html)))

    ok = skipped = failed = 0
    for href in hrefs:
        url = urljoin(BASE + "/", href.replace(" ", "%20"))
        # Yol içindeki ASCII dışı karakterleri de yüzde-kodla
        scheme, rest = url.split("://", 1)
        host, _, path = rest.partition("/")
        url = f"{scheme}://{host}/" + quote(unquote(path), safe="/%")

        target = RAW_WEB / safe_name(href)
        if target.exists() or (RAW_WEB / "docs_mevzuattr.pdf").name == target.name:
            skipped += 1
            continue
        try:
            data = urlopen(Request(url, headers=UA), timeout=120).read()
            if not data.startswith(b"%PDF"):
                print(f"✗  PDF değil, atlandı: {href}")
                failed += 1
                continue
            target.write_bytes(data)
            ok += 1
            print(f"✓  {target.name} ({len(data) // 1024} KB)")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            print(f"✗  {href}: {exc}")

    print(f"\nBitti: {ok} indirildi, {skipped} zaten vardı/atlandı, {failed} hata.")


if __name__ == "__main__":
    main()
