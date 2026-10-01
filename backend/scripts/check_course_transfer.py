"""Ders saydırma regresyonu ve mevcut geliştirme soruları için canlı erişim ölçümü.

Çalıştırma (backend/):
    .venv/bin/python -m scripts.check_course_transfer --benchmark --api-url http://127.0.0.1:8000

İndeksi değiştirmez. Alıntı eşleşmesi uzman onaylı yanıt doğruluğu değildir.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import statistics
import time

import httpx

from app.config import ROOT, settings
from app.rag.retrieval import text_key
from app.rag.vectorstore import get_store


COURSE_CASES = [
    ("başka kurumdan aldığım dersi saydırabilir miyim", "undergraduate"),
    ("Başka üniversiteden aldığım dersleri saydırabilir miyim?", "undergraduate"),
    ("Eski üniversitemde geçtiğim dersleri burada saydırabilir miyim?", "undergraduate"),
    ("Önceki okulda geçtiğim derslerden muaf olabilir miyim?", "undergraduate"),
    ("Lisansta daha önce aldığım dersleri saydırmanın şartları neler?", "undergraduate"),
    ("Önlisans öğrencisiyim, başka kurumda aldığım dersleri saydırabilir miyim?", "undergraduate"),
    ("Yüksek lisans ders saydırma koşulları nelerdir?", "graduate"),
    ("Doktorada başka üniversiteden aldığım dersleri saydırabilir miyim?", "graduate"),
]


def article_rank(hits, level):
    for rank, hit in enumerate(hits, 1):
        text = text_key(hit["text"])
        if level == "undergraduate":
            found = "Ders Saydırma, Ders Muafiyeti ve İntibak" in text and "Madde 25" in text
        else:
            found = "Ders Saydırma, Kredi Aktarma ve Ders Muafiyeti" in text or (
                "LİSANSÜSTÜ" in hit["title"] and "başarı notunun" in text and "CB" in text
            )
        if found:
            return rank
    return None


def citation_found(citation, hits, sources, units):
    quote = text_key(citation["quote"])
    width = min(80, len(quote))
    anchors = [quote[start:start + width] for start in range(0, len(quote) - width + 1, 20)]
    anchors.append(quote[-width:])
    document = Path(sources[units[citation["evidence_id"]]["source_id"]]["path"]).name
    return any((len(quote) >= 80 or hit["document"] == document)
               and any(anchor in text_key(hit["text"]) for anchor in anchors) for hit in hits)


def summarize(rows):
    return {"n": len(rows), "hit_at_5": sum(any(row["found"]) for row in rows),
            "all_citations_at_5": sum(all(row["found"]) for row in rows),
            "citation_recall_at_5": statistics.mean(
                sum(row["found"]) / len(row["found"]) for row in rows),
            "p50_ms": statistics.median(row["ms"] for row in rows)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmark", action="store_true")
    parser.add_argument("--api-url")
    parser.add_argument("--output", type=Path, default=ROOT / "docs/course-transfer-retrieval.json")
    args = parser.parse_args()
    store = get_store()
    report = {"created_at": datetime.now(timezone.utc).isoformat(), "embedding": settings.embedding_model,
              "collection": settings.collection_name, "indexed_chunks": store.count(),
              "label_status": "Geliştirme verisi; uzman onaylı bağımsız test değildir.", "course_cases": []}
    for question, level in COURSE_CASES:
        dense = store.query_dense(question, 10)
        start = time.perf_counter()
        hybrid = store.query(question, 10)
        ms = (time.perf_counter() - start) * 1000
        row = {"question": question, "expected_level": level, "dense_rank_at_10": article_rank(dense, level),
               "hybrid_rank_at_10": article_rank(hybrid, level), "hybrid_ms": ms,
               "hits": hybrid[:5]}
        report["course_cases"].append(row)
        print(question, "dense", row["dense_rank_at_10"], "hybrid", row["hybrid_rank_at_10"], flush=True)
    if args.benchmark:
        dataset_path = ROOT / "data/eval/v1/dataset.json"
        evidence_path = ROOT / "data/eval/v1/evidence.json"
        dataset = json.loads(dataset_path.read_text())
        evidence = json.loads(evidence_path.read_text())
        sources = {source["id"]: source for source in evidence["sources"]}
        units = {unit["id"]: unit for unit in evidence["units"]}
        results = {"dense": [], "hybrid": []}
        for case in dataset["cases"]:
            if case["behavior"] != "answer":
                continue
            for i, question in enumerate([case["question"], *case["paraphrases"]]):
                for name, search in [("dense", store.query_dense), ("hybrid", store.query)]:
                    start = time.perf_counter()
                    hits = search(question, 5)
                    ms = (time.perf_counter() - start) * 1000
                    found = [citation_found(citation, hits, sources, units) for citation in case["citations"]]
                    results[name].append({"id": f"{case['id']}-p{i}", "question": question,
                                          "found": found, "ms": ms,
                                          "hits": [{key: hit[key] for key in ("id", "document", "title", "score")}
                                                   for hit in hits]})
            print("Ölçüm", case["id"], flush=True)
        report["benchmark"] = {name: summarize(rows) for name, rows in results.items()}
        report["benchmark_rows"] = results
        report["dataset_sha256"] = hashlib.sha256(dataset_path.read_bytes()).hexdigest()
        report["evidence_sha256"] = hashlib.sha256(evidence_path.read_bytes()).hexdigest()
        print(report["benchmark"], flush=True)
    if args.api_url:
        report["api_cases"] = []
        for question, _ in [COURSE_CASES[i] for i in (0, 1, 4, 6)]:
            response = httpx.post(args.api_url.rstrip("/") + "/chat", json={"question": question}, timeout=180)
            response.raise_for_status()
            result = response.json()
            report["api_cases"].append({"question": question, **result})
            print("API", question, result["answer"], flush=True)
        initial = report["api_cases"][0]
        followup = "Lisans için soruyorum."
        response = httpx.post(args.api_url.rstrip("/") + "/chat", json={
            "question": followup,
            "history": [{"role": "user", "content": initial["question"]},
                        {"role": "assistant", "content": initial["answer"]}],
        }, timeout=180)
        response.raise_for_status()
        report["api_followup"] = {"question": followup, **response.json()}
        print("API takip", followup, report["api_followup"]["answer"], flush=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    failed = [case for case in report["course_cases"]
              if case["hybrid_rank_at_10"] is None or case["hybrid_rank_at_10"] > 5]
    if failed:
        raise SystemExit(f"İlk 5'te hedef madde bulunamayan {len(failed)} ders saydırma sorusu var.")


if __name__ == "__main__":
    main()
