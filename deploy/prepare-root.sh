#!/usr/bin/env bash
# Yönetici çalıştırır: hazırlanmış dosyaları kurar; servisleri/yayını başlatmaz.
set -euo pipefail

if [[ "$EUID" -ne 0 ]]; then
  echo "Bu komutu root hesabıyla çalıştırın." >&2
  exit 1
fi

stage_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
project_root=/opt/bakay
if [[ "$stage_root" != "$project_root" && -e "$project_root" ]]; then
  echo "/opt/bakay zaten var; mevcut kurulumu incelemeden üzerine yazılmayacak." >&2
  exit 1
fi
if systemctl is-active --quiet bakay-backend.service || systemctl is-active --quiet bakay-frontend.service; then
  echo "BAKAY servisleri çalışıyor; hazırlık öncesi yönetici tarafından durdurulmalıdır." >&2
  exit 1
fi
for required_path in data/chroma/chroma.sqlite3 frontend/.next/BUILD_ID runtime/node/bin/node runtime/wheels deploy/requirements-linux.txt; do
  test -e "$stage_root/$required_path" || { echo "Eksik: $required_path" >&2; exit 1; }
done
if [[ ! -f "$stage_root/.env" && ! -f /etc/bakay/backend.env ]]; then
  echo "Backend ortam dosyası eksik." >&2
  exit 1
fi
(cd "$stage_root" && sha256sum --check --quiet runtime/wheels.sha256)

if ! id -u bakay >/dev/null 2>&1; then
  useradd --system --user-group --home-dir /var/lib/bakay --create-home --shell /usr/sbin/nologin bakay
fi
install -d -m 0750 -o bakay -g bakay /var/lib/bakay
install -d -m 0750 -o root -g bakay /etc/bakay
if [[ "$stage_root" != "$project_root" ]]; then
  mv -- "$stage_root" "$project_root"
fi
cd "$project_root"

if [[ -f .env ]]; then
  if [[ -e /etc/bakay/backend.env ]]; then
    echo "Mevcut /etc/bakay/backend.env korunuyor. Ortam değişikliğini yönetici incelemelidir."
  else
    python3 - <<'PY'
import os
from pathlib import Path
content = Path('.env').read_text()
content = content.replace('HF_HOME=/home/adminbakai/bakay/.cache/huggingface',
                          'HF_HOME=/var/lib/bakay/huggingface')
destination = Path('/etc/bakay/backend.env')
descriptor = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
with os.fdopen(descriptor, 'w') as stream:
    stream.write(content)
PY
  fi
  # Anahtarın uygulama çalışma ağacındaki kopyasını kaldır.
  rm -- .env
fi
if [[ -d .cache/huggingface && ! -e /var/lib/bakay/huggingface ]]; then
  mv -- .cache/huggingface /var/lib/bakay/huggingface
fi
test -d /var/lib/bakay/huggingface/hub/models--sentence-transformers--LaBSE
chown -R bakay:bakay /var/lib/bakay

# Taşınan venv'in mutlak yolları değişir; doğrulanmış Linux wheel'lerinden kur.
python3 -m venv --clear "$project_root/backend/.venv"
backend/.venv/bin/python -m pip install --no-index --find-links runtime/wheels -r deploy/requirements-linux.txt
backend/.venv/bin/python -m pip check
chown -R root:bakay "$project_root"
chmod -R u+rwX,g+rX,o-rwx "$project_root"
chown -R bakay:bakay data frontend/.next
chmod 0600 /etc/bakay/backend.env
install -m 0644 deploy/bakay-backend.service deploy/bakay-frontend.service /etc/systemd/system/
systemctl daemon-reload
systemd-analyze verify /etc/systemd/system/bakay-backend.service /etc/systemd/system/bakay-frontend.service
echo "Kurulum hazır. Servisler ve Apache yayını başlatılmadı."
echo "Yayına almak için: bash /opt/bakay/deploy/publish-root.sh"
