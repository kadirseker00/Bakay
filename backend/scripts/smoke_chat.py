"""Çalışan API'de Qwen geçişini sınar; kalite puanı veya gold etiketi üretmez."""
from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

from evaluation.dataset import DEFAULT_DATA, Dataset, read_json
from scripts.dataset import write_new


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Çıktı zaten var; farklı bir dosya adı kullanın.")
    dataset = Dataset.model_validate(read_json(DEFAULT_DATA / "dataset.json"))
    selected = {"BAKAY-025", "BAKAY-036", "BAKAY-046", "BAKAY-050"}
    rows = []
    with httpx.Client(base_url=args.base_url, timeout=180) as client:
        health = client.get("/health")
        health.raise_for_status()
        status = health.json()
        if status.get("llm_model") != "qwen3.5:9b" or status.get("llm_provider") != "ollama":
            parser.error(f"Beklenen yerel Qwen yapılandırması değil: {status.get('llm_model')}")
        for case in dataset.cases:
            if case.id not in selected:
                continue
            start = time.perf_counter()
            row = {"id": case.id, "question": case.question}
            print(f"{case.id} çalışıyor...", flush=True)
            try:
                response = client.post("/chat", json={"question": case.question})
                response.raise_for_status()
                result = response.json()
                if not result.get("answer") or not result.get("query_id"):
                    raise ValueError("Boş/eksik API yanıtı.")
                if any(not source.get("title") for source in result.get("sources", [])):
                    raise ValueError("Başlıksız kaynak.")
                if "<think>" in result["answer"].lower() or "**Sistem bildirimi**" in result["answer"]:
                    raise ValueError("Düşünme bloğu veya servis hata yanıtı.")
                row["response"] = result
            except (httpx.HTTPError, ValueError) as exc:
                row["error"] = str(exc)
            row["wall_ms"] = round((time.perf_counter() - start) * 1000)
            rows.append(row)
            print(f"{case.id}: {row['wall_ms']} ms, hata={row.get('error')}", flush=True)
    report = {"created_at": datetime.now(timezone.utc).isoformat(), "health": status,
              "method": "Canlı RAG; ilk sorgu soğuk olabilir. Teknik kontrol; cevap kalitesi ayrıca incelenmeli.",
              "dataset_evidence_sha256": dataset.evidence_sha256, "results": rows}
    write_new(args.output, json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    if any("error" in row for row in rows):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
