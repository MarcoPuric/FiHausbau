
import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

st.set_page_config(page_title="Hausbau ETF Tracker", layout="wide")
st.title("Hausbau-Investment: ETF & Aktien-Prognosen")

assets = {
    "MSCI World ETF (URTH)": "URTH",
    "Nasdaq 100 ETF (QQQ)": "QQQ",
    "FTSE High Dividend ETF (VYMI)": "VYMI",
    "Realty Income REIT (O)": "O",
    "Euro Gov Bond Short (IBGL)": "IBGL"
}

choice = st.selectbox("Wähle ein Asset zum Analysieren:", list(assets.keys()))
ticker = assets[choice]

period = st.selectbox("Zeitraum", ["6mo", "1y", "2y", "5y"], index=1)
data = yf.download(ticker, period=period)[['Close']].dropna()

# Prognose vorbereiten
data = data.reset_index()
data['Tage'] = range(len(data))
X = data[['Tage']]
y = data['Close']
model = LinearRegression()
model.fit(X, y)
data['Prognose'] = model.predict(X)

# Plot anzeigen
st.subheader(f"{choice} Kursentwicklung & Prognose")
fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(data['Date'], data['Close'], label='Kurs', linewidth=2)
ax.plot(data['Date'], data['Prognose'], label='Trend-Prognose', linestyle='--')
ax.set_xlabel("Datum")
ax.set_ylabel("Kurs in USD")
ax.set_title(f"{choice} Kurs & Trend")
ax.legend()
ax.grid(True)
st.pyplot(fig)

# Aktueller Stand
st.markdown(f"**Letzter Kurs:** {round(data['Close'].iloc[-1], 2)} USD")
prognose = round(data['Prognose'].iloc[-1], 2)
st.markdown(f"**Modellprognose (Trend-Ende):** {prognose} USD")

st.markdown("---")
st.caption("Diese App ist eine Demo für deinen Hausbau-Finanzplan. Kurse via Yahoo Finance.")
