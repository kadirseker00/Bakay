"""Alarm geçişleri, CAPTCHA ve gerçek şifreli yedek geri yüklemesi."""
import importlib.util
import io
import json
import shutil
import sqlite3
import subprocess
import tempfile
import unittest
from datetime import datetime,timedelta,timezone
from pathlib import Path
from unittest.mock import patch
from email import policy
from email.parser import BytesParser
from fastapi import HTTPException
from app import alerts,captcha,monitoring
from app.abuse import AbuseGuard,Denied
from app.config import Settings

class OperationsTests(unittest.TestCase):
    def setUp(self):
        self.root=Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.cfg=Settings(_env_file=None,db_path=str(self.root/'test.db'),backup_status_path=str(self.root/'status.json'),monitor_session_secret='synthetic-secret')
        with patch.object(monitoring,'settings',self.cfg): monitoring.initialize()
        self.now=datetime(2026,10,13,2,tzinfo=timezone.utc)
        self.sample={'checks':{k:{'ok':True} for k in ('backend','frontend','https')},'resources':{}}
    def tick(self,n=1):
        for _ in range(n):
            alerts.evaluate(self.cfg,self.sample,self.now); self.now+=timedelta(minutes=1)
    def snap(self): return alerts.snapshot(self.cfg)
    def mail_ready(self):
        self.cfg.alert_email_to='ops@example.test'; self.cfg.alert_email_from='bakai@example.test'; self.cfg.alert_smtp_host='smtp.example.test'
    def test_three_failures_two_recoveries_and_flapping(self):
        self.sample['checks']['backend']['ok']=False
        self.tick(2); self.assertEqual(self.snap()['recent'],[])
        self.tick(2); self.assertEqual(len(self.snap()['recent']),1)
        self.sample['checks']['backend']['ok']=True
        self.tick(); self.assertEqual(len(self.snap()['active']),1)
        self.sample['checks']['backend']['ok']=False
        self.tick(); self.assertEqual(len(self.snap()['recent']),1)
        self.sample['checks']['backend']['ok']=True
        self.tick(2); self.assertEqual(self.snap()['recent'][0]['state'],'resolved')
        self.assertEqual(self.snap()['active'],[])
    def test_cost_bishkek_midnight_and_unknown_counters(self):
        with alerts.connect(self.cfg) as db:
            for ts,cost in [('2026-10-12T17:59:59+00:00',4),('2026-10-12T18:00:00+00:00',1),('2026-10-12T18:00:01+00:00',None)]:
                db.execute('INSERT INTO llm_calls (ts,query_id,model,status,latency_ms,cost_usd) VALUES (?,?,?,?,?,?)',(ts,'test','test','ok',1,cost))
        self.tick(); self.assertEqual({x['key'] for x in self.snap()['active']},{'cost_daily','cost_unknown'})
        self.assertIn('1.000000',next(x['message'] for x in self.snap()['active'] if x['key']=='cost_daily'))
        self.now=datetime(2026,10,13,18,1,tzinfo=timezone.utc)
        self.tick(2); self.assertEqual(self.snap()['active'],[])
    def test_malformed_backup_times_no_crash_or_secret_leak(self):
        (self.root/'status.json').write_text(json.dumps({'local_enabled':True,'remote_configured':True,'last_local_at':'bad','last_remote_at':'2026-10-12T00:00:00','secret':'DO-NOT-LEAK'}))
        self.tick(3); self.assertEqual({x['key'] for x in self.snap()['active']},{'backup_local','backup_remote'})
        self.assertNotIn('DO-NOT-LEAK',json.dumps(self.snap()))
        (self.root/'status.json').write_text('[]'); self.tick()
    def test_weekly_remote_only_alert_boundary_and_local_recovery(self):
        status=self.root/'status.json'
        status.write_text(json.dumps({'local_enabled':True,'last_local_at':None}))
        self.tick(3); self.assertEqual({x['key'] for x in self.snap()['active']},{'backup_local'})
        status.write_text(json.dumps({'local_enabled':False,'remote_only':True,'remote_configured':True,
                                     'last_remote_at':(self.now-timedelta(days=7)).isoformat()}))
        self.tick(2); self.assertEqual(self.snap()['active'],[])
        self.now+=timedelta(days=1)
        self.tick(3); self.assertEqual({x['key'] for x in self.snap()['active']},{'backup_remote'})
        self.assertIn('192 saat',self.snap()['active'][0]['message'])
    def test_retry_claim_once_and_recovery_delivery(self):
        self.mail_ready(); self.sample['checks']['backend']['ok']=False; self.tick(3); sent=[]
        def fail(c,e): raise OSError('private-password')
        alerts.deliver_one(self.cfg,fail,lambda:1000)
        alerts.deliver_one(self.cfg,lambda c,e:sent.append(e['state']),lambda:1001)
        self.assertEqual(sent,[])
        def success(c,e):
            alerts.deliver_one(c,lambda c,e:sent.append('duplicate'),lambda:1061)
            sent.append(e['state'])
        alerts.deliver_one(self.cfg,success,lambda:1060)
        alerts.deliver_one(self.cfg,success,lambda:1200)
        self.assertEqual(sent,['active'])
        self.sample['checks']['backend']['ok']=True; self.tick(2)
        alerts.deliver_one(self.cfg,lambda c,e:sent.append(e['state']),lambda:1300)
        self.assertEqual(sent,['active','resolved'])
        self.assertNotIn('private-password',json.dumps(self.snap()))
    def test_stale_unsent_failure_skips_recovery(self):
        self.sample['checks']['backend']['ok']=False; self.tick(3)
        self.sample['checks']['backend']['ok']=True; self.tick(2)
        self.mail_ready(); sent=[]
        alerts.deliver_one(self.cfg,lambda c,e:sent.append(e),lambda:1000)
        self.assertEqual(sent,[]); self.assertTrue(all(x['delivered_at']=='skipped' for x in self.snap()['recent']))
    def test_smtp_verified_tls_no_credentials_in_message(self):
        self.mail_ready(); self.cfg.alert_smtp_username='test'; self.cfg.alert_smtp_password='synthetic-password'
        with patch.object(alerts.smtplib,'SMTP') as smtp:
            server=smtp.return_value; server.send_message.return_value={}
            alerts.send_email(self.cfg,{'id':1,'state':'active','title':'Sistem sağlığı','message':'Erişim başarısız.','ts':'today'})
            server.starttls.assert_called_once()
            self.assertEqual(server.starttls.call_args.kwargs['context'].verify_mode,2)
            server.login.assert_called_once_with('test','synthetic-password')
            self.assertNotIn('synthetic-password',str(server.send_message.call_args.args[0]))
    def test_ses_signed_request_preserves_sender_recipient_and_private_credentials(self):
        import boto3
        from botocore.stub import Stubber, ANY
        self.mail_ready(); self.cfg.alert_email_provider='ses'
        self.assertFalse(alerts.email_ready(self.cfg))
        self.cfg.alert_ses_access_key_id='synthetic-access-key'
        self.cfg.alert_ses_secret_access_key='synthetic-private-key'
        self.assertTrue(alerts.email_ready(self.cfg))
        client=boto3.client('ses',region_name='us-east-1',aws_access_key_id='synthetic-access-key',aws_secret_access_key='synthetic-private-key')
        requests=[]
        client.meta.events.register('before-parameter-build.ses.SendRawEmail',lambda params,**kwargs:requests.append(params.copy()))
        with Stubber(client) as stub, patch.object(boto3,'client',return_value=client), patch.object(alerts.smtplib,'SMTP') as smtp:
            stub.add_response('send_raw_email',{'MessageId':'synthetic-id'},
                              {'Source':'BAKAI <bakai@example.test>','Destinations':['ops@example.test'],'RawMessage':{'Data':ANY}})
            alerts.send_email(self.cfg,{'id':1,'state':'active','title':'Sistem sağlığı','message':'Erişim başarısız.','ts':'today'})
            stub.assert_no_pending_responses(); smtp.assert_not_called()
        message=BytesParser(policy=policy.default).parsebytes(requests[0]['RawMessage']['Data'])
        self.assertEqual(message['From'].addresses[0].display_name,'BAKAI')
        self.assertEqual(message['To'].addresses[0].addr_spec,'ops@example.test')
        self.assertIn('Erişim başarısız.',message.get_content())
        self.assertNotIn('synthetic-private-key',str(message))
        self.assertNotIn('synthetic-private-key',repr(self.cfg))
    def test_captcha_repeated_abuse_expiry_and_quota_stays(self):
        self.cfg.captcha_site_key='public-test'; self.cfg.captcha_secret_key='synthetic-secret'; self.cfg.rate_chat_per_minute=1
        guard=AbuseGuard(self.cfg,clock=lambda:self.now.timestamp()); client=guard.client_key('192.0.2.17')
        guard.admit('chat',client)
        for i in range(3):
            with self.assertRaises(Denied): guard.admit('chat',client)
            self.assertEqual(guard.needs_captcha(client),i==2)
        with self.assertRaises(HTTPException) as error: captcha.require(guard,client,None)
        self.assertEqual(error.exception.status_code,403)
        with patch.object(captcha,'verify',return_value=True): captcha.require(guard,client,'valid')
        self.assertFalse(guard.needs_captcha(client))
        with self.assertRaises(Denied): guard.admit('chat',client)
        self.now+=timedelta(minutes=31); self.assertTrue(guard.needs_captcha(client))
        self.now+=timedelta(hours=2); self.assertFalse(guard.needs_captcha(client))
    def test_captcha_hostname_action_and_provider_failure(self):
        self.cfg.captcha_secret_key='synthetic-secret'
        def opener(result): return lambda req,timeout:io.BytesIO(json.dumps(result).encode())
        base={'success':True,'hostname':'bakai.manas.edu.kg','action':'bakai_chat'}
        self.assertTrue(captcha.verify(self.cfg,'token',opener(base)))
        for change in ({'success':False},{'hostname':'attacker.test'},{'action':'other'}):
            self.assertFalse(captcha.verify(self.cfg,'token',opener({**base,**change})))
        def fail(*a,**k): raise OSError('secret')
        with self.assertRaises(HTTPException) as error: captcha.verify(self.cfg,'token',fail)
        self.assertEqual(error.exception.status_code,503); self.assertNotIn('secret',str(error.exception.detail))

spec=importlib.util.spec_from_file_location('backup_tool',Path(__file__).resolve().parents[2]/'deploy/backup.py')
backup=importlib.util.module_from_spec(spec); spec.loader.exec_module(backup)
@unittest.skipUnless(shutil.which('age'),'age kurulumu gerekli')
class BackupTests(unittest.TestCase):
    def setUp(self):
        self.root=Path(self.enterContext(tempfile.TemporaryDirectory())); self.identity=self.root/'identity.txt'
        subprocess.run(['age-keygen','-o',str(self.identity)],check=True,capture_output=True)
        recipient=subprocess.run(['age-keygen','-y',str(self.identity)],check=True,capture_output=True,text=True).stdout.strip()
        app=self.root/'app'; (app/'data/chroma').mkdir(parents=True)
        for path in (app/'data/bakay.db',app/'data/chroma/chroma.sqlite3'):
            with sqlite3.connect(path) as db:
                db.execute('CREATE TABLE example(value TEXT)'); db.execute("INSERT INTO example VALUES ('original')")
        (app/'VERSION').write_text('test'); (app/'data/chroma/hnsw.bin').write_bytes(b'INDEX'*200)
        self.env=self.root/'private.env'; self.env.write_text('SYNTHETIC_SECRET=never-in-git\n')
        self.cfg={'root':str(app),'directory':str(self.root/'backups'),'recipient':recipient,'private_env':str(self.env),'extra_config':[],'status':str(self.root/'status.json'),'status_group':'','remote':''}
    def archive(self): return self.root/'backups'/backup.read_status(self.cfg)['last_archive']
    def fake_drive(self, bad_hash=False, fail_copy=False, fail_delete=False):
        """Gerçek şifreli paketler; Drive kopya/liste/hash/silme sözleşmesinin taklidi."""
        original=subprocess.run
        files={'BAKAI-index-20261001T020000000000Z.tar.gz.age':b'old-index',
               'BAKAI-daily-20261002T020000000000Z.tar.gz.age':b'old-daily',
               'kullanici-notu.txt':b'koru'}
        def run(args,**kwargs):
            if args[0]!='rclone': return original(args,**kwargs)
            if 'copyto' in args:
                if fail_copy: return subprocess.CompletedProcess(args,1,b'',b'quota')
                source=Path(args[args.index('copyto')+1]); files[source.name]=source.read_bytes()
                return subprocess.CompletedProcess(args,0,b'',b'')
            if 'lsjson' in args:
                if '--stat' in args:
                    name=args[args.index('lsjson')+1].rsplit('/',1)[-1]
                    import hashlib
                    value={'Size':len(files[name]),'Hashes':{'md5':'bad' if bad_hash else hashlib.md5(files[name]).hexdigest()}}
                else:
                    value=[{'Name':name,'Path':name,'IsDir':False,'Size':len(data)} for name,data in files.items()]
                    value.append({'Name':'BAKAI-index-20260101T020000000000Z.tar.gz.age',
                                  'Path':'../disarida','IsDir':False,'Size':1})
                return subprocess.CompletedProcess(args,0,json.dumps(value).encode(),b'')
            if 'deletefile' in args:
                if fail_delete: return subprocess.CompletedProcess(args,1,b'',b'quota')
                self.assertIn('--drive-use-trash=true',args)
                name=args[args.index('deletefile')+1].rsplit('/',1)[-1]
                del files[name]
                return subprocess.CompletedProcess(args,0,b'',b'')
            raise AssertionError(args)
        self.cfg.update(remote='drive:',rclone_config='unused',remote_only=True)
        self.enterContext(patch.object(backup.subprocess,'run',side_effect=run))
        return files
    def test_remote_only_keeps_one_independent_full_and_no_local_archives(self):
        files=self.fake_drive()
        directory=Path(self.cfg['directory']); directory.mkdir()
        unrelated=directory/'yonetici-notu.txt'; unrelated.write_text('koru')
        first=backup.run(self.cfg)
        self.assertEqual(first['kind'],'index'); self.assertTrue(first['remote_verified'])
        self.assertEqual(list(directory.glob('*.age')),[])
        self.assertTrue(unrelated.exists()); self.assertIn('kullanici-notu.txt',files)
        self.assertEqual(len(files),2)
        second=backup.run(self.cfg)
        self.assertEqual(second['kind'],'index'); self.assertEqual(len(files),2)
        self.assertEqual(list(directory.glob('*.age')),[])
        state=backup.read_status(self.cfg)
        self.assertFalse(state['local_enabled']); self.assertTrue(state['remote_only'])
        self.assertIn(state['last_archive'],files)
    def test_remote_checksum_failure_never_deletes_old_drive_backups(self):
        files=self.fake_drive(bad_hash=True)
        previous=set(files)
        with self.assertRaisesRegex(backup.BackupError,'drive_checksum'): backup.run(self.cfg)
        self.assertTrue(previous.issubset(files)); self.assertTrue(self.archive().exists())
        self.assertNotIn('last_remote_at',backup.read_status(self.cfg))
    def test_remote_cleanup_protects_newer_packages(self):
        files=self.fake_drive()
        future='BAKAI-index-20990101T020000000000Z.tar.gz.age'
        files[future]=b'dokunma'
        backup.run(self.cfg)
        self.assertEqual(files[future],b'dokunma'); self.assertEqual(len(files),3)
    def test_failed_retries_keep_only_one_complete_local_package(self):
        files=self.fake_drive(fail_copy=True); previous=dict(files)
        for _ in range(2):
            with self.assertRaisesRegex(backup.BackupError,'drive_upload'): backup.run(self.cfg)
        self.assertEqual(files,previous)
        self.assertEqual(list(Path(self.cfg['directory']).glob('*.age')),[self.archive()])
        self.assertEqual(backup.verify(self.archive(),self.identity)['kind'],'index')
    def test_cleanup_failure_preserves_local_and_records_verified_upload(self):
        files=self.fake_drive(fail_delete=True)
        with self.assertRaisesRegex(backup.BackupError,'drive_cleanup'): backup.run(self.cfg)
        self.assertTrue(self.archive().exists()); self.assertEqual(len(files),4)
        state=backup.read_status(self.cfg)
        self.assertIn('last_remote_at',state); self.assertEqual(state['last_error'],'drive_cleanup')
    def test_full_daily_restore_refuses_existing_target(self):
        self.assertEqual(backup.run(self.cfg)['kind'],'index'); full=self.archive()
        self.assertEqual(full.stat().st_mode&0o777,0o600)
        restored=self.root/'restored'; self.assertEqual(backup.verify(full,self.identity,restored)['sqlite_integrity'],'ok')
        self.assertEqual((restored/'config/backend.env').read_text(),self.env.read_text())
        self.assertEqual((restored/'config/backend.env').stat().st_mode&0o777,0o600)
        with self.assertRaises(FileExistsError): backup.verify(full,self.identity,restored)
        with sqlite3.connect(Path(self.cfg['root'])/'data/bakay.db') as db: db.execute("INSERT INTO example VALUES ('later')")
        self.assertEqual(backup.run(self.cfg)['kind'],'daily')
        self.assertEqual(backup.verify(self.archive(),self.identity)['kind'],'daily')
        full.unlink(); self.assertEqual(backup.run(self.cfg)['kind'],'index')
    def test_wrong_key_and_ciphertext_tamper_rejected(self):
        backup.run(self.cfg); archive=self.archive(); wrong=self.root/'wrong.txt'
        subprocess.run(['age-keygen','-o',str(wrong)],check=True,capture_output=True)
        with self.assertRaises(Exception): backup.verify(archive,wrong)
        data=bytearray(archive.read_bytes()); data[-1]^=1; archive.write_bytes(data)
        with self.assertRaises(Exception): backup.verify(archive,self.identity)
    def test_index_change_does_not_publish_and_cleans_plaintext(self):
        original=backup.fingerprint; calls=0
        def changed(root,files):
            nonlocal calls
            calls+=1; return original(root,files) if calls==1 else 'changed'
        with patch.object(backup,'fingerprint',side_effect=changed):
            with self.assertRaises(backup.BackupError): backup.run(self.cfg)
        self.assertEqual(list((self.root/'backups').glob('*.age')),[])
        self.assertEqual(list((self.root/'backups').glob('.snapshot-*')),[])
        self.assertEqual(backup.read_status(self.cfg)['last_error'],'index_changed')
    def test_upload_failure_keeps_local_retries_base_first(self):
        self.cfg.update(remote='drive:BAKAI-Yedek',rclone_config='unused')
        with patch.object(backup,'upload',side_effect=backup.BackupError('drive_upload')):
            with self.assertRaises(backup.BackupError): backup.run(self.cfg)
        self.assertTrue(self.archive().exists()); self.assertNotIn('last_remote_at',backup.read_status(self.cfg))
        sent=[]
        with patch.object(backup,'upload',side_effect=lambda c,p:sent.append(p.name)): backup.run(self.cfg)
        self.assertEqual(len(sent),2); self.assertIn('index',sent[0]); self.assertIn('daily',sent[1])
        self.assertIn('last_remote_at',backup.read_status(self.cfg))
    def test_retention_removes_daily_only_when_base_is_removed(self):
        directory=self.root/'backups'; directory.mkdir()
        for kind,stamp,digest in [('index','1','old'),('index','2','middle'),('index','3','new'),('daily','1','old'),('daily','2','middle'),('daily','3','new')]:
            path=directory/f'BAKAI-{kind}-{stamp}.tar.gz.age'; path.write_bytes(b'test')
            path.with_suffix('.age.json').write_text(json.dumps({'index_fingerprint':digest}))
        backup.prune(directory)
        self.assertFalse((directory/'BAKAI-index-1.tar.gz.age').exists())
        self.assertFalse((directory/'BAKAI-daily-1.tar.gz.age').exists())
        self.assertTrue((directory/'BAKAI-daily-2.tar.gz.age').exists())
        self.assertTrue((directory/'BAKAI-daily-3.tar.gz.age').exists())
    def test_disk_threshold_and_unsafe_archive(self):
        with patch.object(backup.shutil,'disk_usage',return_value=shutil._ntuple_diskusage(10,9,1)):
            with self.assertRaises(backup.BackupError): backup.run(self.cfg)
        import tarfile
        buffer=io.BytesIO()
        with tarfile.open(fileobj=buffer,mode='w:gz') as tar:
            entry=tarfile.TarInfo('../escaped'); entry.size=1; tar.addfile(entry,io.BytesIO(b'x'))
        archive=self.root/'unsafe.age'
        subprocess.run(['age','-r',self.cfg['recipient'],'-o',str(archive)],input=buffer.getvalue(),check=True,capture_output=True)
        with self.assertRaises(backup.BackupError): backup.verify(archive,self.identity)
        self.assertFalse((self.root/'escaped').exists())
if __name__=='__main__': unittest.main()
