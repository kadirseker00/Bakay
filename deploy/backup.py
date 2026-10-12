#!/usr/bin/env python3
"""Tutarlı SQLite, durağan Chroma dosyaları ve age ile şifreli yedek/geri yükleme testi."""
from __future__ import annotations

import argparse
import fcntl
import grp
import hashlib
import io
import json
import os
import shutil
import sqlite3
import subprocess
import tarfile
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath


class BackupError(Exception):
    pass


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def hashes(path):
    sha, md5 = hashlib.sha256(), hashlib.md5()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024*1024), b''):
            sha.update(block)
            md5.update(block)
    return {'sha256':sha.hexdigest(),'md5':md5.hexdigest()}


def atomic_json(path, value, group=''):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix='.bakai-', dir=path.parent)
    try:
        with os.fdopen(descriptor,'w') as stream:
            json.dump(value,stream,ensure_ascii=False,indent=2)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary,0o640 if group else 0o600)
        if group:
            os.chown(temporary,-1,grp.getgrnam(group).gr_gid)
        os.replace(temporary,path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def read_status(config):
    try:
        value=json.loads(Path(config['status']).read_text())
        return value if isinstance(value,dict) else {}
    except (OSError,ValueError):
        return {}


def sqlite_snapshot(source, destination):
    if not source.is_file():
        raise BackupError('database_missing')
    deadline=time.monotonic()+60
    def progress(*args):
        if time.monotonic()>deadline:
            raise BackupError('database_timeout')
    original=sqlite3.connect(source.as_uri()+'?mode=ro',uri=True,timeout=10)
    copied=sqlite3.connect(destination)
    try:
        original.backup(copied,pages=256,progress=progress,sleep=.1)
        if copied.execute('PRAGMA integrity_check').fetchone()[0]!='ok':
            raise BackupError('database_integrity')
    finally:
        original.close()
        copied.close()
    os.chmod(destination,0o600)


def index_files(root):
    files=[]
    for path in sorted((root/'data/chroma').rglob('*')):
        if path.is_symlink():
            raise BackupError('index_symlink')
        if path.is_file() and not path.name.endswith('-shm'):
            files.append(path)
    if not any(path.name=='chroma.sqlite3' for path in files):
        raise BackupError('index_missing')
    return files


def fingerprint(root, files):
    digest=hashlib.sha256()
    for path in files:
        digest.update(path.relative_to(root).as_posix().encode()+b'\0')
        digest.update(bytes.fromhex(hashes(path)['sha256']))
    return digest.hexdigest()


class HashReader:
    def __init__(self, stream):
        self.stream=stream
        self.digest=hashlib.sha256()

    def read(self, size):
        data=self.stream.read(size)
        self.digest.update(data)
        return data


def encrypt_archive(config, output, full, index_digest, files):
    root=Path(config['root']).resolve()
    manifest={'format':1,'created_at':utc_now(),'kind':'index' if full else 'daily',
              'index_fingerprint':index_digest,'files':{},'collection_name':config.get('collection_name','ktmu_docs')}
    commit=subprocess.run(['git','-C',str(root),'rev-parse','HEAD'],capture_output=True,text=True)
    manifest['git_commit']=commit.stdout.strip() if commit.returncode==0 else None
    with tempfile.TemporaryDirectory(prefix='.snapshot-',dir=output.parent) as temporary:
        temporary=Path(temporary)
        database=temporary/'bakay.db'
        sqlite_snapshot(root/'data/bakay.db',database)
        selected=[(database,'data/bakay.db')]
        small=[(root/'VERSION','VERSION')]
        small += [(p,p.relative_to(root).as_posix()) for p in sorted((root/'data').glob('*.json'))]
        small += [(Path(config['private_env']),'config/backend.env')]
        small += [(Path(path),f'config/{Path(path).name}') for path in config.get('extra_config',[])]
        for number,(path,name) in enumerate(small):
            if not path.is_file() or path.is_symlink():
                raise BackupError('configuration_missing')
            copied=temporary/f'config-{number}'
            shutil.copyfile(path,copied)
            os.chmod(copied,0o600)
            selected.append((copied,name))
        if full:
            chroma=temporary/'chroma.sqlite3'
            sqlite_snapshot(root/'data/chroma/chroma.sqlite3',chroma)
            selected.append((chroma,'data/chroma/chroma.sqlite3'))
            selected += [(p,p.relative_to(root).as_posix()) for p in files
                         if p.name!='chroma.sqlite3' and not p.name.endswith('-wal')]
        with output.open('xb') as encrypted:
            os.chmod(output,0o600)
            process=subprocess.Popen(['age','--recipient',config['recipient']],stdin=subprocess.PIPE,
                                     stdout=encrypted,stderr=subprocess.PIPE)
            try:
                with tarfile.open(fileobj=process.stdin,mode='w|gz') as archive:
                    for path,name in selected:
                        if path.is_symlink():
                            raise BackupError('source_symlink')
                        info=tarfile.TarInfo(name)
                        info.size=path.stat().st_size
                        info.mode=0o600
                        with path.open('rb') as stream:
                            reader=HashReader(stream)
                            archive.addfile(info,reader)
                            manifest['files'][name]={'size':info.size,'sha256':reader.digest.hexdigest()}
                    raw=json.dumps(manifest,ensure_ascii=False).encode()
                    info=tarfile.TarInfo('manifest.json')
                    info.mode,info.size=0o600,len(raw)
                    archive.addfile(info,io.BytesIO(raw))
                process.stdin.close()
                if process.wait(timeout=60)!=0:
                    raise BackupError('encryption_failed')
                encrypted.flush()
                os.fsync(encrypted.fileno())
            except BaseException:
                process.kill()
                process.wait()
                raise
            finally:
                process.stderr.close()
        # SQLite/HNSW ortak snapshot sırasında değiştiyse paket yayınlanmaz.
        after=index_files(root)
        if after!=files or fingerprint(root,after)!=index_digest:
            raise BackupError('index_changed')
    return manifest


def upload(config, archive):
    target=config['remote'].rstrip('/')+'/'+archive.name
    common=['rclone','--config',config['rclone_config'],'--retries','2','--low-level-retries','2',
            '--contimeout','10s','--timeout','60s','--log-level','ERROR']
    result=subprocess.run([*common,'copyto',str(archive),target],capture_output=True,timeout=1800)
    if result.returncode:
        raise BackupError('drive_upload')
    result=subprocess.run([*common,'lsjson',target,'--stat','--hash'],capture_output=True,timeout=90)
    if result.returncode:
        raise BackupError('drive_verify')
    try:
        metadata=json.loads(result.stdout)
        remote_hashes={key.lower():value for key,value in metadata.get('Hashes',{}).items()}
        if metadata['Size']!=archive.stat().st_size or remote_hashes.get('md5')!=hashes(archive)['md5']:
            raise BackupError('drive_checksum')
    except (ValueError,KeyError,TypeError):
        raise BackupError('drive_verify') from None


def prune(directory):
    # Yalnız bu aracın ürettiği yerel kopyalar; Drive'da silme/sync/purge yapılmaz.
    indexes=sorted(directory.glob('BAKAI-index-*.tar.gz.age'),reverse=True)
    def remove(path):
        path.unlink()
        path.with_suffix(path.suffix+'.json').unlink(missing_ok=True)
    for path in indexes[2:]:
        remove(path)
    retained=set()
    complete=True
    for path in indexes[:2]:
        try:
            digest=json.loads(path.with_suffix(path.suffix+'.json').read_text())['index_fingerprint']
            retained.add(digest)
        except (OSError,ValueError,KeyError,TypeError):
            complete=False  # Eski metadata ile eşleşmesi bilinmeyen paket silinmez.
    daily=[]
    for path in sorted(directory.glob('BAKAI-daily-*.tar.gz.age'),reverse=True):
        try:
            digest=json.loads(path.with_suffix(path.suffix+'.json').read_text())['index_fingerprint']
        except (OSError,ValueError,KeyError,TypeError):
            digest=None
        if complete and digest is not None and digest not in retained:
            remove(path)  # Tam indeksi kaldırılmış günlük paket tek başına geri yüklenemez.
        else:
            daily.append(path)
    for path in daily[7:]:
        remove(path)


def run(config, force_full=False, local_only=False):
    directory=Path(config['directory'])
    directory.mkdir(parents=True,exist_ok=True,mode=0o700)
    os.chmod(directory,0o700)
    with (directory/'.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX | fcntl.LOCK_NB)
        state=read_status(config)
        state.update(local_enabled=True,remote_configured=bool(config.get('remote')))
        partial=None
        try:
            root=Path(config['root']).resolve()
            files=index_files(root)
            digest=fingerprint(root,files)
            base_name=state.get('last_index_archive', '')
            full=force_full or digest!=state.get('index_fingerprint') or not base_name or not (directory/base_name).is_file()
            size=sum(path.stat().st_size for path in files) if full else 0
            if shutil.disk_usage(directory).free < size+1024**3:
                raise BackupError('disk_space')
            stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
            archive=directory/f"BAKAI-{'index' if full else 'daily'}-{stamp}.tar.gz.age"
            partial=archive.with_suffix('.partial')
            manifest=encrypt_archive(config,partial,full,digest,files)
            os.replace(partial,archive)
            partial=None
            atomic_json(archive.with_suffix(archive.suffix+'.json'),
                        {'sha256':hashes(archive)['sha256'],'size':archive.stat().st_size,
                         'kind':manifest['kind'],'index_fingerprint':digest})
            state.update(last_local_at=utc_now(),last_backup_bytes=archive.stat().st_size,
                         last_archive=archive.name,last_error=None,index_fingerprint=digest)
            if full:
                state['last_index_archive']=archive.name
            # Aktarım arızası, alınmış yerel yedeği ve referans indeksini silmez.
            atomic_json(config['status'],state,config.get('status_group',''))
            if config.get('remote') and not local_only:
                base=directory/state['last_index_archive']
                if state.get('remote_index_fingerprint')!=digest:
                    if not base.is_file():
                        raise BackupError('index_base_missing')
                    upload(config,base)
                    state['remote_index_fingerprint']=digest
                if archive!=base:
                    upload(config,archive)
                state['last_remote_at']=utc_now()
            atomic_json(config['status'],state,config.get('status_group',''))
            prune(directory)
            return {'kind':manifest['kind'],'bytes':archive.stat().st_size,
                    'remote_verified':bool(config.get('remote') and not local_only)}
        except Exception as exception:
            if partial:
                partial.unlink(missing_ok=True)
            state['last_error']=str(exception) if isinstance(exception,BackupError) else type(exception).__name__
            atomic_json(config['status'],state,config.get('status_group',''))
            raise


def verify(archive_path, identity, destination=None, check_index=False):
    """Yalnız yeni hedefe açar; var olan dizini reddeder, üretime yazmaz."""
    with tempfile.TemporaryDirectory(prefix='bakai-restore-') as temporary:
        root=Path(destination) if destination else Path(temporary)/'restored'
        root.mkdir(mode=0o700,parents=True,exist_ok=False)
        actual={}
        total=0
        process=subprocess.Popen(['age','--decrypt','--identity',str(identity),str(archive_path)],
                                 stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        try:
            with tarfile.open(fileobj=process.stdout,mode='r|gz') as archive:
                for entry in archive:
                    path=PurePosixPath(entry.name)
                    if (not entry.isfile() or path.is_absolute() or '..' in path.parts or
                            str(path)!=entry.name or entry.name in actual or entry.size>1024**3):
                        raise BackupError('archive_unsafe')
                    total+=entry.size
                    if total>2*1024**3:
                        raise BackupError('archive_too_large')
                    target=root.joinpath(*path.parts)
                    target.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
                    digest=hashlib.sha256()
                    with archive.extractfile(entry) as source, target.open('xb') as stream:
                        os.chmod(target,0o600)
                        for block in iter(lambda:source.read(1024*1024),b''):
                            digest.update(block)
                            stream.write(block)
                    actual[entry.name]={'size':entry.size,'sha256':digest.hexdigest()}
            # age son doğrulama etiketini de kontrol etsin; fazladan veri reddedilir.
            if process.stdout.read() or process.wait(timeout=60)!=0:
                raise BackupError('decryption_failed')
            manifest=json.loads((root/'manifest.json').read_text())
            actual.pop('manifest.json')
            if manifest.get('format')!=1 or actual!=manifest['files']:
                raise BackupError('manifest_mismatch')
            for name in ('data/bakay.db','data/chroma/chroma.sqlite3'):
                path=root/name
                if path.exists():
                    with sqlite3.connect(path) as connection:
                        if connection.execute('PRAGMA integrity_check').fetchone()[0]!='ok':
                            raise BackupError('restored_database_integrity')
            result={'kind':manifest['kind'],'files':len(actual),'sqlite_integrity':'ok',
                    'index_fingerprint':manifest['index_fingerprint']}
            if check_index and manifest['kind']=='index':
                import chromadb
                client=chromadb.PersistentClient(path=str(root/'data/chroma'))
                collection=client.get_collection(manifest['collection_name'])
                first=collection.get(limit=1,include=['embeddings'])
                if len(first['ids'])!=1:
                    raise BackupError('restored_index_empty')
                hits=collection.query(query_embeddings=[first['embeddings'][0].tolist()],n_results=1)
                if not hits['ids'][0] or abs(hits['distances'][0][0])>.001:
                    raise BackupError('restored_index_query')
                result['indexed_chunks']=collection.count()
            return result
        finally:
            if process.poll() is None:
                process.kill()
                process.wait()
            process.stdout.close()
            process.stderr.close()


def main():
    os.umask(0o077)
    parser=argparse.ArgumentParser()
    parser.add_argument('--config',default='/etc/bakay/backup.json')
    sub=parser.add_subparsers(dest='command',required=True)
    backup=sub.add_parser('run')
    backup.add_argument('--full',action='store_true')
    backup.add_argument('--local-only',action='store_true')
    restore=sub.add_parser('verify')
    restore.add_argument('archive')
    restore.add_argument('--identity',required=True)
    restore.add_argument('--output')
    restore.add_argument('--check-index',action='store_true')
    args=parser.parse_args()
    try:
        if args.command=='run':
            config=json.loads(Path(args.config).read_text())
            result=run(config,args.full,args.local_only)
        else:
            result=verify(args.archive,args.identity,args.output,args.check_index)
        print(json.dumps(result,ensure_ascii=False))
    except Exception as exception:
        print(json.dumps({'error':str(exception) if isinstance(exception,BackupError) else type(exception).__name__}))
        raise SystemExit(1) from None


if __name__=='__main__':
    main()
