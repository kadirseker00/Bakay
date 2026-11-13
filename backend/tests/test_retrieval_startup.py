"""Hazırlık ilk ziyaretçinin arama maliyetini üstlenir; LLM çağırmaz."""
import unittest
from unittest.mock import patch, Mock

from app import main
from app.rag import vectorstore


class RetrievalStartupTests(unittest.IsolatedAsyncioTestCase):
    async def test_warmup_finishes_before_lifespan_accepts_requests(self):
        guard = Mock()
        ready = []
        with patch.object(main.settings, 'retrieval_warmup', True), \
             patch.object(main.monitoring, 'initialize'), \
             patch.object(main.knowledge, 'initialize'), \
             patch.object(main.abuse, 'AbuseGuard', return_value=guard), \
             patch.object(vectorstore, 'warm_retrieval', side_effect=lambda: ready.append(True)):
            async with main.lifespan(main.app):
                self.assertEqual(ready, [True])
            guard.flush.assert_called_once()

    async def test_failed_preparation_does_not_accept_requests(self):
        with patch.object(main.settings, 'retrieval_warmup', True), \
             patch.object(main.monitoring, 'initialize'), \
             patch.object(main.knowledge, 'initialize'), \
             patch.object(main.abuse, 'AbuseGuard'), \
             patch.object(vectorstore, 'warm_retrieval', side_effect=RuntimeError('index unavailable')):
            with self.assertRaisesRegex(RuntimeError, 'index unavailable'):
                async with main.lifespan(main.app):
                    self.fail('Hazırlanmamış uygulama istek kabul etmemeli')

    async def test_warmup_uses_search_without_answer_pipeline(self):
        store = Mock()
        with patch.object(vectorstore, 'get_store', return_value=store), \
             patch.object(main.pipeline, 'answer', side_effect=AssertionError('LLM çağrılmamalı')):
            vectorstore.warm_retrieval()
        store.query.assert_called_once_with('Kırgızistan-Türkiye Manas Üniversitesi', top_k=1)
