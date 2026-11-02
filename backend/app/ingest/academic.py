"""Kurumdan alınan AXSİS JSON dışa aktarımını doğrular ve yerel indekse alır.

Web taraması veya oturum/CAPTCHA işlemi yapmaz. Şema personnel.md içindedir.
backend/ içinden: .venv/bin/python -m app.ingest.academic DOSYA [--index]
"""
from __future__ import annotations

import argparse
from datetime import date
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

from app.config import ROOT

BASE = "https://publications.manas.edu.kg"


def source_url(value: str, kind: str) -> str:
    """Yalnız kimlik taşıyan resmî profil/yayın adreslerini kabul et."""
    parsed = urlsplit(value)
    pattern = r"/arastirmaci/[\w-]+" if kind == "profile" else r"/yayin/[0-9]+"
    if (parsed.scheme != "https" or parsed.netloc != "publications.manas.edu.kg"
            or parsed.query or parsed.fragment or not re.fullmatch(pattern, parsed.path)):
        raise ValueError(f"Geçersiz AXSİS {kind} adresi: {value}")
    return value


def field(row: dict, key: str, *, required: bool = False) -> str:
    value = row.get(key, "")
    if not isinstance(value, str) or len(value) > 4000:
        raise ValueError(f"Metin alanı gerekli: {key}")
    value = " ".join(value.split())
    if required and not value:
        raise ValueError(f"Eksik alan: {key}")
    return value


def record(url: str, title: str, lines: list[str], checked_at: str, kind: str) -> dict:
    document = "academic_" + hashlib.sha256(url.encode()).hexdigest()[:24] + ".txt"
    return {"id": document + "::0::academic", "document": document,
            "text": "\n".join([*lines, f"Kaynak: {url}", f"Kaynağın kontrol tarihi: {checked_at}"]),
            "meta": {"title": title, "source_type": "academic_" + kind,
                     "source_url": url, "fetched_at": checked_at}}


def prepare(payload: dict) -> list[dict]:
    """Tamlık ve kimlikleri kontrol et; yayınları kaynak adresiyle tekilleştir."""
    if not isinstance(payload, dict) or payload.get("schema_version") != 1:
        raise ValueError("schema_version=1 içeren JSON nesnesi gerekli")
    checked_at = field(payload, "fetched_at", required=True)
    date.fromisoformat(checked_at)
    people = payload.get("researchers")
    expected = payload.get("expected_researchers")
    if (payload.get("complete") is not True or type(expected) is not int
            or not isinstance(people, list) or not people or expected != len(people)):
        raise ValueError("Tam araştırmacı kümesi ve eşleşen expected_researchers sayısı gerekli")
    profiles, publications = {}, {}
    for person in people:
        if not isinstance(person, dict):
            raise ValueError("Araştırmacı nesnesi gerekli")
        url = source_url(field(person, "url", required=True), "profile")
        if url in profiles:
            raise ValueError(f"Tekrarlanan araştırmacı adresi: {url}")
        name = field(person, "name", required=True)
        lines = [f"Ad soyad: {name}"]
        for key, label in (("title", "Unvan"), ("faculty", "Fakülte/birim"),
                           ("department", "Bölüm"), ("email", "Kurumsal e-posta"),
                           ("orcid", "ORCID"), ("variants", "Ad varyantları")):
            value = field(person, key)
            if key == "email" and value and not value.lower().endswith("@manas.edu.kg"):
                raise ValueError("Yalnız kurumsal e-posta adresi kabul edilir")
            if key == "orcid" and value and not re.fullmatch(r"\d{4}-\d{4}-\d{4}-\d{3}[\dX]", value):
                raise ValueError("ORCID kimliği bekleniyor")
            if value:
                lines.append(f"{label}: {value}")
        works = person.get("publications")
        if not isinstance(works, list):
            raise ValueError("Her araştırmacı için publications listesi gerekli (boş olabilir)")
        lines.append(f"Bu dışa aktarımda ilişkilendirilen yayın kaydı: {len(works)}. Toplam kariyer yayını değildir.")
        profiles[url] = record(url, f"{name} — AXSİS Akademik Profil", lines, checked_at, "profile")
        seen = set()
        for work in works:
            if not isinstance(work, dict):
                raise ValueError("Yayın nesnesi gerekli")
            work_url = source_url(field(work, "url", required=True), "publication")
            if work_url in seen:
                raise ValueError("Aynı araştırmacıda tekrarlanan yayın")
            seen.add(work_url)
            values = {key: field(work, key, required=key == "title") for key in ("title", "year", "journal", "doi")}
            if values["year"] and not re.fullmatch(r"\d{4}", values["year"]):
                raise ValueError("Yayın yılı dört basamak olmalı")
            if work_url in publications:
                if publications[work_url]["values"] != values:
                    raise ValueError(f"Aynı yayın için çelişen künye: {work_url}")
                publications[work_url]["authors"].append(name)
            else:
                publications[work_url] = {"values": values, "authors": [name]}
    records = list(profiles.values())
    for url, work in publications.items():
        values = work["values"]
        lines = [f"Yayın: {values['title']}", "AXSİS'te ilişkilendirilen araştırmacılar: " + "; ".join(sorted(set(work["authors"])))]
        for key, label in (("year", "Yıl"), ("journal", "Dergi/kaynak"), ("doi", "DOI")):
            if values[key]:
                lines.append(f"{label}: {values[key]}")
        records.append(record(url, values["title"] + " — AXSİS", lines, checked_at, "publication"))
    return records


def export(records: list[dict], root: Path = ROOT) -> None:
    directory = root / "data/processed/academic"
    directory.mkdir(parents=True, exist_ok=True)
    for item in records:
        (directory / item["document"]).write_text(item["text"], encoding="utf-8")
    for path, data in (
        (root / "data/processed/academic-records.json", records),
        (root / "data/sitemap-academic.json", {"seed": BASE, "pages": [
            {"file": r["document"], "url": r["meta"]["source_url"]} for r in records]}),
    ):
        temp = path.with_suffix(".json.tmp")
        temp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        temp.replace(path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--index", action="store_true")
    args = parser.parse_args()
    records = prepare(json.loads(args.input.read_text(encoding="utf-8-sig")))
    export(records)
    if args.index:
        from app.rag.vectorstore import get_store
        store = get_store()
        for offset in range(0, len(records), 64):
            store.add(records[offset:offset + 64])
    print(f"Hazır: {len(records)} profil/yayın belgesi; indeksleme={args.index}")


if __name__ == "__main__":
    main()
