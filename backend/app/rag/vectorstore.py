"""ChromaDB vektör deposu sarmalayıcı.

İP3'te FAISS ve Elasticsearch (BM25 + hybrid) ile karşılaştırılacak. Aynı
arayüzü (add / query) koruduğumuz için pipeline kodunu değiştirmeden farklı
arka uçlar denenebilir.
"""
from __future__ import annotations

from functools import lru_cache

from app.config import settings
from app.rag.embeddings import get_embedder


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
        return len(ids)

    def query(self, question: str, top_k: int | None = None) -> list[dict]:
        """Soruya en yakın parçaları döndürür."""
        top_k = top_k or settings.top_k
        q_emb = self.embedder.encode_one(question)
        res = self.collection.query(query_embeddings=[q_emb], n_results=top_k)

        hits: list[dict] = []
        docs = res.get("documents", [[]])[0]
        metas = res.get("metadatas", [[]])[0]
        dists = res.get("distances", [[]])[0]
        for text, meta, dist in zip(docs, metas, dists):
            hits.append(
                {
                    "text": text,
                    "document": (meta or {}).get("document", "bilinmiyor"),
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
