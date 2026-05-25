# A/B Test Calculator for VibeCode

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export VIBECODE_API_KEY="<your_key>"
export VIBECODE_MODEL="bitrix/bitrixgpt-5.5"
uvicorn main:app --host 0.0.0.0 --port 8000
```

Open: `http://localhost:8000/docs`

## VibeCode AI Router

The endpoint `/ai/suggest` uses model `bitrix/bitrixgpt-5.5` via AI Router (`https://vibecode.bitrix24.tech/v1/chat/completions`).

## Deploy via VibeCode Deploy API

Use Deploy API (not SSH) as requested.

1) Set required variables:

```bash
export VIBECODE_API_KEY="<your_key>"
export VIBECODE_DEPLOY_API_URL="https://vibecode.bitrix24.tech/v1/infra/deploy"
export VIBECODE_MODEL="bitrix/bitrixgpt-5.5"
```

2) Trigger deployment:

```bash
python deploy_vibecode.py
```

`deploy_vibecode.py` uses Deploy API (default: `https://vibecode.bitrix24.tech/v1/infra/deploy`) and sends config with healthcheck path `/health` and model `bitrix/bitrixgpt-5.5` by default. You can override endpoint via `VIBECODE_DEPLOY_API_URL`.


## Notes

- Do not commit real API keys to the repository.
- `/health` can be used for deployment checks.
- You can override model with `VIBECODE_MODEL` (default: `bitrix/bitrixgpt-5.5`).
