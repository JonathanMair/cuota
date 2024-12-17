import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from typing import Tuple, Dict

from cuota.data_classes.spanish_tax_rules import SpanishAutonomoModel, SpanishRegimenGeneralModel
from cuota.data_classes.foreign_tax_rules import UkEmployeeTaxModel, UkSelfEmployedTaxModel


years = [2022, 2021, 2022, 2023]

# @st.cache_data
def get_cached_data():
    aut_by_year = {year: SpanishAutonomoModel(year) for year in years}
    gen_by_year = {year: SpanishRegimenGeneralModel(year) for year in years}
    uk_employee = UkSelfEmployedTaxModel()
    uk_self_empl = UkSelfEmployedTaxModel()
    return aut_by_year, gen_by_year, uk_employee, uk_self_empl


aut_by_year, gen_by_year, uk_employee, uk_self_empl = get_cached_data()

st.title("Tax App")

plt.figure(figsize=(25, 25))
for year in years:



def plot_chart():
    metric = st.session_state.metric
    cols = [col for col in df.columns if metric in col]
    for col in cols:
        plt.plot(df.index, df[col], label=col[0])

    plt.legend(reverse=True)
    plt.grid(True)
    st.pyplot(plt)

