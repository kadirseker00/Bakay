"""Paragraf bazlı parçalama (İP1).

Form, içeriğin "paragraf düzeyinde bölünmesini" istiyor. Çok kısa paragrafları
bir sonrakiyle birleştirip, çok uzun paragrafları üst sınıra göre bölerek
embedding için dengeli parçalar üretiriz.
"""
from __future__ import annotations

from app.ingest.clean import is_noise

MAX_CHARS = 1000   # bir parçanın üst sınırı
MIN_CHARS = 200    # bundan kısa parçalar bir sonrakiyle birleştirilir


def split_paragraphs(text: str) -> list[str]:
    raw = [p.strip() for p in text.split("\n\n") if p.strip()]
    return [p for p in raw if not is_noise(p)]


def chunk_text(text: str) -> list[str]:
    """Metni dengeli paragraf parçalarına böler."""
    paragraphs = split_paragraphs(text)
    chunks: list[str] = []
    buffer = ""

    for para in paragraphs:
        if len(para) > MAX_CHARS:
            # Uzun paragrafı cümle sınırlarına yakın parçalara böl
            if buffer:
                chunks.append(buffer)
                buffer = ""
            for i in range(0, len(para), MAX_CHARS):
                chunks.append(para[i : i + MAX_CHARS])
            continue

        if not buffer:
            buffer = para
        elif len(buffer) + len(para) + 1 <= MAX_CHARS:
            buffer += "\n" + para
        else:
            chunks.append(buffer)
            buffer = para

    if buffer:
        chunks.append(buffer)

    # Çok kısa kalan son parçaları bir öncekiyle birleştir
    merged: list[str] = []
    for c in chunks:
        if merged and len(c) < MIN_CHARS:
            merged[-1] += "\n" + c
        else:
            merged.append(c)
    return merged
