"""Aynı RAG bağlamıyla yerel modelleri karşılaştırır; uygulama ayarını değiştirmez.

backend/ içinden `python -m scripts.compare_models --help` ile kullanılır.
Kaynaklar bir kez sabitlenir. Kalite puanı otomatik tahmin edilmez; yanıtlar
ve dayanaklar inceleme için saklanır, süreler ayrı özetlenir.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import re
import statistics
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

from app.config import settings
from app.rag.pipeline import SYSTEM_PROMPT, _build_context, _label_source_references, _strip_reasoning


def digest(value: object) -> str:
    content = json.dumps(value, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(content).hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def prepare(args) -> None:
    from app.rag.vectorstore import get_store

    if args.output.exists():
        raise SystemExit(f"Sabit bağlam dosyası zaten var: {args.output}")
    questions = read_json(args.questions)
    ids = [row["id"] for row in questions]
    if not questions or len(ids) != len(set(ids)):
        raise SystemExit("Sorular boş olamaz ve kimlikleri benzersiz olmalıdır.")
    store = get_store()
    store.query("KTMÜ", top_k=1)
    cases = []
    for question in questions:
        start = time.perf_counter()
        hits = store.query(question["question"], top_k=settings.top_k)
        retrieval_ms = round((time.perf_counter() - start) * 1000, 2)
        prompt = SYSTEM_PROMPT.format(context=_build_context(hits), question=question["question"])
        cases.append({
            **question, "hits": hits, "prompt": prompt, "prompt_sha256": digest(prompt),
            "retrieval_ms": retrieval_ms,
            "production_gate_pass": bool(hits and hits[0]["score"] >= settings.score_threshold),
        })
        print(f"{question['id']} kaynaklar sabitlendi: {', '.join(dict.fromkeys(h['title'] for h in hits))}", flush=True)
    save_json(args.output, {
        "created_at": utc_now(), "questions_sha256": digest(questions),
        "embedding_model": settings.embedding_model, "collection": settings.collection_name,
        "indexed_chunks": store.count(), "top_k": settings.top_k,
        "score_threshold": settings.score_threshold, "system_prompt_sha256": digest(SYSTEM_PROMPT),
        "cases": cases,
    })


def generate(client: httpx.Client, model: str, prompt: str, options: dict) -> dict:
    start = time.perf_counter()
    response = client.post("/api/generate", json={
        "model": model, "prompt": prompt, "stream": False, "think": False,
        "keep_alive": "10m", "options": options,
    })
    response.raise_for_status()
    result = response.json()
    if result.get("error") or not result.get("done"):
        raise RuntimeError(result.get("error", "Ollama tamamlanmamış yanıt döndürdü."))
    return {**result, "wall_ms": round((time.perf_counter() - start) * 1000, 2)}


def run(args) -> None:
    snapshot = read_json(args.snapshot)
    snapshot_hash = digest(snapshot)
    for case in snapshot["cases"]:
        if digest(case["prompt"]) != case["prompt_sha256"]:
            raise SystemExit(f"Soru girdisi değiştirilmiş: {case['id']}")
    args.output.mkdir(parents=True, exist_ok=True)
    metadata_path = args.output / f"{args.label}.meta.json"
    answers_path = args.output / f"{args.label}.answers.jsonl"
    options = {
        "temperature": settings.ollama_temperature, "num_ctx": settings.ollama_num_ctx,
        "num_predict": settings.ollama_num_predict, "seed": 42,
    }
    with httpx.Client(base_url=settings.ollama_base_url.rstrip("/"), timeout=180) as client:
        tags_response = client.get("/api/tags")
        tags_response.raise_for_status()
        model = next((m for m in tags_response.json()["models"] if m["name"] == args.model), None)
        if not model:
            raise SystemExit(f"Model yüklü değil: {args.model}")
        contract = {"model": args.model, "model_digest": model["digest"],
                    "snapshot_sha256": snapshot_hash, "options": options, "think": False,
                    "postprocessing_sha256": hashlib.sha256(
                        Path(__file__).resolve().parents[1].joinpath("app/rag/pipeline.py").read_bytes()
                    ).hexdigest()}
        if metadata_path.exists():
            metadata = read_json(metadata_path)
            if any(metadata.get(key) != value for key, value in contract.items()):
                raise SystemExit("Mevcut koşumun modeli, bağlamı veya ayarları farklı; yeni bir etiket kullanın.")
        else:
            if answers_path.exists():
                raise SystemExit("Metaverisiz eski sonuçlar bulundu; yeni bir etiket kullanın.")
            show = client.post("/api/show", json={"model": args.model})
            show.raise_for_status()
            version = client.get("/api/version")
            version.raise_for_status()
            hardware = platform.platform()
            if platform.system() == "Darwin":
                hardware += "\n" + subprocess.check_output(
                    ["sysctl", "-n", "hw.memsize", "machdep.cpu.brand_string"], text=True
                ).strip()
            metadata = {**contract, "created_at": utc_now(), "hardware": hardware,
                        "ollama_version": version.json()["version"], "model_details": show.json()}
            save_json(metadata_path, metadata)
        existing = []
        if answers_path.exists():
            existing = [json.loads(line) for line in answers_path.read_text(encoding="utf-8").splitlines() if line]
        done = {row["id"] for row in existing if not row.get("error")}
        pending = [case for case in snapshot["cases"] if case["id"] not in done]
        if not pending:
            print(f"{args.label}: bütün sorular zaten tamamlandı.")
            return
        warmup = generate(client, args.model, "Yalnızca 'Hazır' yaz.", {**options, "num_predict": 16})
        metadata.setdefault("warmups", []).append({"at": utc_now(), "wall_ms": warmup["wall_ms"],
                                                  "load_duration": warmup.get("load_duration")})
        save_json(metadata_path, metadata)
        for case in pending:
            print(f"{args.label} {case['id']} çalışıyor...", flush=True)
            row = {"id": case["id"], "model": args.model, "snapshot_sha256": snapshot_hash,
                   "prompt_sha256": case["prompt_sha256"], "created_at": utc_now()}
            try:
                result = generate(client, args.model, case["prompt"], options)
                raw = result.get("response", "")
                answer = _label_source_references(_strip_reasoning(raw), case["hits"])
                row.update({"answer": answer, "raw_answer": raw, "thinking": result.get("thinking", ""),
                            "wall_ms": result["wall_ms"], "done_reason": result.get("done_reason"),
                            "metrics": {key: value for key, value in result.items()
                                        if key.endswith("_duration") or key.endswith("_count")}})
                print(f"{args.label} {case['id']}: {row['wall_ms']/1000:.1f} sn, {len(answer)} karakter, {row['done_reason']}", flush=True)
            except (httpx.HTTPError, RuntimeError, ValueError) as exc:
                row["error"] = str(exc)
                print(f"{args.label} {case['id']}: HATA {exc}", flush=True)
            with answers_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
                handle.flush()


def summarize(args) -> None:
    snapshot = read_json(args.snapshot)
    snapshot_hash = digest(snapshot)
    cases = {case["id"]: case for case in snapshot["cases"]}
    summary = {"snapshot_sha256": snapshot_hash, "n_questions": len(cases), "models": {}}
    answers = {}
    for path in args.results:
        rows = {}
        for line in path.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            if row["snapshot_sha256"] != snapshot_hash or row["prompt_sha256"] != cases[row["id"]]["prompt_sha256"]:
                raise SystemExit(f"Farklı kaynak veya soru girdisi: {path}")
            rows[row["id"]] = row
        valid = [row for row in rows.values() if not row.get("error")]
        if not valid:
            raise SystemExit(f"Başarılı sonuç yok: {path}")
        latencies = [row["wall_ms"] / 1000 for row in valid]
        answers[valid[0]["model"]] = rows
        speeds = [row["metrics"]["eval_count"] / (row["metrics"]["eval_duration"] / 1e9)
                  for row in valid if row["metrics"].get("eval_duration")]
        summary["models"][valid[0]["model"]] = {
            "completed": len(valid), "errors": sum(bool(row.get("error")) for row in rows.values()),
            "missing": sorted(set(cases) - set(rows)), "empty_answers": sum(not row["answer"] for row in valid),
            "truncated": sum(row["done_reason"] == "length" for row in valid),
            "raw_think_blocks": sum(bool(re.search(r"<think>", row["raw_answer"], re.IGNORECASE)) for row in valid),
            "separate_thinking_answers": sum(bool(row.get("thinking")) for row in valid),
            "p50_seconds": round(statistics.median(latencies), 2),
            "p95_seconds": round(sorted(latencies)[max(0, math.ceil(len(latencies) * .95) - 1)], 2),
            "mean_seconds": round(statistics.mean(latencies), 2),
            "mean_tokens_per_second": round(statistics.mean(speeds), 2),
            "mean_output_tokens": round(statistics.mean(row["metrics"].get("eval_count", 0) for row in valid), 1),
            "answers_under_10_seconds": sum(value < 10 for value in latencies),
        }
    for path in args.reviews:
        review = read_json(path)
        if review["snapshot_sha256"] != snapshot_hash or review["model"] not in answers:
            raise SystemExit(f"İnceleme farklı bağlama veya modele ait: {path}")
        reviewed = {row["id"]: row for row in review["cases"]}
        if len(reviewed) != len(review["cases"]) or set(reviewed) != set(cases):
            raise SystemExit(f"İncelemede eksik, fazla veya yinelenen soru var: {path}")
        fields = ("grounded", "complete", "citation_correct", "turkish_clear")
        if any(type(row.get(field)) is not bool for row in reviewed.values() for field in fields):
            raise SystemExit(f"İnceleme ölçütleri doğru/yanlış olmalıdır: {path}")
        if any(answers[review["model"]][key].get("error") for key in reviewed):
            raise SystemExit(f"Hatalı API yanıtlarına kalite puanı verilemez: {path}")
        quality = {field: sum(row[field] for row in reviewed.values()) for field in fields}
        quality["grounded_and_complete"] = sum(row["grounded"] and row["complete"] for row in reviewed.values())
        quality["all_criteria"] = sum(all(row[field] for field in fields) for row in reviewed.values())
        quality["reviewer"] = review["reviewer"]
        summary["models"][review["model"]]["quality_review"] = quality
    save_json(args.output, summary)
    lines = ["# Model yanıtları", "", "Aynı soruya ve sabit kaynak parçalarına verilen yanıtlar.", "",
             "Süreler yalnızca LLM isteğini kapsar. Kaynaklar `snapshot.json` içindedir.", ""]
    for case in cases.values():
        lines.extend([f"## {case['id']}: {case['question']}", ""])
        for model, rows in answers.items():
            row = rows.get(case["id"], {})
            lines.extend([f"### {model}", ""])
            if "wall_ms" in row:
                lines.extend([f"Süre: {row['wall_ms']/1000:.2f} sn; bitiş: {row.get('done_reason')}", ""])
            lines.extend([row.get("answer") or row.get("error") or "Yanıt yok.", ""])
    rendered = "\n".join(line.rstrip() for line in "\n".join(lines).splitlines()) + "\n"
    args.output.with_name("answers.md").write_text(rendered, encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    prep = commands.add_parser("prepare", help="Soruları ve kaynakları bir kez sabitle.")
    prep.add_argument("--questions", type=Path, default=Path("evaluation/questions.json"))
    prep.add_argument("--output", type=Path, required=True)
    prep.set_defaults(action=prepare)
    runner = commands.add_parser("run", help="Sabit girdilerle modeli ölç; kesilirse kaldığı yerden sürdür.")
    runner.add_argument("--snapshot", type=Path, required=True)
    runner.add_argument("--model", required=True)
    runner.add_argument("--label", required=True)
    runner.add_argument("--output", type=Path, required=True)
    runner.set_defaults(action=run)
    report = commands.add_parser("summarize", help="Süre ve hata ölçümlerini hesapla.")
    report.add_argument("--snapshot", type=Path, required=True)
    report.add_argument("--results", type=Path, nargs="+", required=True)
    report.add_argument("--reviews", type=Path, nargs="*", default=[])
    report.add_argument("--output", type=Path, required=True)
    report.set_defaults(action=summarize)
    args = parser.parse_args()
    args.action(args)


if __name__ == "__main__":
    main()
