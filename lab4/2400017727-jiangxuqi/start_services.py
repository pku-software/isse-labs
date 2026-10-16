"""Start only this lab's local services, using dedicated data and PID files."""
import argparse
import os
from pathlib import Path
import shutil
import socket
import subprocess
import time
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parent


def start(name):
    runtime = ROOT / '.runtime' / name
    runtime.mkdir(parents=True, exist_ok=True)
    pidfile = runtime / f'{name}.pid'
    env = dict(os.environ)
    if name == 'app':
        port, health = 5001, '/api/lab-status'
        command = [str(ROOT / '.venv/bin/python'), str(ROOT / 'app.py')]
        env.update(MODEL_MODE='mock', PORT=str(port))
    elif name == 'prometheus':
        port, health = 9090, '/-/ready'
        command = [str(ROOT / '.tools/prometheus/prometheus'),
                   '--config.file=' + str(ROOT / 'prometheus.yml'),
                   '--storage.tsdb.path=' + str(runtime),
                   '--web.listen-address=127.0.0.1:9090']
    else:
        port, health = 3000, '/api/health'
        home = ROOT / '.tools/grafana'
        for rel in ['data', 'log', 'plugins', 'dashboards']:
            (runtime / rel).mkdir(exist_ok=True)
        shutil.copy2(ROOT / 'grafana-dashboard.json', runtime / 'dashboards/grafana-dashboard.json')
        command = [str(home / 'bin/grafana'), 'server', '--homepath=' + str(home),
                   '--config=' + str(ROOT / 'grafana.ini')]
        env.update(LAB4_ROOT=str(ROOT), GF_PATHS_DATA=str(runtime / 'data'),
                   GF_PATHS_LOGS=str(runtime / 'log'), GF_PATHS_PLUGINS=str(runtime / 'plugins'),
                   GF_PATHS_PROVISIONING=str(ROOT / 'config/grafana/provisioning'),
                   GF_DASHBOARDS_MIN_REFRESH_INTERVAL='2s')
    if pidfile.exists():
        pid = pidfile.read_text().strip()
        procfile = Path('/proc') / pid / 'cmdline'
        if procfile.exists() and str(ROOT).encode() in procfile.read_bytes():
            print(f'{name}: already running, PID {pid}')
            return
    with socket.socket() as sock:
        try:
            sock.bind(('127.0.0.1', port))
        except OSError as error:
            raise RuntimeError(f'Port {port} is occupied; do not stop unrelated services.') from error
    with (runtime / f'{name}.log').open('ab') as log:
        proc = subprocess.Popen(command, cwd=ROOT, env=env, stdin=subprocess.DEVNULL,
                                stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    pidfile.write_text(str(proc.pid) + '\n')
    for _ in range(60):
        if proc.poll() is not None:
            raise RuntimeError(f'{name} exited; inspect {runtime}')
        try:
            with urlopen(f'http://127.0.0.1:{port}{health}', timeout=1) as response:
                if response.status == 200:
                    print(f'{name}: ready on 127.0.0.1:{port}, PID {proc.pid}')
                    return
        except OSError:
            time.sleep(0.5)
    raise RuntimeError(f'{name}: readiness timeout; inspect {runtime}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--service', choices=['app', 'prometheus', 'grafana', 'all'], default='all')
    args = parser.parse_args()
    for rel in ['.tools/prometheus/prometheus', '.tools/grafana/bin/grafana',
                '.runtime/prometheus/wal', '.runtime/grafana/data/grafana.db',
                '.runtime/app/app.log', '.venv/pyvenv.cfg']:
        subprocess.run(['git', 'check-ignore', '-q', '--', str(ROOT / rel)], cwd=ROOT, check=True)
    tracked = subprocess.check_output(['git', 'ls-files', '--', '.tools', '.runtime', '.venv'], cwd=ROOT)
    if tracked:
        raise SystemExit('Tool/runtime files are tracked; resolve before starting.')
    for service in (['app', 'prometheus', 'grafana'] if args.service == 'all' else [args.service]):
        start(service)
