import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from typing import Tuple, Dict

from cuota.logic.calculations import Calculator

# @st.cache_data
def get_cached_data() -> Tuple[pd.DataFrame, Dict]:
    calculator = Calculator()
    metrics = calculator.metrics
    return calculator.data, metrics

df, metrics = get_cached_data()

st.title("Tax App")
st.subheader("Autónomo Net Income, Allowance = 5500€")
# a = ("Social Security", metrics["NET_THIS"])
# b = ("Income Tax", metrics["NET_THIS"])
#
plt.figure(figsize=(25, 25))
# plt.stackplot(
#     df.index,df[b], df[a], df.index,
#     labels=["Net of Income Tax (Take-Home Pay)", "Net of Social Security", "Gross"]
# )
# plt.plot(df.index, df.index)
#
# # plt.title('Net Income After Application of Tax Rules')
# plt.xlabel('Gross Income')
# # plt.ylabel('Net Income')



def plot_chart():
    metric = st.session_state.metric
    print(metric)
    cols = [col for col in df.columns if metric in col]
    for col in cols:
        plt.plot(df.index, df[col], label=col[0])

    plt.legend(reverse=True)
    plt.grid(True)
    st.pyplot(plt)


st.selectbox(label="Metric", options=metrics.values(), index=0, key="metric", on_change=plot_chart)

st.write(df.head(-20))