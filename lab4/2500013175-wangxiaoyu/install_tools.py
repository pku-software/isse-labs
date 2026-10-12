"""Download verified official macOS arm64 tools into the personal ignored paths."""

import argparse
import hashlib
from pathlib import Path
import platform
import re
import shutil
import subprocess
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parent
DOWNLOADS = ROOT / ".tools" / "downloads"
SOURCES = {
    "prometheus": {
        "archive": "prometheus-3.15.0.darwin-arm64.tar.gz",
        "url": "https://github.com/prometheus/prometheus/releases/download/v3.15.0/",
        "checksum": "sha256sums.txt",
        "executable": "prometheus",
    },
    "grafana": {
        "archive": "grafana_13.2.3_36482603486_darwin_arm64.tar.gz",
        "url": "https://dl.grafana.com/grafana/release/13.2.3/",
        "checksum": "grafana_13.2.3_36482603486_darwin_arm64.tar.gz.sha256",
        "executable": "bin/grafana",
    },
}


def download(url, path, resume=False):
    # System curl supports this Mac's SOCKS proxy without bootstrapping PySocks.
    command = ["curl", "--location", "--fail", "--silent", "--show-error",
               "--retry", "2", "--connect-timeout", "20",
               "--speed-limit", "1024", "--speed-time", "30",
               "--output", str(path)]
    if resume and path.exists():
        command += ["--continue-at", "-"]
    process = subprocess.Popen([*command, "--", url])
    try:
        while process.poll() is None:
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                size = path.stat().st_size if path.exists() else 0
                print(f"{path.name}: downloaded {size / 1048576:.1f} MiB", flush=True)
        if process.returncode:
            raise RuntimeError(f"Official download failed: curl exit {process.returncode}")
    except BaseException:
        process.terminate()
        process.wait()
        raise


def install(name):
    source = SOURCES[name]
    archive = DOWNLOADS / source["archive"]
    checksum = DOWNLOADS / source["checksum"]
    destination = ROOT / ".tools" / name
    executable = destination / source["executable"]
    repo = ROOT.parents[1]
    paths = [str(path.relative_to(repo)) for path in (archive, checksum, executable)]
    for path in paths:
        subprocess.run(["git", "check-ignore", "-q", "--", path], cwd=repo, check=True)
    tracked = subprocess.check_output(["git", "ls-files", "--", str(destination.relative_to(repo)),
                                       str(DOWNLOADS.relative_to(repo))], cwd=repo)
    if tracked:
        raise RuntimeError("Tool paths contain tracked files; stop before downloading")
    if executable.exists():
        print(f"{name}: already installed at {executable}", flush=True)
        return
    if destination.exists():
        raise RuntimeError(f"Existing incomplete directory: {destination}")
    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    download(source["url"] + source["checksum"], checksum)
    lines = checksum.read_text().splitlines()
    line = next((line for line in lines if source["archive"] in line), None)
    if line is None and len(lines) == 1:
        line = lines[0]
    expected = line.split()[0] if line else ""
    if not re.fullmatch(r"[0-9a-fA-F]{64}", expected):
        raise RuntimeError("Official checksum could not be parsed")
    partial = archive.with_suffix(archive.suffix + ".part")
    verified = False
    if archive.exists():
        with archive.open("rb") as file:
            verified = hashlib.file_digest(file, "sha256").hexdigest() == expected.lower()
    if not verified:
        download(source["url"] + source["archive"], partial, resume=True)
        with partial.open("rb") as file:
            actual = hashlib.file_digest(file, "sha256").hexdigest()
        if actual != expected.lower():
            raise RuntimeError("SHA256 mismatch; archive will not be extracted")
        partial.replace(archive)
    print(f"{name}: SHA256 verified", flush=True)
    with tempfile.TemporaryDirectory(dir=DOWNLOADS) as temporary:
        with tarfile.open(archive) as package:
            package.extractall(temporary, filter="data")
        roots = list(Path(temporary).iterdir())
        if len(roots) != 1 or not roots[0].is_dir():
            raise RuntimeError("Unexpected archive layout")
        shutil.move(str(roots[0]), destination)
    if not executable.is_file():
        raise RuntimeError("Expected tool executable is missing")
    print(f"{name}: installed at {destination}", flush=True)


if __name__ == "__main__":
    if platform.system() != "Darwin" or platform.machine() != "arm64":
        raise SystemExit("This installer is for macOS arm64")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tool", choices=("all", *SOURCES), nargs="?", default="all")
    args = parser.parse_args()
    for name in SOURCES if args.tool == "all" else [args.tool]:
        install(name)
