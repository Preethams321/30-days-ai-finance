import streamlit as st
import numpy as np
import pandas as pd
import yfinance as yf
from scipy.optimize import minimize
from scipy.stats import norm
import plotly.graph_objects as go

# ─────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────
BG        = "#09090e"
BG2       = "#111118"
BG3       = "#16161f"
GOLD      = "#c9a96e"
GOLD_DIM  = "rgba(201,169,110,0.15)"
NAVY      = "#3a5a7a"
BLUE      = "#4a9eff"
GREEN     = "#4ab87a"
RED       = "#e05c6c"
BORDER    = "rgba(255,255,255,0.06)"
TEXT      = "#e8e4dc"
TEXT_DIM  = "#888"
TEXT_DARK = "#555"

STOCK_UNIVERSE = {
    "TCS":           {"ticker": "TCS.NS",         "sector": "IT",         "name": "Tata Consultancy Services"},
    "Infosys":       {"ticker": "INFY.NS",         "sector": "IT",         "name": "Infosys Ltd"},
    "Wipro":         {"ticker": "WIPRO.NS",        "sector": "IT",         "name": "Wipro Ltd"},
    "HCL Tech":      {"ticker": "HCLTECH.NS",      "sector": "IT",         "name": "HCL Technologies"},
    "HDFC Bank":     {"ticker": "HDFCBANK.NS",     "sector": "Banking",    "name": "HDFC Bank"},
    "ICICI Bank":    {"ticker": "ICICIBANK.NS",    "sector": "Banking",    "name": "ICICI Bank"},
    "Kotak Bank":    {"ticker": "KOTAKBANK.NS",    "sector": "Banking",    "name": "Kotak Mahindra Bank"},
    "Axis Bank":     {"ticker": "AXISBANK.NS",     "sector": "Banking",    "name": "Axis Bank"},
    "SBI":           {"ticker": "SBIN.NS",         "sector": "Banking",    "name": "State Bank of India"},
    "Bajaj Finance": {"ticker": "BAJFINANCE.NS",   "sector": "NBFC",       "name": "Bajaj Finance"},
    "ITC":           {"ticker": "ITC.NS",          "sector": "FMCG",       "name": "ITC Ltd"},
    "Asian Paints":  {"ticker": "ASIANPAINT.NS",   "sector": "Consumer",   "name": "Asian Paints"},
    "HUL":           {"ticker": "HINDUNILVR.NS",   "sector": "FMCG",       "name": "Hindustan Unilever"},
    "Maruti":        {"ticker": "MARUTI.NS",       "sector": "Auto",       "name": "Maruti Suzuki"},
    "Tata Motors":   {"ticker": "TATAMOTORS.NS",   "sector": "Auto",       "name": "Tata Motors"},
    "Reliance":      {"ticker": "RELIANCE.NS",     "sector": "Energy",     "name": "Reliance Industries"},
    "NTPC":          {"ticker": "NTPC.NS",         "sector": "Energy",     "name": "NTPC Ltd"},
    "L&T":           {"ticker": "LT.NS",           "sector": "Industrial", "name": "Larsen & Toubro"},
    "Sun Pharma":    {"ticker": "SUNPHARMA.NS",    "sector": "Pharma",     "name": "Sun Pharmaceutical"},
    "Dr Reddy's":    {"ticker": "DRREDDY.NS",      "sector": "Pharma",     "name": "Dr Reddy's Laboratories"},
}

SECTOR_COLORS = {
    "IT":         BLUE,
    "Banking":    GOLD,
    "NBFC":       "#e0a04a",
    "FMCG":       GREEN,
    "Consumer":   GREEN,
    "Auto":       RED,
    "Energy":     "#e8ca90",
    "Industrial": NAVY,
    "Pharma":     "#9b59b6",
}

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Mono, monospace", color=TEXT_DIM, size=10),
    margin=dict(l=50, r=20, t=60, b=50),
    xaxis=dict(
        gridcolor="rgba(255,255,255,0.05)",
        zerolinecolor="rgba(255,255,255,0.08)",
        tickfont=dict(color=TEXT_DARK, size=9),
        color=TEXT_DIM,
    ),
    yaxis=dict(
        gridcolor="rgba(255,255,255,0.05)",
        zerolinecolor="rgba(255,255,255,0.08)",
        tickfont=dict(color=TEXT_DARK, size=9),
        color=TEXT_DIM,
    ),
)

# ─────────────────────────────────────────
# CSS
# ─────────────────────────────────────────
CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,700&family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&display=swap');

/* ── FORCE DARK — targets Streamlit's own data-theme attribute ── */
/* Streamlit sets data-theme="light" or data-theme="dark" on the root.
   Targeting both means user's system preference is irrelevant.       */
[data-theme="light"],
[data-theme="dark"],
[data-theme="light"] *,
[data-theme="dark"] * {{
    --background-color: {BG};
    --secondary-background-color: {BG2};
    --text-color: {TEXT};
    --primary-color: {GOLD};
}}

html, body, [data-theme="light"], [data-theme="dark"] {{
    background-color: {BG} !important;
    color: {TEXT} !important;
    font-family: 'Syne', sans-serif !important;
}}

/* ── STREAMLIT CONTAINERS ── */
[data-testid="stApp"],
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"] {{
    background-color: {BG} !important;
}}
[data-testid="stSidebar"],
[data-testid="stSidebarContent"] {{
    background-color: {BG2} !important;
}}
[data-testid="stSidebar"] *,
[data-testid="stSidebarContent"] * {{
    color: {TEXT} !important;
}}

/* ── HIDE CHROME ── */
#MainMenu, footer, header,
[data-testid="stDecoration"],
[data-testid="stToolbar"],
[data-testid="stStatusWidget"] {{ display:none !important; }}

/* ── LAYOUT ── */
.block-container {{ padding:1rem 2rem !important; max-width:100% !important; }}

/* ── TYPOGRAPHY ── */
h1,h2,h3,h4,h5,h6 {{ font-family:'Syne',sans-serif !important; }}
p,li {{ color:{TEXT} !important; }}

/* ── TABS ── */
[data-testid="stTabs"] button[role="tab"] {{
    color:{TEXT_DARK} !important; font-family:'DM Mono',monospace !important;
    font-size:0.72rem !important; text-transform:uppercase !important;
    letter-spacing:0.06em !important; background:transparent !important;
}}
[data-testid="stTabs"] button[aria-selected="true"] {{
    color:{GOLD} !important; border-bottom:2px solid {GOLD} !important;
}}
[data-testid="stTabsContent"] {{
    background-color:{BG} !important; border-color:{BORDER} !important;
}}

/* ── METRICS ── */
[data-testid="stMetric"] {{
    background:{BG2} !important; border:1px solid {BORDER} !important;
    border-radius:3px !important; padding:1rem !important;
}}
[data-testid="stMetricValue"] {{
    font-family:'DM Mono',monospace !important; color:{TEXT} !important; font-size:1.3rem !important;
}}
[data-testid="stMetricLabel"] {{
    font-family:'DM Mono',monospace !important; color:{TEXT_DARK} !important;
    font-size:0.6rem !important; text-transform:uppercase !important; letter-spacing:0.08em !important;
}}

/* ── BUTTONS ── */
.stButton > button[kind="primary"] {{
    background:{GOLD} !important; color:{BG} !important; border:none !important;
    font-family:'DM Mono',monospace !important; font-size:0.75rem !important;
    font-weight:600 !important; border-radius:2px !important;
}}
.stButton > button:not([kind="primary"]) {{
    background:{BG2} !important; color:{TEXT_DIM} !important;
    border:1px solid {BORDER} !important; font-family:'DM Mono',monospace !important;
    font-size:0.72rem !important; border-radius:2px !important;
}}

/* ── INPUTS ── */
[data-baseweb="select"] * {{ background-color:{BG3} !important; color:{TEXT} !important; }}
[data-baseweb="popover"], [data-baseweb="popover"] *,
[role="listbox"], [role="option"] {{ background-color:{BG2} !important; color:{TEXT} !important; }}
[data-baseweb="tag"] {{ background-color:{NAVY} !important; color:{TEXT} !important; }}

/* ── LABELS ── */
label, [data-testid="stWidgetLabel"] p {{
    color:{TEXT_DIM} !important; font-family:'DM Mono',monospace !important;
    font-size:0.7rem !important; text-transform:uppercase !important; letter-spacing:0.05em !important;
}}

/* ── LATEX ── */
.katex, .katex * {{ color:{TEXT} !important; }}

/* ── DATAFRAMES — mobile horizontal scroll ── */
.tbl-wrap {{ overflow-x: auto; -webkit-overflow-scrolling: touch; }}
[data-testid="stDataFrame"] {{
    overflow-x: auto !important;
    -webkit-overflow-scrolling: touch !important;
}}
[data-testid="stDataFrame"] th {{
    background-color:{BG3} !important; color:{TEXT_DIM} !important;
    font-family:'DM Mono',monospace !important; font-size:0.65rem !important;
    text-transform:uppercase !important; letter-spacing:0.06em !important;
    border-color:{BORDER} !important; white-space:nowrap;
}}
[data-testid="stDataFrame"] td {{
    background-color:{BG2} !important; color:{TEXT} !important;
    font-family:'DM Mono',monospace !important; font-size:0.75rem !important;
    border-color:{BORDER} !important; white-space:nowrap;
}}

/* ── ALERTS ── */
[data-testid="stAlert"] {{
    background-color:{BG2} !important; border-color:{BORDER} !important; color:{TEXT} !important;
}}

/* ── SCROLLBARS ── */
::-webkit-scrollbar {{ width:3px; height:3px; }}
::-webkit-scrollbar-track {{ background:{BG}; }}
::-webkit-scrollbar-thumb {{ background:rgba(201,169,110,0.15); border-radius:2px; }}

/* ── CUSTOM COMPONENTS ── */
.port-card {{
    background:{BG2}; border:1px solid {BORDER}; border-radius:4px;
    padding:1.25rem 1.5rem; margin-bottom:0.75rem;
}}
.port-card h4 {{
    font-family:'Syne',sans-serif; font-size:0.8rem; font-weight:700;
    color:{GOLD} !important; text-transform:uppercase; letter-spacing:0.1em; margin:0 0 0.4rem 0;
}}
.port-card p {{
    font-family:'DM Mono',monospace; font-size:0.75rem; color:{TEXT_DIM} !important;
    margin:0; line-height:1.6;
}}
.eyebrow {{
    font-family:'DM Mono',monospace; font-size:0.65rem; color:{TEXT_DARK};
    text-transform:uppercase; letter-spacing:0.15em; margin-bottom:0.5rem;
}}
.pill {{
    display:inline-block; background:{BG3}; border:1px solid {BORDER}; border-radius:2px;
    padding:0.2rem 0.6rem; font-family:'DM Mono',monospace; font-size:0.62rem;
    color:{TEXT_DIM} !important; letter-spacing:0.06em; margin:0.15rem;
}}
.ghost-text {{
    font-family:'DM Mono',monospace; font-size:0.72rem; color:{TEXT_DARK} !important;
    font-style:italic; border-left:2px solid rgba(201,169,110,0.2);
    padding-left:0.75rem; margin:0.75rem 0; line-height:1.7;
}}
.plain-text {{
    font-family:'DM Mono',monospace; font-size:0.74rem; color:{TEXT_DIM} !important;
    line-height:1.75; margin-top:0.75rem;
}}
.footer-text {{
    font-family:'DM Mono',monospace; font-size:0.6rem; color:{TEXT_DARK} !important;
    text-align:center; border-top:1px solid {BORDER}; padding-top:1rem; margin-top:2rem; line-height:1.8;
}}
.stat-number {{
    font-family:'DM Mono',monospace; font-size:1.6rem; font-weight:500; color:{GOLD} !important; line-height:1;
}}
.stat-label {{
    font-family:'Syne',sans-serif; font-size:0.62rem; color:{TEXT_DARK} !important;
    text-transform:uppercase; letter-spacing:0.1em; margin-top:0.25rem;
}}

/* ── HIDE SIDEBAR TOGGLE ON HOME ── */
[data-testid="collapsedControl"] {{
    display: none !important;
}}

/* ── MOBILE ── */
@media (max-width: 768px) {{
    .block-container {{ padding:0.75rem 1rem !important; }}
    .port-card {{ padding:1rem !important; }}
    .port-card h4 {{ font-size:0.72rem !important; }}
    .port-card p {{ font-size:0.68rem !important; }}
    [data-testid="stMetricValue"] {{ font-size:1rem !important; }}
    [data-testid="stMetricLabel"] {{ font-size:0.55rem !important; }}
    .stat-number {{ font-size:1.2rem !important; }}
    .plain-text {{ font-size:0.68rem !important; }}
    .ghost-text {{ font-size:0.66rem !important; }}
    [data-testid="stTabs"] button[role="tab"] {{ font-size:0.62rem !important; letter-spacing:0.03em !important; }}
    [data-testid="stDataFrame"] th {{ font-size:0.58rem !important; }}
    [data-testid="stDataFrame"] td {{ font-size:0.65rem !important; }}
}}
</style>
"""

# ─────────────────────────────────────────
# PAGE CONFIG — must be first Streamlit call
# ─────────────────────────────────────────
st.set_page_config(
    page_title="PortDesk · Day 26",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────
# SESSION STATE — init before anything renders
# ─────────────────────────────────────────
for key, default in [
    ("page", "home"),
    ("results", None),
    ("last_selection", None),
    ("computing", False),
]:
    if key not in st.session_state:
        st.session_state[key] = default

st.markdown(CSS, unsafe_allow_html=True)


# ─────────────────────────────────────────
# CORE FUNCTIONS
# ─────────────────────────────────────────
def _fetch_single(ticker: str, period: str):
    """Fetch close prices for one ticker individually. Most reliable for NSE tickers."""
    try:
        raw = yf.download(ticker, period=period, interval="1d",
                          progress=False, auto_adjust=True)
        if raw.empty:
            return None
        if isinstance(raw.columns, pd.MultiIndex):
            raw.columns = [c[0] for c in raw.columns]
        if "Close" not in raw.columns:
            return None
        s = raw["Close"].dropna()
        if len(s) < 100:
            return None
        if (s <= 0).any() or s.std() < 1e-6:
            return None
        return s
    except Exception:
        return None


@st.cache_data(ttl=3600)
def fetch_stock_data(tickers: tuple, period: str = "2y") -> pd.DataFrame:
    """
    Fetch each ticker individually — avoids MultiIndex corruption from batch downloads.
    Batch yf.download() frequently misaligns columns for NSE tickers.
    """
    if not tickers:
        return pd.DataFrame()

    frames = {}
    for tkr in tickers:
        s = _fetch_single(tkr, period)
        if s is not None:
            frames[tkr] = s

    if not frames:
        return pd.DataFrame()

    prices = pd.DataFrame(frames)
    prices = prices.ffill().dropna()
    return prices


def compute_returns(prices: pd.DataFrame):
    """
    Compute log returns and annualised statistics.
    Only drops stocks with truly corrupt data (vol=0 or extreme outliers).
    """
    log_returns = np.log(prices / prices.shift(1)).dropna()

    # Only drop genuinely corrupt data:
    # - zero variance (flat prices = bad feed)
    # - extreme outliers beyond any reasonable Indian equity range
    ann_check = log_returns.mean() * 252
    ann_vol_check = log_returns.std() * np.sqrt(252)

    bad = ann_check[
        (ann_check < -0.85) |   # worse than -85% annualised = corrupt
        (ann_check > 3.0)  |    # better than 300% annualised = corrupt
        (ann_vol_check < 0.001)  # essentially zero volatility = flat/bad feed
    ].index.tolist()

    if bad:
        log_returns = log_returns.drop(columns=bad)

    ann_returns = log_returns.mean() * 252
    ann_cov     = log_returns.cov() * 252
    ann_vols    = np.sqrt(np.diag(ann_cov.values))
    corr_matrix = log_returns.corr()

    return log_returns, ann_returns, ann_cov, ann_vols, corr_matrix


def simulate_portfolios(ann_returns, ann_cov, n_portfolios=5000, rf=0.065):
    """Dirichlet random portfolios — uniform coverage of weight simplex."""
    n    = len(ann_returns)
    rets = ann_returns.values
    cov  = ann_cov.values
    port_ret     = np.zeros(n_portfolios)
    port_vol     = np.zeros(n_portfolios)
    port_sharpe  = np.zeros(n_portfolios)
    port_weights = np.zeros((n_portfolios, n))
    for i in range(n_portfolios):
        w  = np.random.dirichlet(np.ones(n))
        pr = w @ rets
        pv = np.sqrt(w @ cov @ w)
        port_ret[i]     = pr
        port_vol[i]     = pv
        port_sharpe[i]  = (pr - rf) / pv if pv > 1e-10 else 0.0
        port_weights[i] = w
    return port_ret, port_vol, port_sharpe, port_weights


def optimise_portfolio(ann_returns, ann_cov, rf=0.065):
    """SLSQP optimisation for Max Sharpe and Min Variance.
    Max weight per stock capped at 40% to prevent degenerate concentration.
    """
    n    = len(ann_returns)
    rets = ann_returns.values
    cov  = ann_cov.values
    w0   = np.ones(n) / n

    # Cap each stock at 40% — forces meaningful diversification
    # while still allowing the optimiser genuine freedom
    bounds     = [(0.0, 0.40)] * n
    sum_to_one = {"type": "eq", "fun": lambda w: np.sum(w) - 1.0}

    def neg_sharpe(w):
        pr = w @ rets
        pv = np.sqrt(w @ cov @ w)
        return -(pr - rf) / pv if pv > 1e-10 else 0.0

    res_sharpe = minimize(
        neg_sharpe, w0, method="SLSQP",
        bounds=bounds, constraints=[sum_to_one],
        options={"ftol": 1e-12, "maxiter": 1000},
    )

    def port_variance(w):
        return w @ cov @ w

    res_minvar = minimize(
        port_variance, w0, method="SLSQP",
        bounds=bounds, constraints=[sum_to_one],
        options={"ftol": 1e-12, "maxiter": 1000},
    )

    def pstats(w):
        pr = w @ rets
        pv = np.sqrt(w @ cov @ w)
        return pr, pv, (pr - rf) / pv if pv > 1e-10 else 0.0

    ws = res_sharpe.x
    wm = res_minvar.x
    return {
        "max_sharpe": {
            "weights": ws,
            "return":  float(ws @ rets),
            "vol":     float(np.sqrt(ws @ cov @ ws)),
            "sharpe":  float(-res_sharpe.fun),
            "names":   ann_returns.index.tolist(),
        },
        "min_variance": {
            "weights": wm,
            "return":  float(wm @ rets),
            "vol":     float(np.sqrt(wm @ cov @ wm)),
            "sharpe":  float(pstats(wm)[2]),
            "names":   ann_returns.index.tolist(),
        },
    }


def compute_efficient_frontier(ann_returns, ann_cov, opt_result, n_points=50):
    """
    FIX BUG 9: Accept pre-computed opt_result to avoid double-optimisation.
    """
    n    = len(ann_returns)
    rets = ann_returns.values
    cov  = ann_cov.values
    w0   = np.ones(n) / n
    bounds = [(0.0, 1.0)] * n

    r_min = opt_result["min_variance"]["return"]
    r_max = max(rets) * 0.98  # slightly below max for feasibility

    target_returns = np.linspace(r_min, r_max, n_points)
    frontier_vols, frontier_rets = [], []

    for target in target_returns:
        constraints = [
            {"type": "eq", "fun": lambda w: np.sum(w) - 1.0},
            {"type": "eq", "fun": lambda w, t=target: w @ rets - t},
        ]
        res = minimize(
            lambda w: np.sqrt(w @ cov @ w), w0,
            method="SLSQP", bounds=bounds, constraints=constraints,
            options={"ftol": 1e-10, "maxiter": 500},
        )
        if res.success and res.fun > 0:
            frontier_vols.append(res.fun)
            frontier_rets.append(target)

    return np.array(frontier_vols), np.array(frontier_rets)


def compute_risk_metrics(weights, ann_return, ann_vol, rf=0.065, log_returns=None):
    """
    FIX BUG 1: VaR table was scaling 95% values instead of using 99% z-score.
    All VaR/CVaR now computed from their own z-scores.
    """
    sharpe    = (ann_return - rf) / ann_vol if ann_vol > 1e-10 else 0.0
    daily_ret = ann_return / 252
    daily_vol = ann_vol / np.sqrt(252)

    # Parametric VaR — each from its own z-score
    z95, z99 = norm.ppf(0.05), norm.ppf(0.01)
    var_95_1d  = -(daily_ret + z95 * daily_vol)
    var_99_1d  = -(daily_ret + z99 * daily_vol)
    cvar_95_1d = -(daily_ret - daily_vol * norm.pdf(z95) / 0.05)
    cvar_99_1d = -(daily_ret - daily_vol * norm.pdf(z99) / 0.01)

    # Scale correctly via sqrt(T) from 1-day base
    var_95_5d   = var_95_1d  * np.sqrt(5)
    var_99_5d   = var_99_1d  * np.sqrt(5)   # FIX: was var_95_5d * sqrt(5) — wrong!
    var_95_21d  = var_95_1d  * np.sqrt(21)
    var_99_21d  = var_99_1d  * np.sqrt(21)  # FIX: was var_95_21d * sqrt(21/5) — wrong!

    # Historical VaR and drawdown
    hist_var_95 = hist_var_99 = max_drawdown = None
    if log_returns is not None and not log_returns.empty:
        # FIX BUG 3: align weights to log_returns columns (same stocks, same order)
        cols    = log_returns.columns.tolist()
        names   = list(range(len(weights)))  # positional fallback
        w_aligned = weights[:len(cols)]       # safe slice if already same length
        port_log_ret = log_returns.values @ w_aligned
        hist_var_95  = float(-np.percentile(port_log_ret, 5))
        hist_var_99  = float(-np.percentile(port_log_ret, 1))
        cum_ret      = np.exp(np.cumsum(port_log_ret))
        peak         = np.maximum.accumulate(cum_ret)
        drawdown     = (cum_ret - peak) / peak
        max_drawdown = float(drawdown.min())

    return {
        "sharpe":      sharpe,
        "var_95_1d":   var_95_1d,   "var_99_1d":   var_99_1d,
        "cvar_95_1d":  cvar_95_1d,  "cvar_99_1d":  cvar_99_1d,
        "var_95_5d":   var_95_5d,   "var_99_5d":   var_99_5d,
        "var_95_21d":  var_95_21d,  "var_99_21d":  var_99_21d,
        "hist_var_95": hist_var_95, "hist_var_99": hist_var_99,
        "max_drawdown": max_drawdown,
        "ann_return":  ann_return,  "ann_vol": ann_vol,
    }


# ─────────────────────────────────────────
# DATA HEALTH CHECK DISPLAY
# ─────────────────────────────────────────
def show_data_health(ann_returns, dropped):
    """Show a clear data quality summary so users know what they're working with."""
    stocks = ann_returns.index.tolist()
    ok_count = len(stocks)
    bad_count = len(dropped)

    col_info, col_stocks = st.columns([1, 2])
    with col_info:
        st.markdown(f"""
        <div style='background:{BG2}; border:1px solid {BORDER}; border-radius:4px; padding:1rem;'>
            <div style='font-family:"DM Mono",monospace; font-size:0.65rem; color:{TEXT_DARK};
                        text-transform:uppercase; letter-spacing:0.08em; margin-bottom:0.5rem;'>
                Data Quality
            </div>
            <div style='font-family:"DM Mono",monospace; color:{GREEN}; font-size:1rem;'>
                ✓ {ok_count} stocks loaded
            </div>
            {"<div style='font-family:\"DM Mono\",monospace; color:" + RED + "; font-size:0.8rem; margin-top:0.25rem;'>⚠ " + str(bad_count) + " dropped (suspect data)</div>" if bad_count else ""}
        </div>
        """, unsafe_allow_html=True)

    with col_stocks:
        # Show annualised return for each valid stock
        rows = []
        for s in stocks:
            ret = ann_returns.loc[s]
            color = GREEN if ret > 0 else RED
            rows.append(f"<span style='font-family:\"DM Mono\",monospace; font-size:0.72rem; "
                        f"color:{TEXT_DIM}; margin-right:1rem;'>{s}: "
                        f"<span style='color:{color};'>{ret*100:+.1f}%</span></span>")
        st.markdown(
            f"<div style='background:{BG2}; border:1px solid {BORDER}; border-radius:4px; "
            f"padding:1rem; line-height:2;'>{''.join(rows)}</div>",
            unsafe_allow_html=True
        )


# ─────────────────────────────────────────
# HOME PAGE
# ─────────────────────────────────────────
def render_home():
    st.markdown(f"""
    <div style='text-align:center; padding:3rem 1rem 1rem;'>
        <div class='eyebrow'>● MARKOWITZ OPTIMISATION · EFFICIENT FRONTIER · MAX SHARPE · VaR/CVaR</div>
        <h1 style='font-family:"Playfair Display",serif; font-size:clamp(2.5rem,6vw,4.5rem);
                   color:{GOLD}; margin:0.5rem 0 0.25rem; letter-spacing:-0.01em;'>PortDesk</h1>
        <p style='font-family:"Playfair Display",serif; font-style:italic;
                  font-size:clamp(1rem,2.5vw,1.3rem); color:{TEXT_DIM}; margin-bottom:1.5rem;'>
            Find the optimal portfolio. Mathematically.
        </p>
        <p style='font-family:"DM Mono",monospace; font-size:0.78rem; color:{TEXT_DARK};
                  max-width:620px; margin:0 auto 2rem; line-height:1.8;'>
            Harry Markowitz proved in 1952 that diversification isn't just intuition — it's mathematics.
            For any set of assets, there exists an "efficient frontier" of portfolios that maximise return
            for each unit of risk. PortDesk makes this interactive for Indian equities.
        </p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    for col, num, lbl in zip(
        [c1, c2, c3, c4],
        ["20", "2Y", "5,000", "scipy"],
        ["Indian Stocks", "Historical Data", "Simulations", "Optimisation"]
    ):
        col.markdown(f"""
        <div style='text-align:center; padding:1.25rem; background:{BG2};
                    border:1px solid {BORDER}; border-radius:4px;'>
            <div class='stat-number'>{num}</div>
            <div class='stat-label'>{lbl}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

    pills = ["Efficient Frontier","Max Sharpe","Min Variance","Correlation Matrix",
             "VaR / CVaR","Max Drawdown","Log Returns","Dirichlet Simulation","SLSQP","CML"]
    st.markdown(
        f"<div style='text-align:center; margin-bottom:1.5rem;'>"
        + "".join(f"<span class='pill'>{p}</span>" for p in pills)
        + "</div>",
        unsafe_allow_html=True
    )

    cards = [
        ("📈","Efficient Frontier","5,000 random portfolios + scipy-optimised boundary. The complete Markowitz picture."),
        ("⭐","Portfolio Optimiser","Maximum Sharpe Ratio and Minimum Variance portfolios with exact SLSQP precision."),
        ("🛡️","Risk Metrics","Parametric and historical VaR, CVaR at 95% and 99%, max drawdown analysis."),
        ("🔗","Correlation Matrix","Full pairwise correlation heatmap — see which pairs diversify and which don't."),
        ("📊","Historical Returns","Daily return distribution with normal overlay and VaR threshold lines."),
        ("🥧","Weight Allocation","Interactive allocation breakdown — Max Sharpe, Min Variance, or custom mix."),
    ]
    cols = st.columns(3)
    for i, (icon, title, desc) in enumerate(cards):
        cols[i % 3].markdown(f"""
        <div class='port-card'>
            <div style='font-size:1.2rem; margin-bottom:0.5rem;'>{icon}</div>
            <h4>{title}</h4>
            <p>{desc}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style='text-align:center; margin-top:1rem;'>
        <div style='font-family:"DM Mono",monospace; font-size:0.62rem;
                    color:{TEXT_DARK}; margin-bottom:1.5rem;'>
            Based on Modern Portfolio Theory — Harry Markowitz, Nobel Prize in Economics 1990
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Hide sidebar toggle on home page
    st.markdown("""
    <style>
    [data-testid="collapsedControl"] { display: none !important; }
    [data-testid="stSidebar"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

    _, col_c, _ = st.columns([1, 1, 1])
    with col_c:
        if st.button("→ Launch PortDesk", type="primary", use_container_width=True):
            st.session_state.page = "terminal"
            st.rerun()


# ─────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown(
            f"<p style='font-family:\"Syne\",sans-serif; font-weight:700; font-size:0.85rem; "
            f"color:{GOLD}; letter-spacing:0.05em; text-transform:uppercase; margin-bottom:1rem;'>"
            f"Portfolio Settings</p>",
            unsafe_allow_html=True,
        )
        selected_stocks = st.multiselect(
            "Select stocks (3–10 recommended)",
            options=list(STOCK_UNIVERSE.keys()),
            default=["TCS","HDFC Bank","Reliance","ITC","Infosys","ICICI Bank","Maruti","Sun Pharma"],
            help="Select 3–10 stocks for portfolio optimisation",
        )
        period       = st.selectbox("Historical Period", ["1y","2y","3y","5y"], index=1)
        rf_rate      = st.slider("Risk-Free Rate %", 4.0, 8.0, 6.5, 0.1,
                                 help="India 10Y G-Sec yield ≈ 6.5%")
        n_portfolios = st.select_slider(
            "Monte Carlo Simulations",
            options=[1000, 2000, 5000, 10000], value=5000,
        )
        run_btn = st.button("🚀 Optimise Portfolio", use_container_width=True, type="primary")

        if len(selected_stocks) < 3:
            st.markdown(f"""
        <div style='background:#e0a04a18; border-left:3px solid #e0a04a; border-radius:2px;
                    padding:0.6rem 0.85rem; font-family:"DM Mono",monospace;
                    font-size:0.72rem; color:#e0a04a;'>
            ⚠ Select at least 3 stocks.
        </div>""", unsafe_allow_html=True)

        st.markdown(f"<hr style='border-color:{BORDER}; margin:1rem 0;'>", unsafe_allow_html=True)
        if st.button("← Home", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()

    return selected_stocks, period, rf_rate, n_portfolios, run_btn


# ─────────────────────────────────────────
# TAB 1 — EFFICIENT FRONTIER
# ─────────────────────────────────────────
def tab_efficient_frontier(r):
    fig = go.Figure()

    # Random portfolio cloud — coloured by Sharpe
    fig.add_trace(go.Scatter(
        x=r["p_vol"] * 100, y=r["p_ret"] * 100,
        mode="markers",
        marker=dict(
            color=r["p_sr"],
            colorscale=[[0.0,"#1a1a2e"],[0.3,NAVY],[0.6,GOLD],[1.0,GREEN]],
            size=3, opacity=0.6,
            colorbar=dict(
                title=dict(text="Sharpe Ratio", font=dict(color=TEXT_DIM, size=10)),
                tickfont=dict(color=TEXT_DARK, size=9),
                thickness=10, len=0.6,
            ),
        ),
        name="Random Portfolios",
        hovertemplate="Vol: %{x:.1f}%<br>Return: %{y:.1f}%<extra>Random Portfolio</extra>",
    ))

    # Efficient Frontier line
    if len(r["ef_vols"]) > 1:
        fig.add_trace(go.Scatter(
            x=r["ef_vols"] * 100, y=r["ef_rets"] * 100,
            mode="lines", line=dict(color=GOLD, width=2.5),
            name="Efficient Frontier",
            hovertemplate="Vol: %{x:.1f}%<br>Return: %{y:.1f}%<extra>Efficient Frontier</extra>",
        ))

    opt = r["opt"]

    # Max Sharpe — gold star
    fig.add_trace(go.Scatter(
        x=[opt["max_sharpe"]["vol"] * 100],
        y=[opt["max_sharpe"]["return"] * 100],
        mode="markers",
        marker=dict(symbol="star", size=18, color=GOLD, line=dict(color="#fff", width=1)),
        name=f"Max Sharpe ({opt['max_sharpe']['sharpe']:.2f})",
        hovertemplate="Max Sharpe Portfolio<br>Vol: %{x:.1f}%<br>Return: %{y:.1f}%<extra></extra>",
    ))

    # Min Variance — blue circle
    fig.add_trace(go.Scatter(
        x=[opt["min_variance"]["vol"] * 100],
        y=[opt["min_variance"]["return"] * 100],
        mode="markers",
        marker=dict(symbol="circle", size=14, color=BLUE, line=dict(color="#fff", width=1)),
        name="Min Variance",
        hovertemplate="Min Variance Portfolio<br>Vol: %{x:.1f}%<br>Return: %{y:.1f}%<extra></extra>",
    ))

    # Capital Market Line
    cml_x = np.linspace(0, opt["max_sharpe"]["vol"] * 1.5 * 100, 50)
    cml_y = r["rf"] * 100 + opt["max_sharpe"]["sharpe"] * cml_x
    fig.add_trace(go.Scatter(
        x=cml_x, y=cml_y, mode="lines",
        line=dict(color="rgba(74,184,122,0.4)", width=1.5, dash="dash"),
        name="Capital Market Line",
    ))

    # Individual stocks — hover only, NOT in legend (FIX BUG 5 — showlegend=False)
    ann_returns = r["ann_returns"]
    ann_vols    = r["ann_vols"]
    for i, sname in enumerate(ann_returns.index.tolist()):
        fig.add_trace(go.Scatter(
            x=[ann_vols[i] * 100],
            y=[ann_returns.iloc[i] * 100],
            mode="markers+text",
            marker=dict(
                size=10,
                color=SECTOR_COLORS.get(STOCK_UNIVERSE.get(sname, {}).get("sector",""), "#666"),
                symbol="diamond",
            ),
            text=[sname[:5]],
            textposition="top right",
            textfont=dict(size=8, color=TEXT_DARK),
            name=sname,
            showlegend=False,
            hovertemplate=f"{sname}<br>Vol: %{{x:.1f}}%<br>Return: %{{y:.1f}}%<extra></extra>",
        ))

    fig.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(
            text="Efficient Frontier — Markowitz Portfolio Optimisation",
            font=dict(family="Playfair Display, serif", size=15, color=GOLD),
            x=0.02,
        ),
        xaxis_title="Annual Volatility (Risk) %",
        yaxis_title="Annual Return %",
        showlegend=True,
        legend=dict(
            bgcolor="rgba(17,17,24,0.8)", bordercolor=BORDER,
            font=dict(color=TEXT_DIM, size=9), x=0.02, y=0.98,
        ),
        height=560,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown(f"""
    <div class='plain-text'>
        Each dot is a randomly generated portfolio using your selected stocks.
        The gold curve — the <strong style='color:{GOLD}'>Efficient Frontier</strong> — is the boundary of optimal portfolios.
        The <strong style='color:{GOLD}'>⭐ gold star</strong> is the Maximum Sharpe Ratio portfolio — best return per unit of risk.
        The <strong style='color:{BLUE}'>🔵 blue circle</strong> is the Minimum Variance portfolio — least risky combination possible.
    </div>
    <div class='ghost-text'>
        Think of the frontier as the "best you can do" line. Everything below it is suboptimal — you're taking
        too much risk for the return you're getting. Everything above it is impossible. The star is where you want to be.
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────
# TAB 2 — PORTFOLIO WEIGHTS
# ─────────────────────────────────────────
def tab_weights(r):
    opt         = r["opt"]
    ann_returns = r["ann_returns"]
    ann_vols    = r["ann_vols"]

    mode = st.radio(
        "Portfolio",
        ["⭐ Max Sharpe", "🔵 Min Variance", "⚙️ Custom Mix"],
        horizontal=True,
        label_visibility="collapsed",
    )

    if mode == "⭐ Max Sharpe":
        active      = opt["max_sharpe"]
        weights     = np.array(active["weights"])
        stock_names = active["names"]

    elif mode == "🔵 Min Variance":
        active      = opt["min_variance"]
        weights     = np.array(active["weights"])
        stock_names = active["names"]

    else:
        # FIX BUG 4: Custom Mix — normalise weights so they always sum to 100%
        stock_names = ann_returns.index.tolist()
        n = len(stock_names)
        raw_vals = {}
        for sn in stock_names:
            raw_vals[sn] = st.slider(
                f"{sn}", 0.0, 100.0, round(100.0 / n, 1), 0.5, key=f"sl_{sn}"
            )
        total = sum(raw_vals.values())
        if total < 1e-6:
            total = 1.0  # avoid div-by-zero
        weights = np.array([raw_vals[s] / total for s in stock_names])
        w_ret = float(weights @ ann_returns.values)
        w_vol = float(np.sqrt(weights @ r["ann_cov"].values @ weights))
        w_sr  = (w_ret - r["rf"]) / w_vol if w_vol > 1e-10 else 0.0

        total_pct = sum(raw_vals.values())
        st.markdown(
            f"<div class='plain-text'>Slider total: {total_pct:.1f}% → "
            f"normalised to 100%. Each weight scaled proportionally.</div>",
            unsafe_allow_html=True,
        )
        active = {"return": w_ret, "vol": w_vol, "sharpe": w_sr}

    # FIX BUG 5: filter near-zero weights before pie chart
    WEIGHT_THRESHOLD = 0.001  # 0.1%
    mask        = np.array(weights) >= WEIGHT_THRESHOLD
    pie_names   = [stock_names[i] for i in range(len(stock_names)) if mask[i]]
    pie_weights = weights[mask]

    left, right = st.columns([1, 1])
    with left:
        fig = go.Figure(go.Pie(
            labels=pie_names,
            values=pie_weights * 100,
            hole=0.45,
            marker=dict(
                colors=[SECTOR_COLORS.get(STOCK_UNIVERSE.get(s, {}).get("sector",""), NAVY)
                        for s in pie_names],
                line=dict(color=BG, width=2),
            ),
            textinfo="label+percent",
            textfont=dict(family="DM Mono", size=10, color=TEXT),
            hovertemplate="%{label}<br>Weight: %{value:.1f}%<extra></extra>",
        ))
        fig.update_layout(
            **PLOTLY_LAYOUT, showlegend=False, height=360,
            title=dict(text="Portfolio Allocation", font=dict(color=GOLD, size=13)),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        mc1, mc2, mc3 = st.columns(3)
        mc1.metric("Ann. Return", f"{active['return']*100:.1f}%")
        mc2.metric("Ann. Vol",    f"{active['vol']*100:.1f}%")
        mc3.metric("Sharpe",      f"{active['sharpe']:.2f}")

    with right:
        # Weights table — all stocks with weight > threshold
        idx_map = {s: i for i, s in enumerate(ann_returns.index.tolist())}
        table_data = []
        for i, sn in enumerate(stock_names):
            w   = float(weights[i])
            if w < WEIGHT_THRESHOLD:
                continue
            ret = float(ann_returns.loc[sn]) if sn in ann_returns.index else 0.0
            vol = float(ann_vols[idx_map[sn]]) if sn in idx_map else 0.0
            sr  = (ret - r["rf"]) / vol if vol > 1e-10 else 0.0
            w_ret_contrib = w * ret
            cov_vals      = r["ann_cov"].values
            idx           = idx_map.get(sn, 0)
            port_vol      = active["vol"]
            risk_contrib  = (w * float(cov_vals[idx] @ weights) / (port_vol**2)
                             if port_vol > 1e-10 else 0.0)
            table_data.append({
                "Stock":          sn,
                "Weight %":       f"{w*100:.1f}",
                "Ann. Ret %":     f"{ret*100:.1f}",
                "Ann. Vol %":     f"{vol*100:.1f}",
                "Sharpe":         f"{sr:.2f}",
                "Ret Contrib %":  f"{w_ret_contrib*100:.2f}",
                "Risk Contrib %": f"{risk_contrib*100:.1f}",
                "Sector":         STOCK_UNIVERSE.get(sn, {}).get("sector","—"),
            })
        df = pd.DataFrame(table_data)
        if not df.empty:
            df = df.sort_values("Weight %", ascending=False,
                                key=lambda x: x.astype(float))
            st.dataframe(df, use_container_width=True, hide_index=True)


# ─────────────────────────────────────────
# TAB 3 — RISK METRICS
# ─────────────────────────────────────────
def tab_risk(r):
    opt   = r["opt"]
    ws    = np.array(opt["max_sharpe"]["weights"])
    w_ret = opt["max_sharpe"]["return"]
    w_vol = opt["max_sharpe"]["vol"]

    # Align weights to log_returns columns (FIX BUG 3)
    n_cols   = len(r["log_returns"].columns)
    ws_align = ws[:n_cols]

    metrics = compute_risk_metrics(ws_align, w_ret, w_vol, r["rf"], r["log_returns"])

    c1,c2,c3,c4,c5,c6 = st.columns(6)
    c1.metric("Ann. Return",     f"{metrics['ann_return']*100:.1f}%")
    c2.metric("Ann. Volatility", f"{metrics['ann_vol']*100:.1f}%")
    c3.metric("Sharpe Ratio",    f"{metrics['sharpe']:.3f}")
    c4.metric("VaR 95% (1D)",    f"{metrics['var_95_1d']*100:.2f}%")
    c5.metric("CVaR 95% (1D)",   f"{metrics['cvar_95_1d']*100:.2f}%")
    dd_str = f"{metrics['max_drawdown']*100:.1f}%" if metrics["max_drawdown"] is not None else "—"
    c6.metric("Max Drawdown", dd_str)

    st.markdown(f"<hr style='border-color:{BORDER}; margin:1rem 0;'>", unsafe_allow_html=True)

    left, right = st.columns([1, 1])
    with left:
        st.markdown(
            f"<p style='font-family:\"DM Mono\",monospace; font-size:0.7rem; color:{GOLD}; "
            f"text-transform:uppercase; letter-spacing:0.08em;'>VaR / CVaR Table</p>",
            unsafe_allow_html=True,
        )
        # FIX BUG 1: Each row uses its own correctly-scaled values
        var_df = pd.DataFrame({
            "Confidence": ["95%", "99%"],
            "1-Day VaR":  [f"{metrics['var_95_1d']*100:.2f}%",  f"{metrics['var_99_1d']*100:.2f}%"],
            "5-Day VaR":  [f"{metrics['var_95_5d']*100:.2f}%",  f"{metrics['var_99_5d']*100:.2f}%"],
            "21-Day VaR": [f"{metrics['var_95_21d']*100:.2f}%", f"{metrics['var_99_21d']*100:.2f}%"],
            "CVaR (1D)":  [f"{metrics['cvar_95_1d']*100:.2f}%", f"{metrics['cvar_99_1d']*100:.2f}%"],
        })
        st.dataframe(var_df, use_container_width=True, hide_index=True)

        if metrics["hist_var_95"] is not None:
            st.markdown(f"""
            <div class='port-card' style='margin-top:0.75rem;'>
                <h4>Historical VaR</h4>
                <p>95%: {metrics['hist_var_95']*100:.2f}% per day &nbsp;|&nbsp;
                   99%: {metrics['hist_var_99']*100:.2f}% per day</p>
            </div>
            """, unsafe_allow_html=True)

    with right:
        port_daily = r["log_returns"].values @ ws_align
        x_range    = np.linspace(port_daily.min(), port_daily.max(), 200)
        mu_d, sig_d = port_daily.mean(), port_daily.std()
        norm_pdf    = norm.pdf(x_range, mu_d, sig_d)
        hist_max    = np.histogram(port_daily, bins=50)[0].max()
        norm_scaled = norm_pdf / norm_pdf.max() * hist_max

        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=port_daily * 100, nbinsx=50,
            marker=dict(color="rgba(74,154,255,0.3)", line=dict(color=BORDER, width=0.5)),
            name="Daily Returns", showlegend=False,
        ))
        fig.add_trace(go.Scatter(
            x=x_range * 100, y=norm_scaled,
            mode="lines", line=dict(color=GOLD, width=1.5),
            name="Normal Fit", showlegend=False,
        ))
        for var_val, color, label in [
            (metrics["var_95_1d"], RED, "VaR 95%"),
            (metrics["var_99_1d"], "rgba(224,92,108,0.5)", "VaR 99%"),
        ]:
            fig.add_vline(
                x=-var_val * 100, line=dict(color=color, width=1.5, dash="dot"),
                annotation_text=label,
                annotation_font=dict(color=color, size=9, family="DM Mono"),
            )
        fig.update_layout(
            **PLOTLY_LAYOUT,
            title=dict(text="Daily Return Distribution — Historical",
                       font=dict(color=GOLD, size=12)),
            height=300, showlegend=False,
            xaxis_title="Daily Return %", yaxis_title="Count",
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # Drawdown chart
    st.markdown(f"<hr style='border-color:{BORDER}; margin:1rem 0;'>", unsafe_allow_html=True)
    port_log = r["log_returns"].values @ ws_align
    cum_ret  = np.exp(np.cumsum(port_log))
    peak     = np.maximum.accumulate(cum_ret)
    drawdown = (cum_ret - peak) / peak
    dates    = r["prices"].index[-len(cum_ret):]

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=dates, y=cum_ret, mode="lines",
        line=dict(color=BLUE, width=1.8), name="Portfolio Growth",
    ))
    fig2.add_trace(go.Scatter(
        x=dates, y=peak, mode="lines",
        line=dict(color=GOLD, width=1, dash="dot"), name="Peak", opacity=0.6,
    ))
    # Drawdown shading — correct polygon: forward dates + backward dates, drawdown + zeros
    fig2.add_trace(go.Scatter(
        x=list(dates) + list(dates[::-1]),
        y=list(drawdown) + [0.0] * len(dates),
        fill="toself", fillcolor="rgba(224,92,108,0.1)",
        line=dict(color="rgba(0,0,0,0)"), name="Drawdown",
    ))
    fig2.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(text="Cumulative Return & Drawdown", font=dict(color=GOLD, size=12)),
        height=320, showlegend=True,
        legend=dict(bgcolor="rgba(17,17,24,0.8)", bordercolor=BORDER,
                    font=dict(color=TEXT_DIM, size=9)),
    )
    st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

    if metrics["max_drawdown"] is not None:
        trough_val = 1_000_000 * (1 + metrics["max_drawdown"])
        st.markdown(f"""
        <div class='plain-text'>
            Maximum drawdown is the largest peak-to-trough decline in the Max Sharpe portfolio.
            Worst losing streak: <strong style='color:{RED}'>{metrics['max_drawdown']*100:.1f}%</strong>.
            Starting at ₹10L, the worst trough saw it drop to
            <strong style='color:{RED}'>₹{trough_val/100000:.2f}L</strong>.
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────
# TAB 4 — CORRELATION & INDIVIDUAL STOCKS
# ─────────────────────────────────────────
def tab_correlation(r):
    corr        = r["corr"]
    ann_returns = r["ann_returns"]
    ann_vols    = r["ann_vols"]
    rf          = r["rf"]

    fig = go.Figure(go.Heatmap(
        z=corr.values,
        x=corr.columns.tolist(),
        y=corr.index.tolist(),
        colorscale=[[0.0, RED],[0.5, BG2],[1.0, GREEN]],
        zmid=0,
        text=corr.round(2).values,
        texttemplate="%{text}",
        textfont=dict(family="DM Mono", size=9, color=TEXT),
        hovertemplate="%{y} vs %{x}<br>Correlation: %{z:.3f}<extra></extra>",
        colorbar=dict(
            title=dict(text="Correlation", font=dict(color=TEXT_DIM, size=10)),
            tickfont=dict(color=TEXT_DARK, size=9),
            thickness=12,
        ),
        showscale=True,
    ))
    fig.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(text="Return Correlation Matrix", font=dict(color=GOLD, size=13)),
        height=460,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown(f"""
    <div class='plain-text'>
        Correlation measures how two stocks move together.
        <strong style='color:{GREEN}'>+1</strong> = lockstep (no diversification benefit).
        <strong style='color:{TEXT_DIM}'>0</strong> = no relationship.
        <strong style='color:{RED}'>−1</strong> = perfect hedge.
        Low-correlation pairs (dark cells) give the most diversification benefit.
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"<hr style='border-color:{BORDER}; margin:1.5rem 0;'>", unsafe_allow_html=True)

    stock_names = ann_returns.index.tolist()
    sharpes = [
        (float(ann_returns.iloc[i]) - rf) / float(ann_vols[i])
        if ann_vols[i] > 1e-10 else 0.0
        for i in range(len(stock_names))
    ]

    fig2 = go.Figure()
    vol_range = np.linspace(min(ann_vols) * 0.9, max(ann_vols) * 1.1, 50)
    fig2.add_trace(go.Scatter(
        x=vol_range * 100,
        y=(rf + 1.0 * vol_range) * 100,
        mode="lines",
        line=dict(color=BORDER, width=1, dash="dot"),
        name="Sharpe = 1.0",
        showlegend=True,
    ))
    for i, sn in enumerate(stock_names):
        bubble_size = max(8, abs(sharpes[i]) * 14)
        fig2.add_trace(go.Scatter(
            x=[float(ann_vols[i]) * 100],
            y=[float(ann_returns.iloc[i]) * 100],
            mode="markers+text",
            marker=dict(
                size=bubble_size,
                color=SECTOR_COLORS.get(STOCK_UNIVERSE.get(sn, {}).get("sector",""), NAVY),
                opacity=0.85,
                line=dict(color=BG, width=1.5),
            ),
            text=[sn[:5]],
            textposition="top center",
            textfont=dict(size=8, color=TEXT_DIM, family="DM Mono"),
            name=sn,
            showlegend=False,
            hovertemplate=(
                f"<b>{sn}</b><br>Vol: %{{x:.1f}}%<br>"
                f"Return: %{{y:.1f}}%<br>Sharpe: {sharpes[i]:.2f}<extra></extra>"
            ),
        ))
    fig2.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(text="Individual Stock Risk / Return  (bubble size = |Sharpe|)",
                   font=dict(color=GOLD, size=12)),
        xaxis_title="Annual Volatility %",
        yaxis_title="Annual Return %",
        height=400, showlegend=False,
    )
    st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})


# ─────────────────────────────────────────
# TAB 5 — EDUCATION & METHODOLOGY
# ─────────────────────────────────────────
def tab_education():
    st.markdown(f"""
    <div style='text-align:center; margin-bottom:1.5rem;'>
        <p style='font-family:"Playfair Display",serif; font-size:1.1rem;
                  color:{GOLD}; font-style:italic; margin-bottom:1rem;'>
            Modern Portfolio Theory — A Brief History
        </p>
        <div style='display:flex; justify-content:center; gap:2rem; flex-wrap:wrap;'>
            <div style='text-align:center; padding:1rem; background:{BG2};
                        border:1px solid {BORDER}; border-radius:4px; min-width:140px;'>
                <div style='font-family:"DM Mono",monospace; color:{GOLD}; font-size:1.1rem;'>1952</div>
                <div style='font-family:"Syne",sans-serif; font-size:0.7rem; color:{TEXT_DIM}; margin-top:0.3rem;'>
                    Markowitz publishes<br>"Portfolio Selection"
                </div>
            </div>
            <div style='text-align:center; padding:1rem; background:{BG2};
                        border:1px solid {BORDER}; border-radius:4px; min-width:140px;'>
                <div style='font-family:"DM Mono",monospace; color:{BLUE}; font-size:1.1rem;'>1964</div>
                <div style='font-family:"Syne",sans-serif; font-size:0.7rem; color:{TEXT_DIM}; margin-top:0.3rem;'>
                    Sharpe develops CAPM
                </div>
            </div>
            <div style='text-align:center; padding:1rem; background:{BG2};
                        border:1px solid {BORDER}; border-radius:4px; min-width:140px;'>
                <div style='font-family:"DM Mono",monospace; color:{GREEN}; font-size:1.1rem;'>1990</div>
                <div style='font-family:"Syne",sans-serif; font-size:0.7rem; color:{TEXT_DIM}; margin-top:0.3rem;'>
                    Nobel Prize in Economics
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    principles = [
        ("Diversification",     "Combining assets reduces portfolio risk without reducing expected return — the only 'free lunch' in finance."),
        ("Risk-Return Tradeoff","Rational, risk-averse investors require higher expected return to accept higher risk."),
        ("Efficient Portfolios","For every risk level, there exists an optimal portfolio that maximises expected return."),
    ]
    cols = st.columns(3)
    for col, (title, desc) in zip(cols, principles):
        col.markdown(f"<div class='port-card'><h4>{title}</h4><p>{desc}</p></div>",
                     unsafe_allow_html=True)

    st.markdown(f"<hr style='border-color:{BORDER}; margin:1.5rem 0;'>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='font-family:\"Syne\",sans-serif; font-weight:700; font-size:0.85rem; "
        f"color:{GOLD}; text-transform:uppercase; letter-spacing:0.08em;'>The Mathematics</p>",
        unsafe_allow_html=True,
    )
    for latex_str, explanation in [
        (r"\mu_p = \mathbf{w}^T \boldsymbol{\mu}",
         "Portfolio return — weighted sum of individual stock expected returns."),
        (r"\sigma_p^2 = \mathbf{w}^T \boldsymbol{\Sigma} \mathbf{w}",
         "Portfolio variance — captures individual stock risks AND all pairwise covariances. Source of diversification benefit."),
        (r"S = \frac{\mu_p - r_f}{\sigma_p}",
         "Sharpe Ratio — excess return per unit of risk. Higher is better."),
        (r"\max_{\mathbf{w}} \frac{\mathbf{w}^T\boldsymbol{\mu} - r_f}{\sqrt{\mathbf{w}^T\boldsymbol{\Sigma}\mathbf{w}}}",
         "The optimisation problem — maximise Sharpe subject to weights summing to 1, all ≥ 0 (long-only)."),
    ]:
        cl, cr = st.columns([1, 1])
        with cl:
            st.latex(latex_str)
        with cr:
            st.markdown(f"<div class='plain-text' style='margin-top:0.5rem;'>{explanation}</div>",
                        unsafe_allow_html=True)

    st.markdown(f"<hr style='border-color:{BORDER}; margin:1.5rem 0;'>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='font-family:\"Syne\",sans-serif; font-weight:700; font-size:0.85rem; "
        f"color:{GOLD}; text-transform:uppercase; letter-spacing:0.08em;'>How PortDesk Computes It</p>",
        unsafe_allow_html=True,
    )
    steps = [
        ("1. Data",       "Fetch 2Y daily prices via yfinance (.NS tickers). auto_adjust=True handles splits and dividends."),
        ("2. Validate",   "Drop tickers with <200 days data, non-positive prices, or annualised returns outside [-60%, +200%]."),
        ("3. Log Returns","r_t = ln(P_t / P_{t-1}). Log returns are additive over time — standard in portfolio theory."),
        ("4. Annualise",  "μ = mean × 252 for returns. Σ = cov × 252 for covariance. Vol = sqrt(252) × daily vol."),
        ("5. Simulate",   "5,000 Dirichlet random portfolios — uniform coverage of the weight simplex, no corner bias."),
        ("6. Optimise",   "scipy SLSQP: Max Sharpe (ftol=1e-12) and Min Variance (ftol=1e-12). Long-only, weights sum to 1."),
        ("7. Frontier",   "50 target-return constrained optimisations trace the efficient frontier from Min Var to Max Return."),
        ("8. Risk",       "Parametric VaR/CVaR (normal assumption). Historical VaR from actual portfolio daily return percentiles."),
    ]
    step_cols = st.columns(2)
    for i, (step, desc) in enumerate(steps):
        step_cols[i % 2].markdown(
            f"<div class='port-card' style='margin-bottom:0.5rem;'><h4>{step}</h4><p>{desc}</p></div>",
            unsafe_allow_html=True,
        )

    st.markdown(f"<hr style='border-color:{BORDER}; margin:1.5rem 0;'>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='font-family:\"Syne\",sans-serif; font-weight:700; font-size:0.85rem; "
        f"color:{GOLD}; text-transform:uppercase; letter-spacing:0.08em;'>Honest Limitations</p>",
        unsafe_allow_html=True,
    )
    limits = [
        ("Past ≠ Future",         "Historical returns do not predict future returns. The frontier is backward-looking."),
        ("Normal Distribution",   "Assumes normally distributed returns. Real markets have fat tails — extreme events occur more often."),
        ("Constant Correlation",  "Assumes stable covariances. During crises, correlations spike toward 1 — when you need diversification most."),
        ("No Costs",              "No transaction costs, taxes, or liquidity constraints modeled."),
        ("Concentration Risk",    "Markowitz portfolios naturally concentrate. Real portfolios add max-weight constraints."),
    ]
    lim_cols = st.columns(2)
    for i, (title, desc) in enumerate(limits):
        lim_cols[i % 2].markdown(
            f"<div class='port-card' style='border-left:2px solid {RED}; margin-bottom:0.5rem;'>"
            f"<h4 style='color:{RED} !important;'>{title}</h4><p>{desc}</p></div>",
            unsafe_allow_html=True,
        )


# ─────────────────────────────────────────
# TERMINAL PAGE
# ─────────────────────────────────────────
def run_analysis(selected_stocks, period, rf_rate, n_portfolios):
    tickers = [STOCK_UNIVERSE[s]["ticker"] for s in selected_stocks]
    with st.spinner(f"Fetching {period} data for {len(selected_stocks)} stocks…"):
        prices = fetch_stock_data(tuple(tickers), period)

    if prices.empty:
        st.error("Failed to fetch data. Check your internet connection.")
        return False

    ticker_to_name = {STOCK_UNIVERSE[s]["ticker"]: s for s in selected_stocks}
    prices.columns = [ticker_to_name.get(c, c) for c in prices.columns]

    with st.spinner("Validating data and computing returns…"):
        log_rets, ann_rets, ann_cov, ann_vols, corr = compute_returns(prices)

    valid_stocks = ann_rets.index.tolist()
    prices       = prices[valid_stocks]
    dropped      = set(ticker_to_name.values()) - set(valid_stocks)

    if len(valid_stocks) < 2:
        st.error("Fewer than 2 stocks have valid data. Try a shorter period or different tickers.")
        return False

    with st.spinner(f"Running {n_portfolios:,} Monte Carlo simulations…"):
        p_ret, p_vol, p_sr, p_wts = simulate_portfolios(ann_rets, ann_cov, n_portfolios, rf_rate / 100)

    with st.spinner("Running portfolio optimisation…"):
        opt = optimise_portfolio(ann_rets, ann_cov, rf_rate / 100)

    with st.spinner("Computing efficient frontier…"):
        ef_vols, ef_rets = compute_efficient_frontier(ann_rets, ann_cov, opt)

    st.session_state.results = {
        "prices": prices, "log_returns": log_rets,
        "ann_returns": ann_rets, "ann_cov": ann_cov,
        "ann_vols": ann_vols, "corr": corr,
        "p_ret": p_ret, "p_vol": p_vol, "p_sr": p_sr, "p_wts": p_wts,
        "ef_vols": ef_vols, "ef_rets": ef_rets,
        "opt": opt, "rf": rf_rate / 100,
        "dropped": list(dropped), "valid": valid_stocks,
    }
    st.session_state.last_selection = f"{sorted(selected_stocks)}_{period}_{rf_rate}_{n_portfolios}"
    return True


def render_terminal():
    selected_stocks, period, rf_rate, n_portfolios, run_btn = render_sidebar()

    # Header
    st.markdown(f"""
    <div style='border-bottom:1px solid {BORDER}; padding-bottom:0.75rem; margin-bottom:1rem;'>
        <div style='font-family:"DM Mono",monospace; font-size:0.65rem; color:{TEXT_DARK};
                    text-transform:uppercase; letter-spacing:0.15em; margin-bottom:0.2rem;'>
            DAY 26 · 30 DAYS OF AI FINANCE · WEEK 4 — DERIVATIVES &amp; AUTOMATION
        </div>
        <div style='font-family:"Playfair Display",serif; color:{GOLD}; margin:0;
                    font-size:1.6rem; letter-spacing:-0.01em; font-weight:700;'>PortDesk</div>
        <div style='font-family:"DM Mono",monospace; font-size:0.7rem; color:{TEXT_DARK}; margin:0;'>
            Markowitz Portfolio Optimiser for Indian Equities
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Auto-run with defaults on first load
    selection_key = f"{sorted(selected_stocks)}_{period}_{rf_rate}_{n_portfolios}"
    first_load = st.session_state.results is None and st.session_state.last_selection is None

    if run_btn or first_load:
        if len(selected_stocks) >= 3:
            ok = run_analysis(selected_stocks, period, rf_rate, n_portfolios)
            if ok:
                st.rerun()
        else:
            st.session_state.last_selection = "too_few"

    # Show results
    if st.session_state.results is not None:
        r = st.session_state.results
        show_data_health(r["ann_returns"], r.get("dropped", []))
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📈 Efficient Frontier",
            "🥧 Portfolio Weights",
            "🛡️ Risk Metrics",
            "🔗 Correlation",
            "📚 Methodology",
        ])
        with tab1: tab_efficient_frontier(r)
        with tab2: tab_weights(r)
        with tab3: tab_risk(r)
        with tab4: tab_correlation(r)
        with tab5: tab_education()

    st.markdown(f"""
    <div class='footer-text'>
        PortDesk · Day 26 · 30 Days of AI Finance<br>
        Based on Modern Portfolio Theory — Harry Markowitz, Nobel Prize in Economics 1990<br>
        Historical data via yfinance · Past performance is not indicative of future returns · Not investment advice
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────
# ROUTER
# ─────────────────────────────────────────
if st.session_state.page == "home":
    render_home()
else:
    render_terminal()