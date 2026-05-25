import streamlit as st

st.set_page_config(
    page_title="A/B Test Toolkit",
    page_icon="📊",
)

navigation = st.navigation(
    [
        st.Page(
            "pages/0_Home.py",
            title="Home",
            icon="🏠",
            url_path="",
            default=True,
        ),
        st.Page(
            "pages/1_Калькулятор_размера_выборки.py",
            title="Калькулятор размера выборки",
            icon="📊",
            url_path="sample-size",
        ),
        st.Page(
            "pages/2_Калькулятор_MDE.py",
            title="Калькулятор MDE",
            icon="📏",
            url_path="mde",
        ),
        st.Page(
            "pages/5_Проверка_SRM.py",
            title="SRM",
            icon="⚖️",
            url_path="srm",
        ),
        st.Page(
            "pages/3_Статкритерий_для_конверсии.py",
            title="Статкритерий",
            icon="🧪",
            url_path="stat-test",
        ),
        st.Page(
            "pages/6_Размер_выборки_A_B_C_Bonferroni.py",
            title="Bonferroni",
            icon="📊",
            url_path="bonferroni",
        ),
        st.Page(
            "pages/4_Статкритерий_ARPU.py",
            title="Статкритерий ARPU",
            icon="💰",
            url_path="stat-test-arpu",
        ),
    ]
)

navigation.run()
