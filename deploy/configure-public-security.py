"""Root ortamındaki sırları göstermeden güvenlik ayarlarını ve Apache ağ listesini eşleştir."""
import argparse
import ipaddress
import os
from pathlib import Path
import re
import tempfile
from urllib.parse import urlsplit
from dotenv import dotenv_values

parser = argparse.ArgumentParser()
parser.add_argument('--env', type=Path, default=Path('/etc/bakay/backend.env'))
parser.add_argument('--apache', type=Path, default=Path('/etc/bakay/monitor-networks.apache'))
parser.add_argument('--monitor-networks', required=True, help='BT tarafından doğrulanmış virgülle ayrılmış CIDR listesi')
parser.add_argument('--check', action='store_true')
args = parser.parse_args()
networks = [ipaddress.ip_network(value.strip()) for value in args.monitor_networks.split(',') if value.strip()]
if not networks or any(network.prefixlen == 0 for network in networks):
    raise SystemExit('Panel için açık /0 veya boş ağ listesi kabul edilmez.')
# SSH tüneliyle yönetim yolu korunur. Geniş özel ağları otomatik ekleme.
networks = list(dict.fromkeys([ipaddress.ip_network('127.0.0.1/32'), ipaddress.ip_network('::1/128'), *networks]))
values = dotenv_values(args.env)
for name in ('CAPTCHA_SITE_KEY', 'CAPTCHA_SECRET_KEY', 'CAPTCHA_HOSTNAME', 'MONITOR_SESSION_SECRET'):
    if not values.get(name) or (name == 'MONITOR_SESSION_SECRET' and len(values[name]) < 32):
        raise SystemExit(f'Eksik güvenlik ayarı: {name}; hiçbir dosya değiştirilmedi.')
public = urlsplit(values.get('MONITOR_PUBLIC_URL', ''))
if public.scheme != 'https' or public.hostname != values['CAPTCHA_HOSTNAME']:
    raise SystemExit('HTTPS yayın adresi ve Turnstile hostname eşleşmelidir.')
if values.get('LLM_PROVIDER', '').lower() != 'anthropic':
    raise SystemExit('Bu harcama kesicisi yalnız Anthropic sağlayıcısıyla doğrulandı.')
if args.check:
    print('Ön kontrol tamam: sırlar mevcut, HTTPS/hostname ve ağ listesi geçerli.')
    raise SystemExit(0)
updates = {'PUBLIC_SECURITY_ENABLED': 'true', 'VISITOR_SESSION_SECONDS': '1800',
           'RETRIEVAL_WARMUP': 'true',
           'ANTHROPIC_MAX_TOKENS': '1200',
           'BUDGET_ENABLED': 'true', 'BUDGET_DAILY_USD': '5',
           'MONITOR_ALLOWED_NETWORKS': ','.join(map(str, networks))}
content = args.env.read_text()
for name, value in updates.items():
    pattern = rf'(?m)^{name}=.*$'
    if re.search(pattern, content):
        content = re.sub(pattern, lambda _: name+'='+value, content)
    else:
        content = content.rstrip()+'\n'+name+'='+value+'\n'

def atomic_write(path, text, mode):
    descriptor, temporary = tempfile.mkstemp(dir=path.parent, prefix='.'+path.name+'.')
    try:
        with os.fdopen(descriptor, 'w') as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, mode)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)

atomic_write(args.env, content, 0o600)
atomic_write(args.apache, '# BT tarafından doğrulanmış panel ağları; frontend ve API için ortak.\nRequire ip '+ ' '.join(map(str, networks))+'\n', 0o644)
print('Güvenlik ayarları yazıldı; sırlar değiştirilmedi veya gösterilmedi.')
