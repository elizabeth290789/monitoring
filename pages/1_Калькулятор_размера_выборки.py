import math
import statistics
import streamlit as st


def norm_ppf(p: float) -> float:
    return statistics.NormalDist().inv_cdf(p)


st.title("Калькулятор размера выборки")
baseline = st.number_input("Базовая конверсия", min_value=0.0001, max_value=0.9999, value=0.1)
uplift = st.number_input("Ожидаемый uplift", min_value=0.0001, max_value=5.0, value=0.1)
alpha = st.number_input("alpha", min_value=0.0001, max_value=0.2, value=0.05)
power = st.number_input("power", min_value=0.5, max_value=0.999, value=0.8)

if st.button("Рассчитать"):
    p1 = baseline
    p2 = baseline * (1 + uplift)
    z_alpha = norm_ppf(1 - alpha / 2)
    z_beta = norm_ppf(power)
    p_bar = (p1 + p2) / 2
    num = (z_alpha * math.sqrt(2 * p_bar * (1 - p_bar)) + z_beta * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2
    n = num / (p2 - p1) ** 2
    st.metric("Требуемый размер на группу", f"{math.ceil(n):,}".replace(",", " "))
