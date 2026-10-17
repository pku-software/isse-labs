"""Start this project's local Prometheus and Grafana; preserve occupied ports."""

import argparse
import os
from pathlib import Path
import socket
import subprocess
import time
from urllib.request import ProxyHandler, build_opener

from importlib.util import module_from_spec, spec_from_file_location


ROOT = Path(__file__).resolve().parent


def wait_ready(process, url):
    opener = build_opener(ProxyHandler({}))
    deadline = time.monotonic() + 40
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"Process exited; inspect its log for {url}")
        try:
            with opener.open(url, timeout=1) as response:
                if response.status == 200:
                    return
        except OSError:
            pass
        time.sleep(0.25)
    raise RuntimeError(f"Service not ready yet; inspect its log: {url}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--component", choices=("all", "prometheus", "grafana"), default="all")
    args = parser.parse_args()
    spec = spec_from_file_location("install_monitoring", ROOT / "install-monitoring.py")
    installer = module_from_spec(spec)
    spec.loader.exec_module(installer)
    installer.check_ignored_paths()
    selected = ("prometheus", "grafana") if args.component == "all" else (args.component,)
    executables = {"prometheus": ROOT / ".tools/prometheus/prometheus",
                   "grafana": ROOT / ".tools/grafana/bin/grafana"}
    for name in selected:
        if not executables[name].is_file():
            raise SystemExit(f"Install {name} before starting it")
    # Check selected ports before starting. Never stop a service merely to free a port.
    for port in (9090 if name == "prometheus" else 3000 for name in selected):
        with socket.socket() as sock:
            try:
                sock.bind(("127.0.0.1", port))
            except OSError:
                raise SystemExit(f"Port {port} is occupied; preserve its process and inspect first")

    for name in ("prometheus", "grafana/data", "grafana/logs", "grafana/plugins"):
        (ROOT / ".runtime" / name).mkdir(parents=True, exist_ok=True)

    if "prometheus" in selected:
        prom_command = [
            str(ROOT / ".tools/prometheus/prometheus"),
            f"--config.file={ROOT / 'prometheus.yml'}",
            f"--storage.tsdb.path={ROOT / '.runtime/prometheus'}",
            "--storage.tsdb.retention.time=7d", "--web.listen-address=127.0.0.1:9090",
        ]
        subprocess.run([str(ROOT / ".tools/prometheus/promtool"), "check", "config",
                        str(ROOT / "prometheus.yml")], check=True)
        with (ROOT / ".runtime/prometheus/console.log").open("ab") as log:
            prometheus = subprocess.Popen(prom_command, cwd=ROOT, stdin=subprocess.DEVNULL,
                                          stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        (ROOT / ".runtime/prometheus/server.pid").write_text(f"{prometheus.pid}\n")
        wait_ready(prometheus, "http://127.0.0.1:9090/-/ready")
        print(f"Prometheus ready: http://127.0.0.1:9090/ (PID {prometheus.pid})", flush=True)

    if "grafana" not in selected:
        return

    env = dict(os.environ, LAB4_PROJECT_DIR=str(ROOT))
    for key, path in {
        "GF_PATHS_DATA": ".runtime/grafana/data",
        "GF_PATHS_LOGS": ".runtime/grafana/logs",
        "GF_PATHS_PLUGINS": ".runtime/grafana/plugins",
        "GF_PATHS_PROVISIONING": "grafana/provisioning",
    }.items():
        env[key] = str(ROOT / path)
    grafana_command = [str(ROOT / ".tools/grafana/bin/grafana"), "server",
                       "--homepath", str(ROOT / ".tools/grafana"),
                       "--config", str(ROOT / "grafana.ini")]
    with (ROOT / ".runtime/grafana/logs/console.log").open("ab") as log:
        grafana = subprocess.Popen(grafana_command, cwd=ROOT, env=env, stdin=subprocess.DEVNULL,
                                   stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    (ROOT / ".runtime/grafana/server.pid").write_text(f"{grafana.pid}\n")
    wait_ready(grafana, "http://127.0.0.1:3000/api/health")
    print(f"Grafana ready: http://127.0.0.1:3000/d/lab4-chat (PID {grafana.pid})", flush=True)


if __name__ == "__main__":
    main()
