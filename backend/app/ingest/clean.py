"""Türkçe metin temizleme ve normalize (İP1).

Formdaki gereksinim: Unicode NFC normalize, tekrarlayan boşluk/satır temizliği,
menü/sayfa kalıntılarının atılması. spaCy + Zeyrek tabanlı kök analizi (stemming/
lemmatization) ileride buraya eklenecek; şu an embedding için yeterli olan hafif
temizliği uyguluyoruz (gömme modelleri ham metinle daha iyi çalışır).
"""
from __future__ import annotations

import re
import unicodedata


def normalize(text: str) -> str:
    """Unicode NFC normalize + boşluk düzeltme."""
    text = unicodedata.normalize("NFC", text)
    # Windows satır sonlarını sadeleştir
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # 3+ ardışık boş satırı tek boş satıra indir
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Satır içi tekrarlayan boşlukları tek boşluğa indir
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


def is_noise(paragraph: str) -> bool:
    """Anlamsız/kısa parçaları (menü, sayfa no, başlık kalıntısı) eler."""
    p = paragraph.strip()
    if len(p) < 40:  # çok kısa — muhtemelen başlık/menü
        return True
    # Çoğunlukla rakam/sembol ise (sayfa numarası, tablo kalıntısı)
    letters = sum(c.isalpha() for c in p)
    return letters < len(p) * 0.5
