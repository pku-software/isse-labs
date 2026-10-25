# Lab5 Chat CI

An isolated copy of the Lab2 Flask chat application. Backend: `app.py`;
static UI: `frontend/`; API tests: `tests/`.

## Install and launch

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env
python app.py
```

Configure a real model API key in `.env` for interactive chat, then open
http://127.0.0.1:5001. The development server runs with debug mode enabled.
Never commit `.env`.

Records default to `data/messages.json`, starting empty when the file is absent.
Set `LAB5_DATA_DIR` to a directory to use a different `messages.json` location:

```sh
LAB5_DATA_DIR=/tmp/lab5-chat python app.py
```

The API provides GET `/`, GET `/api/hello`, POST/GET `/api/messages`, and
PATCH/DELETE `/api/messages/<id>`.

## Tests

```sh
.venv/bin/python -m pytest -q --cov=app --cov-report=term-missing --cov-fail-under=70
```

Tests require no real API key. The fixture supplies a placeholder key, removes
the alternative key, and mocks the model HTTP request with a fixed reply.
Each test sets `LAB5_DATA_DIR` to pytest's temporary directory before importing
or reloading the app, so writes never reach the default chat history. Coverage
measures the full `app.py`; the command fails below 70%.

## Smoke test

```sh
.venv/bin/python scripts/smoke_test.py
```

Unlike Flask `test_client`, this check starts a real temporary HTTP service on
a random local port and checks `/` and `/api/hello`. It uses a placeholder key,
requires no real model request, and isolates data with `LAB5_DATA_DIR`. The
service stops and temporary data is removed after the check. CI runs the same
script after the coverage tests.

## Local runner stage

CI currently runs on the user's Mac through a self-hosted runner, only for pushes
to `main`; pull request jobs are skipped during this local stage. Jobs use the
runner's `_work` checkout, not the development folder. The workflow creates an
independent `.venv` using
`/Users/carrie/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3`,
then runs the same dependency installation, coverage tests, and smoke test.
Earlier cloud runs remain preserved in the Actions history. After collecting
the local run evidence, stop the foreground runner with Ctrl+C.
