# A/B Test Calculator for VibeCode

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export VIBECODE_API_KEY="<your_key>"
uvicorn main:app --host 0.0.0.0 --port 8000
```

Open: `http://localhost:8000/docs`

## VibeCode AI Router

The endpoint `/ai/suggest` uses model `bitrix/bitrixgpt-5.5` via AI Router (`https://vibecode.bitrix24.tech/v1/chat/completions`).

## Deploy to server (Docker)

```bash
docker build -t abcalc-vibecode .
docker run -d --name abcalc -p 8000:8000 -e VIBECODE_API_KEY="<your_key>" abcalc-vibecode
```
