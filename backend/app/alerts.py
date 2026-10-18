"""Kalıcı alarm geçişleri ve TLS üzerinden yeniden denenebilir e-posta kuyruğu."""
from __future__ import annotations

import json
import smtplib
import sqlite3
import ssl
import time
from contextlib import contextmanager, closing
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from email.utils import formataddr
from pathlib import Path
from zoneinfo import ZoneInfo

SCHEMA = '''
CREATE TABLE IF NOT EXISTS ops_alerts (
 key TEXT PRIMARY KEY, title TEXT NOT NULL, message TEXT NOT NULL, severity TEXT NOT NULL,
 active INTEGER NOT NULL DEFAULT 0, bad_ticks INTEGER NOT NULL DEFAULT 0,
 good_ticks INTEGER NOT NULL DEFAULT 0, changed_at TEXT NOT NULL, checked_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS ops_alert_events (
 id INTEGER PRIMARY KEY, key TEXT NOT NULL, state TEXT NOT NULL, title TEXT NOT NULL,
 message TEXT NOT NULL, ts TEXT NOT NULL, delivered_at TEXT, attempts INTEGER NOT NULL DEFAULT 0,
 next_attempt REAL NOT NULL DEFAULT 0, error_type TEXT);
'''


@contextmanager
def connect(config):
    connection = sqlite3.connect(config.db_file, timeout=10)
    connection.row_factory = sqlite3.Row
    try:
        with connection:
            connection.executescript(SCHEMA)
            yield connection
    finally:
        connection.close()


def backup_status(config):
    try:
        data = json.loads(Path(config.backup_status_path).read_text())
        if not isinstance(data, dict):
            raise ValueError('invalid_backup_status')
        # Dosya yolları, Drive hesabı, OAuth veya şifreleme anahtarları dışarı çıkmaz.
        keys = ('local_enabled', 'remote_configured', 'last_local_at', 'last_remote_at',
                'last_restore_test_at', 'last_error', 'last_backup_bytes', 'index_fingerprint')
        result = {key: data.get(key) for key in keys}
        for key in ('last_local_at', 'last_remote_at', 'last_restore_test_at'):
            value = result[key]
            try:
                parsed = datetime.fromisoformat(value)
                if parsed.tzinfo is None:
                    raise ValueError('missing_timezone')
            except (ValueError, TypeError):
                result[key] = None
        return result
    except (OSError, ValueError, TypeError):
        return {'local_enabled': False, 'remote_configured': False}


def email_ready(config):
    if not (config.alert_email_to and config.alert_email_from):
        return False
    if config.alert_email_provider == 'ses':
        return bool(config.alert_ses_region and config.alert_ses_access_key_id and config.alert_ses_secret_access_key)
    return bool(config.alert_smtp_host)


def evaluate(config, sample, now=None):
    now = now or datetime.now(timezone.utc)
    ts = now.isoformat()
    local = now.astimezone(ZoneInfo('Asia/Bishkek'))
    cutoff = local.replace(hour=0, minute=0, second=0, microsecond=0).astimezone(timezone.utc).isoformat()
    rules = []
    for key, check in sample['checks'].items():
        label = {'backend': 'Bilgi servisi', 'frontend': 'Web arayüzü', 'https': 'HTTPS erişimi'}[key]
        rules.append(('health_'+key, label+' erişim sorunu',
                      'Sağlık kontrolü başarısız; bağlantı veya yanıt süresi kontrol edilmeli.',
                      'critical', not check['ok'], config.alert_failure_ticks))
    resource = sample.get('resources', {})
    for kind, label, limit in (('disk', 'Disk', config.alert_disk_percent),
                               ('memory', 'RAM', config.alert_memory_percent)):
        total, used = resource.get(kind+'_total_bytes'), resource.get(kind+'_used_bytes')
        if total and used is not None:
            percent = used*100/total
            rules.append((kind, label+' kullanım sınırı', f'{label} kullanımı %{percent:.1f}; uyarı eşiği %{limit:g}.',
                          'warning', percent >= limit, config.alert_failure_ticks))
    backup = backup_status(config)
    if backup.get('local_enabled'):
        last = backup.get('last_local_at')
        stale = not last or not 0 <= (now-datetime.fromisoformat(last)).total_seconds() <= 30*3600
        rules.append(('backup_local', 'Yerel yedek gecikti', 'Son doğrulanmış yerel yedek 30 saatten eski veya henüz alınamadı.',
                      'critical', stale, config.alert_failure_ticks))
        if backup.get('remote_configured'):
            last = backup.get('last_remote_at')
            stale = not last or not 0 <= (now-datetime.fromisoformat(last)).total_seconds() <= 30*3600
            rules.append(('backup_remote', 'Drive yedeği gecikti', 'Son doğrulanmış Drive aktarımı 30 saatten eski veya henüz yapılmadı.',
                          'critical', stale, config.alert_failure_ticks))
    with connect(config) as connection:
        connection.execute('BEGIN IMMEDIATE')
        daily = connection.execute('SELECT COALESCE(SUM(cost_usd),0), SUM(CASE WHEN cost_usd IS NULL THEN 1 ELSE 0 END) FROM llm_calls WHERE ts>=?', (cutoff,)).fetchone()
        rules.append(('cost_daily', 'Günlük API maliyeti eşiği',
                      f'{local.date()}: kaydedilmiş tahmini API maliyeti {daily[0]:.6f} USD; uyarı eşiği {config.alert_daily_usd:g} USD. Bu tutar fatura/kalan kredi değildir.',
                      'warning', daily[0] >= config.alert_daily_usd, 1))
        rules.append(('cost_unknown', 'API maliyetinde eksik sayaç', 'Bugünkü en az bir API çağrısının maliyeti bilinmiyor; paneldeki toplam eksik olabilir.',
                      'warning', bool(daily[1]), 1))
        recent = (now-timedelta(minutes=15)).isoformat()
        count, failures = connection.execute('SELECT COUNT(*),SUM(CASE WHEN status>=500 THEN 1 ELSE 0 END) FROM monitor_events WHERE ts>=?', (recent,)).fetchone()
        rules.append(('errors', 'API hata oranı arttı', f'Son 15 dakikada {failures or 0}/{count} istek sunucu hatasıyla sonuçlandı.',
                      'critical', count >= 10 and (failures or 0) >= 5 and failures/count >= .2, config.alert_failure_ticks))
        for key, title, message, severity, bad, ticks in rules:
            previous = connection.execute('SELECT * FROM ops_alerts WHERE key=?', (key,)).fetchone()
            active = bool(previous and previous['active'])
            bad_ticks = (previous['bad_ticks'] if previous else 0)+1 if bad else 0
            good_ticks = (previous['good_ticks'] if previous else 0)+1 if not bad else 0
            updated = active or bad_ticks >= ticks if bad else active and good_ticks < config.alert_recovery_ticks
            changed = not previous or active != updated
            changed_at = ts if changed else previous['changed_at']
            if active != updated:
                connection.execute('INSERT INTO ops_alert_events (key,state,title,message,ts) VALUES (?,?,?,?,?)',
                                   (key, 'active' if updated else 'resolved', title, message, ts))
            connection.execute('''INSERT INTO ops_alerts VALUES (?,?,?,?,?,?,?,?,?)
              ON CONFLICT(key) DO UPDATE SET title=excluded.title,message=excluded.message,
              severity=excluded.severity,active=excluded.active,bad_ticks=excluded.bad_ticks,
              good_ticks=excluded.good_ticks,changed_at=excluded.changed_at,checked_at=excluded.checked_at''',
                               (key,title,message,severity,int(updated),bad_ticks,good_ticks,changed_at,ts))
        connection.execute('DELETE FROM ops_alert_events WHERE ts<?', ((now-timedelta(days=31)).isoformat(),))


def send_email(config, event):
    message = EmailMessage()
    message['From'], message['To'] = formataddr(('BAKAI', config.alert_email_from)), config.alert_email_to
    state = 'UYARI' if event['state'] == 'active' else 'DÜZELDİ'
    message['Subject'] = f"BAKAI · {state} · {event['title']}"
    message['Message-ID'] = f"<bakai-alert-{event['id']}@bakai.manas.edu.kg>"
    message.set_content(f"{event['title']}\nDurum: {state}\n{event['message']}\n\nYönetim paneli: {config.monitor_public_url.rstrip('/')}/monitor\nZaman: {event['ts']}\n")
    if config.alert_email_provider == 'ses':
        import boto3
        from botocore.config import Config
        # Gönderim tekrarını kuyruk yönetir; belirsiz SDK hatasında çift mail üretmeyelim.
        with closing(boto3.client('ses', region_name=config.alert_ses_region,
                          aws_access_key_id=config.alert_ses_access_key_id,
                          aws_secret_access_key=config.alert_ses_secret_access_key,
                          config=Config(connect_timeout=5, read_timeout=5,
                                        retries={'total_max_attempts': 1}))) as client:
            client.send_raw_email(Source=str(message['From']),
                                  Destinations=[config.alert_email_to],
                                  RawMessage={'Data': message.as_bytes()})
        return
    context = ssl.create_default_context()
    if config.alert_smtp_security == 'ssl':
        server = smtplib.SMTP_SSL(config.alert_smtp_host, config.alert_smtp_port, timeout=5, context=context)
    else:
        server = smtplib.SMTP(config.alert_smtp_host, config.alert_smtp_port, timeout=5)
    with server:
        if config.alert_smtp_security == 'starttls':
            server.starttls(context=context)
            server.ehlo()
        if config.alert_smtp_username:
            server.login(config.alert_smtp_username, config.alert_smtp_password)
        refused = server.send_message(message)
        if refused:
            raise smtplib.SMTPException('recipient_refused')


def deliver_one(config, sender=None, clock=None):
    """Her yoklamada en çok bir bildirim; yalnız açılış/kapanış, değişmeyende sessiz."""
    if not email_ready(config):
        return
    now = (clock or time.time)()
    with connect(config) as connection:
        connection.execute('BEGIN IMMEDIATE')
        events = connection.execute('''SELECT e.*,a.active FROM ops_alert_events e JOIN ops_alerts a ON a.key=e.key
           WHERE e.delivered_at IS NULL AND e.next_attempt<=? ORDER BY e.id LIMIT 20''', (now,)).fetchall()
        event = None
        for candidate in events:
            obsolete = (candidate['state'] == 'active') != bool(candidate['active'])
            latest = connection.execute('SELECT MAX(id) FROM ops_alert_events WHERE key=?', (candidate['key'],)).fetchone()[0]
            obsolete = obsolete or candidate['id'] != latest
            if candidate['state'] == 'resolved':
                prior = connection.execute("SELECT delivered_at FROM ops_alert_events WHERE key=? AND state='active' AND id<? ORDER BY id DESC LIMIT 1", (candidate['key'],candidate['id'])).fetchone()
                obsolete = obsolete or not prior or not prior['delivered_at'] or prior['delivered_at']=='skipped'
            if obsolete:
                connection.execute("UPDATE ops_alert_events SET delivered_at='skipped' WHERE id=?", (candidate['id'],))
            else:
                event = candidate
                connection.execute('UPDATE ops_alert_events SET next_attempt=? WHERE id=?', (now+120,candidate['id']))
                break
    if event is None:
        return
    try:
        (sender or send_email)(config, event)
        delivered, error = datetime.fromtimestamp(now,timezone.utc).isoformat(), None
    except Exception as exception:
        delivered, error = None, type(exception).__name__
    with connect(config) as connection:
        attempts = event['attempts']+1
        connection.execute('UPDATE ops_alert_events SET delivered_at=?,attempts=?,next_attempt=?,error_type=? WHERE id=?',
                           (delivered,attempts,now+min(3600,60*2**min(attempts-1,6)),error,event['id']))


def snapshot(config):
    with connect(config) as connection:
        active = [dict(row) for row in connection.execute('SELECT key,title,message,severity,changed_at FROM ops_alerts WHERE active=1 ORDER BY changed_at DESC')]
        recent = [dict(row) for row in connection.execute('SELECT ts,title,state,delivered_at,error_type FROM ops_alert_events ORDER BY id DESC LIMIT 10')]
        evaluated = connection.execute('SELECT MAX(checked_at) FROM ops_alerts').fetchone()[0]
    return {'active':active,'recent':recent,'email_configured':email_ready(config),
            'daily_usd_limit':config.alert_daily_usd,'evaluated_at':evaluated,'backup':backup_status(config)}
