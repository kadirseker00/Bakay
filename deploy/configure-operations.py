"""Özel SMTP/Turnstile ayarlarını gizli girişle veya stdin ile atomik günceller."""
import argparse
from datetime import datetime,timezone
import getpass
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile

CAPTCHA={'CAPTCHA_SITE_KEY','CAPTCHA_SECRET_KEY','CAPTCHA_HOSTNAME'}
MAIL={'ALERT_EMAIL_FROM','ALERT_EMAIL_TO','ALERT_SMTP_HOST','ALERT_SMTP_PORT','ALERT_SMTP_SECURITY','ALERT_SMTP_USERNAME','ALERT_SMTP_PASSWORD'}
SES={'ALERT_EMAIL_PROVIDER','ALERT_EMAIL_FROM','ALERT_EMAIL_TO','ALERT_SES_REGION','ALERT_SES_ACCESS_KEY_ID','ALERT_SES_SECRET_ACCESS_KEY'}

def update(path,values):
    if not values or not set(values)<=CAPTCHA|MAIL|SES|{'ALERT_DAILY_USD'}:
        raise ValueError('unsupported_settings')
    if any(not isinstance(v,str) or '\n' in v or '\r' in v or '\0' in v for v in values.values()):
        raise ValueError('invalid_value')
    if 'CAPTCHA_SITE_KEY' in values:
        for key in ('CAPTCHA_SITE_KEY','CAPTCHA_SECRET_KEY'):
            if not re.fullmatch(r'[A-Za-z0-9_-]{10,200}',values.get(key,'')):
                raise ValueError('invalid_turnstile_key')
        if values.get('CAPTCHA_HOSTNAME')!='bakai.manas.edu.kg':
            raise ValueError('invalid_hostname')
    if values.get('ALERT_EMAIL_PROVIDER') == 'ses':
        if not SES<=set(values) or any(not values[k] for k in SES):
            raise ValueError('ses_settings_incomplete')
        if not re.fullmatch(r'[a-z]{2}(?:-[a-z]+)+-\d',values['ALERT_SES_REGION']):
            raise ValueError('invalid_region')
    elif set(values)&MAIL:
        if not MAIL<=set(values) or values['ALERT_SMTP_SECURITY'] not in ('ssl','starttls'):
            raise ValueError('mail_settings_incomplete')
        if not 1<=int(values['ALERT_SMTP_PORT'])<=65535:
            raise ValueError('invalid_port')
    if set(values)&(MAIL|SES):
        for key in ('ALERT_EMAIL_FROM','ALERT_EMAIL_TO'):
            if not re.fullmatch(r'[^\s<>@]+@[^\s<>@]+',values[key]):
                raise ValueError('invalid_address')
    lines=[];seen=set()
    for line in path.read_text().splitlines():
        key=line.partition('=')[0].strip()
        if key in values:
            if key not in seen:
                lines.append(key+'='+json.dumps(values[key],ensure_ascii=False));seen.add(key)
        else: lines.append(line)
    lines.extend(k+'='+json.dumps(v,ensure_ascii=False) for k,v in values.items() if k not in seen)
    fd,temporary=tempfile.mkstemp(dir=path.parent,prefix='.ops-env-')
    try:
        with os.fdopen(fd,'w') as stream:
            stream.write('\n'.join(lines)+'\n'); stream.flush();os.fsync(stream.fileno())
        os.chmod(temporary,0o600);os.replace(temporary,path)
    finally:
        Path(temporary).unlink(missing_ok=True)

def main():
    if os.geteuid()!=0: raise SystemExit('Root oturumu gerekli.')
    parser=argparse.ArgumentParser()
    parser.add_argument('mode',choices=['captcha','mail','ses','stdin']);args=parser.parse_args()
    if args.mode=='stdin': values=json.load(sys.stdin)
    elif args.mode=='captcha':
        values={'CAPTCHA_SITE_KEY':input('Turnstile site key: ').strip(),'CAPTCHA_SECRET_KEY':getpass.getpass('Turnstile secret key (gizli): ').strip(),'CAPTCHA_HOSTNAME':'bakai.manas.edu.kg'}
    elif args.mode=='ses':
        values={'ALERT_EMAIL_PROVIDER':'ses','ALERT_EMAIL_FROM':input('Gönderen e-posta: ').strip(),
                'ALERT_EMAIL_TO':input('Alıcı e-posta: ').strip(),'ALERT_SES_REGION':input('AWS bölgesi: ').strip(),
                'ALERT_SES_ACCESS_KEY_ID':getpass.getpass('SES access key ID (gizli): ').strip(),
                'ALERT_SES_SECRET_ACCESS_KEY':getpass.getpass('SES secret access key (gizli): ').strip(),'ALERT_DAILY_USD':'1'}
    else:
        security=input('SMTP TLS yöntemi (starttls/ssl): ').strip()
        values={'ALERT_EMAIL_PROVIDER':'smtp','ALERT_EMAIL_FROM':input('Gönderen e-posta: ').strip(),'ALERT_EMAIL_TO':input('Alıcı e-posta: ').strip(),
                'ALERT_SMTP_HOST':input('SMTP sunucusu: ').strip(),'ALERT_SMTP_SECURITY':security,
                'ALERT_SMTP_PORT':input('SMTP portu: ').strip(),'ALERT_SMTP_USERNAME':input('SMTP kullanıcı adı: ').strip(),
                'ALERT_SMTP_PASSWORD':getpass.getpass('SMTP parolası (gizli): '),'ALERT_DAILY_USD':'1'}
    path=Path('/etc/bakay/backend.env');directory=Path('/var/backups/bakay');directory.mkdir(parents=True,exist_ok=True,mode=0o700)
    target=directory/('backend.env.before-ops.'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
    shutil.copy2(path,target);os.chmod(target,0o600)
    update(path,values)
    print('Ayarlar kaydedildi. Backend yeniden başlatılınca etkinleşir; gizli değerler yazdırılmadı.')
if __name__=='__main__': main()
