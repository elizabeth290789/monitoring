import math
import statistics
import streamlit as st

st.title("SRM проверка")

obs_a = st.number_input("Факт A", min_value=0, value=5000)
obs_b = st.number_input("Факт B", min_value=0, value=5000)
exp_a = st.number_input("Ожидаемая доля A", min_value=0.01, max_value=0.99, value=0.5)

if st.button("Проверить SRM"):
    n = obs_a + obs_b
    e_a = n * exp_a
    e_b = n * (1 - exp_a)
    chi2 = (obs_a - e_a) ** 2 / e_a + (obs_b - e_b) ** 2 / e_b
    pval = 2 * (1 - statistics.NormalDist().cdf(math.sqrt(chi2)))
    st.metric("Chi-square", f"{chi2:.4f}")
    st.metric("p-value", f"{pval:.6f}")
