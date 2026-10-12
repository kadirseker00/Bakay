#!/usr/bin/env bash
# Yalnız yönetici çalıştırır: localhost doğrulamasından sonra Apache'yi bağlar.
set -euo pipefail
if [[ "$EUID" -ne 0 ]]; then
  echo "Bu komutu root hesabıyla çalıştırın." >&2
  exit 1
fi
cd /opt/bakay
test -f /etc/bakay/backend.env
site_path="$(readlink -f /etc/apache2/sites-enabled/bakai.conf)"
test -f "$site_path"
install -d -m 0700 /var/backups/bakay
backup_path="/var/backups/bakay/bakai.conf.$(date -u +%Y%m%dT%H%M%SZ)"
cp -p -- "$site_path" "$backup_path"

systemctl start bakay-backend.service bakay-frontend.service
curl --fail --silent --show-error --retry 5 --retry-connrefused --retry-delay 2 --max-time 180 http://127.0.0.1:8000/health > runtime/publish-health.json
python3 - <<'PY'
import json
from pathlib import Path
health = json.loads(Path('runtime/publish-health.json').read_text())
assert health['status'] == 'ok' and health['indexed_chunks'] == 39659, health
assert health['llm_provider'] == 'anthropic', health
print('Backend ve 39.659 parça doğrulandı.')
PY
curl --fail --silent --show-error --retry 5 --retry-connrefused --retry-delay 2 --max-time 20 http://127.0.0.1:3000/ > /dev/null
a2enmod proxy proxy_http headers
python3 deploy/render-apache.py "$site_path" deploy/apache-proxy.inc
if ! apache2ctl configtest; then
  cp -p -- "$backup_path" "$site_path"
  echo "Apache kontrolü başarısız; önceki dosya geri yüklendi." >&2
  exit 1
fi
if ! systemctl reload apache2; then
  cp -p -- "$backup_path" "$site_path"
  apache2ctl configtest && systemctl reload apache2
  echo "Apache yüklemesi başarısız; önceki ayarlar geri yüklendi." >&2
  exit 1
fi
if ! curl --fail --silent --show-error --max-time 180 --resolve bakai.manas.edu.kg:443:127.0.0.1 https://bakai.manas.edu.kg/api/health > runtime/public-health.json; then
  cp -p -- "$backup_path" "$site_path"
  apache2ctl configtest && systemctl reload apache2
  echo "HTTPS sağlık kontrolü başarısız; Apache ayarları geri yüklendi." >&2
  exit 1
fi
systemctl enable bakay-backend.service bakay-frontend.service
echo "Yayın hazır: https://bakai.manas.edu.kg/"
echo "Apache yedeği: $backup_path"
