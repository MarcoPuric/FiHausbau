import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

st.set_page_config(page_title="Hausbau Investment Cockpit", layout="wide")
st.title("🏡 Hausbau-Investment Cockpit")

# === GLOBAL: Sparziel-Daten vorbereiten ===
zielkapital = 100000
jahre = 4
raten = [1000, 1200, 2000, 2000]  # Jahr 1–4
rendite_slider = st.slider("Erwartete Jahresrendite (%)", 0.0, 10.0, 6.0) / 100

kapital = []
gesamt = 0
for jahr in range(jahre):
    monatsrate = raten[jahr]
    for monat in range(12):
        gesamt *= (1 + rendite_slider / 12)
        gesamt += monatsrate
        kapital.append(gesamt)

endkapital = round(kapital[-1], 2)
fortschritt = min(endkapital / zielkapital * 100, 100)
monatlicher_zuwachs = kapital[-1] - kapital[-13] if len(kapital) > 13 else 0

# === DASHBOARD METRICS ===
st.markdown("### Überblick")
col1, col2, col3 = st.columns(3)
col1.metric("Zielkapital", "100.000 €")
col2.metric("Sparstand (prognostisch)", f"{endkapital:,.2f} €")
col3.metric("Zuwachs (letzte 12 Monate)", f"{monatlicher_zuwachs:,.2f} €")

st.markdown("---")

# === TABS: Portfolio vs Sparziel ===
tab1, tab2 = st.tabs(["📊 Portfolio-Analyse", "💰 Sparziel & Förderung"])

# === TAB 1: PORTFOLIO ===
with tab1:
    st.header("ETF & Aktien-Analyse")

    assets = {
        "MSCI World ETF (URTH)": "URTH",
        "Nasdaq 100 ETF (QQQ)": "QQQ",
        "FTSE High Dividend ETF (VYMI)": "VYMI",
        "Realty Income REIT (O)": "O",
        "Euro Gov Bond Short (IBGL)": "IBGL"
    }

    choices = st.multiselect("Wähle deine Assets:", list(assets.keys()), default=["MSCI World ETF (URTH)"])
    period = st.selectbox("Zeitraum für Kursanalyse:", ["6mo", "1y", "2y", "5y"], index=1)

    for choice in choices:
        ticker = assets[choice]
        data = yf.download(ticker, period=period)[['Close']].dropna()
        data = data.reset_index()
        data['Tage'] = range(len(data))

        # Modell & Kennzahlen
        model = LinearRegression()
        model.fit(data[['Tage']], data['Close'])
        data['Prognose'] = model.predict(data[['Tage']])
        data['SMA_30'] = data['Close'].rolling(window=30).mean()

        start_price = data['Close'].iloc[0]
        end_price = data['Close'].iloc[-1]
        years = (data['Date'].iloc[-1] - data['Date'].iloc[0]).days / 365.25
        cagr = (end_price / start_price) ** (1 / years) - 1

        info = yf.Ticker(ticker).info
        div_yield = info.get('dividendYield', None)

        # Layout in Karte
        with st.container():
            st.markdown(f"#### {choice}")
            c1, c2, c3 = st.columns(3)
            c1.metric("Letzter Kurs", f"{round(end_price, 2)} USD")
            c2.metric("CAGR", f"{round(cagr * 100, 2)} % p.a.")
            if div_yield:
                c3.metric("Dividendenrendite", f"{round(div_yield * 100, 2)} %")

            fig, ax = plt.subplots(figsize=(9, 3))
            ax.plot(data['Date'], data['Close'], label='Kurs', linewidth=2)
            ax.plot(data['Date'], data['Prognose'], '--', label='Trend')
            ax.plot(data['Date'], data['SMA_30'], label='SMA 30d', alpha=0.7)
            ax.set_xticks([])
            ax.set_yticks([])
            ax.grid(True)
            ax.legend()
            st.pyplot(fig)
            st.markdown("---")

# === TAB 2: SPARZIEL & FÖRDERUNG ===
with tab2:
    st.header("Sparziel-Prognose: 100.000 € Eigenkapital")

    k1, k2 = st.columns([4, 1])
    k1.markdown(f"**Kapital nach {jahre} Jahren:** {endkapital:,.2f} €")
    k2.progress(fortschritt / 100)

    fig2, ax2 = plt.subplots(figsize=(10, 3))
    ax2.plot(kapital, label="Kapitalverlauf", linewidth=2)
    ax2.axhline(zielkapital, color="gray", linestyle="--", label="Ziel: 100.000 €")
    ax2.set_title("")
    ax2.set_xticks([])
    ax2.set_yticks([])
    ax2.grid(True)
    ax2.legend()
    st.pyplot(fig2)

    st.markdown("### Förderungen in Bayern")
    query = "Förderprogramme Hausbau Bayern BayernLabo KfW 300 site:.de"
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    if st.button("Google-Suche: Fördermöglichkeiten anzeigen"):
        st.markdown(f"[Ergebnisse auf Google öffnen]({url})", unsafe_allow_html=True)

# === FOOTER ===
st.markdown("---")
st.caption("Diese App ist eine Demo für deinen Hausbau-Finanzplan. Kurse via Yahoo Finance.")
