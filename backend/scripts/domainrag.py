"""Türkçe DomainRAG taslağını üret, doğrula, erişimi ölç ve model girdisi hazırla."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import time

from evaluation.dataset import DEFAULT_DATA, Dataset, digest, read_json
from evaluation.domainrag import (DEFAULT_BUNDLE, build_bundle, citation_ranks,
                                 fixed_prompt, resolve_query, retrieval_summary,
                                 review_markdown, validate_bundle)
from scripts.dataset import write_new


def jsonl(rows):
    return "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows)


def load(args):
    dataset = Dataset.model_validate(read_json(args.source_data / "dataset.json"))
    evidence = read_json(args.source_data / "evidence.json")
    if args.command == "build":
        return dataset, evidence
    rows = [json.loads(line) for line in (args.bundle / "cases.jsonl").read_text().splitlines() if line]
    corpus = [json.loads(line) for line in (args.bundle / "corpus.jsonl").read_text().splitlines() if line]
    manifest = read_json(args.bundle / "manifest.json")
    validate_bundle(rows, manifest, corpus, dataset, evidence, verify_raw=getattr(args, "verify_raw", False))
    return rows, manifest, corpus


def select(rows, ids):
    if not ids:
        return rows
    selected = {id_.strip() for id_ in ids.split(",")}
    unknown = selected - {row["id"] for row in rows}
    if unknown:
        raise ValueError(f"Bilinmeyen senaryo: {', '.join(sorted(unknown))}")
    return [row for row in rows if row["id"] in selected]


def retrieve(rows, manifest):
    from app.config import settings
    from app.rag.llm import get_llm
    from app.rag.vectorstore import get_store
    store, llm = get_store(), get_llm()
    results = []
    for row in rows:
        start = time.perf_counter()
        query = resolve_query(row, llm)
        hits = store.query(query, 10) if query else []
        result = {"id": row["id"], "task": row["metadata"]["task"],
                  "behavior": row["metadata"]["behavior"], "question": row["question"],
                  "resolved_query": query, "ranks": citation_ranks(row, hits),
                  "ms": round((time.perf_counter() - start) * 1000, 2),
                  "hits": [{key: hit[key] for key in ("id", "document", "title", "score")} for hit in hits]}
        results.append(result)
        print(row["id"], result["ranks"], flush=True)
    return {"mode": "live_retrieval", "label_status": manifest["label_status"],
            "bundle_sha256": digest(manifest), "embedding": settings.embedding_model,
            "collection": settings.collection_name, "indexed_chunks": store.count(),
            "summary": retrieval_summary(results),
            "by_task": {task: retrieval_summary([r for r in results if r["task"] == task])
                        for task in dict.fromkeys(r["task"] for r in results)},
            "rows": results,
            "limits": "Geliştirme alıntı erişimi; davranış/cevap doğruluğu veya bağımsız gold başarısı değildir. Sabit bağlam gürültüsü bu modda uygulanmaz."}


def prepare(rows, manifest, corpus):
    from app.config import settings
    from app.rag.llm import get_llm
    from app.rag.pipeline import SYSTEM_PROMPT
    from scripts.compare_models import digest as prompt_digest
    cases = []
    llm = get_llm()
    for row in rows:
        query, hits, prompt = fixed_prompt(row, corpus, llm)
        cases.append({"id": row["id"], "question": row["question"], "resolved_query": query,
                      "task": row["metadata"]["task"], "hits": hits, "prompt": prompt,
                      "prompt_sha256": prompt_digest(prompt), "behavior": row["metadata"]["behavior"]})
    return {"mode": "fixed_context_generation", "label_status": manifest["label_status"],
            "bundle_sha256": digest(manifest), "system_prompt_sha256": prompt_digest(SYSTEM_PROMPT),
            "model_for_history_resolution": settings.ollama_model if settings.llm_provider == "ollama" else settings.gemini_model,
            "cases": cases,
            "limits": "Seçilmiş kaynaklarla kontrollü generation deneyi; üretim retrieval ve yeterlilik kapısı ölçülmez. İnsan incelemesi beklenir."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("build")
    check = commands.add_parser("validate")
    check.add_argument("--verify-raw", action="store_true")
    review = commands.add_parser("review")
    review.add_argument("--output", type=Path, required=True)
    for command in ("retrieve", "prepare"):
        sub = commands.add_parser(command)
        sub.add_argument("--ids", help="Virgülle ayrılmış senaryo kimlikleri; yoksa tümü")
        sub.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command != "build" and getattr(args, "output", None) and args.output.exists():
            raise ValueError(f"Çıktı zaten var: {args.output}")
        loaded = load(args)
        if args.command == "build":
            rows, manifest, corpus = build_bundle(*loaded)
            validate_bundle(rows, manifest, corpus, *loaded)
            # Eski inceleme/veri paketi ezilmez. Ham belgeler indekse eklenmez.
            args.bundle.mkdir(parents=True, exist_ok=False)
            write_new(args.bundle / "cases.jsonl", jsonl(rows))
            write_new(args.bundle / "corpus.jsonl", jsonl(corpus))
            write_new(args.bundle / "manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
            print(json.dumps({"cases": len(rows), "tasks": manifest["tasks"], "bundle": str(args.bundle)}, ensure_ascii=False, indent=2))
        else:
            rows, manifest, corpus = loaded
            if args.command == "validate":
                print(json.dumps({"cases": len(rows), "tasks": manifest["tasks"],
                                  "label_status": manifest["label_status"], "raw_verified": args.verify_raw}, ensure_ascii=False, indent=2))
            elif args.command == "review":
                write_new(args.output, review_markdown(rows, manifest))
            else:
                rows = select(rows, args.ids)
                result = retrieve(rows, manifest) if args.command == "retrieve" else prepare(rows, manifest, corpus)
                write_new(args.output, json.dumps(result, ensure_ascii=False, indent=2) + "\n")
                print(json.dumps(result.get("summary", {"cases": len(rows)}), ensure_ascii=False))
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(1, f"HATA: {exc}\n")


if __name__ == "__main__":
    main()
