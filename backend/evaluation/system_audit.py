"""Kaynak bağlı geliştirme pilotu: canlı retrieval ve yalıtılmış embedding deneyi.

Üretim indeksini/ayarlarını değiştirmez. Etiketler uzman onaylı gold değildir.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
import math
from pathlib import Path
import re
import statistics
import time
import unicodedata

import numpy as np

from app.config import ROOT, settings
from app.rag.pipeline import SYSTEM_PROMPT, _build_context
from scripts.compare_models import digest, save_json, utc_now


def normalized(text):
    return " ".join(unicodedata.normalize("NFC", text).split())


def tokens(text):
    return re.findall(r"\w+", text.replace("İ", "i").replace("I", "ı").lower())


def load_inputs():
    dataset = json.loads((ROOT / "data/eval/v1/dataset.json").read_text())
    evidence = json.loads((ROOT / "data/eval/v1/evidence.json").read_text())
    sources = {s["id"]: s for s in evidence["sources"]}
    units = {u["id"]: u for u in evidence["units"]}
    queries = []
    for case in dataset["cases"]:
        for i, question in enumerate([case["question"], *case["paraphrases"]]):
            queries.append({**case, "id": case["id"] + (f"-p{i}" if i else ""),
                            "base_id": case["id"], "question": question})
    return dataset, evidence, sources, units, queries


class BM25:
    """Türkçe küçük harf dönüşümü; gövdeleme yok. k1=1.5, b=0.75."""

    def __init__(self, chunks):
        self.postings = defaultdict(list)
        self.lengths = []
        for i, chunk in enumerate(chunks):
            counts = Counter(tokens(chunk["text"]))
            self.lengths.append(sum(counts.values()))
            for word, frequency in counts.items():
                self.postings[word].append((i, frequency))
        lengths = np.array(self.lengths)
        norm = 1.5 * (.25 + .75 * lengths / max(1, lengths.mean()))
        n = len(chunks)
        for word, postings in self.postings.items():
            indices, tf = np.array(postings).T
            idf = math.log(1 + (n - len(indices) + .5) / (len(indices) + .5))
            self.postings[word] = (indices, idf * tf * 2.5 / (tf + norm[indices]))

    def query(self, question, n=50):
        scores = np.zeros(len(self.lengths))
        for word in set(tokens(question)):
            if word in self.postings:
                indices, weights = self.postings[word]
                scores[indices] += weights
        return [int(i) for i in np.argsort(-scores, kind="stable")[:n] if scores[i] > 0]


def fuse(dense, lexical, n=10):
    scores = defaultdict(float)
    for ranking in [dense, lexical]:
        for rank, index in enumerate(ranking, 1):
            scores[index] += 1 / (60 + rank)
    return sorted(scores, key=lambda i: (-scores[i], i))[:n]


def qrels(queries, chunks, sources, units):
    """Alıntının en az 80 ardışık karakterini içeren parça eşleşir.

    Kısa alıntıda aynı belge ve tüm alıntı gerekir. Uzun alıntıda diğer belge
    kopyaları da kabul edilir. Tam alıntı eşleşmesi ayrıca saklanır.
    Bu mekanik dayanak eşleşmesi semantik uzman etiketlemesinin yerine geçmez.
    """
    by_document = defaultdict(list)
    texts = [normalized(c["text"]) for c in chunks]
    for i, chunk in enumerate(chunks):
        by_document[chunk["document"]].append(i)
    labels = {}
    for query in queries:
        groups = []
        for citation in query["citations"]:
            source = sources[units[citation["evidence_id"]]["source_id"]]
            quote = normalized(citation["quote"])
            width = min(80, len(quote))
            anchors = [quote[i:i + width] for i in range(0, len(quote) - width + 1, 20)]
            anchors.append(quote[-width:])
            indices = (range(len(chunks)) if len(quote) >= 80
                       else by_document[Path(source["path"]).name])
            groups.append({"evidence_id": citation["evidence_id"], "section": citation["section"],
                           "relevant": [i for i in indices if any(a in texts[i] for a in anchors)],
                           "full_quote": [i for i in indices if quote in texts[i]]})
        labels[query["id"]] = groups
    return labels


def score(ranking, groups):
    relevant = set(i for g in groups for i in g["relevant"])
    first = next((r for r, i in enumerate(ranking[:10], 1) if i in relevant), None)
    found = [bool(set(g["relevant"]) & set(ranking[:5])) for g in groups]
    full = [bool(set(g["full_quote"]) & set(ranking[:5])) for g in groups]
    return {"hit_at_5": any(found), "all_citations_at_5": bool(found) and all(found),
            "citation_recall_at_5": sum(found) / len(found) if found else None,
            "all_full_quotes_at_5": bool(full) and all(full),
            "mrr_at_10": 1 / first if first else 0,
            "citation_found_at_5": found, "first_relevant_rank": first}


def aggregate(rows):
    # Açıklama isteme ve çekimserlik soruları retrieval başarısı paydasına girmez.
    scored = [r for r in rows if r["behavior"] == "answer"]
    return {"n_answer_queries": len(scored),
            "hit_at_5_count": sum(r["hit_at_5"] for r in scored),
            "all_citations_at_5_count": sum(r["all_citations_at_5"] for r in scored),
            "all_full_quotes_at_5_count": sum(r["all_full_quotes_at_5"] for r in scored),
            "citation_recall_at_5": statistics.mean(r["citation_recall_at_5"] for r in scored),
            "mrr_at_10": statistics.mean(r["mrr_at_10"] for r in scored)}


def retrieve(args):
    import chromadb
    from app.rag.embeddings import get_embedder
    from app.ingest.titles import title_from_filename

    if args.output.exists():
        raise SystemExit("Yeni bir çıktı dizini kullanın; sabit anlık görüntü üzerine yazılmaz.")
    dataset, evidence, sources, units, queries = load_inputs()
    client = chromadb.PersistentClient(path=str(settings.chroma_path))
    collection = client.get_collection(settings.collection_name)
    chunks = []
    for offset in range(0, collection.count(), 5000):
        batch = collection.get(offset=offset, limit=5000, include=["documents", "metadatas"])
        for id_, text, meta in zip(batch["ids"], batch["documents"], batch["metadatas"]):
            meta = meta or {}
            document = meta.get("document", "bilinmiyor")
            chunks.append({"id": id_, "text": text, "document": document,
                           "title": meta.get("title") or title_from_filename(document)})
    chunks.sort(key=lambda c: c["id"])
    index = {c["id"]: i for i, c in enumerate(chunks)}
    print(f"Koleksiyon: {len(chunks)} parça", flush=True)
    labels = qrels(queries, chunks, sources, units)
    start = time.perf_counter()
    bm25 = BM25(chunks)
    bm25_build_seconds = time.perf_counter() - start
    embedder = get_embedder()
    embedder.encode_one("Isıtma: Manas Üniversitesi")
    results = {"dense": [], "bm25": [], "hybrid_rrf": []}
    pilot_indices = {i for i, c in enumerate(chunks) if c["document"] in
                     {Path(s["path"]).name for s in sources.values()}}
    for query in queries:
        start = time.perf_counter()
        vector = embedder.encode_one(query["question"])
        batch = collection.query(query_embeddings=[vector], n_results=50, include=["distances"])
        dense_ms = (time.perf_counter() - start) * 1000
        dense = [index[id_] for id_ in batch["ids"][0]]
        start = time.perf_counter()
        lexical = bm25.query(query["question"])
        lexical_ms = (time.perf_counter() - start) * 1000
        hybrid = fuse(dense, lexical)
        pilot_indices.update(dense[:10])
        pilot_indices.update(lexical[:10])
        for label, ranking, latency in [("dense", dense[:10], dense_ms),
                                         ("bm25", lexical[:10], lexical_ms),
                                         ("hybrid_rrf", hybrid, dense_ms + lexical_ms)]:
            hits = [{**chunks[i], "score": float(1 - batch["distances"][0][dense.index(i)])
                     if i in dense else 0.0} for i in ranking]
            results[label].append({"id": query["id"], "base_id": query["base_id"],
                                   "question": query["question"], "behavior": query["behavior"],
                                   "category": query["category"], "latency_ms": latency,
                                   **score(ranking, labels[query["id"]]), "hits": hits,
                                   "gate_pass": bool(hits and hits[0]["score"] >= settings.score_threshold)})
        print(query["id"], "dense", results["dense"][-1]["all_citations_at_5"],
              "hybrid", results["hybrid_rrf"][-1]["all_citations_at_5"], flush=True)
    # Zor negatifler yanında kimlik hash'iyle kararlı, sorgudan bağımsız örneklem.
    pilot_indices.update(sorted(range(len(chunks)), key=lambda i: digest(chunks[i]["id"]))[:1000])
    pilot = [chunks[i] for i in sorted(pilot_indices)]
    args.output.mkdir(parents=True)
    save_json(args.output / "pilot-corpus.json", pilot)
    metrics = {}
    for label, rows in results.items():
        latencies = sorted(r["latency_ms"] for r in rows)
        metrics[label] = {**aggregate(rows), "original": aggregate([r for r in rows if r["id"] == r["base_id"]]),
                          "paraphrases": aggregate([r for r in rows if r["id"] != r["base_id"]]),
                          "p50_retrieval_ms": statistics.median(latencies),
                          "p95_retrieval_ms": latencies[math.ceil(.95 * len(latencies)) - 1]}
        save_json(args.output / f"{label}.retrieval.json", rows)
    save_json(args.output / "retrieval-metrics.json", {
        "created_at": utc_now(), "dataset_sha256": digest(dataset), "evidence_sha256": digest(evidence),
        "collection": settings.collection_name, "collection_metadata": collection.metadata,
        "indexed_chunks": len(chunks), "corpus_sha256": digest(chunks), "pilot_chunks": len(pilot),
        "pilot_sha256": digest(pilot), "embedding": settings.embedding_model,
        "max_seq_length": embedder.model.max_seq_length, "device": str(embedder.model.device),
        "bm25_build_seconds": bm25_build_seconds, "metrics": metrics,
        "missing_citation_anchors": {id_: [g["section"] for g in groups if not g["relevant"]]
                                     for id_, groups in labels.items() if any(not g["relevant"] for g in groups)},
        "example_chunks": [c for c in chunks if "ornek" in c["document"].lower()],
    })
    # 12 kritik örnek: gerçek erişim ve yalnız doğru alıntılardan oluşan oracle bağlamı.
    selected = {f"BAKAY-{i:03}" for i in [1, 4, 14, 21, 25, 36, 39, 45, 46, 48, 49, 50]}
    for mode in ["live", "oracle"]:
        cases = []
        for query, row in zip(queries, results["dense"]):
            if query["id"] not in selected:
                continue
            if mode == "live":
                hits = row["hits"][:5]
            else:
                hits = []
                for citation in query["citations"]:
                    s = sources[units[citation["evidence_id"]]["source_id"]]
                    hits.append({"text": citation["quote"], "title": s["title"],
                                 "document": Path(s["path"]).name, "score": 1.0})
            prompt = SYSTEM_PROMPT.format(context=_build_context(hits), question=query["question"])
            cases.append({**query, "hits": hits, "prompt": prompt, "prompt_sha256": digest(prompt),
                          "production_gate_pass": row["gate_pass"] if mode == "live" else None})
        save_json(args.output / f"{mode}.snapshot.json", {
            "created_at": utc_now(), "mode": mode, "indexed_chunks": len(chunks),
            "system_prompt_sha256": digest(SYSTEM_PROMPT), "cases": cases})


def embedding(args):
    import chromadb
    from sentence_transformers import SentenceTransformer

    _, _, sources, units, queries = load_inputs()
    corpus_path = args.output / "pilot-corpus.json"
    chunks = json.loads(corpus_path.read_text())
    labels = qrels(queries, chunks, sources, units)
    model = SentenceTransformer(args.model)
    e5 = "multilingual-e5" in args.model
    start = time.perf_counter()
    if args.model == settings.embedding_model:
        collection = chromadb.PersistentClient(path=str(settings.chroma_path)).get_collection(settings.collection_name)
        stored = collection.get(ids=[c["id"] for c in chunks], include=["embeddings"])
        vectors_by_id = dict(zip(stored["ids"], stored["embeddings"]))
        vectors = np.array([vectors_by_id[c["id"]] for c in chunks], dtype=np.float32)
        check = model.encode([c["text"] for c in chunks[:10]], normalize_embeddings=True)
        consistency = (check * vectors[:10]).sum(axis=1).tolist()
    else:
        vectors = model.encode([("passage: " if e5 else "") + c["text"] for c in chunks],
                               batch_size=32, normalize_embeddings=True, show_progress_bar=True)
        consistency = None
    corpus_seconds = time.perf_counter() - start
    start = time.perf_counter()
    query_vectors = model.encode([("query: " if e5 else "") + q["question"] for q in queries],
                                 batch_size=32, normalize_embeddings=True)
    query_seconds = time.perf_counter() - start
    similarities = query_vectors @ vectors.T
    rows = []
    for query, sims in zip(queries, similarities):
        ranking = np.argsort(-sims, kind="stable")[:10].tolist()
        rows.append({"id": query["id"], "base_id": query["base_id"], "behavior": query["behavior"],
                     **score(ranking, labels[query["id"]]),
                     "hits": [{**chunks[i], "score": float(sims[i])} for i in ranking]})
    # Token kesilmesi: varsayılan tokenizer sınırından önce gerçek uzunluk.
    lengths = []
    for offset in range(0, len(chunks), 128):
        encoded = model.tokenizer([("passage: " if e5 else "") + c["text"]
                                   for c in chunks[offset:offset + 128]], truncation=False)
        lengths.extend(len(ids) for ids in encoded["input_ids"])
    save_json(args.output / f"{args.label}.embedding.json", {
        "created_at": utc_now(), "model": args.model, "pilot_sha256": digest(chunks),
        "queries_sha256": digest(queries), "model_revision": getattr(model[0].auto_model.config, "_commit_hash", None),
        "device": str(model.device), "max_seq_length": model.max_seq_length, "dimension": vectors.shape[1],
        "corpus_encode_or_load_seconds": corpus_seconds, "query_batch_seconds": query_seconds,
        "prefixes": {"query": "query: ", "passage": "passage: "} if e5 else None,
        "truncated_chunks": sum(n > model.max_seq_length for n in lengths),
        "stored_vector_cosine_checks": consistency, "metrics": aggregate(rows),
        "original": aggregate([r for r in rows if r["id"] == r["base_id"]]),
        "paraphrases": aggregate([r for r in rows if r["id"] != r["base_id"]]), "rows": rows})
    print(args.label, json.dumps(aggregate(rows)), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for command, action in [("retrieve", retrieve), ("embedding", embedding)]:
        sub = commands.add_parser(command)
        sub.add_argument("--output", required=True, type=Path)
        if command == "embedding":
            sub.add_argument("--model", required=True)
            sub.add_argument("--label", required=True)
        sub.set_defaults(action=action)
    args = parser.parse_args()
    args.action(args)


if __name__ == "__main__":
    main()
