"""Personel sorusu öğrenci düzeyine sapmaz; statü yanıtı konuyu korur."""
import unittest
from unittest.mock import Mock
from app.rag import pipeline
from app.rag.retrieval import needs_education_level
from app.schemas import ChatMessage


class StaffContextTests(unittest.TestCase):
    def test_staff_workload_does_not_ask_student_degree(self):
        hits=[{'title':'Lisans Yönetmeliği','text':'Lisans bölüm başkanı zorunlu ders yükü'},
              {'title':'Lisansüstü Yönetmeliği','text':'Lisansüstü bölüm başkanı zorunlu ders yükü'}]
        self.assertFalse(needs_education_level('bölüm başkanı zorunlu ders yükü kaçtır?',hits))
        self.assertFalse(needs_education_level('Öğretim üyesinin ek ders ücreti nedir?',hits))

    def test_teacher_asking_about_student_credit_transfer_still_needs_degree(self):
        hits=[{'title':'Lisans Yönetmeliği','text':'Lisans ders saydırma koşulları'},
              {'title':'Lisansüstü Yönetmeliği','text':'Lisansüstü ders saydırma koşulları'}]
        self.assertTrue(needs_education_level('Öğretim üyesiyim, ders saydırma koşulları nedir?',hits))
        self.assertTrue(needs_education_level('Öğretim görevlisiyim, ders saydırma koşulları nedir?',hits))

    def test_staff_role_reply_preserves_original_question_without_llm(self):
        question='bölüm başkanı zorunlu ders yükü kaçtır?'
        history=[ChatMessage(role='user',content=question),
                 ChatMessage(role='assistant',content=pipeline.NEEDS_LEVEL)]
        llm=Mock()
        for role in ('öğretim üyesiyim.','Ben bölüm başkanıyım','öğretim görevlisiyim'):
            self.assertTrue(pipeline._needs_history(role))
            resolved=pipeline._resolve_question(role,history,llm)
            self.assertIn(question,resolved)
            self.assertIn(role,resolved)
        llm.generate.assert_not_called()

    def test_role_alone_without_real_topic_requests_context(self):
        history=[ChatMessage(role='user',content='Öğretim üyesiyim'),
                 ChatMessage(role='assistant',content='Ne öğrenmek istiyorsunuz?')]
        self.assertIsNone(pipeline._resolve_question('Bölüm başkanıyım',history,Mock()))
