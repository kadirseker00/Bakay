#!/usr/bin/env bash
# Mevcut /opt/bakay kurulumu için; git pull + yeniden derleme sonrasında root çalıştırır.
# Ağ listesini BT doğrular. Betik canlı veriyi veya API anahtarını değiştirmez.
set -euo pipefail
if [[ "$EUID" -ne 0 || "$#" -ne 1 ]]; then
  echo "Kullanım: sudo bash deploy/harden-root.sh 'KURUM_CIDR,VPN_CIDR'" >&2
  exit 1
fi
cd /opt/bakay
runtime_node="$(readlink -f /opt/bakay/runtime/node)"
case "$runtime_node" in /opt/bakay/runtime/*) ;; *) echo "Beklenmeyen Node yolu" >&2; exit 1 ;; esac
test -f frontend/.next/BUILD_ID
test -f /etc/bakay/backend.env
backend/.venv/bin/python deploy/configure-public-security.py --monitor-networks "$1" --check
backend/.venv/bin/python - <<'PY'
import json
from pathlib import Path
version=Path('VERSION').read_text().strip()
assert version==json.loads(Path('frontend/package.json').read_text())['version']
assert version==json.loads(Path('frontend/package-lock.json').read_text())['version']
assert json.loads(Path('frontend/node_modules/next/package.json').read_text())['version']=='15.5.29'
print('Paket sürümleri kontrol edildi. Arayüz bu committen yeniden derlenmiş olmalıdır.')
PY
site_path="$(readlink -f /etc/apache2/sites-enabled/bakai.conf)"
test -f "$site_path"
previous_web_user="$(systemctl show bakay-frontend.service -p User --value)"
previous_web_group="$(systemctl show bakay-frontend.service -p Group --value)"
if [[ "$previous_web_user" != bakay && "$previous_web_user" != bakay-web ]]; then
  echo "Beklenmeyen frontend hesabı; önce kurulum incelenmeli." >&2
  exit 1
fi
if [[ "$previous_web_group" != bakay && "$previous_web_group" != bakay-web ]]; then
  echo "Beklenmeyen frontend grubu; önce kurulum incelenmeli." >&2
  exit 1
fi
backup_path="/var/backups/bakay/security-$(date -u +%Y%m%dT%H%M%SZ)"
install -d -m 0700 "$backup_path"
cp -p /etc/bakay/backend.env "$backup_path/backend.env"
cp -p "$site_path" "$backup_path/apache.conf"
cp -p /etc/systemd/system/bakay-backend.service /etc/systemd/system/bakay-frontend.service "$backup_path/"
if [[ -f /etc/bakay/monitor-networks.apache ]]; then cp -p /etc/bakay/monitor-networks.apache "$backup_path/"; fi
git rev-parse HEAD > "$backup_path/revision.txt"
changed=false
services_stopped=false
rollback() {
  result=$?
  trap - ERR
  if [[ "$changed" == true ]]; then
    set +e
    cp -p "$backup_path/backend.env" /etc/bakay/backend.env
    cp -p "$backup_path/apache.conf" "$site_path"
    cp -p "$backup_path/bakay-backend.service" "$backup_path/bakay-frontend.service" /etc/systemd/system/
    if [[ -f "$backup_path/monitor-networks.apache" ]]; then
      cp -p "$backup_path/monitor-networks.apache" /etc/bakay/monitor-networks.apache
    fi
    # Eski frontend hesabının dosya erişimini koru; yeni kullanıcıya backend grubunu verme.
    chown -R "root:$previous_web_group" /opt/bakay/frontend "$runtime_node"
    chown -R "$previous_web_user:$previous_web_group" /opt/bakay/frontend/.next
    systemctl daemon-reload
    if [[ "$services_stopped" == true ]]; then
      systemctl restart bakay-backend.service bakay-frontend.service
    fi
    apache2ctl configtest && systemctl reload apache2
    echo "İşlem başarısız; ortam/servis/Apache ayarları geri alındı. Yedek: $backup_path" >&2
  fi
  exit "$result"
}
trap rollback ERR
if ! id -u bakay-web >/dev/null 2>&1; then
  useradd --system --user-group --home-dir /nonexistent --no-create-home --shell /usr/sbin/nologin bakay-web
fi
# Yeniden başlatmadan önce Apache ayarı doğrulanır; hata halinde eski dosya korunur.
changed=true
backend/.venv/bin/python deploy/configure-public-security.py --monitor-networks "$1"
python3 deploy/render-apache.py "$site_path" deploy/apache-proxy.inc
if ! apache2ctl configtest; then
  cp -p "$backup_path/apache.conf" "$site_path"
  cp -p "$backup_path/backend.env" /etc/bakay/backend.env
  echo "Apache testi başarısız; ortam ve site dosyası geri alındı. Yedek: $backup_path" >&2
  false # ERR tuzağı geri dönüşü tamamlar.
fi
services_stopped=true
systemctl stop bakay-frontend.service bakay-backend.service
# SQLite'ın güvenli kopyası; indeks ve çalışma verisi olduğu yerde kalır.
backend/.venv/bin/python - "$backup_path" <<'PY'
from pathlib import Path
import sqlite3,sys
from dotenv import dotenv_values
values=dotenv_values('/etc/bakay/backend.env')
path=Path(values.get('DB_PATH','data/bakay.db'))
with sqlite3.connect(path) as source, sqlite3.connect(Path(sys.argv[1])/'bakay.db') as destination:
    source.backup(destination)
PY
chmod 0711 /opt/bakay /opt/bakay/runtime
chown -R root:bakay-web frontend "$runtime_node"
chmod -R u+rwX,g+rX,g-w,o-rwx frontend "$runtime_node"
chown -R bakay-web:bakay-web frontend/.next
chmod 0700 data /var/lib/bakay
install -m 0644 deploy/bakay-backend.service deploy/bakay-frontend.service /etc/systemd/system/
systemctl daemon-reload
systemd-analyze verify /etc/systemd/system/bakay-backend.service /etc/systemd/system/bakay-frontend.service
systemctl start bakay-backend.service bakay-frontend.service
if ! curl --fail --silent --show-error --retry 20 --retry-connrefused --retry-delay 2 --max-time 180 http://127.0.0.1:8000/health >/dev/null; then
  echo "Backend doğrulanamadı. Servis günlüklerini ve geri dönüş rehberini inceleyin. Yedek: $backup_path" >&2
  false # ERR tuzağı geri dönüşü tamamlar.
fi
curl --fail --silent --show-error --retry 5 --retry-connrefused --retry-delay 2 --max-time 20 http://127.0.0.1:3000/ >/dev/null
runuser -u bakay-web -- test ! -r /etc/bakay/backend.env
runuser -u bakay-web -- test ! -r /opt/bakay/data/bakay.db
systemctl reload apache2
trap - ERR
printf 'Kurulum uygulandı; son HTTPS güvenlik/oturum/sürüm kontrolünü tamamlayın. Yedek: %s\n' "$backup_path"
