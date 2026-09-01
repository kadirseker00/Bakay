"""Mevcut Chroma kayıtlarına okunabilir belge başlığı ekler.

Embedding'lere ve doküman metnine dokunmaz; yalnızca metadata içindeki ``title``
alanını günceller. ``backend/`` içinden çalıştırılır:

    python -m scripts.backfill_document_titles --dry-run
    python -m scripts.backfill_document_titles
"""
from __future__ import annotations

import argparse
from pathlib import Path

import chromadb

from app.config import ROOT, settings
from app.ingest.titles import extract_document_title, title_from_filename

RAW_DIR = ROOT / "data" / "raw"
BATCH_SIZE = 1_000


def _raw_file_index() -> dict[str, Path]:
    files: dict[str, Path] = {}
    for path in RAW_DIR.rglob("*"):
        if path.is_file():
            files.setdefault(path.name, path)
    return files


def backfill(*, dry_run: bool = False, force: bool = False) -> None:
    client = chromadb.PersistentClient(path=str(settings.chroma_path))
    collection = client.get_collection(settings.collection_name)
    raw_files = _raw_file_index()
    title_cache: dict[str, str] = {}
    missing_documents: set[str] = set()
    updated_chunks = 0
    skipped_chunks = 0

    total = collection.count()
    for offset in range(0, total, BATCH_SIZE):
        page = collection.get(
            limit=BATCH_SIZE,
            offset=offset,
            include=["metadatas"],
        )
        update_ids: list[str] = []
        update_metadatas: list[dict] = []

        for chunk_id, raw_metadata in zip(page["ids"], page["metadatas"]):
            metadata = dict(raw_metadata or {})
            if metadata.get("title") and not force:
                skipped_chunks += 1
                continue

            document = str(metadata.get("document") or "")
            if document not in title_cache:
                source_path = raw_files.get(document)
                if source_path is None:
                    missing_documents.add(document)
                    title_cache[document] = title_from_filename(document)
                else:
                    title_cache[document] = extract_document_title(source_path)

            metadata["title"] = title_cache[document]
            update_ids.append(chunk_id)
            update_metadatas.append(metadata)

        if update_ids and not dry_run:
            collection.update(ids=update_ids, metadatas=update_metadatas)
        updated_chunks += len(update_ids)
        print(f"{min(offset + BATCH_SIZE, total):>6}/{total} parça tarandı")

    action = "güncellenecek" if dry_run else "güncellendi"
    print(
        f"\n{updated_chunks} parça {action}; {skipped_chunks} parçada başlık zaten vardı."
    )
    print(
        f"{len(title_cache)} belge başlığı çıkarıldı; "
        f"{len(missing_documents)} ham dosya bulunamadı."
    )
    for document, title in list(title_cache.items())[:10]:
        print(f"- {document} -> {title}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Mevcut Chroma kayıtlarına belge başlığı ekle"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Veritabanına yazmadan önizle"
    )
    parser.add_argument(
        "--force", action="store_true", help="Var olan başlıkları da yeniden çıkar"
    )
    args = parser.parse_args()
    backfill(dry_run=args.dry_run, force=args.force)
