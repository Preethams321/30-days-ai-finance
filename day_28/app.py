import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────────────
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,700&family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Syne', sans-serif !important;
    background-color: #09090e !important;
    color: #e8e4dc !important;
}
[data-testid="stApp"], .stApp,
[data-testid="stAppViewContainer"],
[data-testid="stVerticalBlock"] {
    background-color: #09090e !important;
}
#MainMenu, footer, header,
[data-testid="stDecoration"],
[data-testid="stToolbar"] { display: none !important; }
.block-container { padding: 1rem 2rem !important; max-width: 100% !important; }
[data-testid="stMetric"] {
    background: #111118 !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 3px !important;
    padding: 1rem !important;
}
[data-testid="stMetricValue"] {
    font-family: 'DM Mono', monospace !important;
    color: #e8e4dc !important;
    font-size: 1.4rem !important;
}
[data-testid="stMetricLabel"] {
    font-family: 'DM Mono', monospace !important;
    color: #555 !important;
    font-size: 0.6rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}
.stButton > button[kind="primary"] {
    background: #c9a96e !important;
    color: #09090e !important;
    border: none !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    border-radius: 2px !important;
}
.stSlider [data-baseweb="slider"] { padding: 0 !important; }
::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-thumb { background: rgba(201,169,110,0.15); border-radius: 2px; }

/* Slider label color */
[data-testid="stSlider"] label {
    font-family: 'DM Mono', monospace !important;
    color: #888 !important;
    font-size: 0.72rem !important;
}
/* Caption color */
[data-testid="stCaptionContainer"] p {
    font-family: 'DM Mono', monospace !important;
    color: #444 !important;
    font-size: 0.65rem !important;
}
/* Expander */
[data-testid="stExpander"] {
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 4px !important;
    background: #111118 !important;
}
</style>
"""

# ─────────────────────────────────────────────────────────────────────
# PLOTLY LAYOUT DEFAULTS
# ─────────────────────────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='DM Mono, monospace', color='#888', size=10),
    margin=dict(l=40, r=20, t=50, b=40),
    xaxis=dict(gridcolor='rgba(255,255,255,0.04)', zerolinecolor='rgba(255,255,255,0.06)'),
    yaxis=dict(gridcolor='rgba(255,255,255,0.04)', zerolinecolor='rgba(255,255,255,0.06)'),
)

# ─────────────────────────────────────────────────────────────────────
# COMPONENT DEFINITIONS
# ─────────────────────────────────────────────────────────────────────
COMPONENTS = {
    "india_vix": {
        "name": "India VIX",
        "ticker": "^INDIAVIX",
        "weight": 25,
        "live": True,
        "description": "NSE's volatility index — measures expected market volatility over next 30 days",
        "source": "NSE India via Yahoo Finance (^INDIAVIX)",
        "current_fallback": 12.84,
    },
    "nifty_momentum": {
        "name": "Nifty Momentum",
        "ticker": "^NSEI",
        "weight": 20,
        "live": True,
        "description": "Nifty 50 vs its 125-day moving average — above = bullish momentum, below = bearish",
        "source": "NSE Nifty 50 via Yahoo Finance (^NSEI)",
        "current_fallback": 0.03,
    },
    "high_low": {
        "name": "52-Week High-Low",
        "ticker": "^NSEI",
        "weight": 20,
        "live": True,
        "description": "Where Nifty sits within its 52-week range — near high = greed, near low = fear",
        "source": "NSE Nifty 50 via Yahoo Finance (^NSEI)",
        "current_fallback": 0.72,
    },
    "nifty_pe": {
        "name": "Nifty P/E Ratio",
        "ticker": None,
        "weight": 20,
        "live": False,
        "user_editable": True,
        "description": "Nifty 50 trailing PE — measures market valuation vs historical average",
        "source": "NSE India (nifty-pe-ratio.com) · Updated manually · Current: 20.75 as of 26 Jun 2026",
        "current_value": 20.75,
    },
    "pcr": {
        "name": "Put-Call Ratio",
        "ticker": None,
        "weight": 15,
        "live": False,
        "user_editable": True,
        "description": "Nifty options PCR — high PCR = bearish positioning (fear), low = bullish (greed)",
        "source": "NSE India F&O data · Input manually from ChainDesk (Day 24) or NSE website",
        "current_value": 1.05,
    },
}

# ─────────────────────────────────────────────────────────────────────
# SCORING ENGINE
# ─────────────────────────────────────────────────────────────────────
def score_vix(vix_value: float) -> float:
    score = 100 * (30 - vix_value) / (30 - 8)
    return float(np.clip(score, 0, 100))

def score_momentum(pct_above_ma: float) -> float:
    score = 50 + (pct_above_ma / 0.05) * 50
    return float(np.clip(score, 0, 100))

def score_high_low(percentile: float) -> float:
    return float(np.clip(percentile * 100, 0, 100))

def score_pe(pe_value: float) -> float:
    score = 100 * (28 - pe_value) / (28 - 15)
    return float(np.clip(score, 0, 100))

def score_pcr(pcr_value: float) -> float:
    score = 100 * (1.5 - pcr_value) / (1.5 - 0.5)
    return float(np.clip(score, 0, 100))

def compute_composite_score(component_scores: dict, weights: dict) -> float:
    total_weight = sum(weights.values())
    weighted_sum = sum(
        component_scores[k] * weights[k] / total_weight
        for k in component_scores
    )
    return round(weighted_sum, 1)

def interpret_score(score: float) -> dict:
    if score >= 80:
        return {
            "label": "Extreme Greed",
            "color": "#4ab87a",
            "emoji": "🚀",
            "short": "Markets are dangerously optimistic. Historically precedes corrections.",
            "ghost": "Everyone is buying. Valuations are stretched. The market feels invincible right now — which is usually when it isn't. Not a signal to sell immediately, but a signal to be more selective with new positions.",
        }
    elif score >= 60:
        return {
            "label": "Greed",
            "color": "#8ab87a",
            "emoji": "😊",
            "short": "Optimism is driving markets higher. Momentum is positive.",
            "ghost": "Markets are feeling good. More buyers than sellers, VIX is calm, Nifty is trending up. Good time to be invested, but don't chase everything blindly.",
        }
    elif score >= 40:
        return {
            "label": "Neutral",
            "color": "#c9a96e",
            "emoji": "😐",
            "short": "Mixed signals. Neither fear nor euphoria dominates.",
            "ghost": "The market is undecided. Some signals point up, others point down. This is actually a healthy state — extreme readings in either direction are more dangerous.",
        }
    elif score >= 20:
        return {
            "label": "Fear",
            "color": "#e0a04a",
            "emoji": "😰",
            "short": "Nervousness is spreading. Investors are cautious.",
            "ghost": "People are worried. VIX is elevated, Nifty is struggling, and options traders are buying more puts than calls. Historically, sustained fear creates buying opportunities — but timing it is hard.",
        }
    else:
        return {
            "label": "Extreme Fear",
            "color": "#e05c6c",
            "emoji": "😱",
            "short": "Panic is setting in. Maximum pessimism in the market.",
            "ghost": "Everyone wants out. Historically, this is when the best long-term buying opportunities emerge — if you have a stomach for volatility. 'Be fearful when others are greedy, be greedy when others are fearful' — Warren Buffett.",
        }

# ─────────────────────────────────────────────────────────────────────
# LIVE DATA FETCH
# ─────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def fetch_live_data() -> dict:
    result = {
        "vix":            12.84,
        "nifty_current":  23500.0,
        "nifty_ma125":    23000.0,
        "nifty_52w_high": 24500.0,
        "nifty_52w_low":  20300.0,
        "pct_above_ma":   0.022,
        "hl_percentile":  0.72,
        "data_fresh":     False,
        "fetch_time":     None,
        "errors":         [],
        "nifty_df":       None,
        "vix_df":         None,
    }

    # Fetch India VIX
    try:
        vix_df = yf.download("^INDIAVIX", period="1y", interval="1d",
                              progress=False, auto_adjust=True)
        if isinstance(vix_df.columns, pd.MultiIndex):
            vix_df.columns = [c[0] for c in vix_df.columns]
        if not vix_df.empty and 'Close' in vix_df.columns:
            result["vix"] = float(vix_df['Close'].dropna().iloc[-1])
            result["vix_df"] = vix_df
            result["data_fresh"] = True
    except Exception as e:
        result["errors"].append(f"VIX: {str(e)[:60]}")

    # Fetch Nifty 50
    try:
        nifty_df = yf.download("^NSEI", period="2y", interval="1d",
                                progress=False, auto_adjust=True)
        if isinstance(nifty_df.columns, pd.MultiIndex):
            nifty_df.columns = [c[0] for c in nifty_df.columns]
        if not nifty_df.empty and 'Close' in nifty_df.columns:
            closes = nifty_df['Close'].dropna()
            current = float(closes.iloc[-1])
            ma125 = float(closes.rolling(125).mean().iloc[-1]) if len(closes) >= 125 else float(closes.mean())
            pct_above = (current - ma125) / ma125
            high_52w = float(closes.tail(252).max())
            low_52w  = float(closes.tail(252).min())
            hl_pct   = (current - low_52w) / (high_52w - low_52w) if high_52w > low_52w else 0.5

            result.update({
                "nifty_current":  current,
                "nifty_ma125":    ma125,
                "nifty_52w_high": high_52w,
                "nifty_52w_low":  low_52w,
                "pct_above_ma":   pct_above,
                "hl_percentile":  hl_pct,
                "data_fresh":     True,
                "nifty_df":       nifty_df,
            })
    except Exception as e:
        result["errors"].append(f"Nifty: {str(e)[:60]}")

    result["fetch_time"] = datetime.now().strftime('%H:%M:%S IST')
    return result

# ─────────────────────────────────────────────────────────────────────
# CHARTS
# ─────────────────────────────────────────────────────────────────────
def make_gauge(score: float, interpretation: dict) -> go.Figure:
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={
            "font": {"size": 52, "color": "#e8e4dc", "family": "DM Mono"},
            "suffix": "",
        },
        title={
            "text": f"{interpretation['emoji']} {interpretation['label']}",
            "font": {"size": 22, "color": interpretation['color'],
                     "family": "Playfair Display, serif"},
        },
        gauge={
            "axis": {
                "range": [0, 100],
                "tickvals": [0, 25, 50, 75, 100],
                "ticktext": ["0", "25", "50", "75", "100"],
                "tickfont": {"color": "#444", "family": "DM Mono", "size": 10},
                "tickcolor": "#333",
            },
            "bar": {"color": interpretation['color'], "thickness": 0.25},
            "bgcolor": "rgba(0,0,0,0)",
            "bordercolor": "rgba(0,0,0,0)",
            "steps": [
                {"range": [0, 20],   "color": "rgba(224,92,108,0.15)"},
                {"range": [20, 40],  "color": "rgba(224,160,74,0.12)"},
                {"range": [40, 60],  "color": "rgba(201,169,110,0.10)"},
                {"range": [60, 80],  "color": "rgba(138,184,122,0.12)"},
                {"range": [80, 100], "color": "rgba(74,184,122,0.15)"},
            ],
            "threshold": {
                "line": {"color": interpretation['color'], "width": 4},
                "thickness": 0.85,
                "value": score,
            },
        },
    ))

    for x, label, color in [
        (0.10, "EXTREME<br>FEAR",  "#e05c6c"),
        (0.28, "FEAR",             "#e0a04a"),
        (0.50, "NEUTRAL",          "#c9a96e"),
        (0.72, "GREED",            "#8ab87a"),
        (0.90, "EXTREME<br>GREED", "#4ab87a"),
    ]:
        fig.add_annotation(
            x=x, y=0.10, text=label, showarrow=False,
            font=dict(size=7, color=color, family="DM Mono"),
            xref="paper", yref="paper", align="center"
        )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=40, t=80, b=20),
        height=340,
        font=dict(family="DM Mono", color="#888"),
    )
    return fig


def make_nifty_sentiment_chart(nifty_df, vix_df) -> go.Figure:
    fig = go.Figure()

    # Use last 252 trading days of Nifty
    if nifty_df is not None and 'Close' in nifty_df.columns:
        nifty_plot = nifty_df['Close'].dropna().tail(252)
    else:
        return fig

    # Color bands from VIX if available
    if vix_df is not None and 'Close' in vix_df.columns:
        vix_plot = vix_df['Close'].dropna()
        # Align on common dates
        merged = pd.DataFrame({'nifty': nifty_plot, 'vix': vix_plot}).dropna()
        if not merged.empty:
            # Add background rectangles for fear/greed zones
            fear_dates  = merged[merged['vix'] > 18].index
            greed_dates = merged[merged['vix'] < 13].index

            def add_band_shapes(dates, fillcolor):
                if len(dates) == 0:
                    return
                # Group consecutive dates into ranges
                groups, start = [], None
                prev = None
                for d in sorted(dates):
                    if prev is None or (d - prev).days > 5:
                        if start is not None:
                            groups.append((start, prev))
                        start = d
                    prev = d
                if start is not None:
                    groups.append((start, prev))
                for s, e in groups:
                    fig.add_vrect(x0=s, x1=e, fillcolor=fillcolor,
                                  opacity=0.15, layer="below", line_width=0)

            add_band_shapes(fear_dates,  "#e05c6c")
            add_band_shapes(greed_dates, "#4ab87a")

            fig.add_trace(go.Scatter(
                x=merged.index, y=merged['nifty'],
                mode='lines', name='Nifty 50',
                line=dict(color='#c9a96e', width=2),
                showlegend=False,
            ))
        else:
            fig.add_trace(go.Scatter(
                x=nifty_plot.index, y=nifty_plot.values,
                mode='lines', name='Nifty 50',
                line=dict(color='#c9a96e', width=2),
                showlegend=False,
            ))
    else:
        fig.add_trace(go.Scatter(
            x=nifty_plot.index, y=nifty_plot.values,
            mode='lines', name='Nifty 50',
            line=dict(color='#c9a96e', width=2),
            showlegend=False,
        ))

    # Legend annotations
    fig.add_annotation(x=0.01, y=0.95, text="🟥 VIX > 18 (Fear Zone)",
                       xref="paper", yref="paper", showarrow=False,
                       font=dict(size=8, color="#e05c6c", family="DM Mono"), align="left")
    fig.add_annotation(x=0.01, y=0.85, text="🟩 VIX < 13 (Greed Zone)",
                       xref="paper", yref="paper", showarrow=False,
                       font=dict(size=8, color="#4ab87a", family="DM Mono"), align="left")

    layout = dict(PLOTLY_LAYOUT)
    layout.update(dict(
        title=dict(text='Nifty 50 — 1 Year Price History with Sentiment Zones',
                   font=dict(color='#c9a96e', family='Playfair Display', size=13)),
        xaxis_title='Date',
        yaxis_title='Nifty 50 Level',
        height=280,
        showlegend=False,
    ))
    fig.update_layout(**layout)
    return fig

# ─────────────────────────────────────────────────────────────────────
# UI HELPERS
# ─────────────────────────────────────────────────────────────────────
def show_data_banner(live_data: dict):
    if live_data.get('data_fresh'):
        color  = "#4ab87a"
        status = f"🟢 Live · VIX and Nifty data from Yahoo Finance · Refreshed at {live_data['fetch_time']}"
    else:
        color  = "#e0a04a"
        status = "🟡 Using fallback data · Yahoo Finance unavailable · Values approximate"

    st.markdown(f"""
    <div style="background:{color}12;border:1px solid {color}25;padding:0.4rem 0.8rem;
                border-radius:3px;margin-bottom:1rem;font-family:'DM Mono',monospace;
                font-size:0.68rem;color:{color}">
        {status} · PE and PCR are manually updated — not real-time
    </div>""", unsafe_allow_html=True)


def component_card(name, raw_value, score, source, is_live, description):
    live_badge  = "🟢 LIVE" if is_live else "🔵 MANUAL"
    badge_color = "#4ab87a" if is_live else "#4a9eff"
    score_color = "#4ab87a" if score >= 60 else "#e05c6c" if score <= 40 else "#c9a96e"
    src_short   = source[:32] + "..." if len(source) > 32 else source

    st.markdown(f"""
    <div style="background:#111118;border:1px solid rgba(255,255,255,0.06);
                border-radius:4px;padding:1.2rem;height:100%;box-sizing:border-box">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
            <span style="font-family:'DM Mono',monospace;font-size:0.62rem;color:#555;
                         text-transform:uppercase;letter-spacing:0.1em">{name}</span>
            <span style="font-family:'DM Mono',monospace;font-size:0.58rem;
                         color:{badge_color}">{live_badge}</span>
        </div>
        <div style="font-family:'DM Mono',monospace;font-size:1.5rem;
                    color:#e8e4dc;margin-bottom:4px">{raw_value}</div>
        <div style="font-size:0.72rem;color:#555;margin-bottom:10px;
                    font-family:'Syne',sans-serif">{description}</div>
        <div style="background:rgba(255,255,255,0.04);border-radius:2px;
                    height:4px;margin-bottom:8px;overflow:hidden">
            <div style="width:{score:.0f}%;height:100%;
                        background:{score_color};border-radius:2px"></div>
        </div>
        <div style="display:flex;justify-content:space-between;align-items:center">
            <span style="font-family:'DM Mono',monospace;font-size:0.65rem;
                         color:{score_color}">Score: {score:.0f}/100</span>
            <span style="font-family:'DM Mono',monospace;font-size:0.58rem;
                         color:#333">{src_short}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'pe_value' not in st.session_state:
    st.session_state.pe_value = 20.75
if 'pcr_value' not in st.session_state:
    st.session_state.pcr_value = 1.05

# ─────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SentiDesk · India Fear & Greed Index",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)
st.markdown(CSS, unsafe_allow_html=True)

# Fetch live data once on load
live_data = fetch_live_data()

# ─────────────────────────────────────────────────────────────────────
# HOME PAGE
# ─────────────────────────────────────────────────────────────────────
if st.session_state.page == 'home':

    # Quick composite for hero preview
    _vix_s  = score_vix(live_data["vix"])
    _mom_s  = score_momentum(live_data["pct_above_ma"])
    _hl_s   = score_high_low(live_data["hl_percentile"])
    _pe_s   = score_pe(st.session_state.pe_value)
    _pcr_s  = score_pcr(st.session_state.pcr_value)
    _scores = {"india_vix": _vix_s, "nifty_momentum": _mom_s, "high_low": _hl_s,
               "nifty_pe": _pe_s, "pcr": _pcr_s}
    _weights = {k: COMPONENTS[k]["weight"] for k in _scores}
    _composite = compute_composite_score(_scores, _weights)
    _interp    = interpret_score(_composite)

    # Hero
    st.markdown("""
    <div style="text-align:center;padding:3rem 1rem 1.5rem">
        <div style="font-family:'DM Mono',monospace;font-size:0.68rem;color:#555;
                    letter-spacing:0.18em;text-transform:uppercase;margin-bottom:1rem">
            ● INDIA FEAR & GREED INDEX · 5 LIVE SIGNALS · NSE DATA
        </div>
        <h1 style="font-family:'Playfair Display',serif;font-size:clamp(2.2rem,5vw,3.8rem);
                   font-weight:700;color:#e8e4dc;margin:0 0 0.5rem;line-height:1.1">
            SentiDesk
        </h1>
        <p style="font-family:'Playfair Display',serif;font-style:italic;
                  color:#c9a96e;font-size:1.1rem;margin:0 0 1.5rem">
            How does the Indian market feel right now?
        </p>
        <p style="font-family:'Syne',sans-serif;color:#666;font-size:0.88rem;
                  max-width:600px;margin:0 auto 2rem;line-height:1.6">
            CNN's Fear &amp; Greed Index is the most-watched sentiment tool in US markets.
            There was no equivalent for India — until now. SentiDesk aggregates 5 real market
            signals into a single composite score: how fearful or greedy is the Indian market today?
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Live stat strip
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Current Score", f"{_composite:.0f} / 100",
                  delta=_interp['label'])
    with c2:
        st.metric("India VIX", f"{live_data['vix']:.2f}",
                  delta="Live" if live_data['data_fresh'] else "Fallback")
    with c3:
        st.metric("Nifty 50", f"{live_data['nifty_current']:,.0f}",
                  delta="Live" if live_data['data_fresh'] else "Fallback")
    with c4:
        _hl_pct = live_data['hl_percentile']
        st.metric("52-Week Position", f"{_hl_pct*100:.0f}th pctl",
                  delta="Live" if live_data['data_fresh'] else "Fallback")

    st.markdown("<br>", unsafe_allow_html=True)

    # Feature pills
    pills_html = "".join([
        f'<span style="font-family:\'DM Mono\',monospace;font-size:0.65rem;'
        f'background:#111118;border:1px solid rgba(255,255,255,0.08);'
        f'border-radius:20px;padding:0.3rem 0.8rem;color:#888;margin:0.2rem;">{p}</span>'
        for p in ["India VIX", "Nifty Momentum", "52-Week High-Low", "Nifty PE", "Put-Call Ratio"]
    ])
    st.markdown(f'<div style="text-align:center;margin-bottom:2rem">{pills_html}</div>',
                unsafe_allow_html=True)

    # Feature grid
    st.markdown("""
    <div style="font-family:'DM Mono',monospace;font-size:0.62rem;color:#555;
                letter-spacing:0.12em;text-transform:uppercase;margin-bottom:1rem">
        The 5 Signals
    </div>
    """, unsafe_allow_html=True)

    feature_data = [
        ("India VIX", "Expected market volatility over next 30 days",
         "High VIX = fear. Low VIX = calm. NSE's own volatility gauge, live via Yahoo Finance.", "🌡️", True),
        ("Nifty Momentum", "Nifty 50 vs its 125-day moving average",
         "Above the average = bullish trend. Below = bearish. Catches trend reversals early.", "📈", True),
        ("52-Week High-Low", "Nifty's position within its annual range",
         "Near 52-week high = greed. Near 52-week low = fear. Simple, powerful.", "📏", True),
        ("Nifty P/E Ratio", "Market valuation vs historical average",
         "Cheap market (low PE) = greed opportunity. Expensive market (high PE) = fear of overpaying.", "💹", False),
        ("Put-Call Ratio", "Options positioning of institutional traders",
         "More puts than calls = bearish (fear). More calls = bullish (greed). The smart-money signal.", "🎯", False),
    ]

    cols = st.columns(5)
    for i, (name, what, why, icon, is_live) in enumerate(feature_data):
        badge_color = "#4ab87a" if is_live else "#4a9eff"
        badge_text  = "🟢 LIVE" if is_live else "🔵 MANUAL"
        with cols[i]:
            st.markdown(f"""
            <div style="background:#111118;border:1px solid rgba(255,255,255,0.06);
                        border-radius:4px;padding:1.2rem;height:100%">
                <div style="font-size:1.4rem;margin-bottom:8px">{icon}</div>
                <div style="font-family:'DM Mono',monospace;font-size:0.6rem;
                            color:#555;text-transform:uppercase;letter-spacing:0.1em;
                            margin-bottom:6px">{name}</div>
                <div style="font-family:'DM Mono',monospace;font-size:0.58rem;
                            color:{badge_color};margin-bottom:10px">{badge_text}</div>
                <div style="font-family:'Syne',sans-serif;color:#888;
                            font-size:0.78rem;margin-bottom:8px;font-weight:600">{what}</div>
                <div style="font-family:'Syne',sans-serif;color:#555;
                            font-size:0.72rem;line-height:1.5">{why}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # CTA
    col_l, col_c, col_r = st.columns([2, 1, 2])
    with col_c:
        if st.button("→ Check the Market Pulse", type="primary", use_container_width=True):
            st.session_state.page = 'terminal'
            st.rerun()

    st.markdown("""
    <div style="text-align:center;margin-top:1rem;font-family:'DM Mono',monospace;
                font-size:0.65rem;color:#333">
        3 of 5 signals are live via Yahoo Finance · PE and PCR are manually updated — see sources
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────
# TERMINAL PAGE
# ─────────────────────────────────────────────────────────────────────
else:
    # Nav
    c_back, c_title = st.columns([1, 6])
    with c_back:
        if st.button("← Home", type="secondary"):
            st.session_state.page = 'home'
            st.rerun()
    with c_title:
        st.markdown("""
        <div style="font-family:'DM Mono',monospace;font-size:0.68rem;color:#555;
                    letter-spacing:0.14em;text-transform:uppercase;padding-top:0.5rem">
            SentiDesk · India Fear & Greed Index · Terminal
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Data banner
    show_data_banner(live_data)

    # ── SECTION 3 first: sliders for instant recompute
    st.markdown("""
    <div style="font-family:'DM Mono',monospace;font-size:0.62rem;color:#555;
                letter-spacing:0.12em;text-transform:uppercase;margin-bottom:0.5rem">
        ⚙️ Update Manual Inputs
    </div>
    """, unsafe_allow_html=True)
    st.caption("PE Ratio and PCR are not available via free APIs. Update these daily from NSE or ChainDesk (Day 24).")

    col_pe, col_pcr = st.columns(2)
    with col_pe:
        pe_value = st.slider(
            "Nifty PE Ratio",
            min_value=12.0, max_value=35.0,
            value=float(st.session_state.pe_value),
            step=0.1, format="%.1f",
            help="Source: nifty-pe-ratio.com or NSE website · Current: 20.75 (26 Jun 2026)"
        )
        st.session_state.pe_value = pe_value
        st.caption("📊 Source: NSE India · Historical consolidated avg: ~20-21")

    with col_pcr:
        pcr_value = st.slider(
            "Put-Call Ratio (Nifty F&O)",
            min_value=0.4, max_value=2.0,
            value=float(st.session_state.pcr_value),
            step=0.01, format="%.2f",
            help="Source: NSE F&O data or ChainDesk (Day 24) · Neutral range: 0.9-1.1"
        )
        st.session_state.pcr_value = pcr_value
        st.caption("📊 Source: NSE F&O · Get live value from ChainDesk ↗")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Compute scores
    vix_score  = score_vix(live_data["vix"])
    mom_score  = score_momentum(live_data["pct_above_ma"])
    hl_score   = score_high_low(live_data["hl_percentile"])
    pe_score   = score_pe(pe_value)
    pcr_score  = score_pcr(pcr_value)

    component_scores = {
        "india_vix":      vix_score,
        "nifty_momentum": mom_score,
        "high_low":       hl_score,
        "nifty_pe":       pe_score,
        "pcr":            pcr_score,
    }
    weights = {k: COMPONENTS[k]["weight"] for k in component_scores}
    composite   = compute_composite_score(component_scores, weights)
    interp      = interpret_score(composite)

    # ── SECTION 1: Big Gauge
    st.markdown(f"""
    <h2 style="font-family:'Playfair Display',serif;font-size:1.1rem;
               color:#c9a96e;margin-bottom:0.5rem;font-style:italic">
        Composite Sentiment Score
    </h2>
    """, unsafe_allow_html=True)

    gauge_col, interp_col = st.columns([3, 2])
    with gauge_col:
        fig_gauge = make_gauge(composite, interp)
        st.plotly_chart(fig_gauge, use_container_width=True)

    with interp_col:
        st.markdown("<br><br>", unsafe_allow_html=True)
        # Technical card
        st.markdown(f"""
        <div style="background:#111118;border:1px solid rgba(255,255,255,0.06);
                    border-radius:4px;padding:1.2rem;margin-bottom:0.8rem">
            <div style="font-family:'DM Mono',monospace;font-size:0.6rem;color:#555;
                        text-transform:uppercase;letter-spacing:0.1em;margin-bottom:8px">
                Score Breakdown
            </div>
            <div style="font-family:'DM Mono',monospace;font-size:0.72rem;
                        color:#888;line-height:1.8">
                <span style="color:#555">India VIX (25%)</span> → {vix_score:.1f}<br>
                <span style="color:#555">Nifty Momentum (20%)</span> → {mom_score:.1f}<br>
                <span style="color:#555">52-Week H/L (20%)</span> → {hl_score:.1f}<br>
                <span style="color:#555">Nifty PE (20%)</span> → {pe_score:.1f}<br>
                <span style="color:#555">Put-Call Ratio (15%)</span> → {pcr_score:.1f}<br>
                <div style="border-top:1px solid rgba(255,255,255,0.06);margin-top:8px;
                            padding-top:8px;color:#e8e4dc">
                    Composite → <strong>{composite}</strong> / 100
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Plain English card
        st.markdown(f"""
        <div style="background:{interp['color']}10;border:1px solid {interp['color']}25;
                    border-radius:4px;padding:1.2rem">
            <div style="font-family:'DM Mono',monospace;font-size:0.6rem;
                        color:{interp['color']};text-transform:uppercase;
                        letter-spacing:0.1em;margin-bottom:8px">
                {interp['emoji']} What This Means
            </div>
            <div style="font-family:'Syne',sans-serif;font-size:0.8rem;
                        color:#e8e4dc;margin-bottom:8px;font-weight:600">
                {interp['short']}
            </div>
            <div style="font-family:'Syne',sans-serif;font-size:0.75rem;
                        color:#888;line-height:1.6">
                {interp['ghost']}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── SECTION 2: Component Breakdown
    st.markdown("""
    <div style="font-family:'DM Mono',monospace;font-size:0.62rem;color:#555;
                letter-spacing:0.12em;text-transform:uppercase;margin-bottom:1rem">
        Component Breakdown
    </div>
    """, unsafe_allow_html=True)

    # Row 1: 3 live components
    c1, c2, c3 = st.columns(3)
    with c1:
        component_card(
            name="India VIX",
            raw_value=f"{live_data['vix']:.2f}",
            score=vix_score,
            source=COMPONENTS['india_vix']['source'],
            is_live=True,
            description=COMPONENTS['india_vix']['description'],
        )
    with c2:
        pct_display = f"{live_data['pct_above_ma']*100:+.2f}% vs 125d MA"
        component_card(
            name="Nifty Momentum",
            raw_value=pct_display,
            score=mom_score,
            source=COMPONENTS['nifty_momentum']['source'],
            is_live=True,
            description=COMPONENTS['nifty_momentum']['description'],
        )
    with c3:
        hl_display = f"{live_data['hl_percentile']*100:.0f}th pctl"
        component_card(
            name="52-Week High-Low",
            raw_value=hl_display,
            score=hl_score,
            source=COMPONENTS['high_low']['source'],
            is_live=True,
            description=COMPONENTS['high_low']['description'],
        )

    st.markdown("<div style='margin-top:0.6rem'></div>", unsafe_allow_html=True)

    # Row 2: 2 manual components (centered)
    _, c4, c5, _ = st.columns([0.5, 2, 2, 0.5])
    with c4:
        component_card(
            name="Nifty P/E Ratio",
            raw_value=f"{pe_value:.2f}x",
            score=pe_score,
            source=COMPONENTS['nifty_pe']['source'],
            is_live=False,
            description=COMPONENTS['nifty_pe']['description'],
        )
    with c5:
        component_card(
            name="Put-Call Ratio",
            raw_value=f"{pcr_value:.2f}",
            score=pcr_score,
            source=COMPONENTS['pcr']['source'],
            is_live=False,
            description=COMPONENTS['pcr']['description'],
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── SECTION 4: Historical Chart
    st.markdown("""
    <div style="font-family:'DM Mono',monospace;font-size:0.62rem;color:#555;
                letter-spacing:0.12em;text-transform:uppercase;margin-bottom:0.5rem">
        Historical Context
    </div>
    """, unsafe_allow_html=True)

    nifty_df_raw = live_data.get("nifty_df")
    vix_df_raw   = live_data.get("vix_df")

    if nifty_df_raw is not None:
        fig_hist = make_nifty_sentiment_chart(nifty_df_raw, vix_df_raw)
        st.plotly_chart(fig_hist, use_container_width=True)
    else:
        st.markdown("""
        <div style="background:#111118;border:1px solid rgba(255,255,255,0.06);
                    border-radius:4px;padding:1.5rem;text-align:center;
                    font-family:'DM Mono',monospace;font-size:0.72rem;color:#444">
            Historical chart unavailable · Yahoo Finance data not loaded
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── SECTION 5: Methodology
    with st.expander("📋 Methodology & Sources", expanded=False):
        methodology = {
            "India VIX (25%)": {
                "source": "NSE India via Yahoo Finance ticker ^INDIAVIX",
                "update": "Live — refreshes every 5 minutes during market hours",
                "scoring": "VIX 8 = score 100 (extreme greed) · VIX 30 = score 0 (extreme fear)",
                "note": "India VIX measures expected Nifty volatility over next 30 days. High VIX = fear. Low VIX = calm/greed.",
            },
            "Nifty Momentum (20%)": {
                "source": "NSE Nifty 50 via Yahoo Finance ticker ^NSEI",
                "update": "Live — refreshes every 5 minutes",
                "scoring": ">5% above 125-day MA = 100 · 5% below = 0",
                "note": "125-day MA chosen as medium-term trend signal. Above = bullish momentum. Below = bearish.",
            },
            "52-Week High-Low (20%)": {
                "source": "NSE Nifty 50 via Yahoo Finance ticker ^NSEI (252 days)",
                "update": "Live — refreshes every 5 minutes",
                "scoring": "At 52w high = 100 · At 52w low = 0",
                "note": "Position within annual range shows where we are in the cycle.",
            },
            "Nifty PE Ratio (20%)": {
                "source": "NSE India daily publication · nifty-pe-ratio.com",
                "update": "Manual — updated daily by user. Current value: 20.75 (26 Jun 2026)",
                "scoring": "PE 15 = score 100 (cheap/greed) · PE 28 = score 0 (expensive/fear)",
                "note": "Based on consolidated earnings (post-April 2021 methodology). Historical consolidated avg: ~20-21.",
            },
            "Put-Call Ratio (15%)": {
                "source": "NSE India F&O data · ChainDesk (Day 24 of this challenge)",
                "update": "Manual — updated by user from NSE or ChainDesk",
                "scoring": "PCR 0.5 = score 100 (greed) · PCR 1.5 = score 0 (fear)",
                "note": "PCR > 1.2 = bearish positioning. PCR < 0.8 = bullish. Neutral: 0.9-1.1.",
            },
        }

        for component, info in methodology.items():
            st.markdown(f"""
            <div style="margin-bottom:1rem;padding-bottom:1rem;
                        border-bottom:1px solid rgba(255,255,255,0.04)">
                <div style="font-family:'DM Mono',monospace;font-size:0.7rem;
                            color:#c9a96e;margin-bottom:6px">{component}</div>
                <div style="font-family:'DM Mono',monospace;font-size:0.65rem;
                            color:#555;line-height:1.9">
                    <span style="color:#444">Source:</span> {info['source']}<br>
                    <span style="color:#444">Update:</span> {info['update']}<br>
                    <span style="color:#444">Scoring:</span> {info['scoring']}<br>
                    <span style="color:#444">Note:</span> {info['note']}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Footer
    st.markdown("""
    <div style="margin-top:3rem;padding-top:1rem;border-top:1px solid rgba(255,255,255,0.04);
                font-family:'DM Mono',monospace;font-size:0.6rem;color:#333;line-height:1.8;
                text-align:center">
        SentiDesk · Day 28 · 30 Days of AI Finance<br>
        India VIX and Nifty data via Yahoo Finance (^INDIAVIX, ^NSEI) ·
        Nifty PE sourced from NSE India (nifty-pe-ratio.com) ·
        PCR from NSE F&O data<br>
        Composite score is educational — not a trading signal · Not investment advice
    </div>
    """, unsafe_allow_html=True)
