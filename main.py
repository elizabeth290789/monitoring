import math
import os
from typing import Literal

import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from scipy import stats
from scipy.stats import norm
import requests

app = FastAPI(title="A/B Test Calculator")

MDE_RANGE_PP = [0.1, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0]

Hypothesis = Literal["two-sided", "one-sided"]


def calculate_sample_size_per_group(p1: float, mde_pp: float, alpha: float = 0.05, power: float = 0.8, hypothesis_type: Hypothesis = "two-sided") -> tuple[int, float]:
    p2 = p1 + mde_pp / 100
    p_bar = (p1 + p2) / 2
    z_alpha = norm.ppf(1 - alpha / 2) if hypothesis_type == "two-sided" else norm.ppf(1 - alpha)
    z_power = norm.ppf(power)
    numerator = (z_alpha * np.sqrt(2 * p_bar * (1 - p_bar)) + z_power * np.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2
    denominator = (p2 - p1) ** 2
    n = numerator / denominator
    return math.ceil(n), p2


def calculate_mde_for_proportion(baseline_rate: float, n_per_group: float, alpha: float = 0.05, power: float = 0.8, hypothesis_type: Hypothesis = "two-sided") -> tuple[float, float, float]:
    z_alpha = norm.ppf(1 - alpha / 2) if hypothesis_type == "two-sided" else norm.ppf(1 - alpha)
    z_power = norm.ppf(power)
    mde = (z_alpha + z_power) * math.sqrt(2 * baseline_rate * (1 - baseline_rate) / n_per_group)
    detectable_rate = baseline_rate + mde
    uplift_pct = (mde / baseline_rate) * 100
    return mde, detectable_rate, uplift_pct


def calculate_two_proportion_z_test(n_a: int, success_a: int, n_b: int, success_b: int, alpha: float, hypothesis_type: Hypothesis = "two-sided") -> dict[str, float]:
    p_a = success_a / n_a
    p_b = success_b / n_b
    diff = p_b - p_a
    p_pool = (success_a + success_b) / (n_a + n_b)
    se_pool = math.sqrt(p_pool * (1 - p_pool) * (1 / n_a + 1 / n_b))
    if se_pool == 0:
        raise ValueError("Стандартная ошибка по pooled-оценке равна 0.")
    z_stat = diff / se_pool
    p_value = 2 * (1 - norm.cdf(abs(z_stat))) if hypothesis_type == "two-sided" else 1 - norm.cdf(z_stat)
    z_crit = norm.ppf(1 - alpha / 2)
    se_unpooled = math.sqrt(p_a * (1 - p_a) / n_a + p_b * (1 - p_b) / n_b)
    ci_low = diff - z_crit * se_unpooled
    ci_high = diff + z_crit * se_unpooled
    return {"p_a": p_a, "p_b": p_b, "diff": diff, "z_stat": z_stat, "p_value": p_value, "ci_low": ci_low, "ci_high": ci_high}


def welch_ttest_from_stats(mean_a: float, std_a: float, n_a: int, mean_b: float, std_b: float, n_b: int, alpha: float = 0.05, hypothesis_type: Hypothesis = "two-sided") -> dict[str, float]:
    if n_a <= 1 or n_b <= 1:
        raise ValueError("Размер групп должен быть больше 1.")
    t_stat, _ = stats.ttest_ind_from_stats(mean1=mean_b, std1=std_b, nobs1=n_b, mean2=mean_a, std2=std_a, nobs2=n_a, equal_var=False)
    se = np.sqrt((std_a**2 / n_a) + (std_b**2 / n_b))
    df_num = (std_a**2 / n_a + std_b**2 / n_b) ** 2
    df_den = ((std_a**2 / n_a) ** 2) / (n_a - 1) + ((std_b**2 / n_b) ** 2) / (n_b - 1)
    if df_den == 0:
        raise ValueError("Не удалось вычислить степени свободы.")
    df = df_num / df_den
    t_crit = stats.t.ppf(1 - alpha / 2, df)
    p_value = 2 * (1 - stats.t.cdf(abs(t_stat), df)) if hypothesis_type == "two-sided" else 1 - stats.t.cdf(t_stat, df)
    diff = mean_b - mean_a
    ci_low = diff - t_crit * se
    ci_high = diff + t_crit * se
    uplift_pct = np.nan if mean_a == 0 else diff / mean_a * 100
    return {"mean_a": mean_a, "mean_b": mean_b, "diff": diff, "uplift_pct": uplift_pct, "t_stat": t_stat, "p_value": p_value, "ci_low": ci_low, "ci_high": ci_high}


def calculate_srm_chi_square(observed: list[int], expected_shares: list[float]) -> dict[str, float | list[float]]:
    if len(observed) != len(expected_shares):
        raise ValueError("Количество наблюдаемых значений и ожидаемых долей должно совпадать.")
    total_share = sum(expected_shares)
    if not math.isclose(total_share, 1.0, rel_tol=0.0, abs_tol=1e-6):
        raise ValueError("Сумма ожидаемых долей должна быть равна 1.")
    sample_size = sum(observed)
    expected_sizes = [sample_size * share for share in expected_shares]
    chi2_stat = sum((obs - exp) ** 2 / exp for obs, exp in zip(observed, expected_sizes, strict=True))
    dof = len(observed) - 1
    p_value = 1 - stats.chi2.cdf(chi2_stat, dof)
    diffs = [obs - exp for obs, exp in zip(observed, expected_sizes, strict=True)]
    return {"sample_size": sample_size, "expected_sizes": expected_sizes, "diffs": diffs, "chi2_stat": chi2_stat, "degrees_of_freedom": dof, "p_value": p_value}


class VibePrompt(BaseModel):
    prompt: str = Field(min_length=1)


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return """
    <h1>A/B Test Calculator API</h1>
    <p>Endpoints: /docs, /sample-size, /mde, /z-test, /welch, /srm, /ai/suggest, /health</p>
    """




@app.get('/health')
def health() -> dict[str, str]:
    return {"status": "ok"}
@app.post('/ai/suggest')
def ai_suggest(payload: VibePrompt) -> dict:
    api_key = os.getenv("VIBECODE_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="VIBECODE_API_KEY is not set")

    url = os.getenv("VIBECODE_ROUTER_URL", "https://vibecode.bitrix24.tech/v1/chat/completions")
    model = os.getenv("VIBECODE_MODEL", "bitrix/bitrixgpt-5.5")
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": "Ты ассистент по A/B тестам."},
            {"role": "user", "content": payload.prompt},
        ],
        "temperature": 0.2,
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    r = requests.post(url, headers=headers, json=body, timeout=30)
    if r.status_code >= 400:
        raise HTTPException(status_code=r.status_code, detail=r.text)
    return r.json()

app.post('/sample-size')(calculate_sample_size_per_group)
app.post('/mde')(calculate_mde_for_proportion)
app.post('/z-test')(calculate_two_proportion_z_test)
app.post('/welch')(welch_ttest_from_stats)
app.post('/srm')(calculate_srm_chi_square)
