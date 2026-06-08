import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import requests
from datetime import datetime, timedelta
import time

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Macro Terminal | Day 08 · 30 Days of AI Finance",
    page_icon="🖥️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────
# STYLING
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Syne:wght@400;600;700;800&family=Playfair+Display:ital,wght@0,700;1,700&display=swap');

/* Base */
html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
    background-color: #0a0a0f;
    color: #e8e4dc;
}

.stApp { background-color: #0a0a0f; }

/* Hide default elements */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2rem 2rem; max-width: 1400px; }

/* Terminal header */
.terminal-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 1.5rem;
    background: #111118;
    border: 1px solid rgba(201,169,110,0.2);
    border-radius: 4px;
    margin-bottom: 1.5rem;
}
.terminal-logo {
    font-family: 'Playfair Display', serif;
    font-size: 1.4rem;
    font-weight: 700;
    color: #c9a96e;
    letter-spacing: -0.02em;
}
.terminal-sub {
    font-family: 'DM Mono', monospace;
    font-size: 0.6rem;
    color: #666;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-top: 2px;
}
.terminal-time {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    color: #c9a96e;
    text-align: right;
}
.live-dot {
    display: inline-block;
    width: 6px;
    height: 6px;
    background: #4ab87a;
    border-radius: 50%;
    margin-right: 5px;
    animation: pulse 2s ease-in-out infinite;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }

/* Section labels */
.section-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.58rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #c9a96e;
    margin-bottom: 0.6rem;
    padding-bottom: 0.4rem;
    border-bottom: 1px solid rgba(201,169,110,0.15);
}

/* Metric cards */
.metric-card {
    background: #111118;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 3px;
    padding: 1rem 1.1rem;
    transition: border-color 0.2s;
}
.metric-card:hover { border-color: rgba(201,169,110,0.3); }
.metric-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.58rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #666;
    margin-bottom: 0.4rem;
}
.metric-value {
    font-family: 'DM Mono', monospace;
    font-size: 1.3rem;
    font-weight: 500;
    color: #e8e4dc;
    letter-spacing: -0.01em;
    line-height: 1;
}
.metric-change {
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    margin-top: 0.3rem;
}
.metric-change.pos { color: #4ab87a; }
.metric-change.neg { color: #e05c6c; }
.metric-change.neu { color: #888; }
.metric-tag {
    font-family: 'DM Mono', monospace;
    font-size: 0.52rem;
    color: #555;
    margin-top: 0.2rem;
    letter-spacing: 0.04em;
}

/* Divider */
.term-divider {
    height: 1px;
    background: rgba(255,255,255,0.06);
    margin: 1.5rem 0;
}

/* Chart container */
.chart-container {
    background: #111118;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 3px;
    padding: 1rem;
}

/* FII/DII table */
.fii-table {
    width: 100%;
    border-collapse: collapse;
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
}
.fii-table th {
    text-align: left;
    padding: 0.5rem 0.8rem;
    background: rgba(201,169,110,0.08);
    color: #c9a96e;
    font-size: 0.58rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    border-bottom: 1px solid rgba(201,169,110,0.15);
}
.fii-table td {
    padding: 0.5rem 0.8rem;
    border-bottom: 1px solid rgba(255,255,255,0.04);
    color: #b0ac9f;
}
.fii-table tr:hover td { background: rgba(255,255,255,0.02); }
.pos-val { color: #4ab87a !important; }
.neg-val { color: #e05c6c !important; }

/* Breadcrumb */
.breadcrumb {
    font-family: 'DM Mono', monospace;
    font-size: 0.6rem;
    color: #444;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 1rem;
}

/* Alert / Signal */
.signal-card {
    padding: 0.7rem 1rem;
    border-radius: 3px;
    font-size: 0.73rem;
    font-family: 'Syne', sans-serif;
    line-height: 1.5;
    margin-bottom: 0.5rem;
}
.signal-bull { background: rgba(74,184,122,0.08); border-left: 2px solid #4ab87a; color: #b0e8c0; }
.signal-bear { background: rgba(224,92,108,0.08); border-left: 2px solid #e05c6c; color: #f0b0b8; }
.signal-neu  { background: rgba(201,169,110,0.08); border-left: 2px solid #c9a96e; color: #e8d4a8; }

/* Footer */
.term-footer {
    font-family: 'DM Mono', monospace;
    font-size: 0.58rem;
    color: #333;
    text-align: center;
    margin-top: 2rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# DATA FETCHING
# ─────────────────────────────────────────────

TICKERS = {
    # Indian Markets
    "nifty50":     ("^NSEI",     "Nifty 50",         "India"),
    "sensex":      ("^BSESN",    "Sensex",            "India"),
    "india_vix":   ("^INDIAVIX", "India VIX",         "India"),
    "nifty_bank":  ("^NSEBANK",  "Nifty Bank",        "India"),
    "nifty_it":    ("^CNXIT",    "Nifty IT",          "India"),
    "nifty_midcap":("^NSMIDCP",  "Nifty Midcap 100",  "India"),
    # Global / Commodities
    "sp500":       ("^GSPC",     "S&P 500",           "Global"),
    "nasdaq":      ("^IXIC",     "Nasdaq",            "Global"),
    "dxy":         ("DX-Y.NYB",  "DXY Index",         "Forex"),
    "usdinr":      ("USDINR=X",  "USD / INR",         "Forex"),
    "eurusd":      ("EURUSD=X",  "EUR / USD",         "Forex"),
    "gold":        ("GC=F",      "Gold",              "Commodity"),
    "crude_wti":   ("CL=F",      "Crude WTI",         "Commodity"),
    "silver":      ("SI=F",      "Silver",            "Commodity"),
    "us10y":       ("^TNX",      "US 10Y Yield",      "Rates"),
    "us2y":        ("^IRX",      "US 3M Yield",       "Rates"),
    "vix":         ("^VIX",      "CBOE VIX",          "Volatility"),
}

@st.cache_data(ttl=300)  # cache 5 mins
def fetch_quote(ticker_symbol):
    """Fetch latest price + change for a ticker."""
    try:
        t = yf.Ticker(ticker_symbol)
        hist = t.history(period="2d", interval="1d")
        if hist.empty or len(hist) < 1:
            return None
        close = hist['Close'].iloc[-1]
        prev  = hist['Close'].iloc[-2] if len(hist) >= 2 else close
        chg   = close - prev
        pct   = (chg / prev) * 100 if prev != 0 else 0
        return {
            "price": close,
            "change": chg,
            "pct": pct,
            "prev": prev
        }
    except Exception:
        return None

@st.cache_data(ttl=300)
def fetch_history(ticker_symbol, period="6mo"):
    """Fetch OHLCV history."""
    try:
        df = yf.download(ticker_symbol, period=period, progress=False, auto_adjust=True)
        if df.empty:
            return None
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
        return df
    except Exception:
        return None

@st.cache_data(ttl=1800)  # 30 min cache for FII data
def fetch_fii_dii():
    """Fetch FII/DII data from nselib."""
    try:
        from nselib import cash_market
        df = cash_market.nsdl_fpi_latest_investment_activity()
        return df
    except Exception:
        # Fallback: return sample structure
        return None

@st.cache_data(ttl=300)
def fetch_all_quotes():
    """Fetch all ticker quotes in parallel-friendly way."""
    results = {}
    for key, (symbol, name, category) in TICKERS.items():
        results[key] = fetch_quote(symbol)
    return results

# ─────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────

def fmt_price(val, decimals=2):
    if val is None: return "—"
    if val >= 10000: return f"{val:,.0f}"
    if val >= 100:   return f"{val:,.2f}"
    return f"{val:.{decimals}f}"

def fmt_change(chg, pct):
    if chg is None: return "—", "neu"
    sign = "▲" if chg >= 0 else "▼"
    cls  = "pos" if chg >= 0 else "neg"
    return f"{sign} {abs(chg):.2f} ({abs(pct):.2f}%)", cls

def render_metric(label, key, quotes, prefix="", suffix="", decimals=2):
    q = quotes.get(key)
    if q:
        price  = f"{prefix}{fmt_price(q['price'], decimals)}{suffix}"
        change_str, cls = fmt_change(q['change'], q['pct'])
    else:
        price, change_str, cls = "—", "—", "neu"
    
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{price}</div>
        <div class="metric-change {cls}">{change_str}</div>
    </div>
    """, unsafe_allow_html=True)

def make_chart(df, title, color="#c9a96e", height=280, show_volume=False):
    """Create a clean Plotly chart."""
    if df is None or df.empty:
        return None
    
    fig = make_subplots(
        rows=2 if show_volume else 1,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.8, 0.2] if show_volume else [1.0]
    )
    
    # Candlestick or line
    if all(c in df.columns for c in ['Open','High','Low','Close']):
        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df['Open'], high=df['High'],
            low=df['Low'],   close=df['Close'],
            name=title,
            increasing_line_color='#4ab87a',
            decreasing_line_color='#e05c6c',
            increasing_fillcolor='rgba(74,184,122,0.3)',
            decreasing_fillcolor='rgba(224,92,108,0.3)',
            line_width=1
        ), row=1, col=1)
    else:
        close_col = 'Close' if 'Close' in df.columns else df.columns[0]
        fig.add_trace(go.Scatter(
            x=df.index, y=df[close_col],
            mode='lines', name=title,
            line=dict(color=color, width=1.5),
            fill='tozeroy',
            fillcolor=f'rgba(201,169,110,0.07)'
        ), row=1, col=1)
    
    # Volume bars
    if show_volume and 'Volume' in df.columns:
        vol_colors = ['#4ab87a' if df['Close'].iloc[i] >= df['Open'].iloc[i] else '#e05c6c'
                      for i in range(len(df))]
        fig.add_trace(go.Bar(
            x=df.index, y=df['Volume'],
            name='Volume', marker_color=vol_colors, opacity=0.6
        ), row=2, col=1)
    
    fig.update_layout(
        height=height,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=24, b=0),
        title=dict(text=title, font=dict(family='DM Mono', size=11, color='#888'), x=0),
        xaxis=dict(showgrid=False, zeroline=False, color='#555',
                   showspikes=True, spikecolor='#c9a96e', spikethickness=1),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.04)',
                   zeroline=False, color='#555', tickfont=dict(family='DM Mono', size=10)),
        legend=dict(display=False),
        xaxis_rangeslider_visible=False,
        hovermode='x unified',
        hoverlabel=dict(bgcolor='#1a1a24', font=dict(family='DM Mono', size=11)),
    )
    return fig

def yield_curve_chart(quotes):
    """US Yield Curve snapshot."""
    tenors = {
        "3M": quotes.get("us2y"),
        "10Y": quotes.get("us10y"),
    }
    
    # Build with available data
    y_vals, x_labels = [], []
    for label, q in tenors.items():
        if q:
            x_labels.append(label)
            y_vals.append(round(q['price'], 2))
    
    if not y_vals:
        return None
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x_labels, y=y_vals,
        mode='lines+markers+text',
        line=dict(color='#c9a96e', width=2),
        marker=dict(size=8, color='#c9a96e'),
        text=[f"{v:.2f}%" for v in y_vals],
        textposition='top center',
        textfont=dict(family='DM Mono', size=10, color='#c9a96e')
    ))
    fig.update_layout(
        height=200,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=10, b=0),
        xaxis=dict(showgrid=False, color='#555',
                   tickfont=dict(family='DM Mono', size=10)),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.04)',
                   color='#555', tickfont=dict(family='DM Mono', size=10),
                   ticksuffix='%'),
    )
    return fig

def generate_signals(quotes):
    """Generate simple macro signals from live data."""
    signals = []
    
    nifty = quotes.get("nifty50")
    vix   = quotes.get("india_vix")
    dxy   = quotes.get("dxy")
    gold  = quotes.get("gold")
    crude = quotes.get("crude_wti")
    us10y = quotes.get("us10y")
    
    if nifty:
        if nifty['pct'] > 0.5:
            signals.append(("bull", f"Nifty 50 up {nifty['pct']:.2f}% today — domestic risk appetite positive."))
        elif nifty['pct'] < -0.5:
            signals.append(("bear", f"Nifty 50 down {abs(nifty['pct']):.2f}% today — watch for follow-through selling."))
    
    if vix:
        if vix['price'] > 20:
            signals.append(("bear", f"India VIX at {vix['price']:.1f} — elevated volatility. Market pricing uncertainty."))
        elif vix['price'] < 13:
            signals.append(("bull", f"India VIX at {vix['price']:.1f} — low volatility regime. Calm market environment."))
        else:
            signals.append(("neu", f"India VIX at {vix['price']:.1f} — volatility in neutral zone."))
    
    if dxy:
        if dxy['pct'] > 0.3:
            signals.append(("bear", f"DXY up {dxy['pct']:.2f}% — strong dollar typically pressures EM capital flows and INR."))
        elif dxy['pct'] < -0.3:
            signals.append(("bull", f"DXY down {abs(dxy['pct']):.2f}% — dollar weakness supportive of FII inflows into India."))
    
    if gold and gold['pct'] > 0.5:
        signals.append(("neu", f"Gold up {gold['pct']:.2f}% — risk-off or inflation hedge demand active."))
    
    if crude and crude['pct'] > 1.5:
        signals.append(("bear", f"Crude WTI up {crude['pct']:.2f}% — India imports ~85% of oil. CAD pressure and inflation risk."))
    elif crude and crude['pct'] < -1.5:
        signals.append(("bull", f"Crude WTI down {abs(crude['pct']):.2f}% — relief for India's current account and fiscal deficit."))
    
    if us10y:
        if us10y['price'] > 4.5:
            signals.append(("bear", f"US 10Y yield at {us10y['price']:.2f}% — high US rates compete with EM assets for global capital."))
    
    if not signals:
        signals.append(("neu", "Markets in quiet mode. No strong directional signals today."))
    
    return signals

# ─────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────

# Header
now_str = datetime.now().strftime("%A, %d %b %Y  %H:%M IST")
st.markdown(f"""
<div class="terminal-header">
    <div>
        <div class="terminal-logo">🖥️ Macro Terminal</div>
        <div class="terminal-sub">Day 08 · 30 Days of AI Finance · India & Global Markets</div>
    </div>
    <div class="terminal-time">
        <span class="live-dot"></span>LIVE DATA<br>{now_str}
    </div>
</div>
""", unsafe_allow_html=True)

# Refresh controls
col_r1, col_r2, col_r3 = st.columns([1, 1, 6])
with col_r1:
    if st.button("⟳ Refresh", type="primary", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
with col_r2:
    period = st.selectbox("Chart period", ["1mo", "3mo", "6mo", "1y"], index=2, label_visibility="collapsed")

st.markdown('<div class="term-divider"></div>', unsafe_allow_html=True)

# Fetch all quotes
with st.spinner("Fetching live market data…"):
    quotes = fetch_all_quotes()

# ── SECTION 1: INDIA MARKETS ──────────────────
st.markdown('<div class="section-label">🇮🇳 India Markets</div>', unsafe_allow_html=True)
c1, c2, c3, c4, c5, c6 = st.columns(6)
with c1: render_metric("Nifty 50",       "nifty50",      quotes)
with c2: render_metric("Sensex",         "sensex",       quotes)
with c3: render_metric("Nifty Bank",     "nifty_bank",   quotes)
with c4: render_metric("Nifty IT",       "nifty_it",     quotes)
with c5: render_metric("Nifty Midcap",   "nifty_midcap", quotes)
with c6: render_metric("India VIX",      "india_vix",    quotes, decimals=1)

st.markdown('<div class="term-divider"></div>', unsafe_allow_html=True)

# ── SECTION 2: FOREX & COMMODITIES ───────────
st.markdown('<div class="section-label">💱 Forex & Commodities</div>', unsafe_allow_html=True)
c1, c2, c3, c4, c5, c6 = st.columns(6)
with c1: render_metric("USD / INR",   "usdinr",    quotes, decimals=2)
with c2: render_metric("EUR / USD",   "eurusd",    quotes, decimals=4)
with c3: render_metric("DXY Index",   "dxy",       quotes, decimals=2)
with c4: render_metric("Gold ($/oz)", "gold",      quotes, prefix="$")
with c5: render_metric("Crude WTI",   "crude_wti", quotes, prefix="$")
with c6: render_metric("Silver",      "silver",    quotes, prefix="$")

st.markdown('<div class="term-divider"></div>', unsafe_allow_html=True)

# ── SECTION 3: GLOBAL & RATES ─────────────────
st.markdown('<div class="section-label">🌍 Global Indices & Rates</div>', unsafe_allow_html=True)
c1, c2, c3, c4, c5 = st.columns(5)
with c1: render_metric("S&P 500",    "sp500",   quotes)
with c2: render_metric("Nasdaq",     "nasdaq",  quotes)
with c3: render_metric("CBOE VIX",  "vix",     quotes, decimals=1)
with c4: render_metric("US 10Y %",  "us10y",   quotes, suffix="%", decimals=2)
with c5: render_metric("US 3M %",   "us2y",    quotes, suffix="%", decimals=2)

st.markdown('<div class="term-divider"></div>', unsafe_allow_html=True)

# ── SECTION 4: CHARTS ─────────────────────────
st.markdown('<div class="section-label">📊 Market Charts</div>', unsafe_allow_html=True)

chart_tab1, chart_tab2, chart_tab3, chart_tab4 = st.tabs([
    "🇮🇳 Nifty 50", "💵 USD/INR", "🥇 Gold", "🛢️ Crude Oil"
])

with chart_tab1:
    df = fetch_history("^NSEI", period=period)
    fig = make_chart(df, "Nifty 50", show_volume=True, height=360)
    if fig: st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    else: st.info("Chart data unavailable. Market may be closed.")

with chart_tab2:
    df = fetch_history("USDINR=X", period=period)
    fig = make_chart(df, "USD/INR", color="#4ab87a", height=360)
    if fig: st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    else: st.info("Chart data unavailable.")

with chart_tab3:
    df = fetch_history("GC=F", period=period)
    fig = make_chart(df, "Gold", color="#c9a96e", height=360)
    if fig: st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    else: st.info("Chart data unavailable.")

with chart_tab4:
    df = fetch_history("CL=F", period=period)
    fig = make_chart(df, "Crude WTI", color="#e05c6c", height=360)
    if fig: st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    else: st.info("Chart data unavailable.")

st.markdown('<div class="term-divider"></div>', unsafe_allow_html=True)

# ── SECTION 5: SIGNALS + YIELD CURVE ──────────
col_sig, col_yc = st.columns([3, 2])

with col_sig:
    st.markdown('<div class="section-label">⚡ Live Macro Signals</div>', unsafe_allow_html=True)
    signals = generate_signals(quotes)
    for sig_type, sig_text in signals:
        css = {"bull": "signal-bull", "bear": "signal-bear", "neu": "signal-neu"}[sig_type]
        icon = {"bull": "▲", "bear": "▼", "neu": "●"}[sig_type]
        st.markdown(f'<div class="signal-card {css}">{icon} {sig_text}</div>', unsafe_allow_html=True)

with col_yc:
    st.markdown('<div class="section-label">📈 US Yield Curve Snapshot</div>', unsafe_allow_html=True)
    fig_yc = yield_curve_chart(quotes)
    if fig_yc:
        st.plotly_chart(fig_yc, use_container_width=True, config={"displayModeBar": False})
        spread = None
        us10y_q = quotes.get("us10y")
        us2y_q  = quotes.get("us2y")
        if us10y_q and us2y_q:
            spread = us10y_q['price'] - us2y_q['price']
            if spread < 0:
                st.markdown(f'<div class="signal-card signal-bear">⚠ Inverted: 10Y-3M spread = {spread:.2f}%. Historically a recession precursor.</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="signal-card signal-bull">✓ Normal curve. 10Y-3M spread = +{spread:.2f}%.</div>', unsafe_allow_html=True)
    else:
        st.info("Yield data unavailable.")

st.markdown('<div class="term-divider"></div>', unsafe_allow_html=True)

# ── SECTION 6: FII / DII DATA ─────────────────
st.markdown('<div class="section-label">🏦 FII / DII Activity (Latest from NSE)</div>', unsafe_allow_html=True)

fii_data = fetch_fii_dii()
if fii_data is not None and not fii_data.empty:
    st.dataframe(
        fii_data.head(10),
        use_container_width=True,
        hide_index=True
    )
else:
    # Elegant fallback with explanation
    st.markdown("""
    <div class="signal-card signal-neu">
        ℹ NSE FII/DII data refreshes after 6 PM IST on trading days.
        Real-time data fetched via <code>nselib</code> — available when NSE servers are accessible.
        Check <a href="https://www.nseindia.com/market-data/fii-dii-activity" style="color:#c9a96e" target="_blank">NSE India</a> for latest figures.
    </div>
    """, unsafe_allow_html=True)
    
    # Show a sample table structure
    sample = pd.DataFrame({
        "Category": ["FII/FPI", "DII", "MF (DII subset)"],
        "Buy Value (₹ Cr)": ["—", "—", "—"],
        "Sell Value (₹ Cr)": ["—", "—", "—"],
        "Net Value (₹ Cr)": ["—", "—", "—"],
    })
    st.dataframe(sample, use_container_width=True, hide_index=True)

st.markdown('<div class="term-divider"></div>', unsafe_allow_html=True)

# ── SECTION 7: NIFTY SECTORS ──────────────────
st.markdown('<div class="section-label">📂 Nifty Sector Indices</div>', unsafe_allow_html=True)

SECTOR_TICKERS = {
    "IT":        "^CNXIT",
    "Bank":      "^NSEBANK",
    "FMCG":      "^CNXFMCG",
    "Pharma":    "^CNXPHARMA",
    "Auto":      "^CNXAUTO",
    "Energy":    "^CNXENERGY",
    "Metal":     "^CNXMETAL",
    "Realty":    "^CNXREALTY",
}

@st.cache_data(ttl=300)
def fetch_sector_quotes():
    results = {}
    for name, sym in SECTOR_TICKERS.items():
        results[name] = fetch_quote(sym)
    return results

sector_quotes = fetch_sector_quotes()

sec_cols = st.columns(8)
for i, (sec_name, q) in enumerate(sector_quotes.items()):
    with sec_cols[i]:
        if q:
            chg_str, cls = fmt_change(q['change'], q['pct'])
            color = "#4ab87a" if q['pct'] >= 0 else "#e05c6c"
            st.markdown(f"""
            <div class="metric-card" style="text-align:center; padding:0.8rem 0.5rem">
                <div class="metric-label">{sec_name}</div>
                <div class="metric-value" style="font-size:0.9rem">{fmt_price(q['price'])}</div>
                <div class="metric-change {'pos' if q['pct']>=0 else 'neg'}" style="font-size:0.6rem">
                    {'▲' if q['pct']>=0 else '▼'} {abs(q['pct']):.2f}%
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="metric-card" style="text-align:center; padding:0.8rem 0.5rem">
                <div class="metric-label">{sec_name}</div>
                <div class="metric-value" style="font-size:0.9rem">—</div>
            </div>
            """, unsafe_allow_html=True)

# ── FOOTER ────────────────────────────────────
st.markdown("""
<div class="term-divider"></div>
<div class="term-footer">
    Macro Terminal · Day 08 of 30 Days of AI Finance · 
    Data: Yahoo Finance, NSE India · 
    Built with Python + Streamlit · 
    Refreshes every 5 minutes · Not investment advice
</div>
""", unsafe_allow_html=True)
