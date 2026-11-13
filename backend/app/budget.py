"""Bişkek takvim gününde her ücretli çağrı için kalıcı, atomik harcama rezervasyonu.

Bu yerel sayaç sağlayıcı faturası değildir. Zaman aşımı/eksik kullanım durumunda
rezervasyon tutulur; süreç yeniden başlasa da belirsiz maliyet sıfırlanmaz.
"""
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_CEILING
import sqlite3
from uuid import uuid4
from zoneinfo import ZoneInfo

from fastapi import HTTPException

from app import monitoring

SCALE = 1_000_000_000
SCHEMA = '''
CREATE TABLE IF NOT EXISTS budget_days (day TEXT PRIMARY KEY, opening INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS budget_calls (
 id TEXT PRIMARY KEY, day TEXT NOT NULL, reserved INTEGER NOT NULL,
 charged INTEGER, state TEXT NOT NULL, created_at TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS budget_calls_day ON budget_calls(day);
'''


def units(value):
    amount = Decimal(str(value))
    if not amount.is_finite() or amount < 0:
        raise ValueError('Geçersiz maliyet')
    return int((amount * SCALE).to_integral_value(rounding=ROUND_CEILING))


def unavailable():
    return HTTPException(503, 'Harcama kontrolü şu anda hazır değil. Biraz sonra yeniden deneyin.',
                         headers={'Cache-Control': 'no-store'})


class Budget:
    def __init__(self, config, clock=None):
        self.config = config
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    @contextmanager
    def connect(self):
        connection = sqlite3.connect(self.config.db_file, timeout=10)
        try:
            connection.executescript(SCHEMA)
            with connection:
                yield connection
        finally:
            connection.close()

    def period(self):
        now = self.clock().astimezone(ZoneInfo('Asia/Bishkek'))
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
        return now, start, end

    def opening(self, connection, start, end):
        day = start.date().isoformat()
        existing = connection.execute('SELECT opening FROM budget_days WHERE day=?', (day,)).fetchone()
        if existing:
            return existing[0]
        # İlk etkinleştirmeden önce bugün yapılan çağrıları da hesaba kat.
        # Tutarı bilinmeyen eski çağrı varsa o gün için kapalı kal: yönetici inceler.
        row = connection.execute('''SELECT COALESCE(SUM(cost_usd),0),
            COALESCE(SUM(CASE WHEN cost_usd IS NULL THEN 1 ELSE 0 END),0)
            FROM llm_calls WHERE ts>=? AND ts<?''',
            (start.astimezone(timezone.utc).isoformat(), end.astimezone(timezone.utc).isoformat())).fetchone()
        amount = units(self.config.budget_daily_usd) if row[1] else units(row[0])
        connection.execute('INSERT INTO budget_days VALUES (?,?)', (day, amount))
        return amount

    @staticmethod
    def used(connection, day):
        return connection.execute('SELECT COALESCE(SUM(COALESCE(charged,reserved)),0) FROM budget_calls WHERE day=?',
                                  (day,)).fetchone()[0]

    def reserve(self, model, prompt, system, max_tokens):
        if not self.config.budget_enabled:
            return None
        # Yalnız metin, tek user + system, araç/cache yok. UTF-8 bayt sayısı +
        # geniş protokol payı ve en yüksek bilinen fiyatla ihtiyatlı üst tahmin.
        incoming = len(prompt.encode()) + len((system or '').encode()) + 4096
        if model == 'claude-haiku-5-5' or model.startswith('claude-haiku-5-5-'):
            estimate = (Decimal(incoming) * Decimal('0.5') + Decimal(max_tokens) * Decimal('2.5')) / 1_000_000
        elif model == 'claude-sonnet-5-5' or model.startswith('claude-sonnet-5-5-'):
            estimate = (Decimal(incoming) * 2 + Decimal(max_tokens) * 10) / 1_000_000
        else:
            raise unavailable()  # Yeni modelin fiyatı bilinmeden ücretli istek yok.
        now, start, end = self.period()
        day, identifier = start.date().isoformat(), uuid4().hex
        try:
            with self.connect() as connection:
                connection.execute('BEGIN IMMEDIATE')
                used = self.opening(connection, start, end) + self.used(connection, day)
                if used + units(estimate) > units(self.config.budget_daily_usd):
                    raise HTTPException(429, {'code': 'budget_exhausted',
                        'message': 'Bugünkü hizmet bütçesine ulaşıldı. Bişkek saatiyle gece 00.00’dan sonra yeniden deneyebilirsiniz.'},
                        headers={'Retry-After': str(max(1, int((end-now).total_seconds()))), 'Cache-Control': 'no-store'})
                connection.execute('INSERT INTO budget_calls VALUES (?,?,?,?,?,?)',
                                   (identifier, day, units(estimate), None, 'pending', now.isoformat()))
        except sqlite3.Error:
            raise unavailable() from None
        return identifier

    def settle(self, identifier, model, usage):
        if identifier is None:
            return
        cost = monitoring.cost_estimate(model, usage)
        if cost is None:
            return  # Eksik sayaçta tüm rezervasyon tutulur.
        try:
            with self.connect() as connection:
                connection.execute('BEGIN IMMEDIATE')
                row = connection.execute('SELECT day,reserved FROM budget_calls WHERE id=? AND state=?',
                                         (identifier, 'pending')).fetchone()
                if not row:
                    return
                connection.execute("UPDATE budget_calls SET charged=?,state='accounted' WHERE id=?", (units(cost), identifier))
                if units(cost) > row[1]:
                    # Fiyat/token varsayımı bozulursa sonraki çağrılara kapat.
                    connection.execute('UPDATE budget_days SET opening=MAX(opening,?) WHERE day=?',
                                       (units(self.config.budget_daily_usd), row[0]))
        except sqlite3.Error:
            raise unavailable() from None

    def snapshot(self):
        if not self.config.budget_enabled:
            return {'enabled': False, 'daily_limit_usd': self.config.budget_daily_usd}
        now, start, end = self.period()
        try:
            with self.connect() as connection:
                connection.execute('BEGIN IMMEDIATE')
                opening = self.opening(connection, start, end)
                used = opening + self.used(connection, start.date().isoformat())
                pending = connection.execute("SELECT COUNT(*) FROM budget_calls WHERE day=? AND state='pending'",
                                             (start.date().isoformat(),)).fetchone()[0]
        except sqlite3.Error:
            raise unavailable() from None
        return {'enabled': True, 'daily_limit_usd': self.config.budget_daily_usd,
                'used_and_reserved_usd': used/SCALE, 'pending_calls': pending,
                'remaining_usd': max(0, self.config.budget_daily_usd-used/SCALE),
                'resets_at': end.isoformat(), 'timezone': 'Asia/Bishkek'}
