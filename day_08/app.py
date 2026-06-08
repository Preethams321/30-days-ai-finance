import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="TerminalOne · Macro Intelligence",
    page_icon="⬛",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Syne:wght@400;600;700;800&family=Playfair+Display:ital,wght@0,700;1,400&display=swap');

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"], .stApp,
section.main, .main,
[data-testid="stVerticalBlock"],
[data-testid="stHorizontalBlock"],
[data-testid="stTabsContent"],
[data-testid="stTabs"],
div[class*="block-container"],
div[class*="css"] {
    background-color: #09090e !important;
    color: #e8e4dc !important;
}

#MainMenu, footer, header,
[data-testid="stDecoration"],
[data-testid="stToolbar"],
[data-testid="collapsedControl"] {
    display: none !important;
    visibility: hidden !important;
}

html, body, * { font-family: 'Syne', sans-serif; }

.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* ── BUTTONS ── */
.stButton > button {
    background: #111118 !important;
    color: #c9a96e !important;
    border: 1px solid rgba(201,169,110,0.3) !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.78rem !important;
    border-radius: 2px !important;
    padding: 0.4rem 0.9rem !important;
    transition: all 0.18s !important;
    white-space: nowrap !important;
}
.stButton > button:hover {
    background: rgba(201,169,110,0.1) !important;
    border-color: #c9a96e !important;
}

/* ── TABS ── */
[data-testid="stTabs"] [role="tablist"] {
    background: #0f0f18 !important;
    border-bottom: 1px solid rgba(255,255,255,0.06) !important;
    padding: 0 1.5rem !important;
    gap: 0 !important;
}
[data-testid="stTabs"] button[role="tab"] {
    color: #555 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    background: transparent !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    padding: 0.75rem 1.2rem !important;
    margin: 0 !important;
    transition: all 0.15s !important;
}
[data-testid="stTabs"] button[role="tab"]:hover { color: #c9a96e !important; }
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    color: #c9a96e !important;
    border-bottom: 2px solid #c9a96e !important;
    background: transparent !important;
}
[data-testid="stTabsContent"] {
    background: #09090e !important;
    padding: 0 !important;
    border: none !important;
}

/* ── SELECT / RADIO ── */
[data-testid="stSelectbox"] > div > div {
    background: #111118 !important;
    color: #e8e4dc !important;
    border-color: rgba(255,255,255,0.08) !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.72rem !important;
    border-radius: 2px !important;
}
[data-testid="stRadio"] label {
    color: #888 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.72rem !important;
}
[data-testid="stRadio"] [aria-checked="true"] + span {
    color: #c9a96e !important;
}

/* ── DATAFRAME ── */
[data-testid="stDataFrame"] iframe { background: #111118 !important; }

/* ── SPINNER ── */
.stSpinner > div { border-top-color: #c9a96e !important; }

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 3px; height: 3px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(201,169,110,0.25); border-radius: 2px; }

/* ══════════════════════════════
   TICKER TAPE
══════════════════════════════ */
.tape-outer {
    background: #0a0a10;
    border-bottom: 1px solid rgba(201,169,110,0.1);
    height: 36px;
    overflow: hidden;
    position: relative;
}
.tape-inner {
    display: flex;
    animation: scrollTape 40s linear infinite;
    white-space: nowrap;
    height: 100%;
    align-items: center;
    width: max-content;
}
.tape-inner:hover { animation-play-state: paused; }
@keyframes scrollTape {
    0%   { transform: translateX(0); }
    100% { transform: translateX(-50%); }
}
.tape-item {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0 1.5rem;
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    border-right: 1px solid rgba(255,255,255,0.04);
}
.tape-name { color: #666; }
.tape-price { color: #c8c4bc; }
.tape-pos { color: #4ab87a; }
.tape-neg { color: #e05c6c; }

/* ══════════════════════════════
   TOP BAR
══════════════════════════════ */
.topbar {
    background: #0f0f18;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    padding: 0 1.5rem;
    height: 52px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
}
.topbar-logo {
    font-family: 'Playfair Display', serif;
    font-size: 1.15rem;
    font-weight: 700;
    color: #c9a96e;
    white-space: nowrap;
    flex-shrink: 0;
}
.topbar-live {
    font-family: 'DM Mono', monospace;
    font-size: 0.6rem;
    color: #555;
    letter-spacing: 0.05em;
    white-space: nowrap;
    flex: 1;
    padding-left: 1rem;
}
.live-dot {
    display: inline-block;
    width: 6px; height: 6px;
    background: #4ab87a;
    border-radius: 50%;
    margin-right: 4px;
    animation: blink 2s ease-in-out infinite;
    vertical-align: middle;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:.25} }

/* ══════════════════════════════
   HOME PAGE
══════════════════════════════ */
.home-hero {
    background: linear-gradient(135deg, #0f0f18 0%, #111118 60%, #0a0a10 100%);
    border-bottom: 1px solid rgba(201,169,110,0.12);
    padding: 3.5rem 3rem 2.5rem;
    position: relative;
    overflow: hidden;
}
.home-hero::before {
    content: '';
    position: absolute;
    top: -80px; right: -80px;
    width: 400px; height: 400px;
    background: radial-gradient(circle, rgba(201,169,110,0.05) 0%, transparent 70%);
    pointer-events: none;
}
.hero-eyebrow {
    font-family: 'DM Mono', monospace;
    font-size: 0.6rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #c9a96e;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.hero-dot {
    width: 6px; height: 6px;
    background: #4ab87a;
    border-radius: 50%;
    animation: blink 2s ease-in-out infinite;
    display: inline-block;
}
.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: clamp(2.4rem, 5vw, 4rem);
    font-weight: 700;
    color: #e8e4dc;
    letter-spacing: -0.03em;
    line-height: 1.1;
    margin-bottom: 0.5rem;
}
.hero-title span { color: #c9a96e; font-style: italic; }
.hero-sub {
    font-size: 0.9rem;
    color: #777;
    max-width: 560px;
    line-height: 1.7;
    margin-bottom: 2rem;
    font-weight: 400;
}
.hero-stats {
    display: flex;
    gap: 2.5rem;
    flex-wrap: wrap;
    margin-bottom: 2rem;
}
.hero-stat-val {
    font-family: 'DM Mono', monospace;
    font-size: 1.5rem;
    font-weight: 500;
    color: #c9a96e;
    line-height: 1;
}
.hero-stat-lbl {
    font-family: 'DM Mono', monospace;
    font-size: 0.58rem;
    color: #555;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-top: 4px;
}

/* ── FEATURES GRID ── */
.features-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1px;
    background: rgba(201,169,110,0.08);
    border: 1px solid rgba(201,169,110,0.1);
    border-radius: 3px;
    overflow: hidden;
    margin: 2rem 3rem;
}
.feat-card {
    background: #0f0f18;
    padding: 1.6rem 1.8rem;
    transition: background 0.2s;
}
.feat-card:hover { background: #13131e; }
.feat-icon { font-size: 1.5rem; margin-bottom: 0.8rem; }
.feat-title {
    font-family: 'Syne', sans-serif;
    font-size: 0.95rem;
    font-weight: 700;
    color: #e8e4dc;
    margin-bottom: 0.4rem;
}
.feat-desc { font-size: 0.8rem; color: #666; line-height: 1.65; }

.sources-bar {
    display: flex;
    align-items: center;
    gap: 1.5rem;
    padding: 1rem 3rem;
    border-top: 1px solid rgba(255,255,255,0.04);
    flex-wrap: wrap;
}
.src-item {
    font-family: 'DM Mono', monospace;
    font-size: 0.6rem;
    color: #444;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    display: flex;
    align-items: center;
    gap: 0.4rem;
}
.src-item::before {
    content: '';
    width: 4px; height: 4px;
    background: rgba(201,169,110,0.4);
    border-radius: 50%;
}

/* ══════════════════════════════
   DASHBOARD CONTENT
══════════════════════════════ */
.dash-wrap { padding: 1.4rem 1.6rem; }

.sec-hdr {
    font-family: 'DM Mono', monospace;
    font-size: 0.62rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #c9a96e;
    padding: 0 0 0.55rem;
    border-bottom: 1px solid rgba(201,169,110,0.1);
    margin-bottom: 1rem;
    margin-top: 1.5rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.sec-hdr:first-child { margin-top: 0; }

/* ── METRIC CARD ── */
.mc {
    background: #111118;
    border: 1px solid rgba(255,255,255,0.055);
    border-radius: 3px;
    padding: 1.1rem 1.2rem 1rem;
    transition: border-color 0.18s;
    height: 100%;
    box-sizing: border-box;
}
.mc:hover { border-color: rgba(201,169,110,0.22); }
.mc-lbl {
    font-family: 'DM Mono', monospace;
    font-size: 0.62rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #555;
    margin-bottom: 0.5rem;
}
.mc-val {
    font-family: 'DM Mono', monospace;
    font-size: 1.45rem;
    font-weight: 500;
    color: #e8e4dc;
    letter-spacing: -0.01em;
    line-height: 1.15;
}
.mc-pos { color: #4ab87a; font-family:'DM Mono',monospace; font-size:0.73rem; margin-top:0.3rem; letter-spacing:0.02em; }
.mc-neg { color: #e05c6c; font-family:'DM Mono',monospace; font-size:0.73rem; margin-top:0.3rem; letter-spacing:0.02em; }
.mc-neu { color: #555;    font-family:'DM Mono',monospace; font-size:0.73rem; margin-top:0.3rem; }
.mc-52lbl {
    font-family: 'DM Mono', monospace;
    font-size: 0.56rem;
    color: #444;
    margin-top: 0.7rem;
    margin-bottom: 0.3rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
.mc-bar-outer {
    height: 3px;
    background: rgba(255,255,255,0.06);
    border-radius: 2px;
    position: relative;
    overflow: hidden;
}
.mc-bar-fill {
    height: 100%;
    border-radius: 2px;
    background: linear-gradient(90deg, #e05c6c 0%, #c9a96e 50%, #4ab87a 100%);
    transition: width 0.4s ease;
}
.mc-range {
    display: flex;
    justify-content: space-between;
    font-family: 'DM Mono', monospace;
    font-size: 0.55rem;
    color: #444;
    margin-top: 4px;
}

.divider { height: 1px; background: rgba(255,255,255,0.04); margin: 1.2rem 0; }

/* ── SIGNALS ── */
.sig-bull { background:rgba(74,184,122,.06);  border-left:2px solid #4ab87a; color:#a0d8b0; padding:.7rem 1rem; border-radius:2px; font-size:.8rem; margin-bottom:.45rem; line-height:1.65; font-family:'DM Mono',monospace; }
.sig-bear { background:rgba(224,92,108,.06); border-left:2px solid #e05c6c; color:#e8a0a8; padding:.7rem 1rem; border-radius:2px; font-size:.8rem; margin-bottom:.45rem; line-height:1.65; font-family:'DM Mono',monospace; }
.sig-neu  { background:rgba(201,169,110,.06); border-left:2px solid #c9a96e; color:#d8c898; padding:.7rem 1rem; border-radius:2px; font-size:.8rem; margin-bottom:.45rem; line-height:1.65; font-family:'DM Mono',monospace; }

/* ── FEAR GREED ── */
.fg-card {
    background: #111118;
    border: 1px solid rgba(255,255,255,0.055);
    border-radius: 3px;
    padding: 1.4rem;
    text-align: center;
}
.fg-score { font-family:'Playfair Display',serif; font-size:3.6rem; font-weight:700; line-height:1; }
.fg-name  { font-family:'DM Mono',monospace; font-size:0.78rem; letter-spacing:0.1em; text-transform:uppercase; margin-top:.4rem; }
.fg-bar-outer {
    height: 8px; border-radius: 4px;
    background: linear-gradient(90deg,#e05c6c,#e8c060 50%,#4ab87a);
    margin: 1.1rem 0 .4rem; position: relative;
}
.fg-needle {
    position: absolute; top: -6px;
    width: 20px; height: 20px;
    background: #e8e4dc; border-radius: 50%;
    border: 2px solid #0f0f18;
    transform: translateX(-50%);
    box-shadow: 0 0 8px rgba(0,0,0,0.6);
}
.fg-scale { display:flex; justify-content:space-between; font-family:'DM Mono',monospace; font-size:0.58rem; color:#555; }

/* ── CHART CARD ── */
.chart-card {
    background: #111118;
    border: 1px solid rgba(255,255,255,0.055);
    border-radius: 3px;
    padding: 1rem 1rem 0.5rem;
}

/* ── SECTOR HEATMAP ── */
.shm-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 6px;
    margin-bottom: 1rem;
}
.shm-cell {
    border-radius: 3px;
    padding: 1rem 0.8rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    transition: opacity 0.15s;
    cursor: default;
}
.shm-cell:hover { opacity: 0.85; }
.shm-name {
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.7);
    margin-bottom: 0.3rem;
}
.shm-pct {
    font-family: 'DM Mono', monospace;
    font-size: 1.1rem;
    font-weight: 500;
    color: #fff;
}
.shm-price {
    font-family: 'DM Mono', monospace;
    font-size: 0.6rem;
    color: rgba(255,255,255,0.45);
    margin-top: 0.2rem;
}

@media (max-width: 768px) {
    .features-grid { grid-template-columns: 1fr; margin: 1rem; }
    .home-hero { padding: 2rem 1.2rem 1.5rem; }
    .hero-stats { gap: 1.5rem; }
    .dash-wrap { padding: 0.8rem; }
    .shm-grid { grid-template-columns: repeat(2, 1fr); }
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TICKERS
# ─────────────────────────────────────────────
TICKERS = {
    "nifty50":      ("^NSEI",     "Nifty 50",       "india"),
    "sensex":       ("^BSESN",    "Sensex",          "india"),
    "india_vix":    ("^INDIAVIX", "India VIX",       "india"),
    "nifty_bank":   ("^NSEBANK",  "Nifty Bank",      "india"),
    "nifty_it":     ("^CNXIT",    "Nifty IT",        "india"),
    "nifty_midcap": ("^NSMIDCP",  "Midcap 100",      "india"),
    "nifty_small":  ("^CNXSC",    "Smallcap 100",    "india"),
    "sp500":        ("^GSPC",     "S&P 500",         "global"),
    "nasdaq":       ("^IXIC",     "Nasdaq",          "global"),
    "dow":          ("^DJI",      "Dow Jones",       "global"),
    "vix":          ("^VIX",      "CBOE VIX",        "global"),
    "dxy":          ("DX-Y.NYB",  "DXY Index",       "forex"),
    "usdinr":       ("USDINR=X",  "USD/INR",         "forex"),
    "eurusd":       ("EURUSD=X",  "EUR/USD",         "forex"),
    "gbpusd":       ("GBPUSD=X",  "GBP/USD",         "forex"),
    "gold":         ("GC=F",      "Gold",            "commodity"),
    "silver":       ("SI=F",      "Silver",          "commodity"),
    "crude_wti":    ("CL=F",      "Crude WTI",       "commodity"),
    "crude_brent":  ("BZ=F",      "Brent",           "commodity"),
    "us10y":        ("^TNX",      "US 10Y",          "rates"),
    "us3m":         ("^IRX",      "US 3M",           "rates"),
}

SECTORS = {
    "IT":      "^CNXIT",
    "Bank":    "^NSEBANK",
    "FMCG":    "^CNXFMCG",
    "Pharma":  "^CNXPHARMA",
    "Auto":    "^CNXAUTO",
    "Energy":  "^CNXENERGY",
    "Metal":   "^CNXMETAL",
    "Realty":  "^CNXREALTY",
}

# ─────────────────────────────────────────────
# DATA FETCHING
# ─────────────────────────────────────────────
def _flatten(df):
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
    return df

@st.cache_data(ttl=300)
def fetch_quote(symbol):
    try:
        df = _flatten(yf.download(symbol, period="5d", interval="1d",
                                   progress=False, auto_adjust=True))
        if df.empty or 'Close' not in df.columns: return None
        close = float(df['Close'].iloc[-1])
        prev  = float(df['Close'].iloc[-2]) if len(df) >= 2 else close
        return {
            "price": close, "prev": prev,
            "change": close - prev,
            "pct": ((close - prev) / prev * 100) if prev else 0,
            "high5d": float(df['High'].max()) if 'High' in df.columns else close,
            "low5d":  float(df['Low'].min())  if 'Low'  in df.columns else close,
        }
    except Exception:
        return None

@st.cache_data(ttl=600)
def fetch_52w(symbol):
    try:
        df = _flatten(yf.download(symbol, period="1y", interval="1d",
                                   progress=False, auto_adjust=True))
        if df.empty: return None, None
        return float(df['High'].max()), float(df['Low'].min())
    except Exception:
        return None, None

@st.cache_data(ttl=300)
def fetch_history(symbol, period="6mo"):
    """
    Fetch daily OHLCV. Drop weekends/holidays that yfinance sometimes
    returns as NaN rows, forward-fill any remaining gaps, then return
    a clean integer-indexed dataframe with a 'Date' column for labels.
    This eliminates the blank-space gaps that appear with type='date'.
    """
    try:
        df = _flatten(yf.download(symbol, period=period, interval="1d",
                                   progress=False, auto_adjust=True))
        if df.empty:
            return None
        # Drop rows where Close is NaN (non-trading days yfinance sometimes includes)
        df = df[df['Close'].notna()].copy()
        if df.empty:
            return None
        # Forward-fill any remaining NaNs in OHLCV (rare partial rows)
        df = df.ffill()
        # Store the actual dates as a column before resetting index
        df['Date'] = df.index
        df = df.reset_index(drop=True)
        return df
    except Exception:
        return None

@st.cache_data(ttl=300)
def fetch_all():
    return {k: fetch_quote(v[0]) for k, v in TICKERS.items()}

@st.cache_data(ttl=300)
def fetch_sectors():
    return {k: fetch_quote(v) for k, v in SECTORS.items()}

@st.cache_data(ttl=600)
def fetch_correlation():
    syms = {
        "Nifty":   "^NSEI",
        "Gold":    "GC=F",
        "Crude":   "CL=F",
        "USD/INR": "USDINR=X",
        "S&P 500": "^GSPC",
        "DXY":     "DX-Y.NYB",
    }
    closes = {}
    for name, sym in syms.items():
        df = _flatten(yf.download(sym, period="3mo", interval="1d",
                                   progress=False, auto_adjust=True))
        if not df.empty and 'Close' in df.columns:
            closes[name] = df['Close'].pct_change().dropna()
    if len(closes) < 2: return None
    return pd.DataFrame(closes).dropna().corr()

@st.cache_data(ttl=1800)
def fetch_fii_dii():
    try:
        from nselib import cash_market
        return cash_market.nsdl_fpi_latest_investment_activity()
    except Exception:
        return None

# ─────────────────────────────────────────────
# FORMATTERS
# ─────────────────────────────────────────────
def fp(val, dec=2):
    if val is None: return "—"
    if val >= 100000: return f"{val:,.0f}"
    if val >= 10000:  return f"{val:,.0f}"
    if val >= 100:    return f"{val:,.2f}"
    return f"{val:.{dec}f}"

def fc(chg, pct):
    if chg is None: return "—", "neu"
    sign = "▲" if chg >= 0 else "▼"
    return f"{sign} {abs(chg):.2f}  ({abs(pct):.2f}%)", "pos" if chg >= 0 else "neg"

# ─────────────────────────────────────────────
# METRIC CARD
# ─────────────────────────────────────────────
def metric_card(label, q, prefix="", suffix="", dec=2, show52=False, sym=None):
    if q and q.get('price') is not None:
        price = f"{prefix}{fp(q['price'], dec)}{suffix}"
        chg_str, cls = fc(q['change'], q['pct'])
        chg_html = f'<div class="mc-{cls}">{chg_str}</div>'
        bar52 = ""
        if show52 and sym:
            h52, l52 = fetch_52w(sym)
            if h52 and l52 and h52 > l52:
                pct52 = max(2, min(98, int((q['price'] - l52) / (h52 - l52) * 100)))
                bar52 = (
                    f'<div class="mc-52lbl">52W RANGE</div>'
                    f'<div class="mc-bar-outer">'
                    f'<div class="mc-bar-fill" style="width:{pct52}%"></div>'
                    f'</div>'
                    f'<div class="mc-range">'
                    f'<span>{prefix}{fp(l52, dec)}</span>'
                    f'<span>{prefix}{fp(h52, dec)}</span>'
                    f'</div>'
                )
    else:
        price = "—"
        chg_html = '<div class="mc-neu">—</div>'
        bar52 = ""

    html = (
        f'<div class="mc">'
        f'<div class="mc-lbl">{label}</div>'
        f'<div class="mc-val">{price}</div>'
        f'{chg_html}'
        f'{bar52}'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CHARTS — properly tuned Plotly
# ─────────────────────────────────────────────
BASE_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    margin=dict(l=8, r=8, t=36, b=8),
    showlegend=False,
    hovermode='x unified',
    hoverlabel=dict(
        bgcolor='#1a1a28',
        bordercolor='rgba(201,169,110,0.35)',
        font=dict(family='DM Mono', size=11, color='#e8e4dc'),
    ),
    xaxis=dict(
        showgrid=False,
        zeroline=False,
        color='#555',
        tickfont=dict(family='DM Mono', size=9, color='#555'),
        linecolor='rgba(255,255,255,0.06)',
        showspikes=True,
        spikecolor='rgba(201,169,110,0.4)',
        spikethickness=1,
        spikedash='dot',
        rangeslider=dict(visible=False),
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor='rgba(255,255,255,0.04)',
        zeroline=False,
        color='#555',
        tickfont=dict(family='DM Mono', size=9, color='#555'),
        side='right',
    ),
    font=dict(family='DM Mono', color='#666', size=10),
)

def make_chart(df, title, color="#c9a96e", height=420, show_volume=True, ctype="candle"):
    """
    Render a clean OHLCV chart with NO weekend/holiday gaps.

    Key technique: use integer positions (0,1,2…N) on the x-axis and map
    them to date labels. This is the only reliable way to prevent Plotly
    from rendering blank space for non-trading days when using type='date'.
    """
    if df is None or df.empty:
        return None
    try:
        has_ohlc = all(c in df.columns for c in ['Open','High','Low','Close'])
        has_vol  = show_volume and 'Volume' in df.columns and has_ohlc

        rows  = 2 if has_vol else 1
        row_h = [0.78, 0.22] if rows == 2 else [1.0]

        fig = make_subplots(
            rows=rows, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.015,
            row_heights=row_h,
        )

        # ── Integer x positions ──────────────────
        x_int = list(range(len(df)))

        # ── Date column (from fetch_history) ─────
        if 'Date' in df.columns:
            dates = pd.to_datetime(df['Date'])
        else:
            dates = pd.to_datetime(df.index)

        # ── Build clean x-axis tick positions & labels ──
        # ~6-8 ticks spread evenly across the data range
        n    = len(df)
        step = max(1, n // 7)
        tick_positions = list(range(0, n, step))
        if (n - 1) not in tick_positions:
            tick_positions.append(n - 1)
        tick_labels = [dates.iloc[i].strftime("%d %b '%y") for i in tick_positions]

        # ── CANDLESTICK ──────────────────────────
        if ctype == "candle" and has_ohlc:
            fig.add_trace(go.Candlestick(
                x=x_int,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name=title,
                increasing=dict(
                    line=dict(color='#4ab87a', width=0.8),
                    fillcolor='#4ab87a',
                ),
                decreasing=dict(
                    line=dict(color='#e05c6c', width=0.8),
                    fillcolor='#e05c6c',
                ),
                whiskerwidth=0,
                showlegend=False,
            ), row=1, col=1)
            # Remove the default range slider Candlestick adds
            fig.update_layout(xaxis_rangeslider_visible=False)

        # ── LINE ─────────────────────────────────
        else:
            c_col = 'Close' if 'Close' in df.columns else df.columns[0]
            y_vals = df[c_col].values

            # Subtle gradient fill: two overlapping fills for depth
            r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)

            fig.add_trace(go.Scatter(
                x=x_int,
                y=y_vals,
                mode='lines',
                name=title,
                line=dict(color=color, width=2.0),
                fill='tozeroy',
                fillcolor=f'rgba({r},{g},{b},0.07)',
                hovertemplate='%{customdata}<br><b>%{y:,.2f}</b><extra></extra>',
                customdata=[d.strftime("%d %b %Y") for d in dates],
            ), row=1, col=1)

        # ── VOLUME BARS ──────────────────────────
        if has_vol:
            c_col = 'Close' if 'Close' in df.columns else df.columns[0]
            o_col = 'Open'  if 'Open'  in df.columns else c_col
            vol_colors = [
                '#3a9660' if float(df[c_col].iloc[i]) >= float(df[o_col].iloc[i])
                else '#b04050'
                for i in range(len(df))
            ]
            fig.add_trace(go.Bar(
                x=x_int,
                y=df['Volume'],
                marker_color=vol_colors,
                marker_line_width=0,
                opacity=0.55,
                name='Volume',
                showlegend=False,
                hovertemplate='Vol: %{y:,.0f}<extra></extra>',
            ), row=2, col=1)
            fig.update_yaxes(
                row=2, col=1,
                showgrid=False,
                tickfont=dict(family='DM Mono', size=7, color='#3a3a50'),
                showticklabels=False,
                side='right',
            )

        # ── LAYOUT ───────────────────────────────
        layout = {**BASE_LAYOUT}
        layout['height']  = height
        layout['title']   = dict(
            text=f'<b>{title}</b>',
            font=dict(family='DM Mono', size=11, color='#666'),
            x=0.01, y=0.985,
            xanchor='left', yanchor='top',
        )
        fig.update_layout(**layout)

        # Apply integer x-axis with date labels to ALL x-axes
        x_axis_cfg = dict(
            tickmode='array',
            tickvals=tick_positions,
            ticktext=tick_labels,
            tickfont=dict(family='DM Mono', size=9, color='#555'),
            showgrid=False,
            zeroline=False,
            linecolor='rgba(255,255,255,0.05)',
            showspikes=True,
            spikecolor='rgba(201,169,110,0.35)',
            spikethickness=1,
            spikedash='dot',
            rangeslider=dict(visible=False),
            type='linear',   # integer positions — NO gaps
        )
        fig.update_xaxes(**x_axis_cfg)
        fig.update_yaxes(
            row=1, col=1,
            side='right',
            zeroline=False,
            showgrid=True,
            gridcolor='rgba(255,255,255,0.035)',
            tickfont=dict(family='DM Mono', size=9, color='#555'),
        )

        return fig
    except Exception:
        return None


def make_corr_heatmap(corr_df):
    if corr_df is None:
        return None
    try:
        lbls = list(corr_df.columns)
        z    = corr_df.values.tolist()
        txt  = [[f"{corr_df.values[i][j]:.2f}" for j in range(len(lbls))] for i in range(len(lbls))]

        fig = go.Figure(go.Heatmap(
            z=z, x=lbls, y=lbls,
            text=txt,
            texttemplate="%{text}",
            textfont=dict(family='DM Mono', size=11, color='#e8e4dc'),
            colorscale=[
                [0.0,  '#c0374a'],
                [0.25, '#7a2030'],
                [0.5,  '#1a1a28'],
                [0.75, '#1e4030'],
                [1.0,  '#2ea86a'],
            ],
            zmin=-1, zmax=1,
            showscale=True,
            colorbar=dict(
                tickfont=dict(family='DM Mono', size=9, color='#888'),
                thickness=8,
                len=0.8,
                tickvals=[-1, -0.5, 0, 0.5, 1],
                ticktext=['-1.0', '-0.5', '0', '+0.5', '+1.0'],
            ),
            xgap=2, ygap=2,
        ))

        fig.update_layout(
            **{**BASE_LAYOUT,
               'height': 340,
               'title': dict(
                   text='3-Month Return Correlation',
                   font=dict(family='DM Mono', size=11, color='#888'),
                   x=0.01, xanchor='left',
               ),
               'xaxis': {**BASE_LAYOUT['xaxis'],
                         'tickfont': dict(family='DM Mono', size=10, color='#b0ac9f'),
                         'showspikes': False},
               'yaxis': {**BASE_LAYOUT['yaxis'],
                         'tickfont': dict(family='DM Mono', size=10, color='#b0ac9f'),
                         'showgrid': False, 'side': 'left'},
               'margin': dict(l=60, r=80, t=40, b=40),
            }
        )
        return fig
    except Exception:
        return None


# ─────────────────────────────────────────────
# SECTOR HEATMAP (colour-coded grid, not bar chart)
# ─────────────────────────────────────────────
def sector_heatmap_html(sq):
    """Returns an HTML string for a colour-coded sector heatmap grid."""
    cells = []
    for name, q in sq.items():
        if q and q.get('pct') is not None:
            pct = q['pct']
            price = fp(q['price'])
            # Map pct → colour:  deep red -3%, neutral #1a1a28, deep green +3%
            intensity = min(abs(pct) / 3.0, 1.0)
            if pct > 0:
                r = int(26  + (46  - 26)  * intensity)
                g = int(26  + (184 - 26)  * intensity)
                b = int(40  + (122 - 40)  * intensity)
            else:
                r = int(26  + (224 - 26)  * intensity)
                g = int(26  + (92  - 26)  * intensity)
                b = int(40  + (108 - 40)  * intensity)
            bg = f"rgb({r},{g},{b})"
            sign = "+" if pct >= 0 else ""
            cells.append(
                f'<div class="shm-cell" style="background:{bg}">'
                f'<div class="shm-name">{name}</div>'
                f'<div class="shm-pct">{sign}{pct:.2f}%</div>'
                f'<div class="shm-price">{price}</div>'
                f'</div>'
            )
        else:
            cells.append(
                f'<div class="shm-cell" style="background:#111118">'
                f'<div class="shm-name">{name}</div>'
                f'<div class="shm-pct" style="color:#444">—</div>'
                f'</div>'
            )
    return f'<div class="shm-grid">{"".join(cells)}</div>'


# ─────────────────────────────────────────────
# SECTOR ROTATION CHART (momentum vs change)
# ─────────────────────────────────────────────
@st.cache_data(ttl=600)
def fetch_sector_momentum():
    """Fetch 1-month return for each sector for rotation analysis."""
    results = {}
    for name, sym in SECTORS.items():
        df = _flatten(yf.download(sym, period="2mo", interval="1d",
                                   progress=False, auto_adjust=True))
        if df.empty or 'Close' not in df.columns:
            continue
        ret_1m  = float((df['Close'].iloc[-1] / df['Close'].iloc[-22] - 1) * 100) if len(df) >= 22 else None
        ret_1w  = float((df['Close'].iloc[-1] / df['Close'].iloc[-6]  - 1) * 100) if len(df) >= 6  else None
        if ret_1m is not None and ret_1w is not None:
            results[name] = {"1m": ret_1m, "1w": ret_1w}
    return results


def make_rotation_chart(momentum):
    """Scatter: x=1M return, y=1W return. Four-quadrant sector rotation."""
    if not momentum:
        return None
    names = list(momentum.keys())
    x1m   = [momentum[n]["1m"] for n in names]
    x1w   = [momentum[n]["1w"] for n in names]
    colors= ['#4ab87a' if momentum[n]["1w"] >= 0 else '#e05c6c' for n in names]

    fig = go.Figure()

    # Quadrant shading
    fig.add_hrect(y0=0, y1=max(x1w+[1])*1.4, fillcolor='rgba(74,184,122,0.03)', line_width=0)
    fig.add_hrect(y0=min(x1w+[-1])*1.4, y1=0, fillcolor='rgba(224,92,108,0.03)', line_width=0)
    fig.add_vline(x=0, line_width=1, line_dash='dot', line_color='rgba(255,255,255,0.1)')
    fig.add_hline(y=0, line_width=1, line_dash='dot', line_color='rgba(255,255,255,0.1)')

    fig.add_trace(go.Scatter(
        x=x1m, y=x1w,
        mode='markers+text',
        text=names,
        textposition='top center',
        textfont=dict(family='DM Mono', size=10, color='#b0ac9f'),
        marker=dict(
            color=colors,
            size=14,
            line=dict(color='rgba(255,255,255,0.15)', width=1),
        ),
        hovertemplate='<b>%{text}</b><br>1M: %{x:.2f}%<br>1W: %{y:.2f}%<extra></extra>',
    ))

    fig.update_layout(
        **{**BASE_LAYOUT,
           'height': 360,
           'title': dict(
               text='Sector Rotation Map — 1W vs 1M Return',
               font=dict(family='DM Mono', size=11, color='#888'),
               x=0.01, xanchor='left',
           ),
           'xaxis': {**BASE_LAYOUT['xaxis'],
                     'title': dict(text='1-Month Return %', font=dict(family='DM Mono', size=9, color='#555')),
                     'ticksuffix': '%', 'showspikes': False},
           'yaxis': {**BASE_LAYOUT['yaxis'],
                     'title': dict(text='1-Week Return %', font=dict(family='DM Mono', size=9, color='#555')),
                     'ticksuffix': '%', 'side': 'left'},
           'margin': dict(l=60, r=20, t=40, b=40),
        }
    )

    # Quadrant labels
    for txt, x, y, anchor in [
        ("LEADING",    max(x1m+[1])*0.85,  max(x1w+[1])*0.85, "right"),
        ("IMPROVING",  min(x1m+[-1])*0.85, max(x1w+[1])*0.85, "left"),
        ("LAGGING",    min(x1m+[-1])*0.85, min(x1w+[-1])*0.85,"left"),
        ("WEAKENING",  max(x1m+[1])*0.85,  min(x1w+[-1])*0.85,"right"),
    ]:
        fig.add_annotation(
            x=x, y=y, text=txt,
            showarrow=False,
            font=dict(family='DM Mono', size=8, color='rgba(255,255,255,0.12)'),
            xanchor=anchor,
        )
    return fig


# ─────────────────────────────────────────────
# FEAR & GREED
# ─────────────────────────────────────────────
def fear_greed(quotes):
    score = 50
    factors = []
    vix = quotes.get("india_vix")
    if vix and vix.get('price'):
        v = vix['price']
        vix_s = max(0, min(100, 100 - ((v - 10) / 20 * 100)))
        score += (vix_s - 50) * 0.35
        factors.append(f"India VIX {v:.1f} → {'elevated fear' if v > 18 else 'complacency' if v < 12 else 'neutral'}")
    nifty = quotes.get("nifty50")
    if nifty and nifty.get('pct') is not None:
        m = nifty['pct']
        score += min(max(m * 8, -20), 20) * 0.3
        factors.append(f"Nifty momentum {m:+.2f}%")
    gold = quotes.get("gold")
    crude = quotes.get("crude_wti")
    if gold and crude and gold.get('price') and crude.get('price') and crude['price'] > 0:
        ratio = gold['price'] / crude['price']
        r_s   = max(0, min(100, 100 - ((ratio - 12) / 15 * 100)))
        score += (r_s - 50) * 0.2
        factors.append(f"Gold/Crude ratio {ratio:.1f}")
    dxy = quotes.get("dxy")
    if dxy and dxy.get('pct') is not None:
        score += -(dxy['pct'] * 10) * 0.15
        factors.append(f"DXY {dxy['pct']:+.2f}%")
    score = int(max(0, min(100, score)))
    if score <= 25:   lbl, col = "Extreme Fear",  "#e05c6c"
    elif score <= 45: lbl, col = "Fear",          "#e08c4a"
    elif score <= 55: lbl, col = "Neutral",       "#c9a96e"
    elif score <= 75: lbl, col = "Greed",         "#8ab87a"
    else:             lbl, col = "Extreme Greed", "#4ab87a"
    return score, lbl, col, factors


# ─────────────────────────────────────────────
# SIGNALS
# ─────────────────────────────────────────────
def signals(quotes):
    out = []
    n   = quotes.get("nifty50")
    vix = quotes.get("india_vix")
    dxy = quotes.get("dxy")
    inr = quotes.get("usdinr")
    crd = quotes.get("crude_wti")
    y10 = quotes.get("us10y")
    sp  = quotes.get("sp500")

    if n:
        if n['pct'] > 0.8:
            out.append(("bull", f"Nifty 50 ▲ {n['pct']:.2f}% — broad risk appetite. Momentum positive."))
        elif n['pct'] < -0.8:
            out.append(("bear", f"Nifty 50 ▼ {abs(n['pct']):.2f}% — selling pressure. Watch key supports."))
        else:
            out.append(("neu", f"Nifty 50 {n['pct']:+.2f}% — consolidation range. No strong directional signal."))
    if vix and vix.get('price'):
        v = vix['price']
        if v > 22:   out.append(("bear", f"India VIX {v:.1f} — elevated. Market pricing significant uncertainty."))
        elif v < 12: out.append(("bull", f"India VIX {v:.1f} — suppressed. Low volatility, watch for complacency."))
    if dxy and abs(dxy.get('pct', 0)) > 0.3:
        if dxy['pct'] > 0: out.append(("bear", f"DXY ▲ {dxy['pct']:.2f}% — dollar strength pressures EM and INR."))
        else:              out.append(("bull", f"DXY ▼ {abs(dxy['pct']):.2f}% — dollar weakness supports FII inflows."))
    if inr and inr.get('price'):
        r = inr['price']
        if r > 84.5: out.append(("bear", f"USD/INR {r:.2f} — rupee under pressure. Watch RBI intervention."))
        elif r < 83: out.append(("bull", f"USD/INR {r:.2f} — rupee firm. Positive for imports and inflation outlook."))
    if crd and crd.get('pct') is not None:
        if crd['pct'] > 2:   out.append(("bear", f"Crude ▲ {crd['pct']:.2f}% — adds to India's import bill. CAD pressure."))
        elif crd['pct'] < -2: out.append(("bull", f"Crude ▼ {abs(crd['pct']):.2f}% — relief for CAD, OMC margins improve."))
    if y10 and y10.get('price'):
        y = y10['price']
        if y > 4.6: out.append(("bear", f"US 10Y {y:.2f}% — high rates raise the floor for EM risk-return."))
        elif y < 4: out.append(("bull", f"US 10Y {y:.2f}% — falling yields reduce FII outflow pressure from EM."))
    if sp and n:
        if sp['pct'] < -1 and n['pct'] > 0.5:
            out.append(("bull", f"Decoupling signal — Nifty {n['pct']:+.2f}% vs S&P {sp['pct']:.2f}%. India resilience."))
        elif sp['pct'] > 1 and n['pct'] < -0.5:
            out.append(("bear", f"India underperforming — Nifty {n['pct']:.2f}% vs S&P {sp['pct']:+.2f}%."))
    if not out:
        out.append(("neu", "Macro conditions quiet. No strong directional signals detected today."))
    return out


# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
if 'page' not in st.session_state:
    st.session_state.page = 'home'

# ─────────────────────────────────────────────
# TICKER TAPE (animated scroll)
# ─────────────────────────────────────────────
@st.cache_data(ttl=300)
def tape_quotes():
    syms = [
        ("^NSEI",     "Nifty 50"),
        ("^BSESN",    "Sensex"),
        ("^GSPC",     "S&P 500"),
        ("^IXIC",     "Nasdaq"),
        ("GC=F",      "Gold"),
        ("CL=F",      "WTI"),
        ("USDINR=X",  "USD/INR"),
        ("^INDIAVIX", "India VIX"),
        ("DX-Y.NYB",  "DXY"),
        ("^TNX",      "US 10Y"),
        ("^NSEBANK",  "Bank Nifty"),
        ("SI=F",      "Silver"),
    ]
    out = []
    for sym, name in syms:
        q = fetch_quote(sym)
        if q:
            out.append((name, q['price'], q['pct']))
    return out


tape = tape_quotes()

# Build items twice for seamless loop
def _tape_item(name, price, pct):
    cls  = "tape-pos" if pct >= 0 else "tape-neg"
    sign = "▲" if pct >= 0 else "▼"
    return (
        f'<span class="tape-item">'
        f'<span class="tape-name">{name}</span>'
        f'<span class="tape-price">{fp(price)}</span>'
        f'<span class="{cls}">{sign}{abs(pct):.2f}%</span>'
        f'</span>'
    )

items_html = "".join(_tape_item(*t) for t in tape)
# Duplicate for seamless CSS scroll
tape_html = (
    f'<div class="tape-outer">'
    f'<div class="tape-inner">'
    f'{items_html}{items_html}'
    f'</div>'
    f'</div>'
)
st.markdown(tape_html, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# HOME PAGE
# ─────────────────────────────────────────────
if st.session_state.page == 'home':
    now_str = datetime.now().strftime("%A, %d %b %Y")
    st.markdown(f"""
    <div class="home-hero">
        <div class="hero-eyebrow">
            <span class="hero-dot"></span>
            Day 08 · 30 Days of AI Finance &nbsp;·&nbsp; {now_str}
        </div>
        <div class="hero-title">Terminal<span>One</span></div>
        <div class="hero-sub">
            A Bloomberg-lite macro intelligence terminal for India and global markets.
            Live prices, signals, correlation analysis, sector rotation maps,
            and a Fear &amp; Greed index — all free, no API key.
        </div>
        <div class="hero-stats">
            <div><div class="hero-stat-val">20+</div><div class="hero-stat-lbl">Live Instruments</div></div>
            <div><div class="hero-stat-val">8</div><div class="hero-stat-lbl">Nifty Sectors</div></div>
            <div><div class="hero-stat-val">5 min</div><div class="hero-stat-lbl">Refresh Cycle</div></div>
            <div><div class="hero-stat-val">Free</div><div class="hero-stat-lbl">No API Key</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    cta_l, cta_m, cta_r = st.columns([1, 2, 1])
    with cta_m:
        st.markdown("<div style='height:0.3rem'></div>", unsafe_allow_html=True)
        if st.button("→  Open TerminalOne — Live Markets", use_container_width=True):
            st.session_state.page = 'terminal'
            st.rerun()
        st.markdown(
            "<div style='font-family:\"DM Mono\",monospace;font-size:0.6rem;"
            "color:#444;text-align:center;margin-top:0.4rem'>"
            "No login · No API key · Refreshes every 5 min</div>",
            unsafe_allow_html=True
        )

    st.markdown("""
    <div class="features-grid">
        <div class="feat-card">
            <div class="feat-icon">📊</div>
            <div class="feat-title">Live Market Dashboard</div>
            <div class="feat-desc">Real-time prices for Nifty 50, Sensex, Bank Nifty, global indices, forex pairs, and commodities — with 52-week range bars and daily change.</div>
        </div>
        <div class="feat-card">
            <div class="feat-icon">📈</div>
            <div class="feat-title">Interactive Charts</div>
            <div class="feat-desc">Clean candlestick and line charts with volume for Nifty, USD/INR, Gold, Crude, and S&P 500. Y-axis on right, proper date axis, no clutter.</div>
        </div>
        <div class="feat-card">
            <div class="feat-icon">🧠</div>
            <div class="feat-title">Fear & Greed Index</div>
            <div class="feat-desc">Composite India market sentiment score built from VIX, Nifty momentum, Gold/Crude ratio, and DXY — updated every 5 minutes.</div>
        </div>
        <div class="feat-card">
            <div class="feat-icon">⚡</div>
            <div class="feat-title">Live Macro Signals</div>
            <div class="feat-desc">Auto-generated signals from live data — DXY pressure on INR, crude impact on CAD, US yield effects on FII flows, India-US decoupling detection.</div>
        </div>
        <div class="feat-card">
            <div class="feat-icon">🔄</div>
            <div class="feat-title">Sector Rotation Map</div>
            <div class="feat-desc">Four-quadrant scatter: 1-week vs 1-month returns for all 8 Nifty sectors. Instantly see which sectors are Leading, Improving, Weakening, or Lagging.</div>
        </div>
        <div class="feat-card">
            <div class="feat-icon">🔗</div>
            <div class="feat-title">Correlation Matrix</div>
            <div class="feat-desc">3-month return correlation across Nifty, Gold, Crude, DXY, USD/INR, and S&P 500. Understand cross-asset relationships at a glance.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="sources-bar">
        <div class="src-item">Yahoo Finance (yfinance)</div>
        <div class="src-item">NSE India (nselib)</div>
        <div class="src-item">No API key required</div>
        <div class="src-item">Refreshes every 5 minutes</div>
        <div class="src-item">Not investment advice</div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# TERMINAL PAGE
# ─────────────────────────────────────────────
else:
    # ── TOP BAR ──────────────────────────────
    now_str = datetime.now().strftime("%a %d %b %Y  %H:%M IST")

    # Use a single HTML block for logo + live indicator, then Streamlit controls in columns
    tb_left, tb_mid, tb_period, tb_ctype, tb_ref, tb_home = st.columns([2.2, 3, 1.2, 1.2, 0.9, 0.9])

    with tb_left:
        st.markdown(
            f'<div style="padding:.6rem 0 .4rem 1.5rem;display:flex;align-items:center;gap:0.8rem">'
            f'<span style="font-family:\'Playfair Display\',serif;font-size:1.15rem;font-weight:700;color:#c9a96e">TerminalOne</span>'
            f'</div>',
            unsafe_allow_html=True
        )
    with tb_mid:
        st.markdown(
            f'<div style="padding:.65rem 0;font-family:\'DM Mono\',monospace;font-size:.6rem;color:#555">'
            f'<span class="live-dot" style="display:inline-block;width:6px;height:6px;background:#4ab87a;'
            f'border-radius:50%;margin-right:5px;animation:blink 2s ease-in-out infinite"></span>'
            f'LIVE &nbsp;·&nbsp; {now_str}'
            f'</div>',
            unsafe_allow_html=True
        )
    with tb_period:
        period = st.selectbox("Period", ["1mo","3mo","6mo","1y"], index=2,
                               label_visibility="collapsed")
    with tb_ctype:
        ctype = st.selectbox("Chart", ["Candle","Line"], index=0,
                              label_visibility="collapsed")
    with tb_ref:
        if st.button("⟳ Refresh", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    with tb_home:
        if st.button("⌂ Home", use_container_width=True):
            st.session_state.page = 'home'
            st.rerun()

    st.markdown('<div style="height:2px;background:rgba(255,255,255,0.04)"></div>', unsafe_allow_html=True)

    # ── FETCH DATA ───────────────────────────
    with st.spinner(""):
        quotes = fetch_all()
        sq     = fetch_sectors()

    # ── TABS ─────────────────────────────────
    t1, t2, t3, t4 = st.tabs([
        "📊  Markets",
        "📈  Charts",
        "🔄  Sectors & Rotation",
        "⚡  Signals"
    ])

    # ════════════════════════════════════════
    # TAB 1 — MARKETS
    # ════════════════════════════════════════
    with t1:
        st.markdown('<div class="dash-wrap">', unsafe_allow_html=True)

        # India
        st.markdown('<div class="sec-hdr">🇮🇳 India Markets</div>', unsafe_allow_html=True)
        c = st.columns(4)
        for i, (lbl, key, sym) in enumerate([
            ("Nifty 50",    "nifty50",    "^NSEI"),
            ("Sensex",      "sensex",     "^BSESN"),
            ("Nifty Bank",  "nifty_bank", "^NSEBANK"),
            ("India VIX",   "india_vix",  "^INDIAVIX"),
        ]):
            with c[i]:
                metric_card(lbl, quotes.get(key), show52=True, sym=sym,
                            dec=1 if "VIX" in lbl else 2)

        c2 = st.columns(4)
        for i, (lbl, key, sym) in enumerate([
            ("Nifty IT",     "nifty_it",     "^CNXIT"),
            ("Midcap 100",   "nifty_midcap", "^NSMIDCP"),
            ("Smallcap 100", "nifty_small",  "^CNXSC"),
        ]):
            with c2[i]:
                metric_card(lbl, quotes.get(key), show52=True, sym=sym)

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        # Forex
        st.markdown('<div class="sec-hdr">💱 Forex</div>', unsafe_allow_html=True)
        c3 = st.columns(4)
        for i, (lbl, key, sym, dec) in enumerate([
            ("USD / INR", "usdinr", "USDINR=X",  2),
            ("EUR / USD", "eurusd", "EURUSD=X",  4),
            ("GBP / USD", "gbpusd", "GBPUSD=X",  4),
            ("DXY Index", "dxy",    "DX-Y.NYB",  2),
        ]):
            with c3[i]:
                metric_card(lbl, quotes.get(key), show52=True, sym=sym, dec=dec)

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        # Commodities
        st.markdown('<div class="sec-hdr">🛢️ Commodities</div>', unsafe_allow_html=True)
        c4 = st.columns(4)
        for i, (lbl, key, sym, pfx) in enumerate([
            ("Gold $/oz",  "gold",        "GC=F", "$"),
            ("Crude WTI",  "crude_wti",   "CL=F", "$"),
            ("Brent",      "crude_brent", "BZ=F", "$"),
            ("Silver",     "silver",      "SI=F", "$"),
        ]):
            with c4[i]:
                metric_card(lbl, quotes.get(key), prefix=pfx, show52=True, sym=sym)

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        # Global
        st.markdown('<div class="sec-hdr">🌍 Global Indices & Rates</div>', unsafe_allow_html=True)
        c5 = st.columns(5)
        for i, (lbl, key, sym, s52, sfx) in enumerate([
            ("S&P 500",  "sp500",  "^GSPC", True,  ""),
            ("Nasdaq",   "nasdaq", "^IXIC", True,  ""),
            ("Dow Jones","dow",    "^DJI",  False, ""),
            ("CBOE VIX", "vix",    "^VIX",  False, ""),
            ("US 10Y %", "us10y",  "^TNX",  False, "%"),
        ]):
            with c5[i]:
                metric_card(lbl, quotes.get(key), suffix=sfx, show52=s52, sym=sym,
                            dec=1 if "VIX" in lbl else 2)

        st.markdown('</div>', unsafe_allow_html=True)

    # ════════════════════════════════════════
    # TAB 2 — CHARTS
    # ════════════════════════════════════════
    with t2:
        st.markdown('<div class="dash-wrap">', unsafe_allow_html=True)

        chart_tabs = st.tabs(["Nifty 50", "USD/INR", "Gold", "Crude WTI", "S&P 500"])
        chart_cfgs = [
            ("^NSEI",    "Nifty 50",   "#c9a96e", True),
            ("USDINR=X", "USD / INR",  "#4ab87a", False),
            ("GC=F",     "Gold",       "#c9a96e", True),
            ("CL=F",     "Crude WTI",  "#e05c6c", True),
            ("^GSPC",    "S&P 500",    "#6aaad8", True),
        ]
        ctype_lower = ctype.lower()

        for i, (sym, ttl, col, vol) in enumerate(chart_cfgs):
            with chart_tabs[i]:
                df = fetch_history(sym, period=period)
                fig = make_chart(df, ttl, color=col, height=460,
                                 show_volume=vol, ctype=ctype_lower)
                if fig:
                    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
                    st.plotly_chart(fig, use_container_width=True,
                                    config={"displayModeBar": True,
                                            "modeBarButtonsToRemove": ["select2d","lasso2d","toImage"],
                                            "displaylogo": False})
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.info(f"No data available for {ttl}.")

        st.markdown('</div>', unsafe_allow_html=True)

    # ════════════════════════════════════════
    # TAB 3 — SECTORS & ROTATION
    # ════════════════════════════════════════
    with t3:
        st.markdown('<div class="dash-wrap">', unsafe_allow_html=True)

        # Heatmap grid
        st.markdown('<div class="sec-hdr">🏭 Sector Heatmap — Today\'s Performance</div>', unsafe_allow_html=True)
        st.markdown(sector_heatmap_html(sq), unsafe_allow_html=True)

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        # Rotation scatter
        st.markdown('<div class="sec-hdr">🔄 Sector Rotation Map</div>', unsafe_allow_html=True)
        with st.spinner("Loading sector momentum…"):
            momentum = fetch_sector_momentum()

        fig_rot = make_rotation_chart(momentum)
        if fig_rot:
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            st.plotly_chart(fig_rot, use_container_width=True,
                            config={"displayModeBar": False})
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown(
                '<div style="font-family:\'DM Mono\',monospace;font-size:0.58rem;color:#444;'
                'line-height:1.8;margin-top:0.5rem">'
                'LEADING: strong 1M + strong 1W &nbsp;·&nbsp; '
                'IMPROVING: weak 1M but recovering 1W &nbsp;·&nbsp; '
                'WEAKENING: strong 1M but fading 1W &nbsp;·&nbsp; '
                'LAGGING: weak across both timeframes'
                '</div>',
                unsafe_allow_html=True
            )
        else:
            st.info("Sector rotation data unavailable.")

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        # Correlation matrix
        st.markdown('<div class="sec-hdr">🔗 Asset Correlation Matrix</div>', unsafe_allow_html=True)
        with st.spinner("Computing 3-month correlations…"):
            corr = fetch_correlation()
        fig_c = make_corr_heatmap(corr)
        if fig_c:
            st.markdown('<div class="chart-card">', unsafe_allow_html=True)
            st.plotly_chart(fig_c, use_container_width=True,
                            config={"displayModeBar": False})
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown(
                '<div style="font-family:\'DM Mono\',monospace;font-size:0.58rem;color:#444;line-height:1.8;margin-top:.4rem">'
                '+1.0 = perfect positive correlation &nbsp;·&nbsp; '
                '-1.0 = perfect inverse &nbsp;·&nbsp; '
                'Gold vs DXY historically shows strong negative correlation &nbsp;·&nbsp; '
                'Based on 3-month daily returns'
                '</div>',
                unsafe_allow_html=True
            )
        else:
            st.info("Correlation data unavailable.")

        st.markdown('</div>', unsafe_allow_html=True)

    # ════════════════════════════════════════
    # TAB 4 — SIGNALS
    # ════════════════════════════════════════
    with t4:
        st.markdown('<div class="dash-wrap">', unsafe_allow_html=True)
        sig_col, fg_col = st.columns([3, 2])

        with sig_col:
            st.markdown('<div class="sec-hdr">⚡ Live Macro Signals</div>', unsafe_allow_html=True)
            for stype, stxt in signals(quotes):
                icon = {"bull": "▲", "bear": "▼", "neu": "●"}[stype]
                st.markdown(f'<div class="sig-{stype}">{icon} {stxt}</div>',
                            unsafe_allow_html=True)

            # Yield curve
            st.markdown('<div class="sec-hdr" style="margin-top:1.2rem">📈 US Yield Snapshot</div>',
                        unsafe_allow_html=True)
            y10 = quotes.get("us10y")
            y3m = quotes.get("us3m")
            yc  = {}
            if y3m and y3m.get('price'): yc["3M"]  = y3m['price']
            if y10 and y10.get('price'): yc["10Y"] = y10['price']
            if yc:
                fig_yc = go.Figure(go.Scatter(
                    x=list(yc.keys()),
                    y=list(yc.values()),
                    mode='lines+markers+text',
                    line=dict(color='#c9a96e', width=2, shape='spline'),
                    marker=dict(size=10, color='#c9a96e',
                                line=dict(color='#09090e', width=2)),
                    text=[f"{v:.2f}%" for v in yc.values()],
                    textposition='top center',
                    textfont=dict(family='DM Mono', size=11, color='#c9a96e'),
                ))
                fig_yc.update_layout(
                    **{**BASE_LAYOUT,
                       'height': 200,
                       'yaxis': {**BASE_LAYOUT['yaxis'],
                                 'ticksuffix': '%', 'side': 'right'},
                       'margin': dict(l=8, r=40, t=8, b=8),
                    }
                )
                st.markdown('<div class="chart-card">', unsafe_allow_html=True)
                st.plotly_chart(fig_yc, use_container_width=True,
                                config={"displayModeBar": False})
                st.markdown('</div>', unsafe_allow_html=True)

                if len(yc) == 2:
                    spread = yc.get("10Y", 0) - yc.get("3M", 0)
                    cls    = "bear" if spread < 0 else "bull"
                    icon   = "⚠" if spread < 0 else "✓"
                    note   = (
                        f"Inverted yield curve — 10Y–3M spread = {spread:.2f}%. Historically a recession signal."
                        if spread < 0 else
                        f"Normal yield curve — 10Y–3M spread = +{spread:.2f}%."
                    )
                    st.markdown(f'<div class="sig-{cls}">{icon} {note}</div>',
                                unsafe_allow_html=True)

        with fg_col:
            st.markdown('<div class="sec-hdr">🧠 Market Sentiment</div>', unsafe_allow_html=True)
            score, lbl, col, factors = fear_greed(quotes)
            st.markdown(f"""
            <div class="fg-card">
                <div style="font-family:'DM Mono',monospace;font-size:.56rem;color:#555;
                     letter-spacing:.1em;text-transform:uppercase;margin-bottom:.5rem">
                     India Market Sentiment</div>
                <div class="fg-score" style="color:{col}">{score}</div>
                <div class="fg-name" style="color:{col}">{lbl}</div>
                <div class="fg-bar-outer">
                    <div class="fg-needle" style="left:{score}%"></div>
                </div>
                <div class="fg-scale">
                    <span>Extreme<br>Fear</span>
                    <span>Neutral</span>
                    <span>Extreme<br>Greed</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown('<div style="height:.6rem"></div>', unsafe_allow_html=True)
            st.markdown('<div class="sec-hdr">Sentiment Factors</div>', unsafe_allow_html=True)
            for f in factors:
                st.markdown(
                    f'<div class="sig-neu" style="font-size:.65rem;margin-bottom:.3rem;padding:.5rem .8rem">· {f}</div>',
                    unsafe_allow_html=True
                )

            st.markdown('<div class="sec-hdr" style="margin-top:1rem">🏦 FII / DII Activity</div>',
                        unsafe_allow_html=True)
            fii = fetch_fii_dii()
            if fii is not None and not fii.empty:
                st.dataframe(fii.head(6), use_container_width=True, hide_index=True)
            else:
                st.markdown(
                    '<div class="sig-neu">ℹ NSE FII/DII data available after 6 PM IST on trading days.</div>',
                    unsafe_allow_html=True
                )

        st.markdown('</div>', unsafe_allow_html=True)

    # ── FOOTER ───────────────────────────────
    st.markdown("""
    <div style="font-family:'DM Mono',monospace;font-size:.54rem;color:#252530;
         text-align:center;padding:1.5rem 0 1rem;
         border-top:1px solid rgba(255,255,255,.03);
         margin-top:1rem;letter-spacing:.08em;text-transform:uppercase">
        TerminalOne &nbsp;·&nbsp; Day 08 · 30 Days of AI Finance &nbsp;·&nbsp;
        Data: Yahoo Finance + NSE India &nbsp;·&nbsp;
        Not investment advice
    </div>
    """, unsafe_allow_html=True)
