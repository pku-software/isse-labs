"""下载、校验并解压本实验固定版本的 Windows x64 监控工具。"""

from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import tarfile
import time
import zipfile

import requests


ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
PACKAGES = [
    ('prometheus', '3.15.0',
     'https://github.com/prometheus/prometheus/releases/download/v3.15.0/prometheus-3.15.0.windows-amd64.zip',
     '5d333b385557d9adc2ff015d13da9809baccc52fb800a82d1e5c94b79258f87e'),
    ('grafana', '13.2.4',
     'https://dl.grafana.com/grafana/release/13.2.4/grafana_13.2.4_38252365904_windows_amd64.tar.gz',
     '3e005ff50fe3bb6b8cb428ef127636fac4ee676bf9b6d819c6a2297d21f4bcbd'),
]


def check_ignored():
    prefix = ROOT.relative_to(REPO).as_posix()
    for suffix in ['.tools/downloads/archive.zip', '.tools/prometheus/prometheus.exe',
                   '.tools/grafana/bin/grafana.exe', '.runtime/prometheus/wal',
                   '.runtime/grafana/grafana.db', '.venv/pyvenv.cfg']:
        subprocess.run(['git', 'check-ignore', '-q', '--', f'{prefix}/{suffix}'],
                       cwd=REPO, check=True)
    tracked = subprocess.check_output(['git', 'ls-files', '--',
                                      *[f'{prefix}/{p}' for p in ['.tools', '.runtime', '.venv']]], cwd=REPO)
    if tracked:
        raise RuntimeError('工具、运行数据或虚拟环境已被 Git 跟踪，请先处理。')


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def download(url, archive, name):
    # 小范围请求支持断点续传，避免单条慢连接阻塞整个大文件。
    with requests.get(url, headers={'Range': 'bytes=0-0'}, timeout=(20, 30)) as probe:
        probe.raise_for_status()
        if probe.status_code != 206:
            raise RuntimeError(f'{name}: server does not support byte ranges')
        size = int(probe.headers['Content-Range'].split('/')[-1])
        resolved_url = probe.url
    parts = archive.with_name(archive.name + '.parts')
    parts.mkdir(exist_ok=True)
    chunk_size = 256 * 1024
    ranges = [(i, start, min(start + chunk_size, size) - 1)
              for i, start in enumerate(range(0, size, chunk_size))]

    def fetch(part):
        index, start, end = part
        path = parts / f'{index:06d}'
        expected_size = end - start + 1
        if path.exists() and path.stat().st_size == expected_size:
            return expected_size
        for attempt in range(3):
            try:
                with requests.get(resolved_url, headers={'Range': f'bytes={start}-{end}'},
                                  timeout=(20, 40)) as response:
                    response.raise_for_status()
                    if response.status_code != 206 or response.headers.get('Content-Range') != f'bytes {start}-{end}/{size}':
                        raise RuntimeError(f'{name}: wrong content range')
                    if len(response.content) != expected_size:
                        raise RuntimeError(f'{name}: incomplete chunk')
                    path.write_bytes(response.content)
                    return expected_size
            except (requests.RequestException, RuntimeError):
                if attempt == 2:
                    raise
                time.sleep(1)
    completed = 0
    reported = 0
    with ThreadPoolExecutor(max_workers=64) as pool:
        for future in as_completed([pool.submit(fetch, part) for part in ranges]):
            completed += future.result()
            if completed - reported >= 8 * 1024 * 1024 or completed == size:
                print(f'{name}: {completed // (1024 * 1024)} / {size // (1024 * 1024)} MiB', flush=True)
                reported = completed
    with archive.open('wb') as output:
        for index, _, _ in ranges:
            with (parts / f'{index:06d}').open('rb') as source:
                shutil.copyfileobj(source, output)


def install(package):
    name, version, url, expected = package
    downloads = ROOT / '.tools' / 'downloads'
    downloads.mkdir(parents=True, exist_ok=True)
    archive = downloads / url.rsplit('/', 1)[-1]
    archive.with_name(archive.name + '.sha256').write_text(f'{expected}  {archive.name}\n', encoding='ascii')
    if not archive.exists() or digest(archive) != expected:
        print(f'{name}: downloading {version}', flush=True)
        download(url, archive, name)
    if digest(archive) != expected:
        raise RuntimeError(f'{name}: SHA-256 mismatch; archive was not extracted')
    destination = ROOT / '.tools' / name
    marker = destination / '.installed.json'
    if marker.exists() and json.loads(marker.read_text())['sha256'] == expected:
        print(f'{name}: already installed and verified', flush=True)
        return
    print(f'{name}: checksum verified, extracting', flush=True)

    def output_path(member):
        parts = PurePosixPath(member.replace('\\', '/')).parts
        if len(parts) < 2 or '..' in parts or PurePosixPath(member).is_absolute():
            raise ValueError(f'Unexpected archive path: {member}')
        target = destination.joinpath(*parts[1:]).resolve()
        if not target.is_relative_to(destination.resolve()):
            raise ValueError(f'Unsafe archive path: {member}')
        target.parent.mkdir(parents=True, exist_ok=True)
        return target

    if archive.name.endswith('.zip'):
        with zipfile.ZipFile(archive) as bundle:
            for member in bundle.infolist():
                if not member.is_dir():
                    with bundle.open(member) as source, output_path(member.filename).open('wb') as target:
                        shutil.copyfileobj(source, target)
    else:
        with tarfile.open(archive, 'r:gz') as bundle:
            for member in bundle:
                if member.isfile():
                    with bundle.extractfile(member) as source, output_path(member.name).open('wb') as target:
                        shutil.copyfileobj(source, target)
                elif not member.isdir():
                    raise ValueError(f'Unsupported archive entry: {member.name}')
    marker.write_text(json.dumps({'version': version, 'url': url, 'sha256': expected}, indent=2) + '\n')
    print(f'{name}: installed {version}', flush=True)


if __name__ == '__main__':
    check_ignored()
    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(install, PACKAGES))
    check_ignored()
