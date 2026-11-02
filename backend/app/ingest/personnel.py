"""Resmî personel rehberini kişi/birim bazında toplar ve isteğe bağlı indeksler.

backend/ içinden: .venv/bin/python -m app.ingest.personnel [--index]
Yalnız rehber.manas.edu.kg; robots kontrolü ve saniyelik nazik tarama uygulanır.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import time
from urllib.parse import urljoin, urlsplit
from urllib.robotparser import RobotFileParser

from bs4 import BeautifulSoup
import requests

from app.config import ROOT

BASE = "https://rehber.manas.edu.kg/"
AGENT = "BAKAI-Research-Bot/0.1"
SOURCE_TYPE = "personnel_directory"
PARSE = re.compile(r"JSON\.parse\('((?:\\.|[^'\\])*)'\)")
FIELDS = {"title": "Unvan", "duty": "Görev", "email": "Kurumsal e-posta",
          "phone": "Telefon", "ext": "Dahili", "room": "Oda"}


def official(url: str) -> bool:
    parsed = urlsplit(url)
    return (parsed.scheme == "https" and parsed.netloc == "rehber.manas.edu.kg"
            and not parsed.query and not parsed.fragment)


def parse_people(content: str, url: str, fetched_at: str) -> list[dict]:
    """Sayfanın gösterdiği kart verisini çözer; JavaScript çalıştırmaz."""
    if not official(url):
        raise ValueError("Resmî rehber adresi gerekli")
    soup = BeautifulSoup(content, "html.parser")
    main = soup.select_one("#directory-detail-main")
    if main is None or not main.find("h1"):
        raise ValueError("Personel sayfası yapısı tanınmadı")
    unit = main.find("h1").get_text(" ", strip=True)
    records = {}
    for card in main.find_all(attrs={"@click": True}):
        match = PARSE.search(card.get("@click", ""))
        if not match:
            continue
        try:
            literal = json.loads('"' + match[1].replace('"', '\\"') + '"')
            person = json.loads(literal)
        except (ValueError, TypeError):
            continue
        if not isinstance(person, dict) or not person.get("person_id") or not person.get("name"):
            continue
        heading = card.find_previous(["h1", "h2"])
        section = heading.get_text(" ", strip=True) if heading else unit
        identity = json.dumps([url, section, person["person_id"], person.get("duty", "")], ensure_ascii=False)
        digest = hashlib.sha256(identity.encode()).hexdigest()[:24]
        document = f"personnel_{digest}.txt"
        title = f"{person['name']} — {section} — KTMÜ Personel Rehberi"
        lines = [f"Ad soyad: {person['name']}", f"Birim: {unit}", f"Alt birim: {section}"]
        for key, label in FIELDS.items():
            value = str(person.get(key) or "").strip()
            if value:
                lines.append(f"{label}: {value}")
        lines += [f"Kaynak: {url}", f"Kaynağın kontrol tarihi: {fetched_at}"]
        records[document] = {"id": document + "::0::personnel", "document": document,
                             "text": "\n".join(lines),
                             "meta": {"title": title, "source_type": SOURCE_TYPE,
                                      "source_url": url, "fetched_at": fetched_at}}
    if not records:
        raise ValueError(f"Personel kartı bulunamadı: {url}")
    return list(records.values())


def collect(delay: float = 1.0) -> list[dict]:
    session = requests.Session()
    session.headers.update({"User-Agent": AGENT})
    robots = session.get(urljoin(BASE, "robots.txt"), timeout=25)
    robots.raise_for_status()
    rules = RobotFileParser(); rules.parse(robots.text.splitlines())
    if not rules.can_fetch(AGENT, BASE):
        raise ValueError("robots.txt taramaya izin vermiyor")
    response = session.get(BASE, timeout=25); response.raise_for_status()
    urls = sorted({urljoin(BASE, a["href"]) for a in BeautifulSoup(response.text, "html.parser").select("a[href]")
                   if official(urljoin(BASE, a["href"])) and urlsplit(urljoin(BASE, a["href"])).path not in ("", "/")})
    if not urls:
        raise ValueError("Birim bağlantısı bulunamadı")
    fetched_at = datetime.now(timezone.utc).date().isoformat()
    records = []
    for url in urls:
        if not rules.can_fetch(AGENT, url):
            raise ValueError(f"robots.txt izin vermiyor: {url}")
        time.sleep(max(1.0, delay))
        page = session.get(url, timeout=30); page.raise_for_status()
        if not official(page.url):
            raise ValueError("Beklenmeyen yönlendirme")
        people = parse_people(page.text, url, fetched_at)
        records.extend(people)
        print(f"{url}: {len(people)} kişi/görev kaydı", flush=True)
    return records


def export(records: list[dict], root: Path = ROOT) -> None:
    """Tam tarama başarıyla tamamlanınca ham belgeleri ve kaynak haritasını yazar."""
    directory = root / "data/processed/personnel"
    directory.mkdir(parents=True, exist_ok=True)
    for record in records:
        (directory / record["document"]).write_text(record["text"], encoding="utf-8")
    data = {"seed": BASE, "pages": [{"file": r["document"], "url": r["meta"]["source_url"]} for r in records]}
    (root / "data/processed/personnel-records.json").write_text(
        json.dumps(records, ensure_ascii=False), encoding="utf-8")
    path = root / "data/sitemap-personnel.json"
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(path)


def index_records(records: list[dict], store) -> None:
    """Sabit kimlikle güncelle; eski görev kayıtlarını yalnız tam yeni kümeden sonra kaldır."""
    if not records:
        raise ValueError("Boş personel kümesi indekslenemez")
    previous = store.collection.get(where={"source_type": SOURCE_TYPE}, include=[])["ids"]
    for offset in range(0, len(records), 64):
        store.add(records[offset:offset + 64])
    obsolete = sorted(set(previous) - {r["id"] for r in records})
    if obsolete:
        store.collection.delete(ids=obsolete)
        store._lexical = None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", action="store_true")
    args = parser.parse_args()
    records = collect()
    export(records)
    if args.index:
        from app.rag.vectorstore import get_store
        index_records(records, get_store())
    print(f"Hazır: {len(records)} kişi/görev kaydı; indeksleme={args.index}")


if __name__ == "__main__":
    main()
