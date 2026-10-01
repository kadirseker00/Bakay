"""DomainRAG yaklaşımını Türkçe KTMÜ kaynaklarına uyarlayan geliştirme paketi.

Çince soru/cevap ve kod kopyalanmaz. Bu kayıtlar gold veya eğitim verisi değildir.
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path

from evaluation.dataset import Dataset, digest, normalize, validate

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BUNDLE = ROOT / "data/eval/domainrag-tr-v1"
TASKS = ("single_turn", "conversation", "structured_information", "faithfulness",
         "denoising", "time_sensitive", "multi_document")
METHOD = {
    "paper": "https://arxiv.org/abs/2406.05654",
    "project": "https://github.com/ShootingWong/DomainRAG",
    "format_example": "https://huggingface.co/datasets/RUC-NLPIR/FlashRAG_datasets/tree/main/domainrag",
    "format_revision": "bcafb8dd07d453be3cbeeeb3f78be1841bddf92c",
    "adaptation": "Yöntem ve alan adları örnek alındı; dış kaynak metni/cevabı/kodu aktarılmadı.",
}


def build_bundle(dataset: Dataset, evidence: dict) -> tuple[list[dict], dict, list[dict]]:
    validate(dataset, evidence)
    if any(case.exposure == "private_holdout" or case.split in {"train", "test"} for case in dataset.cases):
        raise ValueError("Bu geliştirme uyarlaması train veya saklı test kayıtlarını kullanamaz.")
    cases = {case.id: case for case in dataset.cases}
    sources = {source["id"]: source for source in evidence["sources"]}
    units = {unit["id"]: unit for unit in evidence["units"]}
    rows = []

    def add(case, id_, question, task="single_turn", *, history=None, distractors=(),
            answer=None, behavior=None, required=None, forbidden=None, as_of=None):
        refs = []
        positive_ids = list(dict.fromkeys(c.evidence_id for c in case.citations))
        for unit_id in positive_ids:
            unit = units[unit_id]
            source = sources[unit["source_id"]]
            refs.append({"id": unit_id, "title": source["title"], "url": source["url"],
                         "document": Path(source["path"]).name,
                         "contents": unit["text"], "page": unit["page"],
                         "printed_page": unit["printed_page"], "source_id": source["id"],
                         "source_sha256": source["sha256"],
                         "quotes": [c.model_dump() for c in case.citations if c.evidence_id == unit_id]})
        rows.append({"id": id_, "question": question, "golden_answers": [answer or case.answer],
                     "metadata": {
                         "task": task, "query": case.question if history else question,
                         "history": history or [],
                         "positive_reference": refs,
                         "context_ids": list(dict.fromkeys([*distractors, *positive_ids])),
                         "distractor_ids": list(distractors), "base_case_id": case.id,
                         "group_ids": case.group_ids, "scope": case.scope,
                         "behavior": behavior or case.behavior,
                         "required_points": required or case.required_points,
                         "forbidden_claims": forbidden or case.forbidden_claims,
                         "status": "pending_review", "split": "dev",
                         "exposure": "development_exposed", "purpose": "evaluation_draft_only",
                         "source_case_sha256": digest(case.model_dump(mode="json")),
                         "as_of": as_of, "history_is_synthetic": bool(history),
                     }})

    for case in dataset.cases:
        for i, question in enumerate([case.question, *case.paraphrases]):
            add(case, f"{case.id}-p{i}", question)

    # Tüm senaryolar aynı kaynak bağlı başlangıç vakalarına izlenir.
    if "BAKAY-011" in cases:
        add(cases["BAKAY-011"], "DTR-CONV-001", "Lisans için soruyorum.", "conversation",
            history=[{"question": "başka kurumdan aldığım dersi saydırabilir miyim",
                      "answers": ["Tüm dersleriniz hiçbir şart olmadan otomatik sayılır."],
                      "positive_reference": []}])
        add(cases["BAKAY-011"], "DTR-NOISE-001", cases["BAKAY-011"].question, "denoising",
            distractors=[id_ for id_ in ("pg:p13", "ug:p6") if id_ in units])
        add(cases["BAKAY-011"], "DTR-TIME-001",
            "Bu arşiv belgelerine bakarak ders saydırma şartlarının 1 Ekim 2026'da hâlâ yürürlükte olduğunu kesin söyleyebilir misin?",
            "time_sensitive", answer="Hayır. Arşiv kopyaları güncel yürürlüğü kanıtlamaz. Geçerli sürüm ve değişiklikler resmî kaynaktan doğrulanmalıdır.",
            behavior="abstain", required=["Arşiv metni ile güncel yürürlüğü ayırmak.", "Güncel sürüm doğrulanmadan kesinlik iddia etmemek."],
            forbidden=["Belge adında Yeni yazmasını güncellik kanıtı saymak.", "1 Ekim 2026 için yürürlük onayı uydurmak."],
            as_of="2026-10-01")
    if "BAKAY-003" in cases:
        add(cases["BAKAY-003"], "DTR-STRUCT-001", cases["BAKAY-003"].question, "structured_information")
    if "BAKAY-048" in cases:
        add(cases["BAKAY-048"], "DTR-FAITH-001", cases["BAKAY-048"].question, "faithfulness")
    if "BAKAY-049" in cases:
        add(cases["BAKAY-049"], "DTR-MULTI-001", cases["BAKAY-049"].question, "multi_document")

    corpus = [{"id": unit["id"], "contents": unit["text"], "metadata": {
        "title": sources[unit["source_id"]]["title"], "url": sources[unit["source_id"]]["url"],
        "document": Path(sources[unit["source_id"]]["path"]).name,
        "source_id": unit["source_id"], "page": unit["page"], "printed_page": unit["printed_page"],
        "source_sha256": sources[unit["source_id"]]["sha256"], "text_sha256": unit["text_sha256"],
        "validity": "human_verification_pending",
    }} for unit in evidence["units"]]
    manifest = {"schema_version": 1, "language": "tr", "institution": "KTMÜ",
                "method": METHOD, "label_status": "pending_review_not_gold",
                "purpose": "evaluation_draft_only", "truth_scope": dataset.truth_scope,
                "dataset_sha256": digest(dataset.model_dump(mode="json")),
                "evidence_sha256": digest(evidence), "rows_sha256": digest(rows),
                "corpus_sha256": digest(corpus), "tasks": dict(Counter(r["metadata"]["task"] for r in rows)),
                "cases": len(rows), "corpus_units": len(corpus)}
    return rows, manifest, corpus


def validate_bundle(rows, manifest, corpus, dataset: Dataset, evidence: dict, *, verify_raw=False):
    base = validate(dataset, evidence, verify_raw=verify_raw)
    expected_rows, expected_manifest, expected_corpus = build_bundle(dataset, evidence)
    # Etiket, dayanak, cevap veya ayrım değişmişse eski paketi kullanma.
    if rows != expected_rows or manifest != expected_manifest or corpus != expected_corpus:
        raise ValueError("Uyarlama paketi kaynak veriden farklı; build ile yeni bir dizinde yeniden üretin.")
    if len({row["id"] for row in rows}) != len(rows):
        raise ValueError("Yinelenen senaryo kimliği.")
    return {"cases": len(rows), "tasks": manifest["tasks"], "corpus_units": len(corpus),
            "label_status": manifest["label_status"], "raw_verified": base["raw_verified"],
            "bundle_sha256": digest(manifest)}


def history_messages(row):
    from app.schemas import ChatMessage
    messages = []
    for turn in row["metadata"]["history"]:
        messages.extend([ChatMessage(role="user", content=turn["question"]),
                         ChatMessage(role="assistant", content=turn["answers"][0])])
    return messages


def resolve_query(row, llm):
    from app.rag.pipeline import _resolve_question
    history = history_messages(row)
    # metadata.query değerlendirme hedefidir, aramaya verilen hazır cevap değildir.
    return _resolve_question(row["question"], history, llm) if history else row["question"]


def context_hits(row, corpus):
    by_id = {unit["id"]: unit for unit in corpus}
    return [{"id": id_, "text": by_id[id_]["contents"],
             "title": by_id[id_]["metadata"]["title"],
             "document": by_id[id_]["metadata"]["document"]}
            for id_ in row["metadata"]["context_ids"]]


def fixed_prompt(row, corpus, llm):
    from app.rag.pipeline import SYSTEM_PROMPT, _build_context
    query = resolve_query(row, llm)
    if query is None:
        raise ValueError(f"Bağlam çözülemedi: {row['id']}")
    hits = context_hits(row, corpus)
    context = ("Bu deney yalnız aşağıdaki arşiv kaynaklarıyla sınırlıdır. "
               "Kaynakların güncel yürürlüğü doğrulanmamıştır; arşivdeki kuralı "
               "güncel yürürlük onayı gibi sunma.\n\n" + _build_context(hits))
    # Referans cevap, beklenen noktalar, negatif etiketleri ve metadata.query
    # modele verilmez. Negatif geçmiş yanıtı da kaynak metnine taşınmaz.
    return query, hits, SYSTEM_PROMPT.format(context=context, question=query)


def citation_ranks(row, hits):
    ranks = []
    for reference in row["metadata"]["positive_reference"]:
        for citation in reference["quotes"]:
            quote = normalize(citation["quote"])
            width = min(80, len(quote))
            anchors = [quote[i:i + width] for i in range(0, len(quote) - width + 1, 20)]
            anchors.append(quote[-width:])
            rank = next((i for i, hit in enumerate(hits, 1)
                         if (len(quote) >= 80 or hit["document"] == reference["document"])
                         and any(anchor in normalize(hit["text"]) for anchor in anchors)), None)
            ranks.append(rank)
    return ranks


def retrieval_summary(rows):
    measured = [row for row in rows if row["behavior"] == "answer" and row["ranks"]]
    n = len(measured)
    return {"n_answer_queries": n,
            "any_citation_at_5": sum(any(r is not None and r <= 5 for r in row["ranks"]) for row in measured),
            "all_citations_at_5": sum(all(r is not None and r <= 5 for r in row["ranks"]) for row in measured),
            "mean_citation_recall_at_5": sum(sum(r is not None and r <= 5 for r in row["ranks"]) / len(row["ranks"])
                                              for row in measured) / n if n else None,
            "mrr_at_10": sum(1 / min(r for r in row["ranks"] if r is not None and r <= 10)
                             if any(r is not None and r <= 10 for r in row["ranks"]) else 0 for row in measured) / n if n else None}


def review_markdown(rows, manifest):
    lines = ["# KTMÜ DomainRAG geliştirme inceleme paketi", "",
             "**TASLAK: insan onaysız, gold veya LoRA eğitim verisi değildir.**", "",
             f"Senaryo: {len(rows)}. Paket özeti: `{digest(manifest)}`.", "",
             "Otomatik erişim metrikleri cevap doğruluğu değildir. Referans cevapları uzman kontrol etmelidir.", ""]
    for row in rows:
        meta = row["metadata"]
        lines += [f"## {row['id']}: {row['question']}", "", f"Görev: `{meta['task']}`; kapsam: {meta['scope']}", ""]
        for turn in meta["history"]:
            lines += [f"Önceki kullanıcı: {turn['question']}", f"Sentetik asistan yanıtı (dayanak değildir): {turn['answers'][0]}", ""]
        lines += [f"Taslak referans: {row['golden_answers'][0]}", "", "Beklenen noktalar:", ""]
        lines += [f"- {point}" for point in meta["required_points"]]
        lines += ["", "Yanlış sayılacak iddialar:", ""] + [f"- {claim}" for claim in meta["forbidden_claims"]]
        lines += ["", "Kaynaklar:", ""]
        for ref in meta["positive_reference"]:
            lines += [f"- [{ref['title']}]({ref['url']}), PDF sayfa {ref['page'] or '—'}; `{ref['id']}`"]
        lines += ["", f"İlgisiz/yanıltıcı bağlamlar: {', '.join(meta['distractor_ids']) or 'yok'}", ""]
    return "\n".join(lines).rstrip() + "\n"
