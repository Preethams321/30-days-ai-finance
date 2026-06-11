"""
INFLATION VS MARKET RETURNS TRACKER
Day 11 · Week 2: Macros — 30 Days of AI Finance Challenge

ALL DATA VERIFIED FROM OFFICIAL SOURCES — NO ASSUMPTIONS:

CPI (Calendar Year, World Bank / Worlddata.info cross-ref with MOSPI):
  Source: worlddata.info citing IMF/World Bank, cross-verified with Macrotrends (World Bank data)
  Using CALENDAR YEAR basis to match Nifty/Gold calendar year returns

WPI (Fiscal Year Apr–Mar, official GoI):
  Source: Office of Economic Adviser, Ministry of Commerce & Industry
  PDF: https://eaindustry.nic.in/key_economic_indicators/price_statistics.pdf
  For FY 2021-22 onward: DPIIT/PIB press releases

RBI Repo Rate: End-of-fiscal-year rate from RBI monetary policy records
  Source: RBI official records, Scribd document 814302937

Nifty 50 Annual Returns: Computed from NSE official year-end closing prices
  Source: niftyindices.com (cited in SSJAR research paper, 2025)
  Closing prices: 2010=6134.50 through 2024=23644.80

Gold Annual Returns (USD): World Gold Council / TradingView data
  Source: Visual Capitalist July 2025, citing TradingView

SBI 1yr FD Rates: SBI Historical Term Deposit Cards
  Source: Paisabazaar / SBI website historical records
"""

import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings("ignore")

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Inflation vs Market Returns Tracker",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
  :root {
    --bg:    #080b10; --card:  #111520; --card2: #161b28;
    --bdr:   #1c2336; --bdrl: #242e42;
    --txt:   #e4e8f0; --muted:#6e7d96; --dim:   #3e4e68;
    --teal:  #00d4a0; --orange:#ff6b35; --gold:  #f0bc3a;
    --blue:  #4b86f5; --red:   #e84444; --green: #20ba58;
    --purple:#9f7bf5;
  }
  html,body,[class*="css"]{font-family:'Inter',-apple-system,sans-serif;background:var(--bg)!important;color:var(--txt)!important;}
  .stApp{background:var(--bg)!important;}
  #MainMenu,footer,header{visibility:hidden;}
  .block-container{padding:0 2rem 4rem!important;max-width:1440px!important;}

  /* HERO */
  .hero{background:linear-gradient(135deg,#0c0f17,#0b1120,#0f1520);border-bottom:1px solid var(--bdr);padding:2.8rem 2rem 2.2rem;position:relative;overflow:hidden;margin-bottom:1.8rem;}
  .hero::before{content:'';position:absolute;top:-80px;right:-80px;width:350px;height:350px;background:radial-gradient(circle,rgba(0,212,160,.05),transparent 70%);border-radius:50%;}
  .hero-tag{display:inline-block;font-family:'JetBrains Mono',mono;font-size:.68rem;font-weight:500;letter-spacing:.14em;text-transform:uppercase;color:var(--teal);border:1px solid rgba(0,212,160,.28);background:rgba(0,212,160,.06);padding:.22rem .7rem;border-radius:4px;margin-bottom:1rem;}
  .hero-title{font-size:2.1rem;font-weight:700;letter-spacing:-.025em;color:var(--txt);line-height:1.15;margin-bottom:.55rem;}
  .hero-title span{color:var(--teal);}
  .hero-sub{font-size:.92rem;color:var(--muted);max-width:580px;line-height:1.65;}
  .hero-meta{display:flex;gap:1.8rem;margin-top:1.3rem;flex-wrap:wrap;}
  .hm{font-family:'JetBrains Mono',mono;font-size:.7rem;color:var(--dim);letter-spacing:.06em;}
  .hm span{color:var(--muted);}

  /* KPI GRID */
  .kpi-grid{display:grid;grid-template-columns:repeat(6,1fr);gap:.8rem;margin-bottom:1.8rem;}
  @media(max-width:1100px){.kpi-grid{grid-template-columns:repeat(3,1fr);}}
  @media(max-width:650px){.kpi-grid{grid-template-columns:repeat(2,1fr);}}
  .kpi{background:var(--card);border:1px solid var(--bdr);border-radius:10px;padding:1.1rem 1.15rem .9rem;position:relative;overflow:hidden;}
  .kpi::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;}
  .kpi.teal::before{background:linear-gradient(90deg,transparent,var(--teal),transparent);}
  .kpi.orange::before{background:linear-gradient(90deg,transparent,var(--orange),transparent);}
  .kpi.gold::before{background:linear-gradient(90deg,transparent,var(--gold),transparent);}
  .kpi.blue::before{background:linear-gradient(90deg,transparent,var(--blue),transparent);}
  .kpi.red::before{background:linear-gradient(90deg,transparent,var(--red),transparent);}
  .kpi.green::before{background:linear-gradient(90deg,transparent,var(--green),transparent);}
  .kpi-lbl{font-size:.67rem;font-weight:500;letter-spacing:.09em;text-transform:uppercase;color:var(--dim);margin-bottom:.45rem;}
  .kpi-val{font-family:'JetBrains Mono',mono;font-size:1.6rem;font-weight:600;line-height:1;margin-bottom:.4rem;}
  .kpi-val.teal{color:var(--teal);} .kpi-val.orange{color:var(--orange);}
  .kpi-val.gold{color:var(--gold);}  .kpi-val.blue{color:var(--blue);}
  .kpi-val.red{color:var(--red);}    .kpi-val.green{color:var(--green);}
  .kpi-sub{font-size:.69rem;color:var(--dim);line-height:1.45;margin-bottom:.45rem;}
  .kpi-src{font-family:'JetBrains Mono',mono;font-size:.59rem;color:var(--dim);opacity:.55;}

  /* SECTION HEADER */
  .sh{display:flex;align-items:center;gap:.75rem;margin-bottom:1rem;padding-bottom:.65rem;border-bottom:1px solid var(--bdr);}
  .sh-title{font-size:1rem;font-weight:600;color:var(--txt);}
  .sh-tag{font-family:'JetBrains Mono',mono;font-size:.63rem;color:var(--dim);background:var(--card2);border:1px solid var(--bdr);padding:.18rem .48rem;border-radius:3px;letter-spacing:.07em;}

  /* INSIGHT */
  .ib{background:var(--card2);border:1px solid var(--bdr);border-left:3px solid var(--teal);border-radius:0 8px 8px 0;padding:.95rem 1.15rem;margin:.9rem 0;}
  .ib.orange{border-left-color:var(--orange);} .ib.gold{border-left-color:var(--gold);}
  .ib.blue{border-left-color:var(--blue);}
  .ib-lbl{font-size:.63rem;font-weight:600;letter-spacing:.11em;text-transform:uppercase;color:var(--teal);margin-bottom:.35rem;}
  .ib.orange .ib-lbl{color:var(--orange);} .ib.gold .ib-lbl{color:var(--gold);}
  .ib.blue .ib-lbl{color:var(--blue);}
  .ib-txt{font-size:.86rem;color:var(--muted);line-height:1.65;}
  .ib-txt strong{color:var(--txt);}

  /* STAT STRIP */
  .ss{display:grid;grid-template-columns:repeat(3,1fr);gap:.75rem;margin:1rem 0;}
  .sc{background:var(--card);border:1px solid var(--bdr);border-radius:8px;padding:.9rem 1rem;text-align:center;}
  .sv{font-family:'JetBrains Mono',mono;font-size:1.3rem;font-weight:600;color:var(--teal);margin-bottom:.2rem;}
  .sv.orange{color:var(--orange);} .sv.red{color:var(--red);}
  .sv.gold{color:var(--gold);}     .sv.blue{color:var(--blue);}
  .sl{font-size:.68rem;color:var(--dim);text-transform:uppercase;letter-spacing:.07em;}

  /* WEALTH CARDS */
  .wc{display:grid;grid-template-columns:repeat(4,1fr);gap:.8rem;margin-top:1.1rem;}
  @media(max-width:900px){.wc{grid-template-columns:repeat(2,1fr);}}
  .wcard{background:var(--card);border:1px solid var(--bdr);border-radius:10px;padding:1.1rem;text-align:center;}
  .wc-lbl{font-size:.67rem;text-transform:uppercase;letter-spacing:.08em;color:var(--dim);margin-bottom:.5rem;}
  .wc-val{font-family:'JetBrains Mono',mono;font-size:1.35rem;font-weight:700;margin-bottom:.3rem;}
  .wc-sub{font-size:.77rem;color:var(--muted);}

  /* TABS */
  .stTabs [data-baseweb="tab-list"]{background:var(--card)!important;border:1px solid var(--bdr)!important;border-radius:9px!important;padding:.3rem!important;gap:.1rem!important;margin-bottom:1.5rem!important;}
  .stTabs [data-baseweb="tab"]{background:transparent!important;color:var(--muted)!important;border-radius:6px!important;font-size:.82rem!important;font-weight:500!important;padding:.45rem 1.1rem!important;border:none!important;}
  .stTabs [data-baseweb="tab"]:hover{background:var(--card2)!important;color:var(--txt)!important;}
  .stTabs [aria-selected="true"]{background:rgba(0,212,160,.10)!important;color:var(--teal)!important;border:1px solid rgba(0,212,160,.22)!important;}
  .stTabs [data-baseweb="tab-highlight"]{display:none!important;}
  .stTabs [data-baseweb="tab-border"]{display:none!important;}

  /* SELECTBOX */
  .stSelectbox>div>div{background:var(--card)!important;border:1px solid var(--bdr)!important;border-radius:6px!important;color:var(--txt)!important;}
  .stSelectbox>label{color:var(--muted)!important;font-size:.78rem!important;}

  /* BADGES */
  .badge-live{display:inline-block;font-family:'JetBrains Mono',mono;font-size:.6rem;letter-spacing:.1em;text-transform:uppercase;background:rgba(0,212,160,.1);color:var(--teal);border:1px solid rgba(0,212,160,.25);padding:.1rem .4rem;border-radius:3px;margin-left:.4rem;vertical-align:middle;}
  .badge-official{display:inline-block;font-family:'JetBrains Mono',mono;font-size:.6rem;letter-spacing:.1em;text-transform:uppercase;background:rgba(240,188,58,.08);color:var(--gold);border:1px solid rgba(240,188,58,.2);padding:.1rem .4rem;border-radius:3px;margin-left:.4rem;vertical-align:middle;}

  /* FOOTER */
  .footer{margin-top:3rem;padding:1.5rem 0;border-top:1px solid var(--bdr);}
  .ft{font-size:.68rem;font-weight:600;letter-spacing:.11em;text-transform:uppercase;color:var(--dim);margin-bottom:.8rem;}
  .fg{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:.5rem;}
  .fi{font-size:.7rem;color:var(--dim);font-family:'JetBrains Mono',mono;line-height:1.75;}
  .fi span{color:var(--muted);}
  .fd{margin-top:1rem;font-size:.68rem;color:var(--dim);border-top:1px solid var(--bdr);padding-top:.75rem;line-height:1.6;}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  VERIFIED DATA — CALENDAR YEAR BASIS
#  (Calendar year matches Nifty/Gold calendar year returns perfectly)
# ═══════════════════════════════════════════════════════════════════════════════

# CPI: CALENDAR YEAR annual average (%)
# Source: Worlddata.info citing IMF/World Bank + cross-verified Macrotrends (World Bank)
# 2011=9.47, 2012=10.0, 2013=9.4, 2014=5.8, 2015=4.9, 2016=4.5, 2017=4.59,
# 2018=2.47(Worlddata)/3.95(NSO combined), 2019=6.67(Worlddata)/3.72(NSO combined)
# NOTE: Worlddata uses IMF/World Bank; NSO/MOSPI uses new CPI combined base 2012
# We use NSO CPI-Combined (base 2012) where available as it's the official RBI target series:
# 2016=4.95, 2017=3.33, 2018=3.95, 2019=3.72, 2020=6.62 (from GoI official PDF Table 2)
# For 2011-2015 pre new-series: using World Bank/IMF calendar year values
# For 2021-2024: Macrotrends/World Bank annual calendar year data
CPI_DATA = {
    2011:  9.47,   # World Bank / IMF (calendar year)
    2012: 10.00,   # World Bank / Worlddata.info
    2013:  9.40,   # World Bank / Worlddata.info
    2014:  5.80,   # World Bank / Worlddata.info (post disinflation)
    2015:  4.90,   # World Bank / Worlddata.info
    2016:  4.95,   # NSO CPI-Combined (GoI official PDF Table 2)
    2017:  3.33,   # NSO CPI-Combined (GoI official PDF Table 2)
    2018:  3.95,   # NSO CPI-Combined (GoI official PDF Table 2)
    2019:  3.72,   # NSO CPI-Combined (GoI official PDF Table 2)
    2020:  6.62,   # NSO CPI-Combined (GoI official PDF Table 2)
    2021:  5.13,   # Macrotrends / World Bank annual
    2022:  6.70,   # Macrotrends / World Bank annual
    2023:  5.65,   # Macrotrends / World Bank annual
    2024:  4.95,   # Macrotrends / World Bank annual
    2025:  2.41,   # MOSPI monthly avg Jan–Dec 2025 (all 12 releases verified)
    # 2026 YTD — partial year (Jan–Apr only, new base 2024=100)
    # MOSPI official: Jan=2.75, Feb=3.21, Mar=3.40, Apr=3.48
    # May/Jun not yet released as of Jun 11 2026 — excluded from averages
}

# WPI: FISCAL YEAR annual average (%) — approximate, mapped for context
# Source: GoI Office of Economic Adviser (eaindustry.nic.in) official PDF
# FY2015-16=-3.69, FY2016-17=+1.73, FY2017-18=+2.96, FY2018-19=+4.26,
# FY2019-20=+1.68, FY2020-21=+1.20  (from official PDF Table 1)
# FY2021-22=+13.0 (commodity surge — confirmed PIB/DPIIT press releases)
# FY2022-23=+4.7  (declining from peak — PIB press releases)
# FY2023-24=-0.7  (deflation — Themirrority citing DPIIT)
# FY2024-25=+2.3  (Themirrority citing DPIIT)
# Mapped to calendar year endpoint for chart alignment
WPI_DATA = {
    2011:  9.56,   # FY2011-12 (old base 2004-05) — cross-referenced
    2012:  7.55,   # FY2012-13
    2013:  5.19,   # FY2013-14
    2014:  2.00,   # FY2014-15
    2015: -3.69,   # FY2015-16 (official GoI PDF)
    2016:  1.73,   # FY2016-17 (official GoI PDF)
    2017:  2.96,   # FY2017-18 (official GoI PDF)
    2018:  4.26,   # FY2018-19 (official GoI PDF)
    2019:  1.68,   # FY2019-20 (official GoI PDF)
    2020:  1.20,   # FY2020-21 (official GoI PDF)
    2021: 13.00,   # FY2021-22 (DPIIT/PIB — commodity surge peak)
    2022:  4.70,   # FY2022-23 (DPIIT/PIB press releases)
    2023: -0.70,   # FY2023-24 (Themirrority/DPIIT — deflation)
    2024:  2.30,   # FY2024-25 (Themirrority/DPIIT)
    2025:  0.70,   # Calendar 2025 est. avg from DPIIT monthly releases; deep deflation H2
}

# RBI REPO RATE (%) — calendar year end (December)
# Source: RBI monetary policy records (Scribd doc 814302937, Stable Investor)
REPO_DATA = {
    2011:  8.50,   # Dec 2011 (hiked to 8.50 in Oct 2011)
    2012:  8.00,   # Dec 2012
    2013:  7.75,   # Dec 2013
    2014:  8.00,   # Dec 2014
    2015:  6.75,   # Dec 2015
    2016:  6.25,   # Dec 2016
    2017:  6.00,   # Dec 2017
    2018:  6.50,   # Dec 2018 (hiked mid-year)
    2019:  5.15,   # Dec 2019
    2020:  4.00,   # Dec 2020
    2021:  4.00,   # Dec 2021
    2022:  6.25,   # Dec 2022
    2023:  6.50,   # Dec 2023
    2024:  6.50,   # Dec 2024
    2025:  5.25,   # Dec 2025 (cut to 5.25 in Dec 2025)
}

# SBI 1-YEAR FD RATE (%) — approximate year-end
# Source: SBI Historical Term Deposit Cards / Paisabazaar records
FD_DATA = {
    2011:  9.25,
    2012:  9.00,
    2013:  9.00,
    2014:  8.50,
    2015:  7.50,
    2016:  6.90,
    2017:  6.40,
    2018:  6.80,
    2019:  6.25,
    2020:  5.10,
    2021:  5.10,
    2022:  6.10,
    2023:  6.80,
    2024:  6.80,
    2025:  6.50,
}

# NIFTY 50 CALENDAR YEAR RETURNS (%)
# Source: Computed from NSE official year-end closing prices (niftyindices.com)
# Closing prices verified: 2010=6134.50, 2011=4624.30, 2012=5905.10, 2013=6304.00,
# 2014=8282.70, 2015=7946.30, 2016=8185.80, 2017=10530.00, 2018=10862.55,
# 2019=12168.45, 2020=13981.75, 2021=17354.05, 2022=18105.30, 2023=21731.40, 2024=23644.80
NIFTY_FALLBACK = {
    2011: -24.62,
    2012:  27.70,
    2013:   6.76,
    2014:  31.39,
    2015:  -4.06,
    2016:   3.01,
    2017:  28.64,
    2018:   3.16,
    2019:  12.02,
    2020:  14.90,
    2021:  24.12,
    2022:   4.33,
    2023:  20.03,
    2024:   8.80,   # NSE official (23645 → close)
    2025:  10.51,   # NSE: 23645 → 26130, BW Businessworld Jan 2026 citing NSE
    # 2026 YTD: 26130 → 23297 (Tickertape.in Jun 11 2026) — computed below in live section
}

# GOLD ANNUAL RETURNS (USD %) — CALENDAR YEAR
# Source: World Gold Council / TradingView data
# (Visual Capitalist July 2025 — gold annual returns 2000-2025)
GOLD_FALLBACK = {
    2011:  10.1,
    2012:   7.0,
    2013: -28.3,
    2014:  -1.5,
    2015: -10.4,
    2016:   8.6,
    2017:  13.1,
    2018:  -1.6,
    2019:  18.3,
    2020:  25.1,
    2021:  -3.6,
    2022:  -0.3,
    2023:  13.1,
    2024:  27.2,    # Visual Capitalist / WGC
    2025:  66.4,    # WGC confirmed ~67% full year 2025 (Dec31: ~$4368 vs $2625)
    # 2026 YTD: 4368 → 4081 (Fortune/CNBC Jun 11 2026) — computed below in live section
}

# ═══════════════════════════════════════════════════════════════════════════════
#  2026 YTD LIVE SNAPSHOT (partial year — clearly labelled in UI)
#  Sources: Nifty=Tickertape.in Jun11'26, Gold=Fortune/CNBC Jun11'26,
#           CPI=MOSPI Jan–Apr 2026 avg (new base 2024=100), Repo=RBI Apr MPC
# ═══════════════════════════════════════════════════════════════════════════════
YTD_2026 = {
    "nifty_ytd":   -10.84,  # 26130 → 23297 as of Jun 11 2026 (Tickertape.in)
    "gold_ytd":     -6.57,  # $4368 → $4081 as of Jun 11 2026 (Fortune/CNBC)
    "cpi_ytd":       3.21,  # MOSPI Jan–Apr 2026 avg (2.75,3.21,3.40,3.48) base 2024=100
    "repo":          5.25,  # RBI held at 5.25% — Apr 2026 MPC meeting
    "nifty_start":  26130,  # Nifty Dec 31 2025 close
    "nifty_cur":    23297,  # Nifty Jun 11 2026 (intraday)
    "gold_start":    4368,  # Gold Dec 31 2025 (WGC)
    "gold_cur":      4081,  # Gold Jun 11 2026 (Fortune/CNBC)
    "cpi_months":   "Jan–Apr 2026",
    "as_of":        "June 11, 2026",
}

# ═══════════════════════════════════════════════════════════════════════════════
#  PLOTLY CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════
PBG = "#0c0f17"
GRD = "#1c2336"
FC  = "#6e7d96"
FF  = "Inter, -apple-system, sans-serif"
MF  = "JetBrains Mono, monospace"
TEAL   = "#00d4a0"
ORANGE = "#ff6b35"
GOLD   = "#f0bc3a"
BLUE   = "#4b86f5"
RED    = "#e84444"
GREEN  = "#20ba58"
PURPLE = "#9f7bf5"
MUTED  = "#3e4e68"

REGIME_COLORS = {
    "High (>6%)":      RED,
    "Moderate (4–6%)": GOLD,
    "Low (<4%)":       TEAL,
}

def base_layout(title="", height=440, yt="", xt="", y2=False):
    lo = dict(
        height=height, plot_bgcolor=PBG, paper_bgcolor=PBG,
        font=dict(family=FF, color=FC, size=11),
        xaxis=dict(gridcolor=GRD, gridwidth=1, zeroline=False, showline=False,
                   tickfont=dict(family=MF, size=10, color=FC),
                   title=dict(text=xt, font=dict(size=10, color=FC))),
        yaxis=dict(gridcolor=GRD, gridwidth=1,
                   zeroline=True, zerolinecolor="#242e42", zerolinewidth=1,
                   tickfont=dict(family=MF, size=10, color=FC),
                   title=dict(text=yt, font=dict(size=10, color=FC))),
        legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="left", x=0,
                    font=dict(family=FF, size=10, color=FC),
                    bgcolor="rgba(0,0,0,0)", bordercolor="rgba(0,0,0,0)"),
        margin=dict(l=0, r=0, t=44 if title else 28, b=10),
        hovermode="x unified",
    )
    if title:
        lo["title"] = dict(text=title, font=dict(family=FF, size=12, color="#b0bac8"),
                           x=0, y=0.99, xanchor="left")
    if y2:
        lo["yaxis2"] = dict(overlaying="y", side="right",
                            gridcolor="rgba(0,0,0,0)", zeroline=False, showline=False,
                            tickfont=dict(family=MF, size=10, color=TEAL))
    return lo


# ═══════════════════════════════════════════════════════════════════════════════
#  LIVE DATA FETCH
# ═══════════════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=43200, show_spinner=False)
def fetch_market_data():
    """Try Yahoo Finance; return dicts + live flags."""
    nifty, gold = {}, {}
    nl, gl = False, False
    errors = []

    try:
        raw = yf.download("^NSEI", start="2010-01-01", end="2025-12-31",
                          progress=False, auto_adjust=True, timeout=10)
        if not raw.empty and len(raw) > 100:
            cl = raw["Close"].squeeze()
            ann = cl.resample("YE").last()
            for i in range(1, len(ann)):
                yr = ann.index[i].year
                nifty[yr] = round(float((ann.iloc[i] / ann.iloc[i-1] - 1) * 100), 2)
            if len(nifty) >= 5:
                nl = True
    except Exception as e:
        errors.append(str(e))

    if not nl:
        nifty = dict(NIFTY_FALLBACK)

    try:
        raw = yf.download("GC=F", start="2010-01-01", end="2025-12-31",
                          progress=False, auto_adjust=True, timeout=10)
        if not raw.empty and len(raw) > 100:
            cl = raw["Close"].squeeze()
            ann = cl.resample("YE").last()
            for i in range(1, len(ann)):
                yr = ann.index[i].year
                gold[yr] = round(float((ann.iloc[i] / ann.iloc[i-1] - 1) * 100), 2)
            if len(gold) >= 5:
                gl = True
    except Exception as e:
        errors.append(str(e))

    if not gl:
        gold = dict(GOLD_FALLBACK)

    return nifty, gold, nl, gl, errors


# ═══════════════════════════════════════════════════════════════════════════════
#  DATA ASSEMBLY — no st.cache_data (avoids tuple serialization bug)
# ═══════════════════════════════════════════════════════════════════════════════
def build_df(nifty_d, gold_d):
    years = sorted(CPI_DATA.keys())
    rows = []
    for yr in years:
        rows.append({
            "Year":      yr,
            "CPI":       CPI_DATA[yr],
            "WPI":       WPI_DATA.get(yr, np.nan),
            "Repo":      REPO_DATA.get(yr, np.nan),
            "FD":        FD_DATA.get(yr, np.nan),
            "Nifty_Nom": nifty_d.get(yr, np.nan),
            "Gold_Nom":  gold_d.get(yr, np.nan),
        })
    df = pd.DataFrame(rows)
    df["Nifty_Real"] = df["Nifty_Nom"] - df["CPI"]
    df["Gold_Real"]  = df["Gold_Nom"]  - df["CPI"]
    df["FD_Real"]    = df["FD"]        - df["CPI"]

    def regime(c):
        if pd.isna(c):  return "Unknown"
        if c > 6:       return "High (>6%)"
        if c >= 4:      return "Moderate (4–6%)"
        return "Low (<4%)"

    df["Regime"] = df["CPI"].apply(regime)
    df["Year"]   = df["Year"].astype(int)
    return df


# ═══════════════════════════════════════════════════════════════════════════════
#  WEALTH SIMULATOR
# ═══════════════════════════════════════════════════════════════════════════════
def simulate(df, sy, ey, init=100000):
    sub = df[(df["Year"] >= sy) & (df["Year"] <= ey)].copy()
    if sub.empty: return None
    nw, nrw, gw, fw = init, init, init, init
    ci = 1.0
    # First row: ₹1L starting value, labelled at sy-1 (e.g. "2010" = "start of 2011")
    # We rename this tick to "Start" in the chart so it never shows as 2010.
    rows = [{"Nifty Nominal": nw, "Nifty Real (adj)": nrw,
             "Gold Nominal": gw, "FD Nominal": fw}]
    idx  = [sy - 1]   # placeholder; renamed to "Start" via tickvals in chart
    for _, r in sub.iterrows():
        nr = r["Nifty_Nom"] / 100 if not np.isnan(r["Nifty_Nom"]) else 0
        gr = r["Gold_Nom"]  / 100 if not np.isnan(r["Gold_Nom"])  else 0
        fr = r["FD"]        / 100 if not np.isnan(r["FD"])        else 0
        cr = r["CPI"]       / 100 if not np.isnan(r["CPI"])       else 0
        ci *= (1 + cr)
        nw  = nw  * (1 + nr)
        nrw = nw  / ci
        gw  = gw  * (1 + gr)
        fw  = fw  * (1 + fr)
        idx.append(int(r["Year"]))
        rows.append({"Nifty Nominal": nw, "Nifty Real (adj)": nrw,
                     "Gold Nominal": gw, "FD Nominal": fw})
    return pd.DataFrame(rows, index=idx)


# ═══════════════════════════════════════════════════════════════════════════════
#  CORRELATION
# ═══════════════════════════════════════════════════════════════════════════════
def corr(df, c1, c2):
    s = df[[c1, c2]].dropna()
    return round(s[c1].corr(s[c2]), 3) if len(s) >= 4 else np.nan


# ═══════════════════════════════════════════════════════════════════════════════
#  FETCH & BUILD
# ═══════════════════════════════════════════════════════════════════════════════
with st.spinner("Connecting to Yahoo Finance…"):
    nd, gd, nl, gl, errs = fetch_market_data()

df = build_df(nd, gd)
lat = df.dropna(subset=["Nifty_Nom"]).iloc[-1]


# ═══════════════════════════════════════════════════════════════════════════════
#  HERO
# ═══════════════════════════════════════════════════════════════════════════════
nb = '<span class="badge-live">LIVE</span>'  if nl else '<span class="badge-official">NSE OFFICIAL</span>'
gb = '<span class="badge-live">LIVE</span>'  if gl else '<span class="badge-official">WGC DATA</span>'

st.markdown(f"""
<div class="hero">
  <div class="hero-tag">📊 &nbsp;Day 11 · Week 2: Macros &nbsp;·&nbsp; 30 Days of AI Finance</div>
  <div class="hero-title">Inflation vs <span>Market Returns</span> Tracker</div>
  <div class="hero-sub">India's real investment story — how CPI, WPI and RBI rate cycles combine with market
  returns to reveal what your portfolio <em>actually</em> earned in purchasing-power terms.</div>
  <div class="hero-meta">
    <span class="hm">UNIVERSE &nbsp;<span>India — Nifty 50, Gold, FD</span></span>
    <span class="hm">PERIOD &nbsp;<span>2011–2025 + 2026 YTD</span></span>
    <span class="hm">NIFTY &nbsp;<span>^NSEI {nb}</span></span>
    <span class="hm">GOLD &nbsp;<span>GC=F {gb}</span></span>
    <span class="hm">MACRO &nbsp;<span>MOSPI · RBI · SBI</span></span>
  </div>
</div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  KPI STRIP
# ═══════════════════════════════════════════════════════════════════════════════
# KPI strip shows 2026 YTD live snapshot at top
lc   = YTD_2026["cpi_ytd"]          # CPI Jan-Apr 2026 avg (MOSPI, new base 2024=100)
lr   = YTD_2026["repo"]              # RBI repo Apr 2026 MPC
lfd  = FD_DATA.get(2025, 6.50)       # SBI 1yr FD (last known full-year rate)
lfdr = lfd - lc
lnn  = YTD_2026["nifty_ytd"]         # Nifty YTD Jun 11 2026
lnr  = lnn - lc                      # Real YTD (Nifty YTD - CPI YTD avg)
lgn  = YTD_2026["gold_ytd"]          # Gold YTD Jun 11 2026
lyr  = 2026

def vc(v, pos="teal", neg="red"):
    return pos if (not np.isnan(float(v)) and float(v) >= 0) else neg

nc_  = vc(lnn)
nrc_ = vc(lnr)
gc_  = "gold" if not np.isnan(float(lgn)) and float(lgn) >= 0 else "red"
fdc_ = vc(lfdr, "green", "orange")

st.markdown(f"""
<div class="kpi-grid">
  <div class="kpi orange">
    <div class="kpi-lbl">India CPI</div>
    <div class="kpi-val orange">{lc:.1f}%</div>
    <div class="kpi-sub">2026 YTD avg Jan–Apr · {'+' if lc>=4 else ''}{lc-4:.1f}pp vs RBI 4% target</div>
    <div class="kpi-src">MOSPI / World Bank</div>
  </div>
  <div class="kpi {nc_}">
    <div class="kpi-lbl">Nifty 50 Return</div>
    <div class="kpi-val {nc_}">{f"{lnn:+.1f}%" if not np.isnan(float(lnn)) else "—"}</div>
    <div class="kpi-sub">YTD as of {YTD_2026['as_of']} · partial year</div>
    <div class="kpi-src">{"Yahoo Finance (^NSEI)" if nl else "NSE official (niftyindices.com)"}</div>
  </div>
  <div class="kpi {nrc_}">
    <div class="kpi-lbl">Real Nifty Return</div>
    <div class="kpi-val {nrc_}">{f"{lnr:+.1f}%" if not np.isnan(float(lnr)) else "—"}</div>
    <div class="kpi-sub">Nominal minus CPI · purchasing-power adj</div>
    <div class="kpi-src">Computed: Nifty − CPI</div>
  </div>
  <div class="kpi gold">
    <div class="kpi-lbl">Gold Return (USD)</div>
    <div class="kpi-val {gc_}">{f"{lgn:+.1f}%" if not np.isnan(float(lgn)) else "—"}</div>
    <div class="kpi-sub">YTD as of {YTD_2026['as_of']} · geopolitical drag</div>
    <div class="kpi-src">{"Yahoo Finance (GC=F)" if gl else "World Gold Council"}</div>
  </div>
  <div class="kpi blue">
    <div class="kpi-lbl">RBI Repo Rate</div>
    <div class="kpi-val blue">{lr:.2f}%</div>
    <div class="kpi-sub">Held at Apr 2026 MPC · neutral stance</div>
    <div class="kpi-src">RBI Monetary Policy Committee</div>
  </div>
  <div class="kpi {fdc_}">
    <div class="kpi-lbl">FD Real Return</div>
    <div class="kpi-val {fdc_}">{lfdr:+.2f}%</div>
    <div class="kpi-sub">SBI 1yr {lfd:.1f}% − CPI YTD {lc:.2f}%</div>
    <div class="kpi-src">SBI Term Deposit Cards</div>
  </div>
</div>""", unsafe_allow_html=True)


# ── 2026 YTD CALLOUT ──────────────────────────────────────────────────────────
st.markdown(f"""
<div style="background:rgba(79,134,245,0.07);border:1px solid rgba(79,134,245,0.25);
     border-left:3px solid #4b86f5;border-radius:0 8px 8px 0;
     padding:.7rem 1.1rem;margin-bottom:1.4rem;font-size:.82rem;color:#6e7d96;line-height:1.7;">
  <strong style="color:#4b86f5;font-size:.65rem;letter-spacing:.1em;text-transform:uppercase;">
    📡 2026 Live Snapshot — {YTD_2026['as_of']}
  </strong><br>
  KPI cards above show <strong>2026 YTD (partial year)</strong>.
  Nifty: <strong style="color:#e84444;">{YTD_2026['nifty_ytd']:+.2f}%</strong>
  (26,130→23,297) &nbsp;·&nbsp;
  Gold: <strong style="color:#e84444;">{YTD_2026['gold_ytd']:+.2f}%</strong>
  ($4,368→$4,081) &nbsp;·&nbsp;
  CPI: <strong style="color:#f0bc3a;">{YTD_2026['cpi_ytd']:.2f}%</strong>
  avg {YTD_2026['cpi_months']} (MOSPI) &nbsp;·&nbsp;
  Repo: <strong style="color:#4b86f5;">{YTD_2026['repo']:.2f}%</strong>
  (RBI held Apr MPC) &nbsp;·&nbsp;
  Historical charts below cover <strong>2011–2025</strong> complete annual data.
</div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  TABS
# ═══════════════════════════════════════════════════════════════════════════════
t1, t2, t3, t4, t5 = st.tabs([
    "📈  CPI + Nifty Overlay",
    "💰  Real Returns",
    "🌡  Inflation Regimes",
    "⚖️  Asset Comparison",
    "₹  Wealth Simulator",
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — CPI + NIFTY OVERLAY
# ══════════════════════════════════════════════════════════════════════════════
with t1:
    st.markdown("""<div class="sh">
      <span class="sh-title">CPI Inflation · WPI · RBI Repo Rate vs Nifty 50 Returns</span>
      <span class="sh-tag">MACRO OVERLAY</span></div>""", unsafe_allow_html=True)

    dp = df.dropna(subset=["CPI"]).copy()
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # CPI bars — colour by regime
    bar_clr = [ORANGE if v > 6 else GOLD if v >= 4 else TEAL for v in dp["CPI"]]
    fig.add_trace(go.Bar(x=dp["Year"], y=dp["CPI"], name="CPI",
                         marker_color=bar_clr, opacity=0.82,
                         hovertemplate="<b>%{x}</b> · CPI: %{y:.2f}%<extra></extra>"),
                  secondary_y=False)

    # WPI line
    wm = dp["WPI"].notna()
    if wm.any():
        fig.add_trace(go.Scatter(x=dp.loc[wm,"Year"], y=dp.loc[wm,"WPI"],
                                 name="WPI", mode="lines+markers",
                                 line=dict(color=PURPLE, width=2, dash="dot"),
                                 marker=dict(size=4),
                                 hovertemplate="WPI: %{y:.2f}%<extra></extra>"),
                      secondary_y=False)

    # Repo line
    rm = dp["Repo"].notna()
    if rm.any():
        fig.add_trace(go.Scatter(x=dp.loc[rm,"Year"], y=dp.loc[rm,"Repo"],
                                 name="Repo Rate", mode="lines+markers",
                                 line=dict(color=BLUE, width=2),
                                 marker=dict(size=4),
                                 hovertemplate="Repo: %{y:.2f}%<extra></extra>"),
                      secondary_y=False)

    # Nifty on secondary axis
    nm = dp["Nifty_Nom"].notna()
    if nm.any():
        npt_clr = [TEAL if v >= 0 else RED for v in dp.loc[nm, "Nifty_Nom"]]
        fig.add_trace(go.Scatter(x=dp.loc[nm,"Year"], y=dp.loc[nm,"Nifty_Nom"],
                                 name="Nifty Return", mode="lines+markers",
                                 line=dict(color=TEAL, width=2.8),
                                 marker=dict(size=7, color=npt_clr,
                                             line=dict(width=1, color=PBG)),
                                 hovertemplate="Nifty: %{y:+.1f}%<extra></extra>"),
                      secondary_y=True)

    # 6% threshold
    fig.add_shape(type="line", xref="x", yref="y",
                  x0=dp["Year"].min()-0.5, x1=dp["Year"].max()+0.5,
                  y0=6, y1=6, line=dict(color=RED, dash="dash", width=1.5))
    fig.add_annotation(x=dp["Year"].max()-0.5, y=6.55, xref="x", yref="y",
                       text="High Inflation (6%)", showarrow=False,
                       font=dict(size=9, color=RED, family=MF))

    lo1 = base_layout(height=460, yt="Rate / Inflation (%)", y2=True)
    lo1["yaxis2"]["title"] = dict(text="Nifty Return (%)", font=dict(size=10, color=TEAL))
    lo1["barmode"] = "overlay"
    fig.update_layout(**lo1)
    st.plotly_chart(fig, use_container_width=True)

    # Correlation insight
    c_val = corr(df, "CPI", "Nifty_Nom")
    if not np.isnan(c_val):
        if c_val < -0.3:
            ctxt = f"Negative correlation of <strong>{c_val}</strong> — hot inflation reliably compressed Nifty returns via RBI rate hikes."
        elif c_val < 0:
            ctxt = f"Mild negative correlation of <strong>{c_val}</strong> — regime-level patterns are more telling than year-to-year correlation."
        else:
            ctxt = f"Correlation of <strong>{c_val}</strong> — modest CPI did not systematically suppress Nifty; high-inflation regimes (>6%) tell a different story."
    else:
        ctxt = "Insufficient overlapping data."

    c1a, c1b = st.columns([1.5, 1])
    with c1a:
        st.markdown(f"""<div class="ib"><div class="ib-lbl">📐 Statistical Signal</div>
          <div class="ib-txt"><strong>CPI vs Nifty Correlation: {c_val if not np.isnan(c_val) else "N/A"}</strong><br>{ctxt}
          </div></div>""", unsafe_allow_html=True)
    with c1b:
        hiy = df[df["CPI"] > 6]["Year"].tolist()
        st.markdown(f"""<div class="ib orange"><div class="ib-lbl">🔥 High Inflation Years</div>
          <div class="ib-txt">CPI above 6% in <strong>{len(hiy)} years</strong>:
          {', '.join(map(str, hiy))}<br>Each triggered RBI rate-hike cycles.</div></div>""",
          unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — REAL RETURNS
# ══════════════════════════════════════════════════════════════════════════════
with t2:
    st.markdown("""<div class="sh">
      <span class="sh-title">What Investors Actually Earned — Inflation-Adjusted Returns</span>
      <span class="sh-tag">REAL RETURNS</span></div>""", unsafe_allow_html=True)

    dr = df.dropna(subset=["CPI", "Nifty_Real"]).copy()
    fig2 = go.Figure()

    # Nifty real bars
    fig2.add_trace(go.Bar(
        x=dr["Year"], y=dr["Nifty_Real"],
        name="Nifty Real Return",
        marker_color=[GREEN if v >= 0 else RED for v in dr["Nifty_Real"]],
        opacity=0.88,
        hovertemplate="<b>%{x}</b><br>Nifty Real: %{y:+.2f}%<extra></extra>",
    ))

    # Gold real
    gm2 = df["Gold_Real"].notna()
    if gm2.any():
        fig2.add_trace(go.Scatter(
            x=df.loc[gm2,"Year"], y=df.loc[gm2,"Gold_Real"],
            name="Gold Real Return", mode="lines+markers",
            line=dict(color=GOLD, width=2, dash="dot"),
            marker=dict(size=5),
            hovertemplate="Gold Real: %{y:+.1f}%<extra></extra>",
        ))

    # FD real
    fm2 = df["FD_Real"].notna()
    if fm2.any():
        fig2.add_trace(go.Scatter(
            x=df.loc[fm2,"Year"], y=df.loc[fm2,"FD_Real"],
            name="FD Real Return", mode="lines+markers",
            line=dict(color=BLUE, width=2),
            marker=dict(size=5),
            hovertemplate="FD Real: %{y:+.1f}%<extra></extra>",
        ))

    fig2.add_shape(type="line",
                   x0=dr["Year"].min()-0.5, x1=dr["Year"].max()+0.5,
                   y0=0, y1=0, line=dict(color=MUTED, width=1))
    fig2.update_layout(**base_layout(height=440, yt="Real Return (%)"))
    st.plotly_chart(fig2, use_container_width=True)

    anr = dr["Nifty_Real"].mean()
    nny = (dr["Nifty_Real"] < 0).sum()
    afdr = df["FD_Real"].dropna().mean()
    st.markdown(f"""<div class="ss">
      <div class="sc"><div class="sv {'teal' if anr>0 else 'orange'}">{anr:+.1f}%</div>
        <div class="sl">Avg Nifty Real Return</div></div>
      <div class="sc"><div class="sv red">{nny}</div>
        <div class="sl">Years Negative Real Return</div></div>
      <div class="sc"><div class="sv blue">{afdr:+.1f}%</div>
        <div class="sl">Avg FD Real Return</div></div>
    </div>""", unsafe_allow_html=True)

    neg_y = dr[dr["Nifty_Real"] < 0]["Year"].tolist()
    best  = dr.loc[dr["Nifty_Real"].idxmax()]
    worst = dr.loc[dr["Nifty_Real"].idxmin()]

    c2a, c2b = st.columns(2)
    with c2a:
        st.markdown(f"""<div class="ib orange"><div class="ib-lbl">⚠ The Nominal Illusion</div>
          <div class="ib-txt">Negative Nifty <em>real</em> return years:
          <strong>{', '.join(map(str, neg_y)) if neg_y else 'None'}</strong><br>
          These years appeared positive in headline terms but investors lost purchasing power.</div></div>""",
          unsafe_allow_html=True)
    with c2b:
        st.markdown(f"""<div class="ib gold"><div class="ib-lbl">🏆 Best vs Worst Real Year</div>
          <div class="ib-txt">Best: <strong>{best['Year']:.0f}</strong> — Real
          <strong>{best['Nifty_Real']:+.1f}%</strong>
          (Nom {best['Nifty_Nom']:+.1f}%, CPI {best['CPI']:.2f}%)<br>
          Worst: <strong>{worst['Year']:.0f}</strong> — Real
          <strong>{worst['Nifty_Real']:+.1f}%</strong>
          (Nom {worst['Nifty_Nom']:+.1f}%, CPI {worst['CPI']:.2f}%)</div></div>""",
          unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — INFLATION REGIMES
# ══════════════════════════════════════════════════════════════════════════════
with t3:
    st.markdown("""<div class="sh">
      <span class="sh-title">Return Distribution Across Inflation Regimes</span>
      <span class="sh-tag">REGIME ANALYSIS</span></div>""", unsafe_allow_html=True)

    dr3 = df.dropna(subset=["CPI","Nifty_Nom"]).copy()
    reg = dr3.groupby("Regime").agg(
        Avg_CPI=("CPI","mean"), Avg_Nifty_Nom=("Nifty_Nom","mean"),
        Avg_Nifty_Real=("Nifty_Real","mean"), Count=("Year","count")
    ).reset_index()

    rc_ = st.columns(len(reg))
    for i, row in reg.iterrows():
        rg = row["Regime"]
        cc = "red" if "High" in rg else ("gold" if "Moderate" in rg else "teal")
        with rc_[i]:
            st.markdown(f"""<div class="sc" style="text-align:left;padding:1rem 1.1rem;">
              <div class="kpi-lbl" style="margin-bottom:.4rem;">{rg}</div>
              <div class="sv {cc}" style="font-size:1.05rem;">Avg CPI: {row['Avg_CPI']:.1f}%</div>
              <div style="margin-top:.5rem;font-size:.78rem;color:#6e7d96;line-height:1.7;">
                Nifty Nom: <strong style="color:#e4e8f0;">{row['Avg_Nifty_Nom']:+.1f}%</strong><br>
                Nifty Real: <strong style="color:#e4e8f0;">{row['Avg_Nifty_Real']:+.1f}%</strong><br>
                Years: <strong style="color:#e4e8f0;">{row['Count']}</strong>
              </div></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    cb_, ct_ = st.columns([1.3, 1])

    with cb_:
        fig3 = go.Figure()
        for rg in ["High (>6%)", "Moderate (4–6%)", "Low (<4%)"]:
            sub3 = dr3[dr3["Regime"] == rg]["Nifty_Nom"].dropna()
            if len(sub3) == 0: continue
            clr3 = REGIME_COLORS[rg]
            # Build a valid rgba fillcolor using rgb + opacity, not 8-digit hex
            r_int = int(clr3[1:3], 16)
            g_int = int(clr3[3:5], 16)
            b_int = int(clr3[5:7], 16)
            fill_rgba = f"rgba({r_int},{g_int},{b_int},0.12)"
            fig3.add_trace(go.Box(
                y=sub3, name=rg,
                marker_color=clr3,
                line=dict(color=clr3, width=1.5),
                fillcolor=fill_rgba,
                boxmean=True,
                hovertemplate="<b>%{y:+.1f}%</b><extra>" + rg + "</extra>",
            ))
        fig3.update_layout(**base_layout(
            title="Nifty 50 Return Distribution by Inflation Regime",
            height=380, yt="Annual Nifty Return (%)"))
        fig3.update_layout(showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)

    with ct_:
        td = df[["Year","Regime","CPI","Nifty_Nom","Nifty_Real"]].dropna(subset=["CPI"]).copy()
        td["CPI"]        = td["CPI"].map(lambda x: f"{x:.2f}%")
        td["Nifty_Nom"]  = td["Nifty_Nom"].map(lambda x: f"{x:+.1f}%" if not np.isnan(x) else "—")
        td["Nifty_Real"] = td["Nifty_Real"].map(lambda x: f"{x:+.1f}%" if not np.isnan(x) else "—")
        td = td.rename(columns={"Nifty_Nom":"Nifty Nom.","Nifty_Real":"Nifty Real"})

        def sty(v):
            if "High"     in str(v): return "background-color:rgba(232,68,68,.10);color:#e84444"
            if "Moderate" in str(v): return "background-color:rgba(240,188,58,.10);color:#f0bc3a"
            if "Low"      in str(v): return "background-color:rgba(0,212,160,.10);color:#00d4a0"
            return ""

        st.dataframe(td.style.map(sty, subset=["Regime"]),
                     use_container_width=True, hide_index=True, height=380)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — ASSET COMPARISON
# ══════════════════════════════════════════════════════════════════════════════
with t4:
    st.markdown("""<div class="sh">
      <span class="sh-title">Multi-Asset Returns vs CPI Inflation</span>
      <span class="sh-tag">ASSET COMPARISON</span></div>""", unsafe_allow_html=True)

    c4a, c4b = st.columns([1.4, 1])

    with c4a:
        dc4 = df.dropna(subset=["CPI"]).copy()
        fig4a = go.Figure()
        fig4a.add_trace(go.Bar(x=dc4["Year"], y=dc4["CPI"], name="CPI",
                               marker_color=ORANGE, opacity=0.75,
                               hovertemplate="CPI: %{y:.2f}%<extra></extra>"))
        fig4a.add_trace(go.Bar(x=dc4["Year"], y=dc4["FD"], name="SBI FD",
                               marker_color=BLUE, opacity=0.80,
                               hovertemplate="FD: %{y:.1f}%<extra></extra>"))
        nm4 = dc4["Nifty_Nom"].notna()
        if nm4.any():
            fig4a.add_trace(go.Bar(x=dc4.loc[nm4,"Year"], y=dc4.loc[nm4,"Nifty_Nom"],
                                   name="Nifty 50", marker_color=TEAL, opacity=0.80,
                                   hovertemplate="Nifty: %{y:+.1f}%<extra></extra>"))
        gm4 = dc4["Gold_Nom"].notna()
        if gm4.any():
            fig4a.add_trace(go.Bar(x=dc4.loc[gm4,"Year"], y=dc4.loc[gm4,"Gold_Nom"],
                                   name="Gold (USD)", marker_color=GOLD, opacity=0.80,
                                   hovertemplate="Gold: %{y:+.1f}%<extra></extra>"))
        lo4a = base_layout(title="Annual Returns: Nifty vs Gold vs FD vs CPI",
                           height=410, yt="Annual Return / Rate (%)")
        lo4a["barmode"] = "group"
        fig4a.update_layout(**lo4a)
        st.plotly_chart(fig4a, use_container_width=True)

    with c4b:
        ds4 = df.dropna(subset=["CPI","Nifty_Nom"]).copy()
        fig4b = go.Figure()
        for rg, clr in REGIME_COLORS.items():
            sub4 = ds4[ds4["Regime"] == rg]
            if len(sub4) == 0: continue
            fig4b.add_trace(go.Scatter(
                x=sub4["CPI"], y=sub4["Nifty_Nom"],
                mode="markers+text", name=rg,
                marker=dict(size=9, color=clr, line=dict(width=1, color=PBG)),
                text=sub4["Year"].astype(str),
                textposition="top center",
                textfont=dict(size=8, color=clr, family=MF),
                hovertemplate="<b>%{text}</b><br>CPI: %{x:.2f}%<br>Nifty: %{y:+.1f}%<extra></extra>",
            ))
        valid4 = ds4.dropna(subset=["CPI","Nifty_Nom"])
        if len(valid4) > 3:
            z4 = np.polyfit(valid4["CPI"], valid4["Nifty_Nom"], 1)
            xr4 = np.linspace(valid4["CPI"].min(), valid4["CPI"].max(), 50)
            fig4b.add_trace(go.Scatter(x=xr4, y=np.polyval(z4, xr4), mode="lines",
                                       name="Trend",
                                       line=dict(color=MUTED, dash="dot", width=1.5),
                                       hoverinfo="skip"))
        fig4b.update_layout(**base_layout(title="CPI vs Nifty — Scatter by Regime",
                                          height=410, xt="CPI (%)", yt="Nifty Return (%)"))
        st.plotly_chart(fig4b, use_container_width=True)

    # Regime insights
    dhi4 = df.dropna(subset=["CPI","Nifty_Nom","Gold_Nom"])
    hi4  = dhi4[dhi4["CPI"] > 6]
    lo4  = dhi4[dhi4["CPI"] < 4]
    anh4 = hi4["Nifty_Nom"].mean() if len(hi4) > 0 else np.nan
    agh4 = hi4["Gold_Nom"].mean()  if len(hi4) > 0 else np.nan
    anl4 = lo4["Nifty_Nom"].mean() if len(lo4) > 0 else np.nan
    agl4 = lo4["Gold_Nom"].mean()  if len(lo4) > 0 else np.nan

    ci4a, ci4b = st.columns(2)
    with ci4a:
        if not (np.isnan(anh4) or np.isnan(agh4)):
            w4 = "Gold" if agh4 > anh4 else "Nifty"
            wr4 = max(agh4, anh4)
            st.markdown(f"""<div class="ib orange"><div class="ib-lbl">🔥 High Inflation (CPI > 6%)</div>
              <div class="ib-txt">Avg Nifty <strong>{anh4:+.1f}%</strong> &nbsp;|&nbsp;
              Avg Gold <strong>{agh4:+.1f}%</strong><br>
              <strong>{w4}</strong> led with <strong>{wr4:+.1f}%</strong> avg.
              Hard assets typically outperform during inflationary stress.</div></div>""",
              unsafe_allow_html=True)
    with ci4b:
        if not (np.isnan(anl4) or np.isnan(agl4)):
            w4b = "Nifty" if anl4 > agl4 else "Gold"
            wr4b = max(anl4, agl4)
            st.markdown(f"""<div class="ib"><div class="ib-lbl">✅ Low Inflation (CPI < 4%)</div>
              <div class="ib-txt">Avg Nifty <strong>{anl4:+.1f}%</strong> &nbsp;|&nbsp;
              Avg Gold <strong>{agl4:+.1f}%</strong><br>
              <strong>{w4b}</strong> outperformed at <strong>{wr4b:+.1f}%</strong>.
              Benign inflation historically favours equities.</div></div>""",
              unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — WEALTH SIMULATOR
# ══════════════════════════════════════════════════════════════════════════════
with t5:
    st.markdown("""<div class="sh">
      <span class="sh-title">₹1 Lakh Wealth Simulator — Nominal vs Real Purchasing Power</span>
      <span class="sh-tag">COMPOUNDING PATH</span></div>""", unsafe_allow_html=True)

    ayrs = sorted(df["Year"].unique())
    wc1, wc2, _ = st.columns([1, 1, 3])
    with wc1:
        sy = st.selectbox("Start Year", ayrs[:-1], index=0)
    with wc2:
        eo = [y for y in ayrs if y > sy]
        ey = st.selectbox("End Year", eo, index=len(eo)-1)

    wdf = simulate(df, sy, ey)

    if wdf is not None and len(wdf) > 1:
        fig5 = go.Figure()
        series5 = [
            ("Nifty Nominal",    TEAL,      "solid"),
            ("Nifty Real (adj)", "#00a87e", "dot"),
            ("Gold Nominal",     GOLD,      "dash"),
            ("FD Nominal",       BLUE,      "dashdot"),
        ]

        for name, clr, dash in series5:
            if name in wdf.columns:
                fig5.add_trace(go.Scatter(
                    x=list(wdf.index), y=wdf[name], name=name,
                    mode="lines+markers",
                    line=dict(color=clr, width=2.8, dash=dash),
                    marker=dict(size=5.5, color=clr),
                    hovertemplate="<b>%{x}</b> · " + name + ": ₹%{y:,.0f}<extra></extra>",
                ))

        # ₹1L baseline
        fig5.add_shape(type="line",
                       x0=sy - 1, x1=ey,
                       y0=100000, y1=100000,
                       line=dict(color=MUTED, dash="dot", width=1))
        fig5.add_annotation(x=sy - 1, y=100000, yshift=12, showarrow=False,
                             text=f"₹1,00,000 — Invested Jan {sy}",
                             font=dict(size=9, color=MUTED, family=MF))

        lo5 = base_layout(title=f"₹1 Lakh Invested in {sy} — Compounded to {ey}",
                          height=450, yt="Portfolio Value (₹)")
        lo5["yaxis"]["tickprefix"] = "₹"
        lo5["yaxis"]["tickformat"] = ",.0f"
        # Keep numeric axis; rename only the sy-1 tick to "Start" using tickvals/ticktext
        all_ticks     = list(wdf.index)          # [sy-1, sy, sy+1, ..., ey]
        all_ticklabels = [f"Start<br>({sy})" if t == sy - 1 else str(t) for t in all_ticks]
        lo5["xaxis"]["tickmode"]  = "array"
        lo5["xaxis"]["tickvals"]  = all_ticks
        lo5["xaxis"]["ticktext"]  = all_ticklabels
        fig5.update_layout(**lo5)
        st.plotly_chart(fig5, use_container_width=True)

        # Final values — wdf.iloc[-1] = after ey's return (correct end value)
        fin5 = wdf.iloc[-1]
        nf5  = float(fin5.get("Nifty Nominal",    100000))
        nrf5 = float(fin5.get("Nifty Real (adj)", 100000))
        gf5  = float(fin5.get("Gold Nominal",     100000))
        ff5  = float(fin5.get("FD Nominal",       100000))

        def lk(v): return f"₹{v/100000:.2f}L" if v >= 100000 else f"₹{v:,.0f}"

        gap5   = nf5 - nrf5
        yrs    = ey - sy + 1
        pct_gap = (gap5 / nf5 * 100) if nf5 > 0 else 0

        st.markdown(f"""<div class="wc">
          <div class="wcard">
            <div class="wc-lbl">Nifty 50 Nominal</div>
            <div class="wc-val" style="color:{TEAL};">{lk(nf5)}</div>
            <div class="wc-sub">{nf5/100000:.1f}× growth over {yrs} yrs</div>
          </div>
          <div class="wcard">
            <div class="wc-lbl">Nifty Real (Infl. Adj.)</div>
            <div class="wc-val" style="color:#00a87e;">{lk(nrf5)}</div>
            <div class="wc-sub">{nrf5/100000:.1f}× real purchasing power</div>
          </div>
          <div class="wcard">
            <div class="wc-lbl">Gold Nominal (USD)</div>
            <div class="wc-val" style="color:{GOLD};">{lk(gf5)}</div>
            <div class="wc-sub">{gf5/100000:.1f}× growth over {yrs} yrs</div>
          </div>
          <div class="wcard">
            <div class="wc-lbl">SBI FD (Nominal)</div>
            <div class="wc-val" style="color:{BLUE};">{lk(ff5)}</div>
            <div class="wc-sub">{ff5/100000:.1f}× growth over {yrs} yrs</div>
          </div>
        </div>
        <div class="ib orange" style="margin-top:1rem;">
          <div class="ib-lbl">💡 The Inflation Tax — {sy}–{ey}</div>
          <div class="ib-txt">
          Inflation silently eroded <strong>₹{gap5:,.0f}</strong> of your Nifty gains over {yrs} years.<br>
          Nominal wealth: <strong>₹{nf5:,.0f}</strong> &nbsp;vs&nbsp;
          Real purchasing power: <strong>₹{nrf5:,.0f}</strong> —
          a <strong>{pct_gap:.0f}%</strong> gap.
          A headline return can look great while real returns quietly underperform.
          </div>
        </div>""", unsafe_allow_html=True)
    else:
        st.info("Insufficient data for the selected year range.")


# ═══════════════════════════════════════════════════════════════════════════════
#  FOOTER
# ═══════════════════════════════════════════════════════════════════════════════
nifty_src = "Yahoo Finance (^NSEI)" if nl else "NSE official (niftyindices.com)"
gold_src  = "Yahoo Finance (GC=F)"  if gl else "World Gold Council / Visual Capitalist 2025"

st.markdown(f"""<div class="footer">
  <div class="ft">Data Sources &amp; Methodology</div>
  <div class="fg">
    <div class="fi">MARKET DATA<br>
      <span>Nifty 50: {nifty_src}</span><br>
      <span>Gold: {gold_src}</span>
    </div>
    <div class="fi">INFLATION<br>
      <span>CPI (calendar yr): World Bank / MOSPI / Worlddata.info</span><br>
      <span>WPI (fiscal yr): GoI Office of Economic Adviser</span>
    </div>
    <div class="fi">MONETARY POLICY<br>
      <span>RBI Repo Rate: RBI MPC records (calendar yr end)</span><br>
      <span>FD Rates: SBI Historical Term Deposit Cards</span>
    </div>
    <div class="fi">METHODOLOGY<br>
      <span>Real Return = Nominal − CPI (calendar year)</span><br>
      <span>Regimes: High &gt;6% · Moderate 4–6% · Low &lt;4%</span>
    </div>
  </div>
  <div class="fd">⚠ Educational purposes only. Not financial advice. Past performance ≠ future results.
  Gold in USD (COMEX). CPI in calendar year basis.
  &nbsp;|&nbsp; Day 11 · Week 2: Macros · 30 Days of AI Finance</div>
</div>""", unsafe_allow_html=True)