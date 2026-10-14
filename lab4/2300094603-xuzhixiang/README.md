# Lab 4 — Chat Service Monitoring

**Student:** 许智翔 (2300094603)

**Branch:** `lab4/2300094603-xuzhixiang`

This lab instruments the personal Flask chat app with Prometheus metrics, scrapes the app locally, and visualizes request outcomes, in-progress work, and request duration in Grafana. The app runs in mock mode for the experiment; no external model API is called.

## Metric meanings

- `chat_requests_total{outcome="success|error"}` is a Counter. It records completed chat requests by outcome and only increases. An error increments the `error` series; it does not reduce the counter.
- `chat_inprogress_requests` is a Gauge. It rises while a chat request is being handled and is decremented in a `finally` block, including when the request ends with an error.
- `chat_request_duration_seconds` is a Histogram. Its bucket series show how observations are distributed across duration thresholds; `_sum` and `_count` support average-duration calculations.

Only `POST /api/messages` is included in these chat metrics. The `/metrics` endpoint and status checks do not change the chat counters.

## Local setup

The downloaded tools and their databases stay in ignored `.tools/` and `.runtime/` directories. The committed Prometheus and Grafana configuration lives beside this README.

The verified official archives for this Mac are Prometheus 3.15.0 (`darwin/arm64`, SHA256 `920df4d17e78b3b0175af144eb318b0c74d1cf7b1d1251b326966f0e81977260`) and Grafana OSS 13.2.3 (`darwin/arm64`, SHA256 `248a51bcfacdb1ec642006cee46b4de44a34bcf41ddea88d96a4605e2e9d808c`). Get official releases from [Prometheus downloads](https://prometheus.io/download/) and [Grafana OSS downloads](https://grafana.com/grafana/download?edition=oss&platform=mac).

### Recreate from a clean checkout

On this Apple Silicon Mac, create the ignored Python environment and runtime directories:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
mkdir -p .tools/downloads .runtime/app .runtime/prometheus \
  .runtime/grafana/data .runtime/grafana/logs .runtime/grafana/plugins
```

Download the official `prometheus-3.15.0.darwin-arm64.tar.gz` and `grafana_13.2.3_36482603486_darwin_arm64.tar.gz` archives into `.tools/downloads/`. Compare their SHA256 values with the hashes above, then extract and rename the top-level directories:

```sh
shasum -a 256 .tools/downloads/prometheus-3.15.0.darwin-arm64.tar.gz
shasum -a 256 .tools/downloads/grafana_13.2.3_36482603486_darwin_arm64.tar.gz
tar -xzf .tools/downloads/prometheus-3.15.0.darwin-arm64.tar.gz -C .tools
mv .tools/prometheus-3.15.0.darwin-arm64 .tools/prometheus
tar -xzf .tools/downloads/grafana_13.2.3_36482603486_darwin_arm64.tar.gz -C .tools
mv .tools/grafana-13.2.3 .tools/grafana
```

Grafana loads the Prometheus data source from `grafana/provisioning/datasources/lab4-prometheus.yml` and the dashboard provider from `grafana/provisioning/dashboards/lab4-provider.yml` at startup; the dashboard JSON is under `grafana/dashboards/`.

Run each service in a separate Terminal window from this directory:

```sh
CHAT_APP_MODE=mock LAB4_EXPERIMENT_ENABLED=1 CHAT_DATA_FILE=.runtime/app/messages.json \
  .venv/bin/python app.py
```

```sh
./.tools/prometheus/prometheus \
  --config.file=prometheus.yml \
  --storage.tsdb.path=.runtime/prometheus \
  --web.listen-address=127.0.0.1:9090
```

```sh
GF_PATHS_HOME="$PWD/.tools/grafana" \
GF_PATHS_DATA="$PWD/.runtime/grafana/data" \
GF_PATHS_LOGS="$PWD/.runtime/grafana/logs" \
GF_PATHS_PLUGINS="$PWD/.runtime/grafana/plugins" \
GF_PATHS_PROVISIONING="$PWD/grafana/provisioning" \
GF_SERVER_HTTP_ADDR=127.0.0.1 \
GF_SERVER_HTTP_PORT=3000 \
  ./.tools/grafana/bin/grafana server --homepath "$PWD/.tools/grafana"
```

Open the local interfaces:

- Chat app: <http://127.0.0.1:5001/>
- App metrics: <http://127.0.0.1:5001/metrics>
- Prometheus targets: <http://127.0.0.1:9090/targets>
- Prometheus query page: <http://127.0.0.1:9090/query>
- Grafana: <http://127.0.0.1:3000/>

## Prometheus and Grafana

Prometheus scrapes `127.0.0.1:5001/metrics` every 2 seconds with a 1-second timeout. The Grafana data source is provisioned with UID `lab4-prometheus`; the dashboard is provisioned from `grafana/dashboards/lab4-monitoring.json`.

The **Lab 4 Chat Monitoring** dashboard contains these panels:

1. Request rate split by outcome: `sum by (outcome) (rate(chat_requests_total{job="chat-app"}[30s]))`
2. Current requests in progress: `sum(chat_inprogress_requests{job="chat-app"})`
3. Mean request duration: `sum(rate(chat_request_duration_seconds_sum{job="chat-app"}[30s])) / sum(rate(chat_request_duration_seconds_count{job="chat-app"}[30s]))`

The request-rate and mean-duration panels need observations in their 30-second range to draw a value. The dashboard refreshes every 5 seconds, Grafana's minimum refresh interval for this local setup.

## Verification notes

- The Flask app reports `mode=mock` and `external_model_calls=false` at `/api/lab4/status`.
- Prometheus is configured with the `chat-app` job and local target. On 2026-10-13, a refreshed Targets view showed `1 / 1 up`, with the last scrape 1.7 seconds earlier and a 2 ms scrape duration.
- The query `chat_requests_total{job="chat-app"}` returned two series: `outcome="success"` = 6 and `outcome="error"` = 1. The success value had been 5 earlier in the observation, so it increased by one.
- Target `UP` means Prometheus successfully scraped `/metrics` at the last scrape. It does not mean a client is online or prove an end-to-end chat reply; that needs a successful chat request and a visible reply, with the success counter increasing as supporting evidence.
- Grafana's local health endpoint reported database `ok`, version 13.2.3. Startup logs show the Prometheus data source and dashboard were provisioned.

## Simulation results

The course-provided `simulate_traffic.py` was adapted through `project_adapter.py` and run against the local mock app. Both result files are kept for reproduction and comparison.

The adapter checks `/api/lab4/status` for mock mode, sends `POST /api/messages`, and classifies replies from the HTTP status and response JSON. To reproduce the two runs after starting the app, Prometheus, and Grafana:

```sh
./.venv/bin/python simulate_traffic.py --base-url http://127.0.0.1:5001 \
  --scenario all --phase-seconds 30 --concurrency 6 --settle-seconds 10 \
  --output results/first-run.json
```

```sh
./.venv/bin/python simulate_traffic.py --base-url http://127.0.0.1:5001 \
  --scenario slow --phase-seconds 30 --concurrency 10 --settle-seconds 10 \
  --output results/changed-run.json
```

Artifacts: [default run](results/first-run.json), [changed run](results/changed-run.json), [Prometheus target UP screenshot](screenshots/prometheus-targets.png), and [Grafana dashboard screenshot](screenshots/grafana-dashboard.png).

### Default run

Run on 2026-10-13 from 09:30:37 to 09:33:10 China Standard Time with all five default phases and a concurrency limit of 6. The script reported no transport errors or unexpected results.

| Phase | Scheduled | Sent | Skipped | Success | HTTP/business errors | Client mean |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `baseline` | 30 | 30 | 0 | 30 | 0 | 0.122 s |
| `burst` | 120 | 120 | 0 | 120 | 0 | 0.124 s |
| `slow` (2 req/s, 3 s delay, concurrency 6) | 60 | 52 | 8 | 52 | 0 | 3.023 s |
| `errors` (every third request fails) | 30 | 30 | 0 | 20 | 10 | 0.121 s |
| `recovery` | 30 | 30 | 0 | 30 | 0 | 0.120 s |

The burst raised successful request rate without producing errors. In the slow phase, the finite concurrency limit caused 8 scheduled send opportunities to be skipped; the script does not queue them for later. The errors phase produced the configured 10 failures, then the recovery phase returned to successful, low-latency requests.

### Changed run

Run on 2026-10-13 from 10:44:17 to 10:44:50 China Standard Time with `--scenario slow --concurrency 10`; the slow rate (2 req/s), mock delay (3 s), and duration (30 s) matched the default run.

| Phase | Concurrency | Scheduled | Sent | Skipped | Success | Errors | Client mean |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `slow` | 10 | 60 | 60 | 0 | 60 | 0 | 3.021 s |

Increasing the concurrency limit from 6 to 10 reduced skipped opportunities from 8 to 0. The mean client duration stayed about 3.02 s. Prometheus's 2-second gauge samples averaged 4.59 in-progress requests in the first slow phase and 5.18 in the changed phase; both phases reached a sampled peak of 6, and the current gauge returned to 0 after completion. The server-side 30-second histogram mean evaluated at each phase end was 3.006 s and 3.005 s, respectively.

The Grafana comparison used a two-hour browser-time range covering both runs. The in-progress Stat showed 0 at the end while its sparkline retained the historical activity.

The JSON reports contain client-side durations, including HTTP overhead. They are useful for comparing these runs, but they are not substitutes for the server-side Prometheus histogram.
