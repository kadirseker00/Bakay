"""Kullanıcıya sunulan kaynaklar için ortak yanıt yeterliliği ve belge sınırı."""
import re

MAX_ANSWER_SOURCES = 3
NO_ANSWER_MARKER = '[YANIT_YOK]'
NO_ANSWER = 'Bu konuda elimdeki belgelerde bilgi bulamadım.'


def lacks_answer(text: str) -> bool:
    """Açık yanıtsızlık beyanını yakala; sondaki kısmi bilgi uyarısını ayır."""
    if not text.strip() or NO_ANSWER_MARKER in text:
        return True
    # Eski modeller işareti kullanmayabilir. İlk paragraftaki açık çekilme
    # beyanı kaynak kartı/bağlantısıyla desteklenmiş cevap gibi sunulmamalı.
    opening = text.split('\n\n', 1)[0].lower().replace('ı', 'i')
    opening = re.sub(r'[*_`]', '', opening)
    return bool(re.search(
        r'\bbilgi\s+(?:bulamadim|bulunamadi|bulunmuyor|bulunmamaktadir|yok(?:tur)?)\b'
        r'|\b(?:yeterli|doğrudan|açik|kesin)\s+bilgi\s+(?:mevcut\s+)?değil'
        r'|\b(?:yanit|cevap)\s+(?:bulamadim|veremiyorum|veremem)\b'
        r'|\bbilgi\s+(?:yer almiyor|yer almamaktadir|mevcut değil)\b'
        r'|\bbilmiyorum\b', opening,
    ))


def answer_hits(text: str, hits: list[dict]) -> list[dict]:
    """Anılan belgeleri öncele; aynı belgenin parçalarını tek kartta göster."""
    if lacks_answer(text):
        return []
    mentioned, other = [], []
    folded = text.casefold()
    for hit in hits:
        title = hit.get('title') or ''
        (mentioned if title and title.casefold() in folded else other).append(hit)
    selected, seen = [], set()
    for hit in (mentioned or other):
        document = hit['document']
        if document in seen:
            continue
        seen.add(document)
        selected.append(hit)
        if len(selected) == MAX_ANSWER_SOURCES:
            break
    return selected
