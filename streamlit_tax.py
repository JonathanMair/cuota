import streamlit as st
import matplotlib.pyplot as plt


from cuota.logic.calculations import Calculator

calculator = Calculator()
metrics = calculator.metrics
df = calculator.data

st.title("Tax App")
st.subheader("Autónomo Net Income, Allowance = 5500€")
a = ("Social Security", metrics["PAYABLE"])
b = ("Income Tax", metrics["PAYABLE"])

plt.figure(figsize=(15, 15))
plt.stackplot(df.index, df[a], df[b], labels=["Social Security", "Income Tax"])
plt.plot(df.index, df.index)

# plt.title('Net Income After Application of Tax Rules')
plt.xlabel('Gross Income')
# plt.ylabel('Net Income')
plt.legend()
plt.grid(True)

st.pyplot(plt)
