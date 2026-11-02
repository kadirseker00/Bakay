"""Rehber kartında kişi/görev ayrımı, güvenli ayrıştırma ve bayat kayıt temizliği."""
import json
import tempfile
from pathlib import Path
from unittest import TestCase
from unittest.mock import Mock

from app.ingest.personnel import export, index_records, official, parse_people


def card(person):
    # Rehberdeki JSON.parse içinde, JSON'un ikinci bir JS dizesinde sunulması.
    encoded = json.dumps(json.dumps(person, ensure_ascii=True))[1:-1].replace('\\"', r'\u0022')
    return '<div @click="open(JSON.parse(\'' + encoded + '\'))"></div>'


def page():
    return '<main id="directory-detail-main"><h1>Mühendislik</h1><h2>Bilgisayar</h2>' + card({
        'person_id': 1, 'name': 'Ayşe ÖZTÜRK', 'title': 'Dr.', 'duty': 'Öğretim Üyesi',
        'email': 'ayse@manas.edu.kg', 'ext': '1234'}) + '<h2>Kimya</h2>' + card({
        'person_id': 2, 'name': 'Ali IŞIK', 'duty': 'Bölüm Başkanı', 'room': '301'}) + '</main>'


class PersonnelTests(TestCase):
    def test_people_and_departments_do_not_mix_and_public_email_is_decoded(self):
        records = parse_people(page(), 'https://rehber.manas.edu.kg/muhendislik', '2026-11-02')
        self.assertEqual(len(records), 2)
        self.assertIn('Ayşe ÖZTÜRK', records[0]['text'])
        self.assertIn('Alt birim: Bilgisayar', records[0]['text'])
        self.assertIn('Kurumsal e-posta: ayse@manas.edu.kg', records[0]['text'])
        self.assertNotIn('301', records[0]['text'])
        self.assertNotIn('ayse@', records[1]['text'])
        self.assertIn('Alt birim: Kimya', records[1]['text'])

    def test_changed_contact_uses_same_id_but_distinct_job_has_own_id(self):
        one = parse_people(page(), 'https://rehber.manas.edu.kg/m', '2026-11-01')
        two = parse_people(page().replace('1234', '5678'), 'https://rehber.manas.edu.kg/m', '2026-11-02')
        self.assertEqual(one[0]['id'], two[0]['id'])
        self.assertIn('5678', two[0]['text'])
        other = parse_people(page().replace('Bilgisayar', 'Elektrik'), 'https://rehber.manas.edu.kg/m', '2026-11-02')
        self.assertNotEqual(one[0]['id'], other[0]['id'])

    def test_structure_or_foreign_source_fails_instead_of_clearing_directory(self):
        for content in ('<h1>Giriş yapın</h1>', '<main id="directory-detail-main"><h1>X</h1></main>'):
            with self.assertRaises(ValueError):parse_people(content, 'https://rehber.manas.edu.kg/m', '2026-11-02')
        for url in ('https://rehber.manas.edu.kg.evil.test/m', 'https://evil@rehber.manas.edu.kg/m', 'http://rehber.manas.edu.kg/m'):
            self.assertFalse(official(url))

    def test_failed_upsert_never_deletes_previous_records(self):
        store = Mock();store.collection.get.return_value = {'ids': ['old']}
        store.add.side_effect = RuntimeError('embedding_failed')
        with self.assertRaises(RuntimeError):index_records([{'id': 'new'}], store)
        store.collection.delete.assert_not_called()
        with self.assertRaises(ValueError):index_records([], store)

    def test_complete_refresh_removes_only_old_personnel_and_exports_real_links(self):
        records = parse_people(page(), 'https://rehber.manas.edu.kg/m', '2026-11-02')
        store = Mock();store.collection.get.return_value = {'ids': ['obsolete', records[0]['id']]}
        index_records(records, store)
        store.collection.get.assert_called_once_with(where={'source_type': 'personnel_directory'}, include=[])
        store.collection.delete.assert_called_once_with(ids=['obsolete'])
        with tempfile.TemporaryDirectory() as directory:
            export(records, Path(directory))
            mapping = json.loads((Path(directory) / 'data/sitemap-personnel.json').read_text())
            self.assertEqual(mapping['pages'][0]['url'], 'https://rehber.manas.edu.kg/m')
            self.assertTrue((Path(directory) / 'data/processed/personnel' / records[0]['document']).exists())
