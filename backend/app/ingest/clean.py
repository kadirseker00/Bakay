"""Türkçe metin temizleme ve normalize (İP1).

Formdaki gereksinim: Unicode NFC normalize, tekrarlayan boşluk/satır temizliği,
menü/sayfa kalıntılarının atılması. spaCy + Zeyrek tabanlı kök analizi (stemming/
lemmatization) ileride buraya eklenecek; şu an embedding için yeterli olan hafif
temizliği uyguluyoruz (gömme modelleri ham metinle daha iyi çalışır).
"""
from __future__ import annotations

import re
import unicodedata


_BROKEN_TURKISH_WORD = re.compile(
    r"\b(?:t[ьЬ]rkiye|[ьЬ]niversite)[a-zçğıöşü]*\b", re.IGNORECASE
)
_SOFT_SIGN_REPAIR = str.maketrans({"ь": "ü", "Ь": "Ü"})


def repair_turkish_encoding(text: str) -> str:
    """Bilinen Türkçe kelimelerdeki Kiril ь/Ь bozulmasını giderir.

    Genel harf dönüşümü yapılmaz: Rusça/Kırgızca kaynaklarda bu harfler geçerlidir.
    Yalnız bozuk Türkiye/üniversite kökleri ve Türkçe ekleri düzeltilir.
    """
    return _BROKEN_TURKISH_WORD.sub(
        lambda match: match.group().translate(_SOFT_SIGN_REPAIR), text
    )


def normalize(text: str) -> str:
    """Unicode NFC normalize + boşluk düzeltme."""
    text = unicodedata.normalize("NFC", text)
    text = repair_turkish_encoding(text)
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
