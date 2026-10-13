"""Download fixed official Windows releases, verify SHA256, and extract locally."""

from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import tarfile
import time
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import zipfile

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
DOWNLOADS = ROOT / '.tools' / 'downloads'
RELEASES = [
    ('prometheus', 'prometheus-3.15.0.windows-amd64.zip',
     'https://github.com/prometheus/prometheus/releases/download/v3.15.0/prometheus-3.15.0.windows-amd64.zip',
     114650144, '5d333b385557d9adc2ff015d13da9809baccc52fb800a82d1e5c94b79258f87e'),
    ('grafana', 'grafana_13.2.3_36482603486_windows_amd64.tar.gz',
     'https://dl.grafana.com/grafana/release/13.2.3/grafana_13.2.3_36482603486_windows_amd64.tar.gz',
     465775092, 'dafe883a7c15543c6d6710b868eb8b4053353441ce7ceacf150942b8de3960f0'),
]


def verify_ignore_rules():
    for path in [DOWNLOADS / name for _, name, _, _, _ in RELEASES] + [
        DOWNLOADS / 'SHA256SUMS', DOWNLOADS / 'prometheus.parts' / '000000.bin',
        ROOT / '.tools/prometheus/prometheus.exe', ROOT / '.tools/grafana/bin/grafana-server.exe',
        ROOT / '.runtime/prometheus/wal', ROOT / '.runtime/grafana/data/grafana.db',
        ROOT / '.venv/pyvenv.cfg',
    ]:
        subprocess.run(['git', 'check-ignore', '-q', '--', path.relative_to(REPO).as_posix()], cwd=REPO, check=True)
    tracked = subprocess.check_output(['git', 'ls-files', '--', *[
        (ROOT / directory).relative_to(REPO).as_posix() for directory in ('.tools', '.runtime', '.venv')
    ]], cwd=REPO)
    if tracked.strip():
        raise RuntimeError('Tools/runtime/venv files are tracked; stop before downloading.')


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def download(tool, filename, url, size, expected):
    target = DOWNLOADS / filename
    if target.exists() and target.stat().st_size == size and sha256(target) == expected:
        print(f'{tool}: existing archive verified', flush=True)
        return target
    parts = DOWNLOADS / f'{tool}.parts'
    parts.mkdir(parents=True, exist_ok=True)
    chunk_size = 512 * 1024
    count = (size + chunk_size - 1) // chunk_size
    # Resolve the official CDN redirect once, instead of repeatedly hitting GitHub.
    with urlopen(Request(url, headers={'Range': 'bytes=0-0', 'User-Agent': 'Lab4-Setup'}), timeout=30) as response:
        download_url = response.geturl()
        response.read(1)
    separator = '&' if '?' in download_url else '?'

    def fetch(index):
        start = index * chunk_size
        end = min(size, start + chunk_size) - 1
        path = parts / f'{index:06d}.bin'
        if path.exists() and path.stat().st_size == end - start + 1:
            return index
        for attempt in range(5):
            try:
                request = Request(download_url + f'{separator}lab4-part={start}', headers={
                    'User-Agent': 'Lab4-Setup', 'Range': f'bytes={start}-{end}'})
                with urlopen(request, timeout=45) as response:
                    if response.status != 206 or response.headers.get('Content-Range') != f'bytes {start}-{end}/{size}':
                        raise RuntimeError('Official server returned an unexpected byte range')
                    body = response.read(end - start + 2)
                if len(body) != end - start + 1:
                    raise RuntimeError('Incomplete download range')
                path.write_bytes(body)
                return index
            except Exception as error:
                if attempt == 4:
                    raise
                pause = min(30, 2 ** attempt)
                if isinstance(error, HTTPError) and error.code == 429:
                    pause = min(30, max(10, int(error.headers.get('Retry-After', '10'))))
                time.sleep(pause)

    completed = 0
    last_print = 0
    print(f'{tool}: downloading official archive with resumable ranges', flush=True)
    with ThreadPoolExecutor(max_workers=12) as pool:
        for future in as_completed([pool.submit(fetch, index) for index in range(count)]):
            future.result()
            completed += 1
            now = time.monotonic()
            if now - last_print >= 10 or completed == count:
                print(f'{tool}: {completed}/{count} ranges ({100 * completed / count:.1f}%)', flush=True)
                last_print = now
    with target.open('wb') as output:
        for index in range(count):
            with (parts / f'{index:06d}.bin').open('rb') as source:
                shutil.copyfileobj(source, output)
    if sha256(target) != expected:
        raise RuntimeError(f'{tool}: SHA256 mismatch; archive will not be extracted')
    print(f'{tool}: official SHA256 verified', flush=True)
    return target


def extract(archive, tool):
    destination = (ROOT / '.tools' / tool).resolve()
    destination.mkdir(parents=True, exist_ok=True)

    def output_path(name):
        parts = PurePosixPath(name.replace('\\', '/')).parts
        if not parts or '..' in parts or PurePosixPath(name).is_absolute():
            raise RuntimeError('Unsafe archive path')
        # Official packages contain one top-level version directory.
        path = destination.joinpath(*parts[1:]).resolve()
        if path != destination and destination not in path.parents:
            raise RuntimeError('Archive path escapes tool directory')
        return path

    if archive.suffix == '.zip':
        with zipfile.ZipFile(archive) as package:
            for member in package.infolist():
                path = output_path(member.filename)
                if member.is_dir():
                    path.mkdir(parents=True, exist_ok=True)
                else:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    with package.open(member) as source, path.open('wb') as output:
                        shutil.copyfileobj(source, output)
    else:
        with tarfile.open(archive, 'r:gz') as package:
            for member in package:
                path = output_path(member.name)
                if member.isdir():
                    path.mkdir(parents=True, exist_ok=True)
                elif member.isfile():
                    path.parent.mkdir(parents=True, exist_ok=True)
                    with package.extractfile(member) as source, path.open('wb') as output:
                        shutil.copyfileobj(source, output)
                else:
                    raise RuntimeError('Unsupported link or special file in tool archive')
    print(f'{tool}: extracted to .tools/{tool}', flush=True)


if __name__ == '__main__':
    verify_ignore_rules()
    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    for tool, filename, url, size, expected in RELEASES:
        (DOWNLOADS / f'{filename}.sha256').write_text(f'{expected}  {filename}\n', encoding='ascii')
        extract(download(tool, filename, url, size, expected), tool)
    verify_ignore_rules()
