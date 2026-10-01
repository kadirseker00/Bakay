"""ChromaDB vektör deposu ve bellekte BM25 ile hibrit erişim.

add/query arayüzü korunur; query_dense önceki erişim tabanını ölçmek içindir.
"""
from __future__ import annotations

from functools import lru_cache
from threading import RLock

import numpy as np

from app.config import settings
from app.ingest.titles import title_from_filename
from app.rag.embeddings import get_embedder
from app.rag.retrieval import LexicalIndex


class VectorStore:
    def __init__(self):
        import chromadb

        self.client = chromadb.PersistentClient(path=str(settings.chroma_path))
        # Embedding'i biz dışarıda üretiyoruz; Chroma sadece saklayıp arıyor.
        self.collection = self.client.get_or_create_collection(
            name=settings.collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        self.embedder = get_embedder()
        self._lexical: LexicalIndex | None = None
        self._lexical_count = -1
        self._lexical_lock = RLock()

    def add(self, chunks: list[dict]) -> int:
        """chunks: [{id, text, document, ...metadata}] formatında parçalar."""
        if not chunks:
            return 0
        ids = [c["id"] for c in chunks]
        docs = [c["text"] for c in chunks]
        metas = [{"document": c["document"], **c.get("meta", {})} for c in chunks]
        embeddings = self.embedder.encode(docs)
        self.collection.upsert(
            ids=ids, documents=docs, embeddings=embeddings, metadatas=metas
        )
        with self._lexical_lock:
            self._lexical = None
        return len(ids)

    def _lexical_index(self, count: int) -> LexicalIndex:
        with self._lexical_lock:
            if self._lexical is None or self._lexical_count != count:
                records = []
                for offset in range(0, count, 5000):
                    batch = self.collection.get(
                        offset=offset, limit=5000, include=["documents", "metadatas"]
                    )
                    for id_, text, meta in zip(batch["ids"], batch["documents"], batch["metadatas"]):
                        metadata = meta or {}
                        records.append({"id": id_, "text": text,
                                        "document": metadata.get("document", "bilinmiyor"),
                                        "title": metadata.get("title")})
                self._lexical = LexicalIndex(records)
                self._lexical_count = count
            return self._lexical

    def query(self, question: str, top_k: int | None = None) -> list[dict]:
        """Vektör ve Türkçe kelime aramasını birleştirir, aynı metni bir kez döndürür."""
        top_k = top_k or settings.top_k
        count = self.count()
        if not count:
            return []
        index = self._lexical_index(count)
        q_emb = self.embedder.encode_one(question)
        candidates = min(count, max(60, top_k * 4))
        res = self.collection.query(
            query_embeddings=[q_emb], n_results=candidates, include=["distances"]
        )
        lexical = index.query(question, candidates)
        ids = index.fuse(question, res["ids"][0], lexical, top_k)
        if not ids:
            return []
        # RRF sırasını koru; API/yeterlilik kapısına gerçek kosinüs skorunu ver.
        batch = self.collection.get(ids=ids, include=["embeddings"])
        vector = np.asarray(q_emb)
        query_norm = np.linalg.norm(vector)
        similarities = {}
        for id_, embedding in zip(batch["ids"], batch["embeddings"]):
            embedding = np.asarray(embedding)
            denominator = np.linalg.norm(embedding) * query_norm
            similarities[id_] = float(embedding @ vector / denominator) if denominator else 0.0
        hits = [{**index.by_id[id_], "score": round(similarities[id_], 4)}
                for id_ in ids if id_ in similarities]
        if hits:
            # Yalnız en ilgili parçayı genişlet; modelin bağlamını gereksiz büyütme.
            hits[0]["context_text"] = index.context_for(hits[0]["id"])
        return hits

    def query_dense(self, question: str, top_k: int | None = None) -> list[dict]:
        """Önceki vektör aramasını karşılaştırma ve teşhis için korur."""
        count = self.count()
        if not count:
            return []
        top_k = min(count, top_k or settings.top_k)
        q_emb = self.embedder.encode_one(question)
        res = self.collection.query(query_embeddings=[q_emb], n_results=top_k)

        hits: list[dict] = []
        docs = res.get("documents", [[]])[0]
        metas = res.get("metadatas", [[]])[0]
        dists = res.get("distances", [[]])[0]
        for id_, text, meta, dist in zip(res["ids"][0], docs, metas, dists):
            metadata = meta or {}
            document = metadata.get("document", "bilinmiyor")
            hits.append(
                {
                    "id": id_,
                    "text": text,
                    "document": document,
                    "title": metadata.get("title") or title_from_filename(document),
                    # cosine distance -> benzerlik skoru
                    "score": round(1.0 - float(dist), 4),
                }
            )
        return hits

    def count(self) -> int:
        return self.collection.count()


@lru_cache
def get_store() -> VectorStore:
    return VectorStore()
