"""İndeksleme komut satırı aracı (İP1 → İP3 köprüsü).

data/raw/ içindeki tüm belgeleri: yükle → temizle → parçala → embed → Chroma'ya
yazar. Çalıştırma:

    python -m app.ingest.run
"""
from __future__ import annotations

import hashlib

from app.config import ROOT
from app.ingest.chunk import chunk_text
from app.ingest.clean import normalize
from app.ingest.loaders import load_file
from app.rag.vectorstore import get_store

RAW_DIR = ROOT / "data" / "raw"


def _chunk_id(document: str, idx: int, text: str) -> str:
    h = hashlib.md5(text.encode("utf-8")).hexdigest()[:8]
    return f"{document}::{idx}::{h}"


def ingest() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    files = [p for p in RAW_DIR.rglob("*") if p.is_file()]
    if not files:
        print(f"⚠  {RAW_DIR} boş. Belgeleri (PDF/HTML/TXT) buraya koyun.")
        return

    store = get_store()
    total_chunks = 0

    for path in files:
        raw = load_file(path)
        if raw is None:
            print(f"⏭  Atlandı (desteklenmeyen tip): {path.name}")
            continue

        text = normalize(raw)
        chunks = chunk_text(text)
        records = [
            {"id": _chunk_id(path.name, i, c), "text": c, "document": path.name}
            for i, c in enumerate(chunks)
        ]
        added = store.add(records)
        total_chunks += added
        print(f"✓  {path.name}: {added} parça")

    print(f"\nBitti. Toplam {total_chunks} parça indekslendi. "
          f"Koleksiyondaki toplam parça: {store.count()}")


if __name__ == "__main__":
    ingest()
