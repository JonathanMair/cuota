import streamlit as st
import matplotlib.pyplot as plt


from cuota.logic.calculations import Calculator

calculator = Calculator()

df = calculator.data

st.title("Tax App")
st.subheader("Autónomo Net Income, Allowance = 5500€")

plt.figure(figsize=(15, 15))
plt.plot(df["gross income"], df["Payable (1 Social Security)"])
# plt.plot(df["gross income"], df["Net (1 Social Security)"], color='blue', label='After Social Security')
plt.plot(df["gross income"], df["gross income"], color='blue', label='Before Deductions')
plt.plot(df["gross income"], df["Payable (2 Income Tax)"], color='red', label='After Tax')
# plt.plot(df["gross income"], df["Net (2 Income Tax)"], color='red', label='After Tax')
# plt.title('Net Income After Application of Tax Rules')
# plt.xlabel('Gross Income')
# plt.ylabel('Net Income')
plt.legend()
plt.grid(True)

st.pyplot(plt)
