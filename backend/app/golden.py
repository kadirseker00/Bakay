"""Geri bildirim düzeltmelerinin izlenebilir aday havuzu ve onaylı dışa aktarımı."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import sqlite3
from pathlib import Path
from uuid import uuid4

from app import knowledge

SCHEMA = '''
CREATE TABLE IF NOT EXISTS feedback_corrections (
 id TEXT PRIMARY KEY, query_id TEXT NOT NULL, fingerprint TEXT NOT NULL UNIQUE,
 knowledge_id TEXT NOT NULL UNIQUE, snapshot TEXT NOT NULL, created_at TEXT NOT NULL);
'''


def record(connection, query_id: str, question: str, answer: str, source: str | None) -> None:
    """Aynı önerinin tekrar gönderimi yeni taslak üretmez; yönetici düzenlemesini korur."""
    fingerprint = hashlib.sha256(json.dumps([query_id, question, answer, source], ensure_ascii=False).encode()).hexdigest()
    if connection.execute('SELECT 1 FROM feedback_corrections WHERE fingerprint=?', (fingerprint,)).fetchone():
        return
    original = connection.execute('''SELECT question,answer,sources_json,history_json,model,ts
        FROM queries WHERE id=?''', (query_id,)).fetchone()
    if original is None:
        raise ValueError('Sorgu bulunamadı.')
    sources = [knowledge.KnowledgeSource(title='Önerilen kaynak', url=source,
               snippet='Kullanıcının önerdiği bağlantı. İlgili madde veya kaynak özeti yönetici tarafından kontrol edilip yazılmalıdır.')] if source else []
    body = knowledge.KnowledgeInput(question=question, answer=answer, sources=sources)
    # sqlite.Row kullanan ortak yardımcıya bu bağlantıda da isimli erişim sağla.
    previous_factory = connection.row_factory
    connection.row_factory = sqlite3.Row
    try:
        draft = knowledge.save_in_connection(connection, body, 'feedback:anonymous')
    finally:
        connection.row_factory = previous_factory
    snapshot = {'original_question': original[0], 'original_answer': original[1],
                'original_sources': json.loads(original[2] or '[]'),
                'history': json.loads(original[3] or '[]'), 'original_model': original[4],
                'query_at': original[5], 'question': question, 'proposed_answer': answer,
                'proposed_source': source}
    connection.execute('INSERT INTO feedback_corrections VALUES (?,?,?,?,?,?)',
                       (uuid4().hex, query_id, fingerprint, draft['id'], json.dumps(snapshot, ensure_ascii=False),
                        datetime.now(timezone.utc).isoformat()))


def list_candidates(db_file: Path) -> list[dict]:
    with knowledge.connect(db_file) as connection:
        rows = connection.execute('''SELECT c.*,a.payload,a.status,a.revision,a.approved_by,a.approved_at
            FROM feedback_corrections c JOIN knowledge_answers a ON a.id=c.knowledge_id
            ORDER BY c.created_at DESC,c.id''').fetchall()
    items = []
    for row in rows:
        entry = knowledge.unpack(row)
        entry.update(json.loads(entry.pop('snapshot')))
        entry.pop('fingerprint')
        entry['review_status'] = ('approved' if entry['status'] == 'published' and entry['approved_by'] and not entry['expired']
                                  else 'archived' if entry['status'] == 'archived' else 'pending')
        # Öneri değişmeden kalır; güncel yönetici cevabı ayrıca gösterilir.
        entry['current_question'] = json.loads(row['payload'])['question']
        items.append(entry)
    return items


def export_dataset(db_file: Path) -> str:
    """Yalnız güncel kaynaklarıyla onaylanmış cevaplar; kimlik/IP ve prompt içermez."""
    records = []
    for item in list_candidates(db_file):
        if item['review_status'] != 'approved':
            continue
        records.append({'schema_version': 1, 'id': item['id'], 'query_id': item['query_id'],
                        'question': item['current_question'], 'reference_answer': item['answer'],
                        'sources': item['sources'], 'original_question': item['original_question'],
                        'original_answer': item['original_answer'], 'history': item['history'],
                        'proposed_answer': item['proposed_answer'], 'original_model': item['original_model'],
                        'knowledge_id': item['knowledge_id'], 'knowledge_revision': item['revision'],
                        'reviewed_on': item['reviewed_on'], 'valid_until': item['valid_until'],
                        'approved_by': item['approved_by'], 'approved_at': item['approved_at'],
                        'split': 'development', 'origin': 'user_correction'})
    return ''.join(json.dumps(record, ensure_ascii=False) + '\n' for record in records)
