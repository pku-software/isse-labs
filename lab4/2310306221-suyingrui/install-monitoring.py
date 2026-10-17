"""Install pinned official macOS arm64 tools into this project's ignored .tools/."""

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
from pathlib import Path
import platform
import shutil
import subprocess


ROOT = Path(__file__).resolve().parent
PACKAGES = {
    "prometheus": (
        "https://github.com/prometheus/prometheus/releases/download/v3.15.0/prometheus-3.15.0.darwin-arm64.tar.gz",
        "920df4d17e78b3b0175af144eb318b0c74d1cf7b1d1251b326966f0e81977260",
        109656029,
    ),
    "grafana": (
        "https://dl.grafana.com/grafana/release/13.2.3/grafana_13.2.3_36482603486_darwin_arm64.tar.gz",
        "248a51bcfacdb1ec642006cee46b4de44a34bcf41ddea88d96a4605e2e9d808c",
        454184444,
    ),
}


def check_ignored_paths():
    for name in (
        ".tools/downloads/example.tar.gz", ".tools/prometheus/prometheus",
        ".tools/grafana/bin/grafana", ".runtime/prometheus/wal",
        ".runtime/grafana/grafana.db", ".runtime/app/server.log", ".venv/pyvenv.cfg",
    ):
        subprocess.run(["git", "check-ignore", "-q", "--", str(ROOT / name)],
                       cwd=ROOT, check=True)
    tracked = subprocess.check_output(
        ["git", "ls-files", "--", ".tools", ".runtime", ".venv"], cwd=ROOT
    )
    if tracked.strip():
        raise RuntimeError("Tools or runtime files are tracked; resolve before installing")


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download_chunks(url, output, size):
    """Keep verified-length chunks across network retries; verify full SHA afterwards."""
    chunk_size = 8 * 1024 * 1024
    parts_dir = output.with_name(output.name + ".chunks")
    parts_dir.mkdir(exist_ok=True)
    ranges = [(start, min(start + chunk_size, size) - 1)
              for start in range(0, size, chunk_size)]

    def fetch(bounds):
        start, end = bounds
        part = parts_dir / f"{start:012d}.bin"
        if not part.exists() or part.stat().st_size != end - start + 1:
            subprocess.run([
                "curl", "--http1.1", "--fail", "--location", "--silent", "--show-error",
                "--retry", "2", "--connect-timeout", "15", "--max-time", "180",
                "--range", f"{start}-{end}", "--output", str(part), url,
            ], check=True)
        if part.stat().st_size != end - start + 1:
            raise RuntimeError("Unexpected download chunk length")
        return end - start + 1

    completed = 0
    with ThreadPoolExecutor(max_workers=4) as pool:
        for future in as_completed([pool.submit(fetch, bounds) for bounds in ranges]):
            completed += future.result()
            print(f"Downloaded {completed / size:.0%}", flush=True)
    with output.open("wb") as target:
        for start, _ in ranges:
            with (parts_dir / f"{start:012d}.bin").open("rb") as part:
                shutil.copyfileobj(part, target)


def install(name):
    url, expected, size = PACKAGES[name]
    downloads = ROOT / ".tools" / "downloads"
    downloads.mkdir(parents=True, exist_ok=True)
    archive = downloads / url.rsplit("/", 1)[1]
    # Published SHA-256 values from the official download pages linked in README.
    archive.with_name(archive.name + ".sha256").write_text(
        f"{expected}  {archive.name}\n", encoding="utf-8"
    )
    if not archive.exists() or sha256(archive) != expected:
        temporary = archive.with_name(archive.name + ".part")
        print(f"Downloading {name} from {url}", flush=True)
        download_chunks(url, temporary, size)
        if sha256(temporary) != expected:
            raise RuntimeError(f"{name}: SHA-256 mismatch; extraction refused")
        temporary.replace(archive)
    print(f"{name}: SHA-256 verified", flush=True)
    target = ROOT / ".tools" / name
    if target.exists() and any(target.iterdir()):
        print(f"{target} already exists; preserving installed files", flush=True)
        return
    target.mkdir(parents=True, exist_ok=True)
    subprocess.run(["tar", "-xzf", str(archive), "-C", str(target), "--strip-components=1"],
                   check=True)
    print(f"{name}: extracted to {target}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--component", choices=("all", *PACKAGES), default="all")
    args = parser.parse_args()
    if platform.system() != "Darwin" or platform.machine() != "arm64":
        raise SystemExit("These pinned packages are for macOS arm64")
    check_ignored_paths()
    for component in PACKAGES if args.component == "all" else (args.component,):
        install(component)
