# 🖥️ Macro Terminal — Day 08 · 30 Days of AI Finance

A Bloomberg-lite personal macro terminal for Indian and global markets. Real-time data, zero API keys needed.

![Macro Terminal](https://img.shields.io/badge/Day-08%2F30-c9a96e?style=flat-square) ![Python](https://img.shields.io/badge/Python-Streamlit-blue?style=flat-square) ![Data](https://img.shields.io/badge/Data-Free%20APIs-green?style=flat-square)

## What it shows

| Section | Data |
|---|---|
| 🇮🇳 India Markets | Nifty 50, Sensex, Bank Nifty, IT, Midcap, India VIX |
| 💱 Forex & Commodities | USD/INR, EUR/USD, DXY, Gold, Crude WTI, Silver |
| 🌍 Global | S&P 500, Nasdaq, CBOE VIX, US yields |
| 📊 Charts | Candlestick + volume for Nifty, USD/INR, Gold, Crude |
| ⚡ Signals | Auto-generated macro signals from live data |
| 📈 Yield Curve | US yield curve with inversion alert |
| 🏦 FII/DII | Live foreign/domestic institutional flows from NSE |
| 📂 Sectors | All 8 Nifty sector indices live |

## Data sources
- **Yahoo Finance** via `yfinance` — all price data (free, no key)
- **NSE India** via `nselib` — FII/DII flows (free, no key)
- No API keys required

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Cloud

1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo → select `app.py`
4. Deploy — live in 2 minutes

## Part of 30 Days of AI Finance

Building one AI × Finance tool every day for 30 days.

→ [Full challenge repo](https://github.com/Preethams321/30-days-ai-finance)

---

*Data refreshes every 5 minutes. Not investment advice.*
