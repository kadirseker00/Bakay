"""Dağıtım ön kontrolü sırları korur; hatalı ağ/hostname dosyayı değiştirmez."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from app.config import ROOT


class DeploymentTests(unittest.TestCase):
    def setUp(self):
        root=Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.env=root/'backend.env'
        self.apache=root/'networks.apache'
        self.original=('LLM_PROVIDER=anthropic\nANTHROPIC_API_KEY=PRIVATE-TEST-KEEP\n'
            'CAPTCHA_SITE_KEY=site\nCAPTCHA_SECRET_KEY=PRIVATE-CHALLENGE-KEEP\n'
            'CAPTCHA_HOSTNAME=bakai.example\nMONITOR_PUBLIC_URL=https://bakai.example\n'
            'MONITOR_SESSION_SECRET='+'x'*48+'\nALERT_DAILY_USD=1\n')
        self.env.write_text(self.original)

    def run_config(self, networks, *extra):
        return subprocess.run([sys.executable,str(ROOT/'deploy/configure-public-security.py'),
            '--env',str(self.env),'--apache',str(self.apache),'--monitor-networks',networks,*extra],
            capture_output=True,text=True)

    def test_check_does_not_modify_and_apply_preserves_secret_and_alert(self):
        result=self.run_config('192.0.2.0/24','--check')
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(self.env.read_text(),self.original)
        self.assertFalse(self.apache.exists())
        result=self.run_config('192.0.2.0/24')
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertNotIn('PRIVATE',result.stdout+result.stderr)
        self.assertIn('ANTHROPIC_API_KEY=PRIVATE-TEST-KEEP',self.env.read_text())
        self.assertIn('ALERT_DAILY_USD=1',self.env.read_text())
        self.assertIn('BUDGET_DAILY_USD=5',self.env.read_text())
        self.assertIn('PUBLIC_SECURITY_ENABLED=true',self.env.read_text())
        self.assertEqual(self.env.stat().st_mode & 0o777,0o600)
        self.assertIn('Require ip 127.0.0.1/32 ::1/128 192.0.2.0/24',self.apache.read_text())
        once=self.env.read_text()
        self.run_config('192.0.2.0/24')
        self.assertEqual(self.env.read_text(),once)

    def test_blank_wide_and_invalid_networks_fail_without_writes(self):
        for networks in ('','0.0.0.0/0','::/0','not-a-network'):
            self.assertNotEqual(self.run_config(networks).returncode,0)
            self.assertEqual(self.env.read_text(),self.original)
            self.assertFalse(self.apache.exists())

    def test_wrong_host_or_missing_secret_fail_without_disclosing_values(self):
        for content in (self.original.replace('CAPTCHA_HOSTNAME=bakai.example','CAPTCHA_HOSTNAME=evil.example'),
                        self.original.replace('CAPTCHA_SECRET_KEY=PRIVATE-CHALLENGE-KEEP','CAPTCHA_SECRET_KEY=')):
            self.env.write_text(content)
            result=self.run_config('192.0.2.0/24')
            self.assertNotEqual(result.returncode,0)
            self.assertNotIn('PRIVATE',result.stdout+result.stderr)
            self.assertEqual(self.env.read_text(),content)
            self.assertFalse(self.apache.exists())
