"""Kaynak bağlı taslakları doğrular; insan incelemesi olmadan gold dışa aktarmaz."""
from __future__ import annotations

import hashlib
import json
import unicodedata
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, model_validator

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA = ROOT / "data/eval/v1"


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(",", ":")).encode()).hexdigest()


def normalize(text: str) -> str:
    return " ".join(unicodedata.normalize("NFC", text).split())


def question_key(text: str) -> str:
    text = normalize(text).translate(str.maketrans("Iİ", "ıi")).lower()
    return "".join(c for c in text if c.isalnum())


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class Record(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Citation(Record):
    evidence_id: str = Field(min_length=1)
    section: str = Field(min_length=1)
    quote: str = Field(min_length=15)


class Review(Record):
    reviewer_id: str = Field(min_length=3)
    kind: Literal["human", "ai"]
    decision: Literal["approve", "revise", "reject"]
    reviewed_at: AwareDatetime
    content_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    source_version_checked: bool
    note: str = Field(min_length=1)


class Case(Record):
    id: str = Field(pattern=r"^BAKAY-\d{3}$")
    question: str = Field(min_length=10)
    paraphrases: list[str] = Field(min_length=1)
    answer: str = Field(min_length=15)
    required_points: list[str] = Field(min_length=1)
    forbidden_claims: list[str] = Field(min_length=1)
    citations: list[Citation]
    behavior: Literal["answer", "clarify", "abstain"]
    category: str = Field(min_length=1)
    scope: str = Field(min_length=1)
    group_ids: list[str] = Field(min_length=1)
    split: Literal["unassigned", "train", "dev", "test"] = "unassigned"
    exposure: Literal["development_exposed", "private_holdout"] = "development_exposed"
    author: Literal["codex_draft", "human"] = "codex_draft"
    status: Literal["pending_review", "approved", "rejected"] = "pending_review"
    review_notes: str = Field(default="Kaynak sürümü, kapsam ve cevap iki uzman tarafından doğrulanmalı.", min_length=1)
    reviews: list[Review] = Field(default_factory=list)

    @model_validator(mode="after")
    def check_case(self):
        if not self.citations and not (self.behavior == "abstain" and self.category == "out_of_scope"):
            raise ValueError("Kurum sorusuna kaynak dayanağı gerekir.")
        if self.split == "test" and self.exposure != "private_holdout":
            raise ValueError("Geliştirmede görülen soru bağımsız test olamaz.")
        for values in [self.group_ids, self.required_points, self.forbidden_claims, self.paraphrases]:
            if any(not normalize(v) for v in values) or len(values) != len(set(values)):
                raise ValueError("Liste alanları boş veya yinelenen öğe içeremez.")
        return self


class Dataset(Record):
    schema_version: Literal[1]
    title: str
    created_on: date
    truth_scope: Literal["archived_source_snapshot_not_current_policy"]
    language: Literal["tr"]
    evidence_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    cases: list[Case] = Field(min_length=1)


def content_hash(case: Case, evidence_hash: str) -> str:
    # Cevap, kaynak, grup veya bölüm değişince eski onay geçersizleşir.
    return digest({"case": case.model_dump(exclude={"reviews", "status"}),
                   "evidence_sha256": evidence_hash})


def human_approved(case: Case, evidence_hash: str) -> bool:
    expected = content_hash(case, evidence_hash)
    latest = {}
    for review in sorted(case.reviews, key=lambda r: r.reviewed_at):
        if review.kind == "human" and review.content_sha256 == expected:
            latest[normalize(review.reviewer_id).casefold()] = review
    return (len(latest) >= 2 and all(r.decision == "approve" and r.source_version_checked
                                   for r in latest.values()))


def extract_units(source: dict, root: Path = ROOT) -> dict[str, str]:
    path = (root / source["path"]).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("Kaynak yolu depo dışına çıkamaz.")
    if source["kind"] == "pdf":
        import fitz
        with fitz.open(path) as document:
            return {f"{source['id']}:p{page}": normalize(document[page - 1].get_text())
                    for page in source["pages"]}
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    element = soup.select_one(source["selector"])
    if element is None:
        raise ValueError(f"HTML bölümü bulunamadı: {source['id']}")
    return {f"{source['id']}:html": normalize(element.get_text(" ", strip=True))}


def snapshot(catalog: list[dict], root: Path = ROOT) -> dict:
    sources, units = [], []
    for source in catalog:
        texts = extract_units(source, root)
        sources.append({**source, "sha256": hashlib.sha256((root / source["path"]).read_bytes()).hexdigest(),
                        "validity": "human_verification_pending"})
        for unit_id, text in texts.items():
            page = int(unit_id.rsplit(":p", 1)[1]) if source["kind"] == "pdf" else None
            units.append({"id": unit_id, "source_id": source["id"], "page": page,
                          "printed_page": page + source["printed_page_offset"] if page else None,
                          "text": text, "text_sha256": digest(text)})
    return {"schema_version": 1, "normalization": "Unicode NFC + whitespace collapse",
            "sources": sources, "units": units}


def validate(dataset: Dataset, evidence: dict, *, verify_raw: bool = False, root: Path = ROOT) -> dict:
    dataset = Dataset.model_validate(dataset.model_dump(mode="json"))
    errors = []
    if digest(evidence) != dataset.evidence_sha256:
        errors.append("Kaynak anlık görüntüsünün özeti değişmiş.")
    sources = {s["id"]: s for s in evidence["sources"]}
    units = {u["id"]: u for u in evidence["units"]}
    if len(sources) != len(evidence["sources"]) or len(units) != len(evidence["units"]):
        errors.append("Yinelenen kaynak veya dayanak kimliği.")
    raw_units = {}
    if verify_raw:
        for source in sources.values():
            try:
                extracted = extract_units(source, root)
                if hashlib.sha256((root / source["path"]).read_bytes()).hexdigest() != source["sha256"]:
                    errors.append(f"Ham belge değişmiş: {source['id']}")
                raw_units.update(extracted)
            except (OSError, ValueError, IndexError) as exc:
                errors.append(f"Ham belge doğrulanamadı: {source['id']}: {exc}")
    for unit in units.values():
        source = sources.get(unit["source_id"])
        if not source or digest(unit["text"]) != unit["text_sha256"]:
            errors.append(f"Dayanak özeti veya kaynağı hatalı: {unit['id']}")
        elif source["kind"] == "pdf" and (
            unit["page"] not in source["pages"] or
            unit["id"] != f"{source['id']}:p{unit['page']}" or
            unit["printed_page"] != unit["page"] + source["printed_page_offset"]
        ):
            errors.append(f"PDF sayfa konumu hatalı: {unit['id']}")
        if verify_raw and raw_units.get(unit["id"]) != unit["text"]:
            errors.append(f"Dayanak metni ham belgeyle uyuşmuyor: {unit['id']}")
    ids, questions, groups = set(), {}, {}
    for case in dataset.cases:
        if case.id in ids:
            errors.append(f"Yinelenen soru kimliği: {case.id}")
        ids.add(case.id)
        for question in [case.question, *case.paraphrases]:
            key = question_key(question)
            if not key or key in questions:
                errors.append(f"Yinelenen/boş soru: {case.id} / {questions.get(key, '')}")
            questions[key] = case.id
        for group in case.group_ids:
            if group in groups and groups[group] != case.split:
                errors.append(f"Bölümler arası kural ailesi sızıntısı: {group}")
            groups[group] = case.split
        for citation in case.citations:
            unit = units.get(citation.evidence_id)
            if not unit or normalize(citation.quote) not in unit["text"]:
                errors.append(f"Kaynakta bulunmayan alıntı: {case.id} / {citation.evidence_id}")
        if case.status == "approved" and not human_approved(case, dataset.evidence_sha256):
            errors.append(f"İki güncel insan onayı yok: {case.id}")
    if errors:
        raise ValueError("\n".join(errors))
    return {"cases": len(dataset.cases), "sources": len(sources), "evidence_units": len(units),
            "behaviors": dict(Counter(c.behavior for c in dataset.cases)),
            "statuses": dict(Counter(c.status for c in dataset.cases)),
            "splits": dict(Counter(c.split for c in dataset.cases)),
            "raw_verified": verify_raw, "evidence_sha256": dataset.evidence_sha256}


def export_rows(dataset: Dataset, evidence: dict, split: str, purpose: str) -> list[dict]:
    validate(dataset, evidence)
    if split not in {"train", "dev", "test"} or purpose not in {"evaluation", "lora"}:
        raise ValueError("Geçersiz dışa aktarma bölümü veya amacı.")
    if purpose == "lora" and split != "train":
        raise ValueError("LoRA yalnızca train bölümünü kullanabilir.")
    selected = [c for c in dataset.cases if c.split == split]
    if not selected:
        raise ValueError(f"{split} bölümü boş; dışa aktarılmadı.")
    if any(c.status != "approved" or not human_approved(c, dataset.evidence_sha256) for c in selected):
        raise ValueError("Seçilen bölümde uzman onayı bekleyen veya reddedilen sorular var.")
    sources = {s["id"]: s for s in evidence["sources"]}
    units = {u["id"]: u for u in evidence["units"]}
    rows = []
    for case in selected:
        row = case.model_dump(mode="json")
        row["content_sha256"] = content_hash(case, dataset.evidence_sha256)
        if purpose == "lora":
            context = "\n\n".join(
                f"{sources[units[c.evidence_id]['source_id']]['title']}, {c.section}: {c.quote}"
                for c in case.citations
            )
            row = {"id": case.id, "content_sha256": row["content_sha256"], "messages": [
                {"role": "system", "content": "Yalnızca verilen kaynaklara dayan. Eksik bilgide açıklama iste veya yanıt veremediğini belirt."},
                {"role": "user", "content": f"Kapsam: {case.scope}\nKaynak sürümü: arşiv kopyası, güncel yürürlük iddiası yok.\n\nKaynaklar:\n{context}\n\nSoru: {case.question}"},
                {"role": "assistant", "content": case.answer},
            ]}
            row["evidence_sha256"] = dataset.evidence_sha256
        rows.append(row)
    return rows


def review_markdown(dataset: Dataset, evidence: dict) -> str:
    validate(dataset, evidence)
    sources = {s["id"]: s for s in evidence["sources"]}
    units = {u["id"]: u for u in evidence["units"]}
    approved = sum(c.status == "approved" and human_approved(c, dataset.evidence_sha256) for c in dataset.cases)
    lines = [f"# BAKAY: {len(dataset.cases)} Soruluk Uzman İnceleme Paketi", "",
             f"İki uzman onaylı kayıt: {approved}/{len(dataset.cases)}. Onaysız kayıtlar **TASLAK, GOLD DEĞİL**.",
             "Kaynakların güncel yürürlüğü doğrulanmadı; bu paket arşiv kopyalarının incelemesidir.", "",
             "Bu dosya `python -m scripts.dataset review` ile üretilir. Asıl kayıt `data/eval/v1/dataset.json`.", "",
             "Her soru için iki farklı insan; kapsamı, kaynak sürümünü, cevabı ve olumsuz örnekleri kontrol etmelidir.",
             "Onay özeti aşağıdadır; cevap/kaynak değişirse eski onay geçersiz olur. İnceleme protokolü: [README](README.md).", ""]
    for case in dataset.cases:
        lines += [f"## {case.id}: {case.question}", "",
                  f"Davranış: `{case.behavior}` | Durum: `{case.status}` | Bölüm: `{case.split}`", "",
                  f"Kapsam: {case.scope}", "", f"Soru varyantı: {' / '.join(case.paraphrases)}", "",
                  f"**Taslak cevap:** {case.answer}", "", "**Beklenen noktalar:**", ""]
        lines += [f"- {p}" for p in case.required_points]
        lines += ["", "**Yanlış sayılacak iddialar:**", ""] + [f"- {p}" for p in case.forbidden_claims]
        lines += ["", "**Dayanaklar:**", ""]
        for citation in case.citations:
            unit = units[citation.evidence_id]
            source = sources[unit["source_id"]]
            location = f"PDF sayfa {unit['page']}, basılı sayfa {unit['printed_page']}" if unit["page"] else "HTML SSS"
            lines += [f"- [{source['title']}]({source['url']}), {location}, {citation.section}", "",
                      f"> {citation.quote}", ""]
        if not case.citations:
            lines += ["Kapsam dışı davranış örneği; kurum belgesine dayanan bir bilgi iddiası yok.", ""]
        lines += [f"İnceleme notu: {case.review_notes}", "",
                  f"Onaylanacak içerik SHA-256: `{content_hash(case, dataset.evidence_sha256)}`", ""]
    return "\n".join(lines).rstrip() + "\n"
