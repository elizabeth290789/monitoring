import json
import os
import sys
import urllib.error
import urllib.request

DEFAULT_DEPLOY_URL = "https://vibecode.bitrix24.tech/v1/infra/deploy"


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"{name} is not set")
    return value


def build_payload() -> dict:
    return {
        "name": os.getenv("VIBECODE_APP_NAME", "abcalc-vibecode"),
        "runtime": "docker",
        "dockerfilePath": os.getenv("VIBECODE_DOCKERFILE_PATH", "Dockerfile"),
        "env": {
            "VIBECODE_MODEL": os.getenv("VIBECODE_MODEL", "bitrix/bitrixgpt-5.5"),
            "VIBECODE_ROUTER_URL": os.getenv(
                "VIBECODE_ROUTER_URL", "https://vibecode.bitrix24.tech/v1/chat/completions"
            ),
        },
        "healthcheckPath": "/health",
    }


def post_json(url: str, token: str, payload: dict) -> str:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as response:
        return response.read().decode("utf-8")


def main() -> int:
    api_key = require_env("VIBECODE_API_KEY")
    deploy_url = os.getenv("VIBECODE_DEPLOY_API_URL", DEFAULT_DEPLOY_URL)
    payload = build_payload()

    try:
        response_body = post_json(deploy_url, api_key, payload)
    except urllib.error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Deploy API HTTP {exc.code}: {details}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Network error while reaching Deploy API: {exc}") from exc

    print(response_body)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Deploy failed: {exc}", file=sys.stderr)
        raise
