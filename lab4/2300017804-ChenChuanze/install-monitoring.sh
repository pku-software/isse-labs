#!/bin/bash
set -euo pipefail
LAB4_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$LAB4_ROOT"

if [[ "$(uname -s)" != Darwin || "$(uname -m)" != arm64 ]]; then
  printf 'This installer is for macOS ARM64; choose official binaries for your platform.\n' >&2
  exit 1
fi

PROM_ARCHIVE=prometheus-3.15.0.darwin-arm64.tar.gz
GRAFANA_ARCHIVE=grafana_13.2.4_38252365904_darwin_arm64.tar.gz
PROM_SHA=920df4d17e78b3b0175af144eb318b0c74d1cf7b1d1251b326966f0e81977260
GRAFANA_SHA=a910966466359212f1d875748a72a4638c7d3724448d0c369210b31d763b165d

for ignored in \
  ".tools/downloads/$PROM_ARCHIVE" ".tools/downloads/$GRAFANA_ARCHIVE" \
  .tools/downloads/checksums.sha256 .tools/prometheus/prometheus \
  .tools/grafana/bin/grafana .runtime/prometheus/wal \
  .runtime/grafana/data/grafana.db .runtime/grafana/logs/grafana.log \
  .runtime/grafana/plugins/example .venv/pyvenv.cfg; do
  git check-ignore -q -- "$LAB4_ROOT/$ignored" || {
    printf 'Missing ignore rule: %s\n' "$ignored" >&2
    exit 1
  }
done
if [[ -n "$(git ls-files -- "$LAB4_ROOT/.tools" "$LAB4_ROOT/.runtime" "$LAB4_ROOT/.venv")" ]]; then
  printf 'Tool/runtime files are already tracked; review them before installing.\n' >&2
  exit 1
fi

mkdir -p .tools/downloads .tools/prometheus .tools/grafana
download() {
  local archive="$1" expected="$2" url="$3"
  if [[ -f ".tools/downloads/$archive" ]] && \
      [[ "$(shasum -a 256 ".tools/downloads/$archive" | cut -d ' ' -f 1)" == "$expected" ]]; then
    printf 'Using verified archive: %s\n' "$archive"
    return
  fi
  curl --fail --location --retry 3 --connect-timeout 20 \
    --output ".tools/downloads/$archive.part" "$url"
  printf '%s  %s\n' "$expected" "$archive.part" > .tools/downloads/checksums.sha256
  (cd .tools/downloads && shasum -a 256 -c checksums.sha256)
  mv ".tools/downloads/$archive.part" ".tools/downloads/$archive"
}

download "$PROM_ARCHIVE" "$PROM_SHA" \
  "https://github.com/prometheus/prometheus/releases/download/v3.15.0/$PROM_ARCHIVE"
download "$GRAFANA_ARCHIVE" "$GRAFANA_SHA" \
  "https://dl.grafana.com/grafana/release/13.2.4/$GRAFANA_ARCHIVE"

tar -xzf ".tools/downloads/$PROM_ARCHIVE" -C .tools/prometheus --strip-components=1
tar -xzf ".tools/downloads/$GRAFANA_ARCHIVE" -C .tools/grafana --strip-components=1
.tools/prometheus/prometheus --version
.tools/grafana/bin/grafana --version
