"""Root oturumunda panel parolasını ayarla; düz parola kaydedilmez/yazdırılmaz."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import getpass
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'backend'))
from app.monitor_auth import password_hash


def main() -> None:
    if os.geteuid() != 0:
        raise SystemExit('Bu aracı root oturumunda çalıştırın.')
    parser = argparse.ArgumentParser(description='BAKAI panel girişini ayarla')
    parser.add_argument('--hash-stdin', action='store_true', help='Güvenli giriş aracının ürettiği hash JSONunu stdin üzerinden oku')
    args = parser.parse_args()
    if args.hash_stdin:
        data = json.load(sys.stdin)
    else:
        password = getpass.getpass('Panel için ayrı parola (en az 12 karakter): ')
        confirmation = getpass.getpass('Parolayı tekrar girin: ')
        if password != confirmation or len(password) < 12:
            raise SystemExit('Parolalar eşleşmeli ve en az 12 karakter olmalı.')
        data = {'password_hash': password_hash(password), 'session_secret': secrets.token_hex(32)}
        del password, confirmation
    if not re.fullmatch(r'scrypt\$[0-9a-f]{32}\$[0-9a-f]{128}', data.get('password_hash', '')):
        raise SystemExit('Parola hash biçimi geçersiz.')
    if not re.fullmatch(r'[0-9a-f]{64}', data.get('session_secret', '')):
        raise SystemExit('Oturum sırrı biçimi geçersiz.')
    path = Path('/etc/bakay/backend.env')
    backups = Path('/var/backups/bakay')
    backups.mkdir(mode=0o700, parents=True, exist_ok=True)
    backup = backups / ('backend.env.before-monitor.' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '.' + secrets.token_hex(3))
    shutil.copy2(path, backup)
    os.chmod(backup, 0o600)
    updates = {'MONITOR_USERNAME': 'adminbakai', 'MONITOR_PASSWORD_HASH': data['password_hash'],
               'MONITOR_SESSION_SECRET': data['session_secret'],
               'MONITOR_PUBLIC_URL': 'https://bakai.manas.edu.kg', 'MONITOR_SHOW_QUERY_DETAILS': 'true'}
    lines, seen = [], set()
    for line in path.read_text().splitlines():
        key = line.partition('=')[0].strip()
        if key in updates:
            if key not in seen:
                lines.append(key + '=' + updates[key])
                seen.add(key)
        else:
            lines.append(line)
    lines.extend(key + '=' + value for key, value in updates.items() if key not in seen)
    fd, temporary = tempfile.mkstemp(dir=path.parent, prefix='.backend.env.')
    try:
        with os.fdopen(fd, 'w') as stream:
            stream.write('\n'.join(lines) + '\n')
        os.chmod(temporary, 0o600)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    print('Panel hesabı ayarlandı: adminbakai. Yeni ayar backend yeniden başlatılınca etkinleşir.')
    print('Özel ortam yedeği:', backup)


if __name__ == '__main__':
    main()
