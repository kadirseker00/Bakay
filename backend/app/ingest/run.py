"""İndeksleme komut satırı aracı (İP1 → İP3 köprüsü).

data/raw/ içindeki tüm belgeleri: yükle → temizle → parçala → embed → Chroma'ya
yazar. Çalıştırma:

    python -m app.ingest.run              # her şeyi (yeniden) indeksle
    python -m app.ingest.run --only-new   # koleksiyonda olmayan belgeleri indeksle
"""
from __future__ import annotations

import argparse
import hashlib

from app.config import ROOT
from app.ingest.chunk import chunk_text
from app.ingest.clean import normalize
from app.ingest.loaders import load_file
from app.ingest.titles import extract_document_title
from app.rag.vectorstore import get_store

RAW_DIR = ROOT / "data" / "raw"


def _chunk_id(document: str, idx: int, text: str) -> str:
    h = hashlib.md5(text.encode("utf-8")).hexdigest()[:8]
    return f"{document}::{idx}::{h}"


def ingest(only_new: bool = False) -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    files = [p for p in RAW_DIR.rglob("*") if p.is_file()]
    if not files:
        print(f"⚠  {RAW_DIR} boş. Belgeleri (PDF/HTML/TXT) buraya koyun.")
        return

    store = get_store()
    if only_new:
        indexed: set[str] = set()
        offset, page = 0, 5000
        while True:
            batch = store.collection.get(
                include=["metadatas"], limit=page, offset=offset
            )["metadatas"]
            if not batch:
                break
            indexed.update(m["document"] for m in batch)
            offset += page
        files = [p for p in files if p.name not in indexed]
        print(f"--only-new: {len(files)} yeni belge indekslenecek")
    total_chunks = 0

    for path in files:
        raw = load_file(path)
        if raw is None:
            print(f"⏭  Atlandı (desteklenmeyen tip): {path.name}")
            continue

        text = normalize(raw)
        chunks = chunk_text(text)
        title = extract_document_title(path)
        records = [
            {
                "id": _chunk_id(path.name, i, c),
                "text": c,
                "document": path.name,
                "meta": {"title": title},
            }
            for i, c in enumerate(chunks)
        ]
        added = store.add(records)
        total_chunks += added
        print(f"✓  {path.name}: {added} parça")

    print(f"\nBitti. Toplam {total_chunks} parça indekslendi. "
          f"Koleksiyondaki toplam parça: {store.count()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="data/raw → Chroma indeksleme")
    parser.add_argument(
        "--only-new",
        action="store_true",
        help="Koleksiyonda hiç parçası olmayan belgeleri indeksle (hızlı artımlı mod)",
    )
    args = parser.parse_args()
    ingest(only_new=args.only_new)
