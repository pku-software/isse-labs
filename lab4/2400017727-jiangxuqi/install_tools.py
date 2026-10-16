"""Download the official Linux amd64 standalone releases into ignored directories."""
import hashlib
from pathlib import Path
import subprocess
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parent
TOOLS = ROOT / '.tools'
DOWNLOADS = TOOLS / 'downloads'
RELEASES = [
    ('prometheus', '3.15.0',
     'https://github.com/prometheus/prometheus/releases/download/v3.15.0/prometheus-3.15.0.linux-amd64.tar.gz',
     '2a542df32eac02ee17b9d844fb2aa1de00dafa5476579ba8a3ba862e9d572ea0'),
    ('grafana', '13.2.4',
     'https://dl.grafana.com/grafana/release/13.2.4/grafana_13.2.4_38252365904_linux_amd64.tar.gz',
     'c48765988fd88572607e4ea670251af8a8e64ab3e360d0f3cf67a6f3587b92ab'),
]


def install(release):
    name, version, url, expected = release
    archive = DOWNLOADS / url.rsplit('/', 1)[1]
    checksum = archive.with_name(archive.name + '.sha256')
    checksum.write_text(f'{expected}  {archive.name}\n')
    if not archive.exists():
        partial = archive.with_name(archive.name + '.part')
        print(f'Downloading {name} {version}', flush=True)
        # HTTP byte ranges allow failed pieces to be retried independently.
        from concurrent.futures import ThreadPoolExecutor, as_completed
        sizes = {"prometheus": 111651578, "grafana": 461295109}
        size = sizes[name]
        chunk_size = 8 * 1024 * 1024
        pieces = []
        def fetch_piece(start):
            end = min(start + chunk_size, size) - 1
            piece = DOWNLOADS / f"{archive.name}.chunk-{start}"
            expected_size = end - start + 1
            if not piece.exists() or piece.stat().st_size != expected_size:
                subprocess.run([
                    'curl', '--silent', '--show-error', '--fail', '--location',
                    '--retry', '3', '--connect-timeout', '20', '--max-time', '180',
                    '--range', f'{start}-{end}', '--output', str(piece),
                    url + f'?lab4_range={start}',
                ], check=True)
            if piece.stat().st_size != expected_size:
                raise RuntimeError(f'Unexpected HTTP range response for {piece.name}')
            return start, piece
        with ThreadPoolExecutor(max_workers=8) as pool:
            futures = [pool.submit(fetch_piece, start) for start in range(0, size, chunk_size)]
            for future in as_completed(futures):
                pieces.append(future.result())
                print(f'{name}: {len(pieces)}/{len(futures)} download pieces ready', flush=True)
        with partial.open('wb') as output:
            for _, piece in sorted(pieces):
                with piece.open('rb') as source:
                    import shutil
                    shutil.copyfileobj(source, output)
        partial.rename(archive)
    with archive.open('rb') as source:
        actual = hashlib.file_digest(source, 'sha256').hexdigest()
    if actual != expected:
        raise RuntimeError(f'{name}: SHA256 mismatch; refusing extraction')
    target = TOOLS / name
    target.mkdir(exist_ok=True)
    subprocess.run(['tar', '-xzf', str(archive), '--strip-components=1', '-C', str(target)], check=True)
    print(f'{name} {version}: SHA256 verified, extracted to {target}', flush=True)


if __name__ == '__main__':
    import platform
    from concurrent.futures import ThreadPoolExecutor
    if platform.system() != 'Linux' or platform.machine() != 'x86_64':
        raise SystemExit('This installer requires Linux x86_64; choose official packages for your OS.')
    for rel in ['.tools/downloads/package.tar.gz', '.tools/prometheus/prometheus',
                '.tools/grafana/bin/grafana', '.runtime/prometheus/wal',
                '.runtime/grafana/data/grafana.db']:
        subprocess.run(['git', 'check-ignore', '-q', '--', str(ROOT / rel)], cwd=ROOT, check=True)
    tracked = subprocess.check_output(['git', 'ls-files', '--', '.tools', '.runtime', '.venv'], cwd=ROOT)
    if tracked:
        raise SystemExit('Tool/runtime files are tracked; resolve before installation.')
    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(install, RELEASES))
