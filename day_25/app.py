import streamlit as st
import numpy as np
from scipy import stats
from scipy.stats import norm, gaussian_kde
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import time
import datetime

# ── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MonteDesk · Monte Carlo Engine",
    page_icon="🎲",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400;1,600&family=Syne:wght@400;600;700;800&family=DM+Mono:wght@400;500&display=swap');

:root { color-scheme: dark !important; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
[data-testid="stVerticalBlock"],
[data-testid="block-container"],
.main, .stApp {
    background-color: #09090e !important;
    color: #e8e8f0 !important;
}

[data-testid="stSidebar"],
[data-testid="stSidebar"] > div {
    background-color: #0d0d14 !important;
    border-right: 1px solid rgba(201,169,110,0.2) !important;
}

[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input {
    background-color: #1a1a28 !important;
    color: #e8e8f0 !important;
    border: 1px solid rgba(201,169,110,0.25) !important;
    font-family: 'DM Mono', monospace !important;
}

.stSelectbox [data-baseweb="select"],
[data-baseweb="popover"],
[data-baseweb="menu"],
[data-baseweb="list"] {
    background-color: #1a1a28 !important;
    color: #e8e8f0 !important;
}
[data-baseweb="option"] { background-color: #111118 !important; color: #e8e8f0 !important; }
[data-baseweb="option"]:hover { background-color: rgba(201,169,110,0.12) !important; }

.stTabs [data-baseweb="tab-list"] {
    background-color: #0d0d14 !important;
    border-bottom: 1px solid rgba(201,169,110,0.2) !important;
    gap: 0px;
    padding: 0 8px;
}
.stTabs [data-baseweb="tab"] {
    background-color: transparent !important;
    color: #6060a0 !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.05em !important;
    padding: 10px 20px !important;
    text-transform: uppercase !important;
}
.stTabs [aria-selected="true"] {
    color: #c9a96e !important;
    border-bottom: 2px solid #c9a96e !important;
    background-color: transparent !important;
}
.stTabs [data-baseweb="tab-panel"] { background-color: #09090e !important; padding-top: 24px !important; }

[data-testid="stMetricLabel"] { color: #9090a8 !important; font-family: 'Syne', sans-serif !important; font-size: 0.68rem !important; letter-spacing: 0.06em !important; }
[data-testid="stMetricValue"] { color: #e8e8f0 !important; font-family: 'DM Mono', monospace !important; }
[data-testid="stRadio"] label { color: #e8e8f0 !important; font-family: 'Syne', sans-serif !important; font-size: 0.85rem !important; }
[data-testid="stCheckbox"] label { color: #e8e8f0 !important; font-family: 'Syne', sans-serif !important; }
[data-testid="stSlider"] > div > div { background-color: rgba(201,169,110,0.25) !important; }

[data-testid="stButton"] button {
    background-color: #c9a96e !important;
    color: #09090e !important;
    border: none !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 0.04em !important;
}
[data-testid="stButton"] button:hover { background-color: #e0c47a !important; transform: translateY(-1px); }

h1, h2, h3, h4 { font-family: 'Playfair Display', serif !important; color: #c9a96e !important; }
p, li { font-family: 'Syne', sans-serif !important; color: #e8e8f0 !important; }

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 0 !important; padding-bottom: 2rem !important; max-width: 100% !important; }

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #09090e; }
::-webkit-scrollbar-thumb { background: rgba(201,169,110,0.3); border-radius: 2px; }

/* ── HERO ── */
.hero-wrap {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 60px 40px;
    position: relative;
    background: radial-gradient(ellipse 80% 60% at 50% 40%, rgba(201,169,110,0.06) 0%, transparent 70%);
}
.hero-nav {
    position: absolute;
    top: 0; left: 0; right: 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px 40px;
    border-bottom: 1px solid rgba(201,169,110,0.1);
}
.hero-nav-logo {
    font-family: 'Playfair Display', serif;
    font-size: 1.15rem;
    color: #c9a96e;
    font-weight: 600;
    letter-spacing: 0.02em;
}
.hero-nav-badge {
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    color: #4a4a6a;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}
.hero-pill-row {
    display: flex;
    gap: 8px;
    margin-bottom: 36px;
    flex-wrap: wrap;
    justify-content: center;
}
.hero-pill {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    color: #6060a0;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 100px;
    padding: 5px 14px;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}
.hero-dot { color: #22c55e; margin-right: 6px; }
.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: clamp(4rem, 10vw, 7.5rem);
    color: #c9a96e;
    font-weight: 700;
    line-height: 0.95;
    margin: 0 0 16px 0;
    letter-spacing: -0.01em;
}
.hero-tagline {
    font-family: 'Playfair Display', serif;
    font-style: italic;
    font-size: clamp(1.1rem, 2.5vw, 1.5rem);
    color: rgba(201,169,110,0.55);
    margin-bottom: 48px;
    letter-spacing: 0.02em;
}
.hero-stats-row {
    display: flex;
    gap: 56px;
    margin-bottom: 48px;
    justify-content: center;
    flex-wrap: wrap;
}
.hero-stat-num {
    font-family: 'Playfair Display', serif;
    font-size: 2.4rem;
    color: #c9a96e;
    font-weight: 700;
    line-height: 1;
}
.hero-stat-label {
    font-family: 'Syne', sans-serif;
    font-size: 0.62rem;
    color: #4a4a6a;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-top: 5px;
}
.hero-feature-row {
    display: flex;
    gap: 10px;
    margin-bottom: 52px;
    flex-wrap: wrap;
    justify-content: center;
}
.hero-feature-chip {
    font-family: 'Syne', sans-serif;
    font-size: 0.78rem;
    color: #9090a8;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 6px;
    padding: 7px 16px;
    letter-spacing: 0.02em;
    transition: all 0.2s;
}
.hero-live-ticker {
    background: rgba(17,17,24,0.9);
    border: 1px solid rgba(201,169,110,0.2);
    border-radius: 12px;
    padding: 18px 32px;
    margin-bottom: 52px;
    display: inline-flex;
    gap: 40px;
    align-items: center;
    backdrop-filter: blur(8px);
}
.ticker-item { text-align: center; }
.ticker-label { font-family: 'Syne', sans-serif; font-size: 0.62rem; color: #4a4a6a; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 3px; }
.ticker-value { font-family: 'DM Mono', monospace; font-size: 1.15rem; color: #c9a96e; font-weight: 500; }
.ticker-value-green { font-family: 'DM Mono', monospace; font-size: 1.15rem; color: #22c55e; }
.ticker-value-red { font-family: 'DM Mono', monospace; font-size: 1.15rem; color: #ef4444; }
.ticker-sep { width: 1px; height: 36px; background: rgba(201,169,110,0.15); }
.hero-cta-row { display: flex; gap: 16px; justify-content: center; align-items: center; margin-bottom: 60px; }
.hero-cta-primary {
    background: #c9a96e;
    color: #09090e;
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 0.9rem;
    padding: 14px 32px;
    border-radius: 8px;
    border: none;
    cursor: pointer;
    letter-spacing: 0.04em;
    text-decoration: none;
    transition: all 0.2s;
}
.hero-cta-secondary {
    color: #c9a96e;
    font-family: 'Syne', sans-serif;
    font-size: 0.9rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    cursor: pointer;
    padding: 14px 20px;
    text-decoration: none;
}
.hero-footer-note {
    font-family: 'DM Mono', monospace;
    font-size: 0.62rem;
    color: #2a2a4a;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    position: absolute;
    bottom: 24px;
}

/* ── DASHBOARD ── */
.dash-header {
    background: linear-gradient(180deg, #0d0d14 0%, #09090e 100%);
    border-bottom: 1px solid rgba(201,169,110,0.15);
    padding: 20px 32px 0 32px;
    margin: -2rem -2rem 0 -2rem;
}
.dash-title-row { display: flex; justify-content: space-between; align-items: flex-end; padding-bottom: 16px; }
.dash-title { font-family: 'Playfair Display', serif; font-size: 1.6rem; color: #c9a96e; font-weight: 700; margin: 0; }
.dash-subtitle { font-family: 'Syne', sans-serif; font-size: 0.75rem; color: #6060a0; margin-top: 2px; letter-spacing: 0.04em; }
.dash-live-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(34,197,94,0.08);
    border: 1px solid rgba(34,197,94,0.2);
    border-radius: 100px;
    padding: 4px 12px;
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem; color: #22c55e;
}
.live-dot { width: 6px; height: 6px; background: #22c55e; border-radius: 50%; display: inline-block; animation: pulse 2s infinite; }
@keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.3; } }

/* ── METRIC CARDS ── */
.kpi-row { display: grid; grid-template-columns: repeat(6,1fr); gap: 12px; padding: 20px 0 0 0; }
.kpi-card {
    background: #111118;
    border: 1px solid rgba(201,169,110,0.15);
    border-radius: 10px;
    padding: 14px 16px;
    position: relative;
    overflow: hidden;
}
.kpi-card::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: #c9a96e;
}
.kpi-card-red::before { background: #ef4444; }
.kpi-card-green::before { background: #22c55e; }
.kpi-card-blue::before { background: #4a9eff; }
.kpi-label { font-family: 'Syne', sans-serif; font-size: 0.62rem; color: #4a4a6a; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 8px; }
.kpi-value { font-family: 'DM Mono', monospace; font-size: 1.3rem; color: #c9a96e; font-weight: 500; line-height: 1.1; }
.kpi-value-red { font-family: 'DM Mono', monospace; font-size: 1.3rem; color: #ef4444; font-weight: 500; }
.kpi-value-green { font-family: 'DM Mono', monospace; font-size: 1.3rem; color: #22c55e; font-weight: 500; }
.kpi-sub { font-family: 'DM Mono', monospace; font-size: 0.65rem; color: #3a3a5a; margin-top: 3px; }
.kpi-sub-red { font-family: 'DM Mono', monospace; font-size: 0.65rem; color: rgba(239,68,68,0.6); margin-top: 3px; }
.kpi-sub-green { font-family: 'DM Mono', monospace; font-size: 0.65rem; color: rgba(34,197,94,0.6); margin-top: 3px; }

/* ── INTERPRET BOXES ── */
.mc-interpret {
    background: rgba(58,90,122,0.12);
    border: 1px solid rgba(74,158,255,0.2);
    border-left: 3px solid #4a9eff;
    border-radius: 8px;
    padding: 16px 20px;
    font-family: 'Syne', sans-serif;
    font-size: 0.88rem;
    color: #c8d8f0;
    margin: 12px 0;
    line-height: 1.7;
}
.mc-interpret-green {
    background: rgba(34,197,94,0.06);
    border: 1px solid rgba(34,197,94,0.2);
    border-left: 3px solid #22c55e;
    border-radius: 8px;
    padding: 16px 20px;
    font-family: 'Syne', sans-serif;
    font-size: 0.88rem;
    color: #bbf7d0;
    margin: 12px 0;
    line-height: 1.7;
}
.mc-risk {
    background: rgba(239,68,68,0.06);
    border: 1px solid rgba(239,68,68,0.2);
    border-left: 3px solid #ef4444;
    border-radius: 8px;
    padding: 16px 20px;
    font-family: 'Syne', sans-serif;
    font-size: 0.88rem;
    color: #fca5a5;
    margin: 12px 0;
    line-height: 1.7;
}
.mc-formula {
    background: #080810;
    border: 1px solid rgba(201,169,110,0.2);
    border-radius: 8px;
    padding: 16px 24px;
    font-family: 'DM Mono', monospace;
    font-size: 1.1rem;
    color: #c9a96e;
    margin: 12px 0;
    letter-spacing: 0.03em;
    text-align: center;
}
.mc-card {
    background: #111118;
    border: 1px solid rgba(201,169,110,0.12);
    border-radius: 12px;
    padding: 20px 24px;
    margin: 8px 0;
}
.section-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.15rem;
    color: #c9a96e;
    font-weight: 600;
    border-bottom: 1px solid rgba(201,169,110,0.15);
    padding-bottom: 10px;
    margin-bottom: 16px;
}
.stat-row {
    display: flex; justify-content: space-between; align-items: center;
    padding: 8px 0;
    border-bottom: 1px solid rgba(255,255,255,0.04);
    font-family: 'DM Mono', monospace;
    font-size: 0.85rem;
}
.stat-label { color: #6060a0; }
.stat-val-gold { color: #c9a96e; }
.stat-val-green { color: #22c55e; }
.stat-val-red { color: #ef4444; }
.stat-val { color: #e8e8f0; }
.vol-pill {
    display: inline-block;
    background: rgba(201,169,110,0.08);
    border: 1px solid rgba(201,169,110,0.15);
    border-radius: 6px;
    padding: 8px 14px;
    font-family: 'DM Mono', monospace;
    font-size: 0.78rem;
    color: #9090a8;
    margin-top: 12px;
    line-height: 1.9;
    width: 100%;
}
.badge-green { display:inline-block; background:rgba(34,197,94,0.1); color:#22c55e; border:1px solid rgba(34,197,94,0.25); border-radius:4px; padding:2px 10px; font-family:'DM Mono',monospace; font-size:0.75rem; }
.badge-gold  { display:inline-block; background:rgba(201,169,110,0.1); color:#c9a96e; border:1px solid rgba(201,169,110,0.25); border-radius:4px; padding:2px 10px; font-family:'DM Mono',monospace; font-size:0.75rem; }
.badge-red   { display:inline-block; background:rgba(239,68,68,0.1); color:#ef4444; border:1px solid rgba(239,68,68,0.25); border-radius:4px; padding:2px 10px; font-family:'DM Mono',monospace; font-size:0.75rem; }
.sidebar-label { font-family:'Syne',sans-serif; font-size:0.6rem; color:#c9a96e; text-transform:uppercase; letter-spacing:0.14em; margin:16px 0 6px 0; border-bottom:1px solid rgba(201,169,110,0.12); padding-bottom:4px; }
.footer-bar { border-top: 1px solid rgba(201,169,110,0.1); padding: 16px 0; margin-top: 40px; }
.footer-text { font-family:'DM Mono',monospace; font-size:0.62rem; color:#2a2a4a; text-align:center; line-height:2; letter-spacing:0.04em; }
table.mc-table { width:100%; border-collapse:collapse; font-family:'DM Mono',monospace; font-size:0.82rem; }
table.mc-table th { color:#6060a0; text-align:left; padding:8px 12px; border-bottom:1px solid rgba(201,169,110,0.15); font-family:'Syne',sans-serif; font-size:0.66rem; text-transform:uppercase; letter-spacing:0.08em; }
table.mc-table td { color:#e8e8f0; padding:8px 12px; border-bottom:1px solid rgba(255,255,255,0.04); }
table.mc-table tr:hover td { background:rgba(201,169,110,0.03); }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════
# LIVE DATA FETCH
# ══════════════════════════════════════════════════════
@st.cache_data(ttl=300)
def fetch_nifty_data():
    """Fetch live NIFTY 50 data from Yahoo Finance. Returns dict with fallback."""
    try:
        import yfinance as yf
        nifty = yf.Ticker("^NSEI")
        hist  = nifty.history(period="5d", interval="1d")
        if hist.empty:
            raise ValueError("Empty data")
        latest    = float(hist["Close"].iloc[-1])
        prev      = float(hist["Close"].iloc[-2]) if len(hist) >= 2 else latest
        chg       = latest - prev
        chg_pct   = chg / prev * 100
        hist_1y   = nifty.history(period="1y", interval="1d")
        if not hist_1y.empty:
            log_rets  = np.log(hist_1y["Close"] / hist_1y["Close"].shift(1)).dropna()
            hist_vol  = float(log_rets.std() * np.sqrt(252) * 100)
            ann_drift = float(log_rets.mean() * 252 * 100)
            high_52   = float(hist_1y["High"].max())
            low_52    = float(hist_1y["Low"].min())
        else:
            hist_vol, ann_drift, high_52, low_52 = 19.5, 9.5, latest*1.15, latest*0.85
        return {
            "price": latest, "prev": prev, "chg": chg, "chg_pct": chg_pct,
            "hist_vol": hist_vol, "ann_drift": ann_drift,
            "high_52": high_52, "low_52": low_52,
            "source": "live", "as_of": datetime.datetime.now().strftime("%H:%M IST")
        }
    except Exception as e:
        return {
            "price": 24500.0, "prev": 24350.0, "chg": 150.0, "chg_pct": 0.62,
            "hist_vol": 19.5, "ann_drift": 9.5,
            "high_52": 26277.0, "low_52": 21964.0,
            "source": "fallback", "as_of": "offline",
            "error": str(e)
        }

@st.cache_data(ttl=3600)
def fetch_india_vix():
    """Fetch India VIX from Yahoo Finance."""
    try:
        import yfinance as yf
        vix = yf.Ticker("^INDIAVIX")
        hist = vix.history(period="2d", interval="1d")
        if hist.empty:
            raise ValueError("Empty")
        return float(hist["Close"].iloc[-1])
    except Exception:
        return 14.5


# ══════════════════════════════════════════════════════
# SIMULATION ENGINE
# ══════════════════════════════════════════════════════
def run_simulation(S0, mu_annual, sigma_annual, T, N, K, r, option_type, conf_level):
    np.random.seed(None)
    mu_daily    = mu_annual / 252
    sigma_daily = sigma_annual / np.sqrt(252)

    Z           = np.random.standard_normal((T, N))
    daily_ret   = np.exp((mu_daily - 0.5*sigma_daily**2) + sigma_daily * Z)
    price_paths = S0 * np.cumprod(daily_ret, axis=0)
    full_paths  = np.vstack([np.full((1, N), S0), price_paths])
    fp          = full_paths[-1, :]

    mean_final   = float(np.mean(fp))
    median_final = float(np.median(fp))
    p5_final     = float(np.percentile(fp, 5))
    p25_final    = float(np.percentile(fp, 25))
    p75_final    = float(np.percentile(fp, 75))
    p95_final    = float(np.percentile(fp, 95))
    std_final    = float(np.std(fp))
    p_gain       = float(np.mean(fp > S0) * 100)
    p_loss       = float(np.mean(fp < S0) * 100)
    exp_ret_pct  = (mean_final - S0) / S0 * 100
    mean_path    = np.mean(full_paths, axis=1)

    p5_idx  = int(np.argmin(np.abs(fp - p5_final)))
    p95_idx = int(np.argmin(np.abs(fp - p95_final)))

    conf   = conf_level / 100
    alpha  = 1 - conf
    rets   = (fp - S0) / S0
    VaR_p  = float(-np.percentile(rets, alpha * 100))
    VaR_a  = VaR_p * S0
    mask   = rets < -VaR_p
    CVaR_p = float(-np.mean(rets[mask])) if mask.sum() > 0 else VaR_p
    CVaR_a = CVaR_p * S0

    r_d    = r / 252
    Z2     = np.random.standard_normal((T, N))
    rn_r   = np.exp((r_d - 0.5*sigma_daily**2) + sigma_daily * Z2)
    rn_p   = S0 * np.cumprod(rn_r, axis=0)
    ST     = rn_p[-1, :]
    payoffs = np.maximum(ST - K, 0) if option_type == "Call" else np.maximum(K - ST, 0)
    disc   = np.exp(-r * T / 252)
    mc_p   = float(np.mean(payoffs) * disc)

    T_y = T / 252
    if T_y > 0 and sigma_annual > 0 and K > 0:
        d1  = (np.log(S0/K) + (r + 0.5*sigma_annual**2)*T_y) / (sigma_annual*np.sqrt(T_y))
        d2  = d1 - sigma_annual * np.sqrt(T_y)
        bs  = float(S0*norm.cdf(d1) - K*np.exp(-r*T_y)*norm.cdf(d2)) if option_type == "Call" \
              else float(K*np.exp(-r*T_y)*norm.cdf(-d2) - S0*norm.cdf(-d1))
    else:
        bs = float(max(S0 - K, 0)) if option_type == "Call" else float(max(K - S0, 0))

    return {
        "S0": S0, "T": T, "N": N,
        "mu_daily": mu_daily, "sigma_daily": sigma_daily,
        "mu_annual": mu_annual, "sigma_annual": sigma_annual,
        "full_paths": full_paths, "fp": fp,
        "mean_final": mean_final, "median_final": median_final,
        "p5_final": p5_final, "p25_final": p25_final,
        "p75_final": p75_final, "p95_final": p95_final,
        "std_final": std_final, "p_gain": p_gain, "p_loss": p_loss,
        "exp_ret_pct": exp_ret_pct, "mean_path": mean_path,
        "p5_idx": p5_idx, "p95_idx": p95_idx,
        "confidence": conf, "alpha": alpha,
        "VaR_pct": VaR_p, "VaR_abs": VaR_a,
        "CVaR_pct": CVaR_p, "CVaR_abs": CVaR_a,
        "K": K, "r": r, "option_type": option_type,
        "ST": ST, "payoffs": payoffs,
        "mc_opt": mc_p, "bs_price": float(bs),
        "pricing_err": abs(mc_p - bs) / max(bs, 0.01) * 100,
    }

def dark_layout(**kw):
    base = dict(
        paper_bgcolor="#09090e", plot_bgcolor="#111118",
        font=dict(family="DM Mono", color="#e8e8f0", size=11),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)", zerolinecolor="rgba(255,255,255,0.1)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)", zerolinecolor="rgba(255,255,255,0.1)"),
        margin=dict(l=55, r=35, t=55, b=45),
        legend=dict(bgcolor="rgba(9,9,14,0.9)", bordercolor="rgba(201,169,110,0.25)", borderwidth=1),
    )
    base.update(kw)
    return base


# ══════════════════════════════════════════════════════
# PAGE STATE
# ══════════════════════════════════════════════════════
if "page" not in st.session_state:
    st.session_state["page"] = "home"


# ══════════════════════════════════════════════════════
# ── HOME PAGE ──────────────────────────────────────
# ══════════════════════════════════════════════════════
if st.session_state["page"] == "home":

    nifty = fetch_nifty_data()
    vix   = fetch_india_vix()
    chg_clr = "ticker-value-green" if nifty["chg"] >= 0 else "ticker-value-red"
    chg_sym = "▲" if nifty["chg"] >= 0 else "▼"
    src_badge = "● LIVE" if nifty["source"] == "live" else "○ OFFLINE"
    src_color = "#22c55e" if nifty["source"] == "live" else "#6060a0"

    st.markdown(f"""
    <div class="hero-wrap">

      <!-- NAV -->
      <div class="hero-nav">
        <div class="hero-nav-logo">🎲 MonteDesk</div>
        <div class="hero-nav-badge">Day 25 · 30 Days of AI Finance</div>
        <div style="font-family:'DM Mono',monospace; font-size:0.68rem; color:{src_color}; letter-spacing:0.08em;">
          {src_badge} · {nifty['as_of']}
        </div>
      </div>

      <!-- PILL -->
      <div class="hero-pill-row">
        <div class="hero-pill"><span class="hero-dot">●</span>MONTE CARLO ENGINE</div>
        <div class="hero-pill">INDIAN MARKETS · NSE</div>
        <div class="hero-pill">GEOMETRIC BROWNIAN MOTION</div>
        <div class="hero-pill">GBM · VaR · CVaR · OPTIONS</div>
      </div>

      <!-- TITLE -->
      <div class="hero-title">MonteDesk</div>
      <div class="hero-tagline">Simulate. Quantify. Understand Risk.</div>

      <!-- STATS -->
      <div class="hero-stats-row">
        <div style="text-align:center;">
          <div class="hero-stat-num">10,000</div>
          <div class="hero-stat-label">Simulations</div>
        </div>
        <div style="text-align:center;">
          <div class="hero-stat-num">3D</div>
          <div class="hero-stat-label">Visualisations</div>
        </div>
        <div style="text-align:center;">
          <div class="hero-stat-num">GBM</div>
          <div class="hero-stat-label">Price Model</div>
        </div>
        <div style="text-align:center;">
          <div class="hero-stat-num">6</div>
          <div class="hero-stat-label">Analysis Tabs</div>
        </div>
      </div>

      <!-- LIVE TICKER -->
      <div class="hero-live-ticker">
        <div class="ticker-item">
          <div class="ticker-label">NIFTY 50</div>
          <div class="ticker-value">₹{nifty['price']:,.2f}</div>
        </div>
        <div class="ticker-sep"></div>
        <div class="ticker-item">
          <div class="ticker-label">Day Change</div>
          <div class="{chg_clr}">{chg_sym} {abs(nifty['chg']):.1f} ({nifty['chg_pct']:+.2f}%)</div>
        </div>
        <div class="ticker-sep"></div>
        <div class="ticker-item">
          <div class="ticker-label">India VIX</div>
          <div class="ticker-value">{vix:.2f}</div>
        </div>
        <div class="ticker-sep"></div>
        <div class="ticker-item">
          <div class="ticker-label">52W High</div>
          <div class="ticker-value-green">₹{nifty['high_52']:,.0f}</div>
        </div>
        <div class="ticker-sep"></div>
        <div class="ticker-item">
          <div class="ticker-label">52W Low</div>
          <div class="ticker-value-red">₹{nifty['low_52']:,.0f}</div>
        </div>
        <div class="ticker-sep"></div>
        <div class="ticker-item">
          <div class="ticker-label">Hist Vol (1Y)</div>
          <div class="ticker-value">{nifty['hist_vol']:.1f}%</div>
        </div>
      </div>

      <!-- FEATURES -->
      <div class="hero-feature-row">
        <div class="hero-feature-chip">📈 Price Paths</div>
        <div class="hero-feature-chip">🌐 3D Visualisation</div>
        <div class="hero-feature-chip">📊 Distribution &amp; VaR</div>
        <div class="hero-feature-chip">💰 Options Payoff</div>
        <div class="hero-feature-chip">🧮 Math Explained</div>
        <div class="hero-feature-chip">📋 Probability Table</div>
      </div>

      <div class="hero-footer-note">
        @Preethams321 · SJCC Bengaluru · For educational purposes only · Not financial advice
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Streamlit button for navigation (pure Streamlit, no JS hacks)
    col_l, col_btn, col_r = st.columns([3, 2, 3])
    with col_btn:
        if st.button("→  Launch Simulator", key="launch_btn", use_container_width=True):
            st.session_state["page"] = "simulator"
            st.session_state["nifty_data"] = nifty
            st.session_state["vix_data"]   = vix
            st.rerun()


# ══════════════════════════════════════════════════════
# ── SIMULATOR PAGE ─────────────────────────────────
# ══════════════════════════════════════════════════════
else:
    nifty = st.session_state.get("nifty_data", fetch_nifty_data())
    vix   = st.session_state.get("vix_data",   fetch_india_vix())

    # ── SIDEBAR ────────────────────────────────────────
    with st.sidebar:
        st.markdown("""
        <div style='text-align:center;padding:12px 0 18px 0;'>
          <div style='font-family:"Playfair Display",serif;font-size:1.5rem;color:#c9a96e;font-weight:700;'>🎲 MonteDesk</div>
          <div style='font-family:"Syne",sans-serif;font-size:0.68rem;color:#4a4a6a;margin-top:2px;letter-spacing:0.06em;'>PARAMETER CONTROL PANEL</div>
        </div>""", unsafe_allow_html=True)

        if st.button("← Back to Home", key="back_btn"):
            st.session_state["page"] = "home"
            st.rerun()

        st.markdown('<div class="sidebar-label">INSTRUMENT</div>', unsafe_allow_html=True)
        instrument = st.text_input("Instrument name", value="NIFTY 50", key="inst_name")
        S0 = st.number_input("Current price (₹)", min_value=100.0, max_value=300000.0,
                              value=float(round(nifty["price"], 0)), step=50.0, key="price_in")
        inst_type = st.selectbox("Type", ["Equity Index","Stock","Crypto"], key="inst_type")

        st.markdown('<div class="sidebar-label">SIMULATION</div>', unsafe_allow_html=True)
        N = st.select_slider("Simulations", options=[1000,5000,10000,25000,50000], value=10000, key="n_sims")
        T = st.slider("Horizon (trading days)", 5, 252, 30, key="horizon")
        use_blend = st.checkbox("Blended vol (VIX + Historical)", value=True, key="use_blend")

        st.markdown('<div class="sidebar-label">VOLATILITY</div>', unsafe_allow_html=True)
        hist_vol = st.slider("Historical annual vol (%)", 5.0, 80.0,
                              float(round(nifty["hist_vol"], 1)), 0.5, key="hist_vol",
                              help="Auto-computed from 1Y daily returns")
        if use_blend:
            india_vix  = st.slider("India VIX", 8.0, 50.0, float(round(vix, 1)), 0.5,
                                    key="india_vix", help="Auto-fetched from Yahoo Finance")
            vix_weight = st.slider("VIX weight (%)", 10, 90, 60, key="vix_wt",
                                    help="60% implied + 40% historical = institutional standard")
            vix_w      = vix_weight / 100
            sigma_ann  = vix_w * (india_vix/100) + (1 - vix_w) * (hist_vol/100)
        else:
            india_vix, vix_weight, vix_w = 0.0, 0, 0.0
            sigma_ann  = hist_vol / 100

        ann_drift = st.slider("Annual drift (%)", -20.0, 40.0,
                               float(round(nifty["ann_drift"], 1)), 0.5, key="drift",
                               help="Auto-computed from 1Y log returns")
        mu_ann = ann_drift / 100

        st.markdown('<div class="sidebar-label">OPTIONS</div>', unsafe_allow_html=True)
        option_type = st.radio("Option type", ["Call","Put"], horizontal=True, key="opt_type")
        K = st.number_input("Strike (₹)", min_value=100.0, max_value=300000.0,
                             value=float(round(S0/500)*500 + 500), step=50.0, key="strike")
        rf_rate = st.slider("Risk-free rate (%)", 3.0, 10.0, 6.5, 0.1, key="rf",
                             help="India 10Y G-Sec yield")
        r = rf_rate / 100

        st.markdown('<div class="sidebar-label">RISK SETTINGS</div>', unsafe_allow_html=True)
        conf_level = int(st.radio("VaR confidence (%)", [90,95,99], index=1, horizontal=True, key="conf"))

        st.markdown("<hr style='border-color:rgba(201,169,110,0.15);margin:18px 0;'>", unsafe_allow_html=True)
        run_btn = st.button("🚀  Run Simulation", key="run_btn", use_container_width=True)

        live_src = "🟢 Live" if nifty["source"] == "live" else "🔴 Offline"
        st.markdown(f"""<div style='font-family:"DM Mono",monospace;font-size:0.62rem;color:#2a2a4a;text-align:center;margin-top:16px;line-height:2;'>
        NIFTY data: {live_src} · {nifty['as_of']}<br>
        Day 25 · @Preethams321 · Educational only
        </div>""", unsafe_allow_html=True)

    # ── RUN SIMULATION ─────────────────────────────────
    if run_btn or "sim_res" not in st.session_state:
        with st.spinner("Running Monte Carlo simulation…"):
            st.session_state["sim_res"] = run_simulation(
                S0, mu_ann, sigma_ann, T, N, K, r, option_type, conf_level
            )
            st.session_state["sim_meta"] = {
                "instrument": instrument, "use_blend": use_blend,
                "hist_vol": hist_vol, "india_vix": india_vix,
                "vix_weight": vix_weight, "vix_w": vix_w, "sigma_ann": sigma_ann,
            }

    res  = st.session_state["sim_res"]
    meta = st.session_state["sim_meta"]

    # unpack
    full_paths   = res["full_paths"];  fp          = res["fp"]
    mean_path    = res["mean_path"];   mean_final  = res["mean_final"]
    median_final = res["median_final"];p5_final    = res["p5_final"]
    p25_final    = res["p25_final"];   p75_final   = res["p75_final"]
    p95_final    = res["p95_final"];   std_final   = res["std_final"]
    p_gain       = res["p_gain"];      p_loss      = res["p_loss"]
    exp_ret_pct  = res["exp_ret_pct"]; VaR_pct     = res["VaR_pct"]
    VaR_abs      = res["VaR_abs"];     CVaR_pct    = res["CVaR_pct"]
    CVaR_abs     = res["CVaR_abs"];    confidence  = res["confidence"]
    alpha        = res["alpha"];       mc_opt      = res["mc_opt"]
    bs_price     = res["bs_price"];    pricing_err = res["pricing_err"]
    ST           = res["ST"];          payoffs     = res["payoffs"]
    mu_daily     = res["mu_daily"];    sigma_daily = res["sigma_daily"]
    p5_idx       = res["p5_idx"];      p95_idx     = res["p95_idx"]
    _inst        = meta["instrument"]; _sig        = meta["sigma_ann"]
    _hv          = meta["hist_vol"];   _vix        = meta["india_vix"]
    _vw          = meta["vix_w"];      _blend      = meta["use_blend"]
    p5_chg  = (p5_final  / S0 - 1) * 100
    p95_chg = (p95_final / S0 - 1) * 100

    # ── DASHBOARD HEADER ───────────────────────────────
    live_src = "live" if nifty["source"] == "live" else "offline"
    chg_c = "#22c55e" if nifty["chg"] >= 0 else "#ef4444"
    chg_s = "▲" if nifty["chg"] >= 0 else "▼"

    st.markdown(f"""
    <div class="dash-header">
      <div class="dash-title-row">
        <div>
          <div class="dash-title">🎲 MonteDesk</div>
          <div class="dash-subtitle">Monte Carlo Simulation Engine · {_inst} · {N:,} paths · {T}D horizon</div>
        </div>
        <div style="display:flex;gap:12px;align-items:center;">
          <div style="text-align:right;">
            <div style="font-family:'DM Mono',monospace;font-size:1.6rem;color:#c9a96e;font-weight:500;">₹{nifty['price']:,.2f}</div>
            <div style="font-family:'DM Mono',monospace;font-size:0.8rem;color:{chg_c};">{chg_s} {abs(nifty['chg']):.1f} ({nifty['chg_pct']:+.2f}%)</div>
          </div>
          <div class="dash-live-badge"><span class="live-dot"></span>{"LIVE" if live_src=="live" else "OFFLINE"}</div>
        </div>
      </div>
    """, unsafe_allow_html=True)

    # KPI row
    kpi_data = [
        ("CURRENT PRICE", f"₹{S0:,.0f}", "", "kpi-card", "kpi-value"),
        ("EXPECTED MEAN",  f"₹{mean_final:,.0f}", f"{exp_ret_pct:+.1f}%", "kpi-card", "kpi-value"),
        ("P5 — BEAR CASE", f"₹{p5_final:,.0f}", f"{p5_chg:.1f}%", "kpi-card kpi-card-red", "kpi-value-red"),
        ("P95 — BULL CASE",f"₹{p95_final:,.0f}", f"+{p95_chg:.1f}%", "kpi-card kpi-card-green","kpi-value-green"),
        ("P(GAIN)",         f"{p_gain:.1f}%", f"of {N:,} sims", "kpi-card", "kpi-value-green" if p_gain>=50 else "kpi-value-red"),
        (f"VAR {conf_level}%", f"₹{VaR_abs:,.0f}", f"{VaR_pct*100:.2f}% loss", "kpi-card kpi-card-red","kpi-value-red"),
    ]
    sub_clrs = ["kpi-sub","kpi-sub","kpi-sub-red","kpi-sub-green",
                "kpi-sub-green" if p_gain>=50 else "kpi-sub-red","kpi-sub-red"]

    kpi_html = '<div class="kpi-row">'
    for i, (lbl, val, sub, card_cls, val_cls) in enumerate(kpi_data):
        kpi_html += f"""<div class="{card_cls}">
          <div class="kpi-label">{lbl}</div>
          <div class="{val_cls}">{val}</div>
          <div class="{sub_clrs[i]}">{sub}</div>
        </div>"""
    kpi_html += "</div></div>"  # closes kpi-row and dash-header
    st.markdown(kpi_html, unsafe_allow_html=True)

    # Interpretation banner
    if p_gain > 60:
        st.markdown(f"""<div class="mc-interpret-green" style="margin:12px 0 4px 0;">
          📈 <strong>Bullish skew</strong> — {p_gain:.1f}% of {N:,} simulations end above ₹{S0:,.0f}.
          Mean expected return: <strong>+{exp_ret_pct:.1f}%</strong> over {T} trading days
          (₹{S0:,.0f} → ₹{mean_final:,.0f}). 90% confidence band: ₹{p5_final:,.0f} — ₹{p95_final:,.0f}.
          Blended σ = {_sig*100:.2f}% | μ = {ann_drift:.1f}% p.a.
        </div>""", unsafe_allow_html=True)
    elif p_gain < 40:
        st.markdown(f"""<div class="mc-risk" style="margin:12px 0 4px 0;">
          📉 <strong>Bearish skew</strong> — {p_loss:.1f}% of simulations end below ₹{S0:,.0f}.
          Mean expected return: <strong>{exp_ret_pct:.1f}%</strong>.
          90% band: ₹{p5_final:,.0f} — ₹{p95_final:,.0f}.
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""<div class="mc-interpret" style="margin:12px 0 4px 0;">
          ⚖️ <strong>Balanced distribution</strong> — P(gain) = {p_gain:.1f}%.
          90% confidence band: ₹{p5_final:,.0f} — ₹{p95_final:,.0f} (range ₹{p95_final-p5_final:,.0f}).
          Blended σ = {_sig*100:.2f}% | μ = {ann_drift:.1f}% p.a.
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    # ── TABS ───────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📈  Price Paths", "🌐  3D Visualisation",
        "📊  Distribution & VaR", "💰  Options Payoff",
        "🧮  Math Explained", "📋  Probability Table",
    ])

    # ──────────────────────────────────────────────────
    # TAB 1 · PRICE PATHS
    # ──────────────────────────────────────────────────
    with tab1:
        cL, cR = st.columns([13, 7])
        with cL:
            st.markdown('<div class="section-title">GBM Simulation — All Price Paths</div>', unsafe_allow_html=True)
            rn     = min(500, N)
            s_idx  = np.random.choice(N, rn, replace=False)
            s_p    = full_paths[:, s_idx]
            s_f    = fp[s_idx]

            fig = go.Figure()
            for i in range(rn):
                c = "rgba(34,197,94,0.035)" if s_f[i] > S0 else "rgba(239,68,68,0.035)"
                fig.add_trace(go.Scatter(y=s_p[:,i], mode='lines',
                    line=dict(color=c, width=0.6), showlegend=False, hoverinfo='none'))

            fig.add_trace(go.Scatter(y=full_paths[:,p5_idx], mode='lines',
                line=dict(color="rgba(239,68,68,0.55)", width=1.2, dash='dot'), name="P5 — Bear"))
            fig.add_trace(go.Scatter(y=full_paths[:,p95_idx], mode='lines',
                line=dict(color="rgba(34,197,94,0.55)", width=1.2, dash='dot'),
                fill='tonexty', fillcolor='rgba(34,197,94,0.03)', name="P95 — Bull"))
            fig.add_trace(go.Scatter(y=mean_path, mode='lines',
                line=dict(color="#c9a96e", width=3), name="Expected Path"))

            fig.add_shape(type="line", x0=0, x1=T, y0=S0, y1=S0,
                line=dict(color="rgba(255,255,255,0.3)", width=1, dash="dash"))
            fig.add_annotation(x=T*0.02, y=S0, text=f"  Current ₹{S0:,.0f}",
                showarrow=False, font=dict(color="#ffffff", size=10, family="DM Mono"), xanchor="left")
            for val, lbl, clr in [(p95_final,f"P95 ₹{p95_final:,.0f}","#22c55e"),
                                   (mean_final,f"Mean ₹{mean_final:,.0f}","#c9a96e"),
                                   (p5_final, f"P5 ₹{p5_final:,.0f}","#ef4444")]:
                fig.add_annotation(x=T, y=val, text=f"  {lbl}", showarrow=False,
                    xanchor="left", font=dict(color=clr, size=10, family="DM Mono"))

            fig.update_layout(**dark_layout(
                title=dict(text=f"{_inst} · {N:,} GBM Paths · {T} Trading Days",
                    font=dict(family="Playfair Display", color="#c9a96e", size=15)),
                xaxis_title="Trading Day", yaxis_title="Price (₹)", height=560,
            ))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        with cR:
            st.markdown('<div class="section-title">Simulation Statistics</div>', unsafe_allow_html=True)
            rows = [
                ("Expected Price", f"₹{mean_final:,.0f}", f"{exp_ret_pct:+.2f}%", "#c9a96e"),
                ("Median Price",   f"₹{median_final:,.0f}", "", "#e8e8f0"),
                ("P95 — Bull",     f"₹{p95_final:,.0f}", f"+{p95_chg:.1f}%", "#22c55e"),
                ("P75",            f"₹{p75_final:,.0f}", f"+{(p75_final/S0-1)*100:.1f}%", "#22c55e"),
                ("P25",            f"₹{p25_final:,.0f}", f"{(p25_final/S0-1)*100:.1f}%", "#f97316"),
                ("P5 — Bear",      f"₹{p5_final:,.0f}", f"{p5_chg:.1f}%", "#ef4444"),
                ("Std Deviation",  f"₹{std_final:,.0f}", "", "#6060a0"),
                ("P(Gain)",        f"{p_gain:.1f}%", f"of {N:,} sims", "#22c55e"),
                ("P(Loss)",        f"{p_loss:.1f}%", f"of {N:,} sims", "#ef4444"),
            ]
            html_rows = ""
            for lbl, val, sub, clr in rows:
                html_rows += f"""<div class="stat-row">
                  <span class="stat-label">{lbl}</span>
                  <span style="color:{clr};font-family:'DM Mono',monospace;font-size:0.88rem;">
                    {val} <span style="color:#3a3a5a;font-size:0.68rem;margin-left:4px;">{sub}</span>
                  </span>
                </div>"""
            st.markdown(f'<div class="mc-card">{html_rows}</div>', unsafe_allow_html=True)

            st.markdown(f"""<div class="mc-interpret">
              <strong>{N:,} GBM paths</strong> over <strong>{T} trading days</strong>.
              90% CI: ₹{p5_final:,.0f} → ₹{p95_final:,.0f} (width ₹{p95_final-p5_final:,.0f}).
              9 of 10 simulations finish inside this band.
              The remaining 10% are tail events — quantified as VaR &amp; CVaR.
            </div>""", unsafe_allow_html=True)

            if _blend:
                st.markdown(f"""<div class="vol-pill">
                  Volatility: <span style="color:#c9a96e">{_sig*100:.2f}%</span> annual (blended)<br>
                  VIX {_vix:.1f}% × {_vw:.0%} = {_vix*_vw:.2f}%  +  Hist {_hv:.1f}% × {1-_vw:.0%} = {_hv*(1-_vw):.2f}%<br>
                  Daily σ = {sigma_daily*100:.4f}%  ·  Daily μ = {mu_daily*100:.4f}%
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""<div class="vol-pill">
                  Volatility: <span style="color:#c9a96e">{_sig*100:.2f}%</span> (historical only)<br>
                  Daily σ = {sigma_daily*100:.4f}%  ·  Daily μ = {mu_daily*100:.4f}%
                </div>""", unsafe_allow_html=True)

    # ──────────────────────────────────────────────────
    # TAB 2 · 3D VISUALISATION
    # ──────────────────────────────────────────────────
    with tab2:
        view = st.radio("3D view", ["🌀 Path Tornado","🌊 Density Wave","☁️ Outcome Cloud"],
                         horizontal=True, key="v3d")

        if view == "🌀 Path Tornado":
            st.markdown('<div class="section-title">3D Path Tornado — 300 GBM Paths in Three Dimensions</div>', unsafe_allow_html=True)
            n3   = min(300, N)
            i3   = np.random.choice(N, n3, replace=False)
            p3   = full_paths[:, i3]
            f3   = fp[i3]
            days = np.arange(T+1, dtype=float)
            fig3 = go.Figure()
            for i in range(n3):
                pct = (f3[i] - S0) / S0
                if pct >= 0:
                    col = f"rgba(34,{min(197,int(80+pct*700))},94,0.07)"
                else:
                    col = f"rgba({min(239,int(120+abs(pct)*700))},68,68,0.07)"
                fig3.add_trace(go.Scatter3d(x=days, y=np.full(T+1,float(i)), z=p3[:,i],
                    mode='lines', line=dict(color=col, width=1.0),
                    showlegend=False, hoverinfo='none'))
            mid = n3 // 2
            for z_p, col, nm, w in [(mean_path,"#00d4ff","Expected Path",5),
                                     (full_paths[:,p95_idx],"#22c55e","P95 Bull",3),
                                     (full_paths[:,p5_idx],"#ef4444","P5 Bear",3)]:
                fig3.add_trace(go.Scatter3d(x=days, y=np.full(T+1,float(mid)), z=z_p,
                    mode='lines', line=dict(color=col, width=w), name=nm))
            fig3.update_layout(
                scene=dict(
                    xaxis=dict(title="Day", backgroundcolor="#09090e", gridcolor="rgba(201,169,110,0.08)", color="#6060a0"),
                    yaxis=dict(title="Simulation #", backgroundcolor="#09090e", gridcolor="rgba(74,158,255,0.06)", color="#6060a0"),
                    zaxis=dict(title="Price (₹)", backgroundcolor="#09090e", gridcolor="rgba(255,255,255,0.04)", color="#6060a0"),
                    bgcolor="#09090e", camera=dict(eye=dict(x=1.8, y=1.2, z=0.9))
                ),
                paper_bgcolor="#09090e",
                title=dict(text=f"{_inst} · {n3} GBM Paths · Drag to rotate",
                    font=dict(family="Playfair Display", color="#c9a96e", size=14)),
                legend=dict(bgcolor="rgba(9,9,14,0.9)", bordercolor="rgba(201,169,110,0.2)", borderwidth=1),
                height=640, margin=dict(l=0,r=0,t=50,b=0)
            )
            st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": True})
            st.markdown(f"""<div class="mc-interpret">
              Green paths end above ₹{S0:,.0f} · Red paths end below · Cyan = expected path.
              The fan shape widens rightward — uncertainty expanding with time.
              Each rotation reveals the same {N:,} outcomes from a different angle.
            </div>""", unsafe_allow_html=True)

        elif view == "🌊 Density Wave":
            st.markdown('<div class="section-title">Probability Density Wave — Uncertainty Grows with Time</div>', unsafe_allow_html=True)
            n_s   = min(T+1, 31)
            d_idx = np.linspace(0, T, n_s, dtype=int)
            n_b   = 40
            p_min = float(np.percentile(fp, 1))
            p_max = float(np.percentile(fp, 99))
            p_bins= np.linspace(p_min, p_max, n_b)
            d_mat = np.zeros((n_b, n_s))
            for j, di in enumerate(d_idx):
                try:
                    kde = gaussian_kde(full_paths[di, :])
                    d_mat[:, j] = kde(p_bins)
                except Exception:
                    pass
            fig_w = go.Figure(go.Surface(
                x=d_idx.astype(float), y=p_bins, z=d_mat,
                colorscale=[[0,"#030610"],[0.2,"#003060"],[0.4,"#006090"],
                            [0.65,"#00c0d0"],[0.85,"#00ff88"],[1,"#ffff00"]],
                showscale=True,
                colorbar=dict(title="Density", tickfont=dict(family="DM Mono", color="#e8e8f0", size=10)),
                opacity=0.92,
                contours=dict(z=dict(show=True, usecolormap=True, project_z=True))
            ))
            fig_w.update_layout(
                scene=dict(
                    xaxis=dict(title="Day",backgroundcolor="#09090e",gridcolor="rgba(255,255,255,0.04)",color="#6060a0"),
                    yaxis=dict(title="Price (₹)",backgroundcolor="#09090e",gridcolor="rgba(255,255,255,0.04)",color="#6060a0"),
                    zaxis=dict(title="Density",backgroundcolor="#09090e",gridcolor="rgba(255,255,255,0.04)",color="#6060a0"),
                    bgcolor="#09090e", camera=dict(eye=dict(x=1.8, y=-1.5, z=1.2))
                ),
                paper_bgcolor="#09090e",
                title=dict(text="Probability Density Wave — Drag to rotate",
                    font=dict(family="Playfair Display", color="#c9a96e", size=14)),
                height=640, margin=dict(l=0,r=0,t=50,b=0)
            )
            st.plotly_chart(fig_w, use_container_width=True, config={"displayModeBar": True})
            st.markdown(f"""<div class="mc-interpret">
              Day 0: all {N:,} paths start at ₹{S0:,.0f} — a sharp narrow spike.
              As days pass, uncertainty accumulates. Bright yellow = highest probability price zone.
              Deep blue = tail regions. This expanding wave is why long-horizon forecasts
              are fundamentally less reliable than short-horizon ones.
            </div>""", unsafe_allow_html=True)

        else:
            st.markdown('<div class="section-title">Monte Carlo Outcome Cloud — Every Price as a Dot</div>', unsafe_allow_html=True)
            nc   = min(400, N)
            ci   = np.random.choice(N, nc, replace=False)
            cp   = full_paths[:, ci]
            ds   = np.arange(0, T+1, max(1, T//25))
            cx, cy, cz = [], [], []
            for si in range(nc):
                for dj in ds:
                    cx.append(si); cy.append(int(dj)); cz.append(float(cp[dj,si]))
            cz_a = np.array(cz)
            fig_c = go.Figure(go.Scatter3d(
                x=cx, y=cy, z=cz, mode='markers',
                marker=dict(size=1.6, color=(cz_a-S0)/S0,
                    colorscale=[[0,"#ff2d55"],[0.35,"#ff8c00"],[0.5,"#ffcc00"],
                                [0.65,"#4a9eff"],[1,"#00ff88"]],
                    cmin=-0.2, cmax=0.2, opacity=0.68,
                    colorbar=dict(title="Return",tickformat=".0%",
                        tickfont=dict(family="DM Mono",color="#e8e8f0",size=10))),
                hovertemplate="Sim %{x}<br>Day %{y}<br>₹%{z:,.0f}<extra></extra>"
            ))
            fig_c.update_layout(
                scene=dict(
                    xaxis=dict(title="Sim #",backgroundcolor="#09090e",gridcolor="rgba(255,255,255,0.03)",color="#6060a0"),
                    yaxis=dict(title="Day",backgroundcolor="#09090e",gridcolor="rgba(255,255,255,0.03)",color="#6060a0"),
                    zaxis=dict(title="Price (₹)",backgroundcolor="#09090e",gridcolor="rgba(255,255,255,0.03)",color="#6060a0"),
                    bgcolor="#09090e", camera=dict(eye=dict(x=1.6,y=1.6,z=1.0))
                ),
                paper_bgcolor="#09090e",
                title=dict(text=f"Outcome Cloud · {len(cx):,} data points · colour = return vs today",
                    font=dict(family="Playfair Display",color="#c9a96e",size=14)),
                height=640, margin=dict(l=0,r=0,t=50,b=0)
            )
            st.plotly_chart(fig_c, use_container_width=True, config={"displayModeBar": True})
            st.markdown(f"""<div class="mc-interpret">
              Red = below ₹{S0:,.0f} · Gold = near current · Blue/Green = above (gain).
              Dense at Day 0, fanning out as time progresses.
              Extreme outlier dots = the tail risks VaR/CVaR quantify.
            </div>""", unsafe_allow_html=True)

    # ──────────────────────────────────────────────────
    # TAB 3 · DISTRIBUTION & VaR
    # ──────────────────────────────────────────────────
    with tab3:
        cA, cB = st.columns([6, 4])
        with cA:
            st.markdown('<div class="section-title">Final Price Distribution</div>', unsafe_allow_html=True)
            fig_h = go.Figure()
            for arr, clr, nm in [
                (fp[fp < p5_final],                    "#ef4444", "Tail Loss (< P5)"),
                (fp[(fp>=p5_final)&(fp<S0)],            "#f97316", "Loss Zone"),
                (fp[(fp>=S0)&(fp<p75_final)],           "#4a9eff", "Gain Zone"),
                (fp[fp>=p75_final],                     "#22c55e", "Upper Gain"),
            ]:
                if len(arr) > 0:
                    fig_h.add_trace(go.Histogram(x=arr, nbinsx=70, histnorm="probability density",
                        marker=dict(color=clr, opacity=0.70), name=nm))
            try:
                kde2 = gaussian_kde(fp)
                xk   = np.linspace(fp.min()*0.97, fp.max()*1.03, 300)
                fig_h.add_trace(go.Scatter(x=xk, y=kde2(xk),
                    line=dict(color="#c9a96e", width=2.5), name="KDE", mode='lines'))
            except Exception:
                pass
            for xv, clr, lbl in [(S0,"rgba(255,255,255,0.6)",f"Current ₹{S0:,.0f}"),
                                  (mean_final,"#c9a96e",f"Mean ₹{mean_final:,.0f}"),
                                  (p5_final,"#ef4444",f"VaR{conf_level}%"),
                                  (p95_final,"#22c55e","P95")]:
                fig_h.add_vline(x=xv, line=dict(color=clr, width=1.2, dash="dash"),
                    annotation_text=lbl,
                    annotation_font=dict(color=clr, size=9, family="DM Mono"),
                    annotation_position="top")
            fig_h.update_layout(**dark_layout(
                title=dict(text=f"Final Price Distribution · {N:,} Simulations",
                    font=dict(family="Playfair Display",color="#c9a96e",size=14)),
                xaxis_title="Final Price (₹)", yaxis_title="Probability Density",
                barmode="overlay", height=420))
            st.plotly_chart(fig_h, use_container_width=True, config={"displayModeBar": False})

            st.markdown('<div class="section-title">Log Return Distribution — GBM Normality Validation</div>', unsafe_allow_html=True)
            lr    = np.log(fp / S0)
            x_n2  = np.linspace(float(lr.min()), float(lr.max()), 300)
            fig_lr= go.Figure()
            fig_lr.add_trace(go.Histogram(x=lr, nbinsx=80, histnorm="probability density",
                marker=dict(color="#3a5a7a", opacity=0.75), name="Log Returns"))
            fig_lr.add_trace(go.Scatter(x=x_n2, y=norm.pdf(x_n2,lr.mean(),lr.std()),
                line=dict(color="#c9a96e",width=2.2), name="Theoretical Normal", mode='lines'))
            fig_lr.add_vline(x=0, line=dict(color="rgba(255,255,255,0.35)",width=1,dash="dash"),
                annotation_text="Break-even",
                annotation_font=dict(color="#ffffff",size=9,family="DM Mono"))
            fig_lr.add_vline(x=-VaR_pct, line=dict(color="#ef4444",width=1,dash="dash"),
                annotation_text=f"VaR {conf_level}%",
                annotation_font=dict(color="#ef4444",size=9,family="DM Mono"))
            fig_lr.update_layout(**dark_layout(
                title=dict(text="Log Return Distribution · Normal Overlay",
                    font=dict(family="Playfair Display",color="#c9a96e",size=13)),
                xaxis_title="Log Return", yaxis_title="Density",
                barmode="overlay", height=320))
            st.plotly_chart(fig_lr, use_container_width=True, config={"displayModeBar": False})
            st.markdown('<div class="mc-interpret">Blue bars should closely match the gold curve — confirming the simulation math is correct. Perfect normal overlay validates GBM implementation.</div>', unsafe_allow_html=True)

        with cB:
            st.markdown('<div class="section-title">VaR &amp; CVaR — Risk Metrics</div>', unsafe_allow_html=True)
            st.markdown(f"""<div class="mc-card">
              <div class="kpi-label">VaR ({conf_level}% CONFIDENCE)</div>
              <div style="font-family:'DM Mono',monospace;font-size:2rem;color:#ef4444;margin:6px 0;">₹{VaR_abs:,.0f}</div>
              <div style="font-family:'DM Mono',monospace;font-size:0.85rem;color:rgba(239,68,68,0.6);">{VaR_pct*100:.2f}% of portfolio</div>
              <div style="height:16px"></div>
              <div class="kpi-label">CVaR / EXPECTED SHORTFALL ({conf_level}%)</div>
              <div style="font-family:'DM Mono',monospace;font-size:2rem;color:#dc2626;margin:6px 0;">₹{CVaR_abs:,.0f}</div>
              <div style="font-family:'DM Mono',monospace;font-size:0.85rem;color:rgba(239,68,68,0.5);">{CVaR_pct*100:.2f}% of portfolio</div>
              <div style="height:14px"></div>
              <div class="stat-row"><span class="stat-label">On ₹1 lakh</span>
                <span class="stat-val-red">VaR ₹{VaR_pct*100000:,.0f} · CVaR ₹{CVaR_pct*100000:,.0f}</span></div>
              <div class="stat-row"><span class="stat-label">On ₹10 lakh</span>
                <span class="stat-val-red">VaR ₹{VaR_pct*1000000:,.0f} · CVaR ₹{CVaR_pct*1000000:,.0f}</span></div>
            </div>""", unsafe_allow_html=True)
            st.markdown(f"""<div class="mc-risk">
              <strong>VaR {conf_level}%</strong> — worst {alpha*100:.0f}% of {N:,} sims lose more than
              <strong>{VaR_pct*100:.2f}%</strong> (₹{VaR_abs:,.0f}) over {T} days.<br><br>
              <strong>CVaR (Expected Shortfall)</strong> — when tail losses occur,
              the average damage is <strong>{CVaR_pct*100:.2f}%</strong> (₹{CVaR_abs:,.0f}).
              CVaR is always ≥ VaR and is the SEBI-preferred institutional risk metric.
            </div>""", unsafe_allow_html=True)

            st.markdown('<div class="section-title">All Confidence Levels</div>', unsafe_allow_html=True)
            rets = (fp - S0) / S0
            var_rows = []
            for cl in [90, 95, 99]:
                a2   = 1 - cl/100
                vp2  = float(-np.percentile(rets, a2*100))
                tm2  = rets < -vp2
                cv2  = float(-np.mean(rets[tm2])) if tm2.sum() > 0 else vp2
                var_rows.append({"Confidence": f"{cl}%", "VaR %": f"{vp2*100:.2f}%",
                    "VaR ₹": f"₹{vp2*S0:,.0f}", "CVaR %": f"{cv2*100:.2f}%", "CVaR ₹": f"₹{cv2*S0:,.0f}"})
            st.dataframe(pd.DataFrame(var_rows), hide_index=True, use_container_width=True)

    # ──────────────────────────────────────────────────
    # TAB 4 · OPTIONS PAYOFF
    # ──────────────────────────────────────────────────
    with tab4:
        cO1, cO2 = st.columns([55, 45])
        with cO1:
            st.markdown(f'<div class="section-title">{option_type} Option — Payoff Distribution (Risk-Neutral MC)</div>', unsafe_allow_html=True)
            itm_m = payoffs > 0
            otm_p = float((~itm_m).mean()*100)
            fig_o = go.Figure()
            if itm_m.sum() > 0:
                fig_o.add_trace(go.Histogram(x=payoffs[itm_m], nbinsx=60, histnorm="probability density",
                    marker=dict(color="#22c55e" if option_type=="Call" else "#ef4444", opacity=0.75),
                    name="ITM Payoff"))
            fig_o.add_annotation(x=0.98,y=0.95,xref="paper",yref="paper",
                text=f"OTM (worthless): {otm_p:.1f}% of sims",
                showarrow=False,font=dict(color="#6060a0",size=10,family="DM Mono"),align="right")
            fig_o.add_vline(x=mc_opt,line=dict(color="#c9a96e",width=1.5,dash="dash"),
                annotation_text=f"MC ₹{mc_opt:.2f}",
                annotation_font=dict(color="#c9a96e",size=10,family="DM Mono"))
            fig_o.add_vline(x=bs_price,line=dict(color="rgba(255,255,255,0.5)",width=1.5,dash="dot"),
                annotation_text=f"BS ₹{bs_price:.2f}",
                annotation_font=dict(color="#ffffff",size=10,family="DM Mono"))
            fig_o.update_layout(**dark_layout(
                title=dict(text=f"{option_type} Payoff Distribution · Strike ₹{K:,.0f} · {T}D",
                    font=dict(family="Playfair Display",color="#c9a96e",size=14)),
                xaxis_title="Payoff (₹)", yaxis_title="Density", height=380))
            st.plotly_chart(fig_o, use_container_width=True, config={"displayModeBar": False})

            st.markdown('<div class="section-title">Hockey-Stick Payoff Profile</div>', unsafe_allow_html=True)
            S_r  = np.linspace(S0*0.70, S0*1.30, 300)
            intr = np.maximum(S_r - K, 0) if option_type=="Call" else np.maximum(K - S_r, 0)
            pnl  = intr - mc_opt
            bev  = K + mc_opt if option_type=="Call" else K - mc_opt
            fig_hs = go.Figure()
            fig_hs.add_trace(go.Scatter(x=S_r, y=intr,
                line=dict(color="#22c55e" if option_type=="Call" else "#ef4444", width=2.5),
                name="Intrinsic Value"))
            fig_hs.add_trace(go.Scatter(x=S_r, y=pnl,
                line=dict(color="#4a9eff", width=2, dash='dash'),
                name="P&L at Expiry", fill='tozeroy', fillcolor='rgba(74,158,255,0.04)'))
            fig_hs.add_vline(x=S0,line=dict(color="rgba(255,255,255,0.35)",width=1,dash="dash"),
                annotation_text=f"Current",annotation_font=dict(color="#ffffff",size=9,family="DM Mono"))
            fig_hs.add_vline(x=K,line=dict(color="#c9a96e",width=1,dash="dash"),
                annotation_text=f"Strike ₹{K:,.0f}",annotation_font=dict(color="#c9a96e",size=9,family="DM Mono"))
            fig_hs.add_hline(y=0,line=dict(color="rgba(255,255,255,0.2)",width=1))
            fig_hs.update_layout(**dark_layout(
                title=dict(text=f"{option_type} Payoff Profile · Break-even ₹{bev:,.0f}",
                    font=dict(family="Playfair Display",color="#c9a96e",size=13)),
                xaxis_title="Underlying at Expiry (₹)", yaxis_title="P&L (₹)", height=300))
            st.plotly_chart(fig_hs, use_container_width=True, config={"displayModeBar": False})

        with cO2:
            st.markdown('<div class="section-title">Pricing Summary</div>', unsafe_allow_html=True)
            if pricing_err < 1:   badge = "<span class='badge-green'>✅ Excellent convergence (&lt;1%)</span>"
            elif pricing_err < 3: badge = "<span class='badge-gold'>✓ Good convergence (&lt;3%)</span>"
            else:                 badge = "<span class='badge-red'>⚠ Increase simulations</span>"
            st.markdown(f"""<div class="mc-card">
              <div style="display:flex;justify-content:space-between;margin-bottom:14px;">
                <div style="text-align:center;flex:1;">
                  <div class="kpi-label">MC PRICE</div>
                  <div style="font-family:'DM Mono',monospace;font-size:2rem;color:#c9a96e;">₹{mc_opt:.2f}</div>
                  <div class="kpi-sub">{N:,} risk-neutral paths</div>
                </div>
                <div style="text-align:center;flex:1;">
                  <div class="kpi-label">BLACK-SCHOLES</div>
                  <div style="font-family:'DM Mono',monospace;font-size:2rem;color:#4a9eff;">₹{bs_price:.2f}</div>
                  <div class="kpi-sub">Analytical</div>
                </div>
              </div>
              {badge}
              <div style="font-family:'DM Mono',monospace;font-size:0.72rem;color:#3a3a5a;margin-top:6px;">
                Diff: ₹{abs(mc_opt-bs_price):.2f} ({pricing_err:.2f}% error)
              </div>
            </div>""", unsafe_allow_html=True)

            mon  = "ITM" if ((option_type=="Call" and S0>K) or (option_type=="Put" and S0<K)) else "OTM"
            itmp = float((ST>K).mean()*100) if option_type=="Call" else float((ST<K).mean()*100)
            mxp  = "Unlimited" if option_type=="Call" else f"₹{(K-mc_opt):,.0f}"
            met_r= [("MONEYNESS",f"{mon} {abs(S0-K)/S0*100:.1f}% from strike"),
                    ("P(ITM AT EXPIRY)",f"{itmp:.1f}%"),
                    ("IV USED",f"{_sig*100:.1f}% annual"),
                    ("BREAK-EVEN",f"₹{bev:,.0f}"),
                    ("TIME TO EXPIRY",f"{T}D ({T/252*365:.0f} cal days)"),
                    ("MAX PROFIT",mxp),
                    ("MAX LOSS",f"₹{mc_opt:.2f} (premium)"),
                    ("RISK-FREE RATE",f"{rf_rate:.1f}%")]
            rows_h = "".join(f"""<div class="stat-row">
              <span class="stat-label">{l}</span>
              <span class="stat-val-gold">{v}</span></div>""" for l,v in met_r)
            st.markdown(f'<div class="mc-card">{rows_h}</div>', unsafe_allow_html=True)

            if option_type == "Call":
                st.markdown(f"""<div class="mc-interpret">
                  Paying <strong>₹{mc_opt:.2f}</strong> for the right to <strong>BUY</strong> {_inst}
                  at ₹{K:,.0f}. {itmp:.1f}% of {N:,} simulations end ITM.
                  Profitable above <strong>₹{bev:,.0f}</strong>.
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""<div class="mc-interpret">
                  Paying <strong>₹{mc_opt:.2f}</strong> for the right to <strong>SELL</strong> {_inst}
                  at ₹{K:,.0f}. {itmp:.1f}% of simulations end ITM.
                  Profitable below <strong>₹{bev:,.0f}</strong>.
                </div>""", unsafe_allow_html=True)

    # ──────────────────────────────────────────────────
    # TAB 5 · MATH EXPLAINED
    # ──────────────────────────────────────────────────
    with tab5:
        st.markdown('<div class="section-title">The Mathematics Behind MonteDesk</div>', unsafe_allow_html=True)
        m1, m2 = st.columns(2)
        with m1:
            st.markdown(f"""<div class="mc-card">
              <div class="section-title">The GBM Formula</div>
              <div class="mc-formula">P(t+1) = P(t) × exp( (μ − ½σ²)·Δt + σ·√Δt·Z )</div>
              <table class="mc-table">
                <tr><th>Symbol</th><th>Meaning</th><th>This Simulation</th></tr>
                <tr><td style="color:#c9a96e">P(t)</td><td>Price today</td><td style="color:#6060a0">₹{S0:,.0f}</td></tr>
                <tr><td style="color:#c9a96e">μ</td><td>Daily drift</td><td style="color:#6060a0">{mu_daily*100:.4f}%/day</td></tr>
                <tr><td style="color:#c9a96e">σ</td><td>Daily volatility</td><td style="color:#6060a0">{sigma_daily*100:.4f}%/day</td></tr>
                <tr><td style="color:#c9a96e">½σ²</td><td>Itô correction</td><td style="color:#6060a0">Prevents upward bias</td></tr>
                <tr><td style="color:#c9a96e">Δt</td><td>Time step</td><td style="color:#6060a0">1 trading day</td></tr>
                <tr><td style="color:#c9a96e">Z</td><td>Random shock N(0,1)</td><td style="color:#6060a0">New draw each step</td></tr>
                <tr><td style="color:#c9a96e">exp()</td><td>Exponential</td><td style="color:#6060a0">Price always &gt; 0</td></tr>
              </table>
            </div>""", unsafe_allow_html=True)
            st.markdown(f"""<div class="mc-interpret">
              <strong>{N:,} paths × {T} days = {N*T:,} random draws.</strong>
              Z = 0 → market moved as expected.
              Z = +2 → strong bullish day (2σ above mean).
              Z = −2 → sharp selloff.
              All outcomes together form the probability distribution.
            </div>""", unsafe_allow_html=True)

        with m2:
            x_n = np.linspace(-3, 3, 200)
            x_ln= np.linspace(0.01, 4, 200)
            fig_ln = make_subplots(cols=2,
                subplot_titles=["Normal — can go negative ❌","Log-Normal — always ≥ 0 ✅"])
            fig_ln.add_trace(go.Scatter(x=x_n,y=norm.pdf(x_n),line=dict(color="#ef4444",width=2),showlegend=False),row=1,col=1)
            fig_ln.add_trace(go.Scatter(x=x_n[x_n<0],y=norm.pdf(x_n[x_n<0]),
                fill='tozeroy',fillcolor='rgba(239,68,68,0.12)',
                line=dict(color="rgba(0,0,0,0)",width=0),showlegend=False),row=1,col=1)
            fig_ln.add_annotation(x=-1.5,y=0.08,text="Price < 0\nimpossible",showarrow=True,
                arrowhead=2,ax=0,ay=35,font=dict(color="#ef4444",size=9,family="DM Mono"),row=1,col=1)
            fig_ln.add_trace(go.Scatter(x=x_ln,y=stats.lognorm.pdf(x_ln,s=0.4),
                line=dict(color="#22c55e",width=2),showlegend=False),row=1,col=2)
            fig_ln.add_annotation(x=1.3,y=0.65,text="Price ≥ 0\nalways ✓",showarrow=True,
                arrowhead=2,ax=0,ay=-30,font=dict(color="#22c55e",size=9,family="DM Mono"),row=1,col=2)
            fig_ln.update_layout(paper_bgcolor="#09090e",plot_bgcolor="#111118",
                font=dict(family="DM Mono",color="#e8e8f0",size=10),
                height=260,margin=dict(l=30,r=20,t=45,b=20),
                xaxis=dict(gridcolor="rgba(255,255,255,0.04)"),
                yaxis=dict(gridcolor="rgba(255,255,255,0.04)"),
                xaxis2=dict(gridcolor="rgba(255,255,255,0.04)"),
                yaxis2=dict(gridcolor="rgba(255,255,255,0.04)"))
            for ann in fig_ln.layout.annotations:
                ann.font=dict(family="DM Mono",color="#6060a0",size=10)
            st.plotly_chart(fig_ln, use_container_width=True, config={"displayModeBar": False})
            st.markdown("""<div class="mc-interpret">
              GBM simulates <em>log returns</em> (can be negative), then exponentiates
              to recover prices — ensuring they are always positive. This is the log-normal property.
            </div>""", unsafe_allow_html=True)

        st.markdown('<div class="section-title">VaR vs CVaR — The Difference That Matters</div>', unsafe_allow_html=True)
        v1, v2 = st.columns([6,4])
        with v1:
            lr2   = np.log(fp / S0)
            vt    = -VaR_pct
            fig_v = go.Figure()
            for arr, clr, nm in [
                (lr2[lr2<vt], "#ef4444", f"CVaR Zone (worst {alpha*100:.0f}%)"),
                (lr2[(lr2>=vt)&(lr2<0)], "#f97316", "Loss Zone"),
                (lr2[lr2>=0], "#22c55e", "Gain Zone"),
            ]:
                if len(arr) > 0:
                    fig_v.add_trace(go.Histogram(x=arr,nbinsx=60,histnorm="probability density",
                        marker=dict(color=clr,opacity=0.72),name=nm))
            fig_v.add_vline(x=vt,line=dict(color="#c9a96e",width=1.5,dash="dash"),
                annotation_text=f"VaR {conf_level}% = {VaR_pct*100:.2f}%",
                annotation_font=dict(color="#c9a96e",size=10,family="DM Mono"),
                annotation_position="top right")
            cvar_x = float(np.mean(lr2[lr2<vt])) if (lr2<vt).sum()>0 else vt-0.05
            fig_v.add_annotation(x=cvar_x,y=0.4,text=f"CVaR\n{CVaR_pct*100:.2f}%",
                showarrow=True,arrowhead=2,ax=50,ay=-20,
                font=dict(color="#ef4444",size=10,family="DM Mono"))
            fig_v.update_layout(**dark_layout(
                title=dict(text="Return Distribution · VaR vs CVaR Zones",
                    font=dict(family="Playfair Display",color="#c9a96e",size=13)),
                xaxis_title="Log Return",yaxis_title="Density",barmode="overlay",height=340))
            st.plotly_chart(fig_v, use_container_width=True, config={"displayModeBar": False})
        with v2:
            st.markdown(f"""<div class="mc-card">
              <div class="section-title">VaR</div>
              <p style="font-size:0.88rem;color:#c8d8f0;line-height:1.7;">
                "Maximum loss with <strong>{conf_level}%</strong> confidence?"<br><br>
                Answer: <span style="color:#ef4444;font-family:'DM Mono',monospace">{VaR_pct*100:.2f}%</span>
                (₹{VaR_abs:,.0f})<br><br>
                But VaR says <strong>nothing</strong> about the remaining {alpha*100:.0f}% tail.
              </p>
              <hr style="border-color:rgba(201,169,110,0.1);margin:10px 0;">
              <div class="section-title">CVaR (Expected Shortfall)</div>
              <p style="font-size:0.88rem;color:#fca5a5;line-height:1.7;">
                "In the worst {alpha*100:.0f}%, what's the <em>average</em> loss?"<br><br>
                Answer: <span style="color:#dc2626;font-family:'DM Mono',monospace">{CVaR_pct*100:.2f}%</span>
                (₹{CVaR_abs:,.0f})<br><br>
                CVaR ≥ VaR always. Preferred by SEBI-regulated institutions.
              </p>
            </div>""", unsafe_allow_html=True)

        if _blend:
            st.markdown('<div class="section-title">Blended Volatility — Why VIX + Historical?</div>', unsafe_allow_html=True)
            b1, b2 = st.columns([5,5])
            with b1:
                fig_bv = go.Figure(go.Bar(
                    x=[_hv, _vix, _sig*100],
                    y=["Historical (Backward)", "VIX-Implied (Forward)", "Blended (Used)"],
                    orientation='h',
                    marker=dict(color=["#3a5a7a","#c9a96e","#4a9eff"]),
                    text=[f"{v:.2f}%" for v in [_hv, _vix, _sig*100]],
                    textposition='outside',
                    textfont=dict(family="DM Mono",color="#e8e8f0",size=11)))
                fig_bv.add_annotation(x=max(_hv,_vix,_sig*100)*0.5, y=-0.75,
                    text=f"σ = {_vw:.0%} × VIX + {1-_vw:.0%} × Historical = {_sig*100:.2f}%",
                    showarrow=False,font=dict(color="#6060a0",size=10,family="DM Mono"))
                fig_bv.update_layout(**dark_layout(
                    title=dict(text="Volatility Sources",font=dict(family="Playfair Display",color="#c9a96e",size=13)),
                    xaxis_title="Annual Vol (%)",height=260,
                    xaxis=dict(range=[0, max(_hv,_vix,_sig*100)*1.3])))
                fig_bv.update_yaxes(gridcolor="rgba(255,255,255,0.04)")
                st.plotly_chart(fig_bv, use_container_width=True, config={"displayModeBar": False})
            with b2:
                st.markdown(f"""<div class="mc-interpret">
                  <strong>Historical vol ({_hv:.1f}%)</strong> looks backward — what happened.<br><br>
                  <strong>VIX ({_vix:.1f}%)</strong> looks forward — options market's collective view
                  on future risk, aggregating thousands of traders.<br><br>
                  Weighting VIX at {_vw:.0%} reflects the institutional standard.
                  Pure historical vol systematically <em>understates</em> risk
                  during regime shifts and crisis events.
                </div>""", unsafe_allow_html=True)

        # Parameters banner
        st.markdown('<div class="section-title">All Parameters — This Simulation</div>', unsafe_allow_html=True)
        p1,p2,p3 = st.columns(3)
        for col, lines in [
            (p1, [f"Instrument: {_inst}", f"Starting Price: ₹{S0:,.0f}", f"Simulations: {N:,}", f"Horizon: {T}D ({T/252*12:.1f} months)"]),
            (p2, [f"Annual Vol (σ): {_sig*100:.2f}%", f"Daily Vol (σ): {sigma_daily*100:.4f}%", f"Annual Drift (μ): {mu_ann*100:.2f}%", f"Daily Drift (μ): {mu_daily*100:.4f}%"]),
            (p3, [f"VaR Confidence: {conf_level}%", f"VaR: ₹{VaR_abs:,.0f} ({VaR_pct*100:.2f}%)", f"CVaR: ₹{CVaR_abs:,.0f} ({CVaR_pct*100:.2f}%)", f"Risk-free: {rf_rate:.2f}%"]),
        ]:
            with col:
                st.markdown(f"""<div style="background:#080810;border:1px solid rgba(201,169,110,0.12);border-radius:8px;
                  padding:14px 18px;font-family:'DM Mono',monospace;font-size:0.8rem;color:#6060a0;line-height:2;">
                  {'<br>'.join(lines)}</div>""", unsafe_allow_html=True)

    # ──────────────────────────────────────────────────
    # TAB 6 · PROBABILITY TABLE
    # ──────────────────────────────────────────────────
    with tab6:
        st.markdown(f'<div class="section-title">Scenario Probability Grid — {_inst} by Day {T}</div>', unsafe_allow_html=True)
        pct_lvls = [-20,-15,-10,-7,-5,-3,-2,-1,0,1,2,3,5,7,10,15,20]
        prob_rows = []
        for pct in pct_lvls:
            tgt  = S0 * (1 + pct/100)
            prob = float(np.mean(fp >= tgt)*100) if pct >= 0 else float(np.mean(fp <= tgt)*100)
            if   prob>70: interp="Very Likely ✅"
            elif prob>55: interp="More Likely 📈"
            elif prob>45: interp="Roughly Even ⚖️"
            elif prob>30: interp="Less Likely 📉"
            elif prob>15: interp="Unlikely ⚠️"
            else:         interp="Very Unlikely 🔴"
            prob_rows.append({"Scenario":f"{pct:+.0f}% move","Target (₹)":f"₹{tgt:,.0f}",
                "Change":f"{pct:+.0f}%","Probability":f"{prob:.1f}%","Interpretation":interp,
                "_prob":prob,"_pct":pct})
        for mult, lbl in [(0.80,"−20% scenario"),(0.85,"−15% zone"),(0.90,"−10% zone"),
                           (1.05,"+5% zone"),(1.10,"+10% zone"),(1.20,"+20% scenario")]:
            lvl  = round(S0*mult/500)*500
            pct2 = (lvl/S0-1)*100
            p2   = float(np.mean(fp >= lvl)*100) if pct2>=0 else float(np.mean(fp <= lvl)*100)
            if   p2>70: i2="Very Likely ✅"
            elif p2>55: i2="More Likely 📈"
            elif p2>45: i2="Roughly Even ⚖️"
            elif p2>30: i2="Less Likely 📉"
            elif p2>15: i2="Unlikely ⚠️"
            else:       i2="Very Unlikely 🔴"
            prob_rows.append({"Scenario":f"Key level ₹{lvl:,.0f} ({lbl})","Target (₹)":f"₹{lvl:,.0f}",
                "Change":f"{pct2:+.1f}%","Probability":f"{p2:.1f}%","Interpretation":i2,
                "_prob":p2,"_pct":pct2})
        prob_rows.sort(key=lambda x: x["_pct"])

        ct, cb = st.columns([5,5])
        with ct:
            df_p = pd.DataFrame([{k:v for k,v in r.items() if not k.startswith("_")} for r in prob_rows])
            def _cp(val):
                try:
                    p = float(val.strip('%'))
                    if p>55: return 'color:#22c55e'
                    if p<45: return 'color:#ef4444'
                    return 'color:#c9a96e'
                except: return ''
            st.dataframe(df_p.style.map(_cp,subset=["Probability"]),
                hide_index=True, use_container_width=True, height=620)
        with cb:
            bls  = [r["Scenario"][:30] for r in prob_rows]
            bps  = [r["_prob"] for r in prob_rows]
            bcs  = ["#22c55e" if p>55 else "#ef4444" if p<45 else "#c9a96e" for p in bps]
            fig_b = go.Figure(go.Bar(x=bps,y=bls,orientation='h',
                marker=dict(color=bcs,opacity=0.8),
                text=[f"{p:.1f}%" for p in bps],textposition='outside',
                textfont=dict(family="DM Mono",color="#e8e8f0",size=9)))
            fig_b.add_vline(x=50,line=dict(color="rgba(255,255,255,0.25)",width=1,dash="dash"),
                annotation_text="50%",annotation_font=dict(color="#6060a0",size=9,family="DM Mono"))
            fig_b.update_layout(**dark_layout(
                title=dict(text="Probability by Scenario",font=dict(family="Playfair Display",color="#c9a96e",size=13)),
                xaxis_title="Probability (%)",
                xaxis=dict(range=[0,max(bps)*1.28]),
                height=620,margin=dict(l=10,r=65,t=50,b=40)))
            st.plotly_chart(fig_b, use_container_width=True, config={"displayModeBar": False})

        s1, s2 = st.columns(2)
        with s1:
            st.markdown(f"""<div class="mc-interpret-green">
              Most likely zone: <strong>₹{p25_final:,.0f} → ₹{p75_final:,.0f}</strong>
              (IQR — 50% of {N:,} simulations land here).
              Central projection: ₹{mean_final:,.0f} ({exp_ret_pct:+.1f}% from current).
            </div>""", unsafe_allow_html=True)
        with s2:
            w1 = float(np.percentile(fp,1)); b1 = float(np.percentile(fp,99))
            st.markdown(f"""<div class="mc-risk">
              ⚠️ Tail Risk · {alpha*100:.0f}% chance loss &gt; {VaR_pct*100:.2f}% (VaR)<br>
              Avg tail loss: {CVaR_pct*100:.2f}% (CVaR)<br>
              Worst 1%: ₹{w1:,.0f} ({(w1/S0-1)*100:.1f}%)<br>
              Best 1%: ₹{b1:,.0f} (+{(b1/S0-1)*100:.1f}%)
            </div>""", unsafe_allow_html=True)

    # ── FOOTER ─────────────────────────────────────────
    st.markdown("""<div class="footer-bar">
      <div class="footer-text">
        🎲 MonteDesk · Day 25 of 30 Days of AI Finance · Built by @Preethams321 · SJCC Bengaluru<br>
        ⚠️ For educational purposes only — not financial advice — all simulations are mathematical models — past volatility ≠ future volatility<br>
        Week 4: Derivatives &amp; Automation · StratEdge · BSDesk · ChainDesk · MonteDesk
      </div>
    </div>""", unsafe_allow_html=True)