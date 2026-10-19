"""Download and verify official Windows x64 stable monitoring binaries."""

from concurrent.futures import ThreadPoolExecutor
import argparse
import hashlib
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parent
TOOLS = ROOT / ".tools"
DOWNLOADS = TOOLS / "downloads"
PACKAGES = [
    (
        "prometheus",
        "https://github.com/prometheus/prometheus/releases/download/v3.15.0/prometheus-3.15.0.windows-amd64.zip",
        "5d333b385557d9adc2ff015d13da9809baccc52fb800a82d1e5c94b79258f87e",
    ),
    (
        "grafana",
        "https://dl.grafana.com/grafana/release/13.2.4/grafana_13.2.4_38252365904_windows_amd64.tar.gz",
        "3e005ff50fe3bb6b8cb428ef127636fac4ee676bf9b6d819c6a2297d21f4bcbd",
    ),
]


def download_grafana(url, archive):
    # Official Content-Length, verified with HTTP HEAD. Bounded ranges avoid
    # a stalled long response; SHA256 below still verifies the entire package.
    total = 466144621
    chunk_size = 4 * 1024 * 1024
    ranges = list(range(0, total, chunk_size))

    def fetch(start):
        end = min(start + chunk_size, total) - 1
        part = DOWNLOADS / f"grafana-{start}.part"
        headers = part.with_suffix(".headers")
        if not part.exists() or part.stat().st_size != end - start + 1:
            subprocess.run([
                "curl.exe", "--fail", "--location", "--retry", "2", "--silent", "--show-error",
                "--connect-timeout", "15", "--max-time", "180",
                "--range", f"{start}-{end}", "--dump-header", str(headers),
                "--output", str(part), url,
            ], check=True)
        expected_range = f"content-range: bytes {start}-{end}/{total}"
        if part.stat().st_size != end - start + 1 or expected_range not in headers.read_text().lower():
            raise RuntimeError(f"Invalid Grafana range: {start}-{end}")
        return part

    with ThreadPoolExecutor(max_workers=8) as pool:
        parts = []
        for index, part in enumerate(pool.map(fetch, ranges), 1):
            parts.append(part)
            if index % 10 == 0 or index == len(ranges):
                print(f"Grafana chunks verified: {index}/{len(ranges)}", flush=True)
    with archive.open("wb") as target:
        for part in parts:
            with part.open("rb") as source:
                shutil.copyfileobj(source, target)


def install(package):
    name, url, expected = package
    archive = DOWNLOADS / url.rsplit("/", 1)[1]
    destination = TOOLS / name
    if destination.exists():
        raise RuntimeError(f"Refusing to overwrite existing tool directory: {destination}")
    print(f"Downloading {name}: {archive.name}", flush=True)
    if name == "grafana":
        download_grafana(url, archive)
    else:
        subprocess.run([
            "curl.exe", "--fail", "--location", "--retry", "2", "--silent", "--show-error",
            "--connect-timeout", "15", "--max-time", "600", "--output", str(archive), url,
        ], check=True)
    with archive.open("rb") as source:
        actual = hashlib.file_digest(source, "sha256").hexdigest()
    if actual != expected:
        raise RuntimeError(f"{name}: SHA256 mismatch; not extracting")
    print(f"Verified SHA256: {name}", flush=True)
    destination.mkdir()
    if archive.suffix == ".zip":
        with zipfile.ZipFile(archive) as source:
            for member in source.infolist():
                parts = PurePosixPath(member.filename).parts
                if len(parts) < 2:
                    continue
                target = destination.joinpath(*parts[1:]).resolve()
                if not target.is_relative_to(destination.resolve()):
                    raise RuntimeError("Unsafe archive path")
                if member.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with source.open(member) as src, target.open("wb") as dst:
                        shutil.copyfileobj(src, dst)
    else:
        # Use Windows' native tar to avoid per-file emulation overhead.
        # The exact official archive has already passed SHA256 verification.
        subprocess.run([
            "tar.exe", "-xzf", str(archive),
            "--exclude", "grafana-13.2.4/docs", "--exclude", "grafana-13.2.4/packaging",
            "--exclude", "*.ts", "--exclude", "*.tsx", "--exclude", "*.map",
            "--exclude", "*.scss", "--exclude", "*.md", "--exclude", "*.snap",
            "--exclude", "*.cue", "--exclude", "*.go", "--exclude", "*.sh",
            "--strip-components", "1",
            "-C", str(destination),
        ], check=True)
    print(f"Extracted {name}: {destination}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", choices=["prometheus", "grafana"])
    args = parser.parse_args()
    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    (DOWNLOADS / "SHA256SUMS.txt").write_text(
        "".join(f"{sha}  {url.rsplit('/', 1)[1]}\n" for _, url, sha in PACKAGES),
        encoding="utf-8",
    )
    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(install, [p for p in PACKAGES if args.only is None or p[0] == args.only]))
