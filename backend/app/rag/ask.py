"""Hızlı CLI soru-cevap: RAG hattını terminalden dener.

Çalıştırma (backend/ içinden):

    .venv/bin/python -m app.rag.ask "Sorunuz buraya"
"""
from __future__ import annotations

import sys

from app.rag.pipeline import answer


def main() -> None:
    if len(sys.argv) < 2:
        print('Kullanım: python -m app.rag.ask "soru"')
        raise SystemExit(1)

    question = " ".join(sys.argv[1:])
    resp = answer(question)

    print(f"\n{resp.answer}\n")
    print("— Kaynaklar " + "—" * 50)
    for s in resp.sources:
        print(f"  [{s.title or s.document}] skor={s.score:.3f}")
        print(f"    {s.snippet[:160].replace(chr(10), ' ')}…")
    print(f"\n⏱  {resp.latency_ms} ms  |  qid={resp.query_id}")


if __name__ == "__main__":
    main()
