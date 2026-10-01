"""Türkçe kelime araması, kopya birleştirme ve hibrit sıralama.

Önek eşleşmesi morfolojik çözümleme değildir; ek almış kelimeler için ek bir
erişim kanalıdır. Yanıt içeriği veya belirli sorulara özel belge listesi içermez.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import math
import re
import unicodedata

import numpy as np

from app.ingest.titles import title_from_filename


STOP_WORDS = frozenset(
    "ve veya bir bu şu o mı mi mu mü miyim mıyım muyum müyüm ne nasıl için ile "
    "de da en olarak olabilir neler nelerdir koşulları şartları".split()
)


def words(text: str) -> list[str]:
    text = unicodedata.normalize("NFC", text).replace("İ", "i").replace("I", "ı").lower()
    return re.findall(r"\w+", text)


def terms(text: str) -> list[str]:
    tokens = [word for word in words(text) if word not in STOP_WORDS]
    prefixes = [
        f"@{word[:width]}" for word in tokens for width in (4, 6) if len(word) > width
    ]
    # "Dersi saydırabilir" ile "ders saydırma" gibi terim birliklerini koru.
    phrases = [f"#{left[:4]}:{right[:4]}" for left, right in zip(tokens, tokens[1:])
               if len(left) >= 4 and len(right) >= 4]
    return tokens + prefixes + phrases


def text_key(text: str) -> str:
    # PDF madde numaraları ve not eşikleri korunur; yalnız boşluklar eşitlenir.
    return " ".join(unicodedata.normalize("NFC", text).split())


def education_level(text: str) -> str | None:
    text = " ".join(words(text))
    if re.search(r"\b(yüksek lisans\w*|lisansüst\w*|doktora\w*)", text):
        return "graduate"
    if re.search(r"\b(önlisans\w*|ön lisans\w*|lisans\w*)", text):
        return "undergraduate"
    return None


def needs_education_level(question: str, hits: list[dict]) -> bool:
    """Aynı terim birden çok düzeyde farklı kurallara bağlıysa kapsamı netleştir."""
    if education_level(question):
        return False
    phrases = {term for term in terms(question) if term.startswith("#")}
    scopes_by_phrase: dict[str, set[str]] = defaultdict(set)
    for hit in hits:
        level = education_level(hit["title"]) or education_level(hit["text"])
        if not level:
            continue
        for phrase in phrases.intersection(terms(hit.get("context_text", hit["text"]))):
            scopes_by_phrase[phrase].add(level)
    return any(len(scopes) > 1 for scopes in scopes_by_phrase.values())


class LexicalIndex:
    """Koleksiyon metninden oluşturulan, bellekte tutulan BM25 indeksi."""

    def __init__(self, records: list[dict]):
        self.by_id: dict[str, dict] = {}
        self.by_position: dict[tuple[str, int], dict] = {}
        canonical: dict[str, dict] = {}
        for record in sorted(records, key=lambda r: r["id"]):
            record = dict(record)
            record["title"] = record.get("title") or title_from_filename(record["document"])
            self.by_id[record["id"]] = record
            parts = record["id"].rsplit("::", 2)
            if len(parts) == 3 and parts[1].isdigit():
                self.by_position[(record["document"], int(parts[1]))] = record
            key = text_key(record["text"])
            previous = canonical.get(key)
            # Mevzuat derlemesiyle aynı metinse ilgili bağımsız belgeyi göster.
            if previous is None or (
                previous["title"] == "KTMÜ Mevzuatı" and record["title"] != "KTMÜ Mevzuatı"
            ):
                canonical[key] = record
        self.aliases = {
            id_: canonical[text_key(record["text"])]["id"]
            for id_, record in self.by_id.items()
        }
        self.records = sorted(canonical.values(), key=lambda r: r["id"])
        self.by_id = {record["id"]: record for record in self.records}
        self.levels = {record["id"]: education_level(record["title"]) for record in self.records}

        postings = defaultdict(list)
        lengths = []
        for index, record in enumerate(self.records):
            frequencies = Counter(terms(record["text"]))
            lengths.append(sum(frequencies.values()))
            for term, frequency in frequencies.items():
                postings[term].append((index, frequency))
        count = len(self.records)
        self.size = count
        lengths = np.asarray(lengths, dtype=float)
        average = max(1.0, float(lengths.mean())) if count else 1.0
        norm = 1.5 * (0.25 + 0.75 * lengths / average)
        self.postings = {}
        for term, posting in postings.items():
            values = np.asarray(posting)
            indices, frequencies = values[:, 0], values[:, 1]
            idf = math.log(1 + (count - len(posting) + 0.5) / (len(posting) + 0.5))
            weights = idf * frequencies * 2.5 / (frequencies + norm[indices])
            self.postings[term] = (indices, weights)

    def context_for(self, id_: str) -> str:
        """En ilgili parçanın kesilmiş başlangıç/sonunu komşu parçalarla tamamlar."""
        record = self.by_id[id_]
        parts = id_.rsplit("::", 2)
        if len(parts) != 3 or not parts[1].isdigit():
            return record["text"]
        position = int(parts[1])
        text = record["text"].strip()
        pieces = [record]
        if text and text[0].islower():
            previous = self.by_position.get((record["document"], position - 1))
            if previous:
                pieces.insert(0, previous)
        if text and text[-1].isalpha():
            following = self.by_position.get((record["document"], position + 1))
            if following:
                pieces.append(following)
        result = pieces[0]["text"]
        for previous, following in zip(pieces, pieces[1:]):
            # Eski 1000 karakterlik parçalama kelimenin ortasında kesebiliyor.
            separator = "" if len(previous["text"]) == 1000 else "\n"
            result += separator + following["text"]
        return result

    def query(self, question: str, limit: int) -> list[str]:
        scores = np.zeros(self.size)
        for term in set(terms(question)):
            if term in self.postings:
                indices, weights = self.postings[term]
                scores[indices] += weights
        indices = np.argsort(-scores, kind="stable")[:limit]
        return [self.records[i]["id"] for i in indices if scores[i] > 0]

    def fuse(self, question: str, dense: list[str], lexical: list[str], limit: int) -> list[str]:
        """Tekilleştirilmiş sıralamaları RRF ile birleştirir; skor kosinüs değildir."""
        scores: dict[str, float] = defaultdict(float)
        for ranking, weight in ((dense, 1.0), (lexical, 1.25)):
            unique = dict.fromkeys(self.aliases[id_] for id_ in ranking if id_ in self.aliases)
            for rank, id_ in enumerate(unique, 1):
                scores[id_] += weight / (10 + rank)
        level = education_level(question)
        if level:
            for id_ in scores:
                candidate_level = self.levels[id_]
                if candidate_level:
                    scores[id_] *= 1.25 if candidate_level == level else 0.5
        return sorted(scores, key=lambda id_: (-scores[id_], id_))[:limit]
