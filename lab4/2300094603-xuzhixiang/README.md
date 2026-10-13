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

This section will be completed after the guided traffic simulation and the student's observations.
