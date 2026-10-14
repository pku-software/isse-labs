"""从仓库根目录运行：个人 .venv/Scripts/python.exe <个人目录>/start-monitoring.py。"""

import argparse
import json
import os
from pathlib import Path
import runpy
import secrets
import socket
import subprocess
import time

import requests


ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--service', choices=['all', 'app', 'prometheus', 'grafana'], default='all')
    selected = parser.parse_args().service
    names = ['app', 'prometheus', 'grafana']
    chosen = names if selected == 'all' else [selected]
    runpy.run_path(str(ROOT / 'install-monitoring.py'))['check_ignored']()
    for name, port in zip(names, [5001, 9090, 3001]):
        if name not in chosen:
            continue
        with socket.socket() as probe:
            try:
                probe.bind(('127.0.0.1', port))
            except OSError:
                raise SystemExit(f'Port {port} is occupied; no new services started. Check existing lab services.')
    executables = [ROOT / '.venv/Scripts/python.exe', ROOT / '.tools/prometheus/prometheus.exe',
                   ROOT / '.tools/grafana/bin/grafana.exe']
    for name, executable in zip(names, executables):
        if name not in chosen:
            continue
        if not executable.is_file():
            raise SystemExit(f'Missing {executable}; install dependencies and monitoring tools first.')
    for directory in ['app', 'prometheus', 'grafana/data', 'grafana/logs', 'grafana/plugins', 'grafana/dashboards']:
        (ROOT / '.runtime' / directory).mkdir(parents=True, exist_ok=True)
    # 仅向专用目录提供仪表盘，避免扫描 results/ 中的 JSON。
    source = ROOT / 'grafana-dashboard.json'
    (ROOT / '.runtime/grafana/dashboards/grafana-dashboard.json').write_bytes(source.read_bytes())
    password_file = ROOT / '.runtime/grafana/admin-password.txt'
    if not password_file.exists():
        password_file.write_text(secrets.token_urlsafe(32), encoding='ascii')
    app_env = {**os.environ, 'CHAT_MODE': 'mock', 'PORT': '5001', 'PYTHONUTF8': '1'}
    grafana_env = {**os.environ,
                   'GF_PATHS_DATA': str(ROOT / '.runtime/grafana/data'),
                   'GF_PATHS_LOGS': str(ROOT / '.runtime/grafana/logs'),
                   'GF_PATHS_PLUGINS': str(ROOT / '.runtime/grafana/plugins'),
                   'GF_PATHS_PROVISIONING': str(ROOT / 'grafana-provisioning'),
                   'GF_SECURITY_ADMIN_PASSWORD': password_file.read_text(encoding='ascii').strip(),
                   'LAB4_DASHBOARD_PATH': str(ROOT / '.runtime/grafana/dashboards')}
    services = [
        ('app', [str(executables[0]), '-u', str(ROOT / 'app.py')], app_env,
         'http://127.0.0.1:5001/api/lab/status'),
        ('prometheus', [str(executables[1]), f'--config.file={ROOT / "prometheus.yml"}',
                        f'--storage.tsdb.path={ROOT / ".runtime/prometheus"}',
                        '--web.listen-address=127.0.0.1:9090', '--storage.tsdb.retention.time=7d'],
         os.environ.copy(), 'http://127.0.0.1:9090/-/ready'),
        ('grafana', [str(executables[2]), 'server', '--homepath', str(ROOT / '.tools/grafana'),
                     '--config', str(ROOT / 'grafana.ini')], grafana_env,
         'http://127.0.0.1:3001/api/health'),
    ]
    processes = []
    records = []
    session = requests.Session()
    session.trust_env = False
    try:
        for name, command, environment, health in services:
            if name not in chosen:
                continue
            log_directory = ROOT / '.runtime' / name
            startup = subprocess.STARTUPINFO()
            startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startup.wShowWindow = subprocess.SW_HIDE
            with (log_directory / 'stdout.log').open('ab') as stdout, (log_directory / 'stderr.log').open('ab') as stderr:
                process = subprocess.Popen(command, cwd=ROOT.parents[1], env=environment,
                                           stdout=stdout, stderr=stderr,
                                           stdin=subprocess.DEVNULL, startupinfo=startup,
                                           creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NEW_CONSOLE)
            processes.append(process)
            records.append({'name': name, 'pid': process.pid, 'command': command, 'health': health})
            deadline = time.monotonic() + 300
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    raise RuntimeError(f'{name} exited; inspect {log_directory / "stderr.log"}')
                try:
                    if session.get(health, timeout=2).status_code == 200:
                        break
                except requests.RequestException:
                    pass
                time.sleep(0.5)
            else:
                raise RuntimeError(f'{name} did not become ready')
            print(f'{name}: ready, PID {process.pid}, {health}', flush=True)
    except BaseException:
        for process in reversed(processes):
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=10)
        raise
    finally:
        session.close()
    record_file = ROOT / '.runtime/processes.json'
    previous = json.loads(record_file.read_text(encoding='utf-8')) if record_file.exists() else []
    records = [record for record in previous if record['name'] not in chosen] + records
    record_file.write_text(json.dumps(records, indent=2) + '\n', encoding='utf-8')
    if 'prometheus' in chosen:
        print('Targets: http://127.0.0.1:9090/targets', flush=True)
    if 'grafana' in chosen:
        print('Dashboard: http://127.0.0.1:3001/d/lab4-chat', flush=True)


if __name__ == '__main__':
    main()
