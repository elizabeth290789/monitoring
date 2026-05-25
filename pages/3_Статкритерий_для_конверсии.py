import math
import statistics
import streamlit as st

st.title("Статкритерий для конверсии")

n1 = st.number_input("n_control", min_value=1, value=1000)
c1 = st.number_input("conv_control", min_value=0, max_value=n1, value=100)
n2 = st.number_input("n_test", min_value=1, value=1000)
c2 = st.number_input("conv_test", min_value=0, max_value=n2, value=115)

if st.button("Проверить"):
    p1 = c1 / n1
    p2 = c2 / n2
    p = (c1 + c2) / (n1 + n2)
    se = math.sqrt(p * (1 - p) * (1 / n1 + 1 / n2))
    z = (p2 - p1) / se if se else 0
    pval = 2 * (1 - statistics.NormalDist().cdf(abs(z)))
    st.metric("p-value", f"{pval:.6f}")
