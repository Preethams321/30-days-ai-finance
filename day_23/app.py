import streamlit as st
import numpy as np
from scipy.stats import norm
from scipy.optimize import brentq
import plotly.graph_objects as go

st.set_page_config(page_title="Black Scholes Desk", layout="wide", initial_sidebar_state="collapsed")

# Force dark theme regardless of system/browser setting
st._config.set_option('theme.base', 'dark')
st._config.set_option('theme.backgroundColor', '#09090e')
st._config.set_option('theme.secondaryBackgroundColor', '#0d0d14')
st._config.set_option('theme.textColor', '#e8e4dc')
st._config.set_option('theme.primaryColor', '#c9a96e')

# ============================================================ MATH ENGINE
def black_scholes(S, K, T, r, sigma, option_type):
    if T <= 0:
        return max(0.0, S - K) if option_type == 'call' else max(0.0, K - S)
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    if option_type == 'call':
        return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    return K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)


def all_greeks(S, K, T, r, sigma, option_type):
    if T <= 0:
        return {'price': black_scholes(S, K, T, r, sigma, option_type),
                'delta': 1.0 if (option_type == 'call' and S > K) else (-1.0 if option_type == 'put' and S < K else 0.0),
                'gamma': 0.0, 'theta': 0.0, 'vega': 0.0, 'rho': 0.0, 'd1': None, 'd2': None}
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    pdf_d1 = norm.pdf(d1)
    price = black_scholes(S, K, T, r, sigma, option_type)
    delta = norm.cdf(d1) if option_type == 'call' else norm.cdf(d1) - 1
    gamma = pdf_d1 / (S * sigma * np.sqrt(T))
    vega = S * pdf_d1 * np.sqrt(T) / 100
    rho = (K * T * np.exp(-r * T) * norm.cdf(d2) / 100 if option_type == 'call'
           else -K * T * np.exp(-r * T) * norm.cdf(-d2) / 100)
    if option_type == 'call':
        theta = (-S * pdf_d1 * sigma / (2 * np.sqrt(T)) - r * K * np.exp(-r * T) * norm.cdf(d2)) / 365
    else:
        theta = (-S * pdf_d1 * sigma / (2 * np.sqrt(T)) + r * K * np.exp(-r * T) * norm.cdf(-d2)) / 365
    return {'price': price, 'delta': delta, 'gamma': gamma, 'theta': theta,
            'vega': vega, 'rho': rho, 'd1': d1, 'd2': d2}


def implied_volatility(market_price, S, K, T, r, option_type):
    if T <= 0:
        return None
    intrinsic = max(0, S - K) if option_type == 'call' else max(0, K - S)
    if market_price <= intrinsic:
        return None
    def objective(sigma):
        return black_scholes(S, K, T, r, sigma, option_type) - market_price
    try:
        if objective(0.001) * objective(10.0) > 0:
            return None
        iv = brentq(objective, 0.001, 10.0, xtol=1e-6, maxiter=200)
        return round(iv * 100, 4)
    except Exception:
        return None


@st.cache_data
def generate_surface(K, r, sigma, option_type, metric):
    spots = np.linspace(K * 0.80, K * 1.20, 41)
    dtes = np.arange(1, 61)
    Z = np.zeros((len(dtes), len(spots)))
    for j, dte in enumerate(dtes):
        T = dte / 365.0
        for i, S in enumerate(spots):
            try:
                g = all_greeks(float(S), float(K), float(T), float(r), float(sigma), option_type)
                val = {'price': g['price'], 'delta': g['delta'],
                       'gamma': g['gamma'] * 1000, 'theta': g['theta'], 'vega': g['vega']}.get(metric, 0)
                Z[j, i] = val if np.isfinite(val) else 0
            except Exception:
                Z[j, i] = 0
    return spots.round(0).astype(int).tolist(), dtes.tolist(), Z.tolist()


# ============================================================ CONFIG
UNDERLYINGS = {
    "NIFTY":     {"spot": 23500, "lot_size": 65,  "typical_iv": 15.0, "strike_gap": 50},
    "BANKNIFTY": {"spot": 54000, "lot_size": 30,  "typical_iv": 18.0, "strike_gap": 100},
    "SENSEX":    {"spot": 77500, "lot_size": 20,  "typical_iv": 15.0, "strike_gap": 100},
    "FINNIFTY":  {"spot": 25000, "lot_size": 60,  "typical_iv": 16.0, "strike_gap": 50},
}

COLORSCALES = {
    'price': [[0,'#0e0e1e'],[0.25,'#1a3a7a'],[0.5,'#3a5a7a'],[0.75,'#c9a96e'],[1,'#e8ca90']],
    'delta': [[0,'#e05c6c'],[0.5,'#111118'],[1,'#4ab87a']],
    'gamma': [[0,'#0e0e1e'],[0.5,'#4a9eff'],[1,'#c9a96e']],
    'theta': [[0,'#e05c6c'],[0.5,'#e0a04a'],[1,'#111118']],
    'vega':  [[0,'#0e0e1e'],[0.5,'#3a5a7a'],[1,'#4ab87a']],
}

SURFACE_CONFIGS = {
    'price': {
        'title': 'Option Price Surface — How Premium Evolves Across Spot and Time',
        'zlabel': 'Price (₹)',
        'plain_english': "The price surface shows everything at once. ATM options (center ridge) lose value fastest as time passes — watch the surface slope toward expiry. Deep ITM options hold intrinsic value. Deep OTM options collapse toward zero.",
        'ghost': "Think of this as a landscape of value. The mountain ridge running through the middle is ATM — where time value is highest. The flanks are OTM options slowly losing value. The cliffs on the right side show how the surface drops as expiry approaches."
    },
    'delta': {
        'title': 'Delta Surface — Directional Sensitivity Across Spot and Time',
        'zlabel': 'Delta',
        'plain_english': "Delta transitions from 0 (deep OTM) to 1 (deep ITM) for calls. Near expiry, this transition becomes a sharp cliff — an ATM option's delta snaps to either 0 or 1 with very little in between.",
        'ghost': "Delta is how much your option moves with Nifty. Notice the smooth S-curve far from expiry — gradual transition. Near expiry, that S-curve becomes a step function. That sharpness is gamma risk materializing."
    },
    'gamma': {
        'title': 'Gamma Surface — Rate of Delta Change (The Gamma Knife)',
        'zlabel': 'Gamma ×1000',
        'plain_english': "Gamma spikes massively for ATM options near expiry. This is the 'gamma knife' — why option sellers get destroyed by sudden moves on weekly expiry day. That sharp peak in the surface is why risk desks hedge gamma aggressively.",
        'ghost': "Gamma is the risk of the risk. High gamma means your delta is changing fast — your position is extremely sensitive to small moves. The spike near ATM at expiry is why Nifty can move 200 points on expiry day and destroy short option positions."
    },
    'theta': {
        'title': "Theta Surface — Daily Time Decay (The Option Seller's Edge)",
        'zlabel': 'Theta (₹/day)',
        'plain_english': "Theta accelerates exponentially near expiry for ATM options. Option sellers harvest this decay. Option buyers fight it every single day.",
        'ghost': "Theta is the rent you pay for holding an option. The surface shows it's not linear — the last week before expiry bleeds value fastest. This is why weekly option sellers love Thursday-to-Tuesday Nifty positions."
    },
    'vega': {
        'title': 'Vega Surface — IV Sensitivity Across Spot and Time',
        'zlabel': 'Vega (₹ per 1% IV)',
        'plain_english': "Vega is highest for ATM, long-dated options. Near expiry, Vega collapses — IV changes barely affect short-dated option prices. This is why pre-event IV spikes help long-dated options far more than weekly options.",
        'ghost': "When India VIX spikes before Budget or RBI policy, which options benefit most? Long-dated ATM options — peak Vega. Weekly ATM options have very low Vega near expiry. The surface makes this visual."
    },
}


def make_surface_fig(x, y, z, title, colorscale, zlabel, height=560):
    # Format x-axis tick labels: show as k if >= 1000
    x_arr = np.array(x)
    if x_arr.max() >= 10000:
        tickvals = x_arr[::5].tolist()
        ticktext = [f"{int(v/1000)}k" if v >= 1000 else str(int(v)) for v in tickvals]
    else:
        tickvals = x_arr[::5].tolist()
        ticktext = [str(int(v)) for v in tickvals]

    axis_common = dict(
        tickfont=dict(color='#b0a898', family='DM Mono', size=10),
        gridcolor='rgba(255,255,255,0.08)',
        backgroundcolor='rgba(9,9,14,0.6)',
        showbackground=True,
        linecolor='rgba(255,255,255,0.15)',
        linewidth=1,
        showline=True,
        zeroline=False,
    )

    fig = go.Figure(data=[go.Surface(
        x=x, y=y, z=z,
        colorscale=colorscale,
        showscale=True,
        colorbar=dict(
            title=dict(text=zlabel, font=dict(color='#c9a96e', family='DM Mono', size=11)),
            tickfont=dict(color='#b0a898', family='DM Mono', size=9),
            thickness=10, len=0.65, x=0.95,
            bgcolor='rgba(9,9,14,0.0)',
            bordercolor='rgba(255,255,255,0.1)',
        ),
        hovertemplate='<b>Spot:</b> %{x}<br><b>DTE:</b> %{y}d<br><b>' + zlabel + ':</b> %{z:.4f}<extra></extra>',
        contours=dict(z=dict(show=True, usecolormap=True, highlightcolor='#c9a96e', project_z=True)),
        lighting=dict(ambient=0.85, diffuse=0.8, fresnel=0.15, roughness=0.5, specular=0.1),
        opacity=0.97,
    )])

    fig.update_layout(
        title=dict(
            text=title,
            font=dict(family='Playfair Display, serif', size=14, color='#c9a96e'),
            x=0.02, y=0.97),
        paper_bgcolor='rgba(9,9,14,1)',
        plot_bgcolor='rgba(9,9,14,1)',
        margin=dict(l=10, r=10, t=55, b=10),
        height=height,
        scene=dict(
            bgcolor='rgba(9,9,14,1)',
            xaxis=dict(
                **axis_common,
                title=dict(text='Spot Price', font=dict(color='#c9a96e', family='DM Mono', size=11)),
                tickvals=tickvals,
                ticktext=ticktext,
            ),
            yaxis=dict(
                **axis_common,
                title=dict(text='Days to Expiry', font=dict(color='#c9a96e', family='DM Mono', size=11)),
            ),
            zaxis=dict(
                **axis_common,
                title=dict(text=zlabel, font=dict(color='#c9a96e', family='DM Mono', size=11)),
            ),
            camera=dict(eye=dict(x=1.6, y=-1.6, z=1.1)),
            aspectmode='manual',
            aspectratio=dict(x=1.2, y=1.2, z=0.8),
        ),
        font=dict(family='DM Mono', color='#b0a898'),
    )
    return fig


# ============================================================ CSS
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,700&family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&display=swap');

/* ============ FORCE DARK ON EVERYTHING — ALL MODES ============ */
:root {
    color-scheme: dark !important;
}
*, *::before, *::after {
    box-sizing: border-box;
}

/* Kill any light-mode overrides from the browser or Streamlit */
@media (prefers-color-scheme: light) {
    html, body { background-color: #09090e !important; color: #e8e4dc !important; }
}

html, body {
    background-color: #09090e !important;
    color: #e8e4dc !important;
    font-family: 'Syne', sans-serif !important;
}

/* All Streamlit containers */
[class*="css"],
[class*="st-"],
[data-testid="stApp"],
[data-testid="stAppViewContainer"],
[data-testid="stVerticalBlock"],
[data-testid="stTabsContent"],
[data-testid="stMainBlockContainer"],
[data-testid="stMain"],
.stApp, .main, section[data-testid="stSidebar"],
.stMarkdown, div[data-testid] {
    background-color: #09090e !important;
    color: #e8e4dc !important;
    font-family: 'Syne', sans-serif !important;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header,
[data-testid="stDecoration"],
[data-testid="stToolbar"],
[data-testid="stStatusWidget"] {
    display: none !important;
    visibility: hidden !important;
}

.block-container {
    padding: 1.8rem 2.5rem !important;
    max-width: 100% !important;
    background-color: #09090e !important;
}

/* ============ st.code — CRITICAL: Streamlit overrides this in light mode ============ */
[data-testid="stCode"],
[data-testid="stCode"] > div,
[data-testid="stCode"] pre,
[data-testid="stCode"] code,
.stCode, .stCode pre, .stCode code,
pre, code {
    background-color: #0d0d14 !important;
    color: #c9a96e !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 4px !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.82rem !important;
}

/* ============ st.latex ============ */
[data-testid="stHtml"],
.stLatex, .katex-display, .katex {
    background-color: transparent !important;
    color: #e8e4dc !important;
}
.katex { color: #e8e4dc !important; }
.katex .mord, .katex .mbin, .katex .mrel,
.katex .mopen, .katex .mclose, .katex .minner {
    color: #e8e4dc !important;
}

/* ============ st.caption ============ */
[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] p,
.stCaption, .stCaption p {
    color: #555 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.68rem !important;
    background: transparent !important;
}

/* ============ st.info / st.warning ============ */
[data-testid="stAlert"],
[data-testid="stAlertContainer"],
div[role="alert"] {
    background-color: #0d0d14 !important;
    border: 1px solid rgba(74,158,255,0.2) !important;
    color: #b0a898 !important;
    border-radius: 4px !important;
}

/* ============ st.markdown prose text ============ */
.stMarkdown p, .stMarkdown li, .stMarkdown span {
    color: #e8e4dc !important;
    background: transparent !important;
}

/* ============ TABS ============ */
[data-testid="stTabs"] [role="tablist"] {
    background: transparent !important;
    border-bottom: 1px solid rgba(255,255,255,0.07) !important;
    gap: 0.25rem !important;
    padding: 0 !important;
}
[data-testid="stTabs"] button[role="tab"] {
    background: transparent !important;
    color: #444 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.72rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    padding: 0.6rem 1.1rem !important;
    border-radius: 0 !important;
    transition: color 0.2s !important;
}
[data-testid="stTabs"] button[role="tab"]:hover { color: #999 !important; }
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    color: #c9a96e !important;
    border-bottom: 2px solid #c9a96e !important;
    background: transparent !important;
}

/* ============ METRICS ============ */
[data-testid="stMetric"] {
    background: #0d0d14 !important;
    border: 1px solid rgba(255,255,255,0.05) !important;
    border-radius: 6px !important;
    padding: 1rem 1.1rem !important;
}
[data-testid="stMetricValue"],
[data-testid="stMetricValue"] > div {
    font-family: 'DM Mono', monospace !important;
    color: #e8e4dc !important;
    font-size: 1.35rem !important;
    font-weight: 400 !important;
    background: transparent !important;
}
[data-testid="stMetricLabel"],
[data-testid="stMetricLabel"] > div {
    font-family: 'DM Mono', monospace !important;
    color: #555 !important;
    font-size: 0.62rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    background: transparent !important;
}
[data-testid="stMetricDelta"] { display: none !important; }

/* ============ RADIO ============ */
[data-testid="stRadio"] > label {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.68rem !important;
    color: #666 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    margin-bottom: 0.4rem !important;
    display: block !important;
    background: transparent !important;
}
[data-testid="stRadio"] [role="radiogroup"] { gap: 0.4rem !important; }
[data-testid="stRadio"] label[data-baseweb="radio"] {
    background: #0d0d14 !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 4px !important;
    padding: 0.35rem 0.85rem !important;
    cursor: pointer !important;
    transition: all 0.15s !important;
}
[data-testid="stRadio"] label[data-baseweb="radio"]:hover {
    border-color: rgba(201,169,110,0.35) !important;
}
[data-testid="stRadio"] label[data-baseweb="radio"] > div:last-child {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.75rem !important;
    color: #888 !important;
}
[data-testid="stRadio"] label[data-baseweb="radio"]:has([aria-checked="true"]) {
    border-color: rgba(201,169,110,0.5) !important;
    background: rgba(201,169,110,0.07) !important;
}
[data-testid="stRadio"] label[data-baseweb="radio"]:has([aria-checked="true"]) > div:last-child {
    color: #c9a96e !important;
}
[data-testid="stRadio"] [data-baseweb="radio"] > div:first-child { display: none !important; }

/* ============ NUMBER INPUTS ============ */
[data-testid="stNumberInput"] input {
    background: #0d0d14 !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 4px !important;
    color: #e8e4dc !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.9rem !important;
}
[data-testid="stNumberInput"] input:focus {
    border-color: rgba(201,169,110,0.4) !important;
    box-shadow: 0 0 0 1px rgba(201,169,110,0.15) !important;
    outline: none !important;
}
[data-testid="stNumberInput"] button {
    background: #0d0d14 !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    color: #666 !important;
}
[data-testid="stNumberInput"] button:hover { color: #c9a96e !important; }

/* ============ SLIDERS ============ */
[data-testid="stSlider"] > label {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.68rem !important;
    color: #555 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    background: transparent !important;
}
[data-testid="stSlider"] [role="slider"] {
    background: #c9a96e !important;
    border: 2px solid #09090e !important;
    box-shadow: 0 0 6px rgba(201,169,110,0.4) !important;
}
[data-testid="stSlider"] [data-baseweb="slider"] div[class] {
    background-color: rgba(201,169,110,0.15) !important;
}
[data-testid="stTickBarMin"],
[data-testid="stTickBarMax"] { visibility: hidden !important; }
[data-testid="stSlider"] p {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.75rem !important;
    color: #c9a96e !important;
    background: transparent !important;
}

/* ============ BUTTONS ============ */
.stButton > button {
    background: transparent !important;
    color: #c9a96e !important;
    border: 1px solid rgba(201,169,110,0.25) !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.07em !important;
    border-radius: 4px !important;
    padding: 0.5rem 1.2rem !important;
    transition: all 0.15s !important;
}
.stButton > button:hover {
    background: rgba(201,169,110,0.07) !important;
    border-color: rgba(201,169,110,0.5) !important;
}
.stButton > button:focus {
    outline: 1px solid rgba(201,169,110,0.3) !important;
    box-shadow: none !important;
}

/* ============ SELECT / DROPDOWN ============ */
[data-baseweb="select"] [data-baseweb="input"],
[data-baseweb="select"] input,
[data-baseweb="popover"] li {
    background: #0d0d14 !important;
    color: #e8e4dc !important;
    border-color: rgba(255,255,255,0.07) !important;
    font-family: 'DM Mono', monospace !important;
}

/* ============ SCROLLBAR ============ */
::-webkit-scrollbar { width: 3px; height: 3px; }
::-webkit-scrollbar-track { background: #09090e; }
::-webkit-scrollbar-thumb { background: rgba(201,169,110,0.2); border-radius: 2px; }

/* ============ CUSTOM CLASSES ============ */
.page-title {
    font-family: 'Playfair Display', serif;
    font-size: 4.5rem;
    font-weight: 700;
    color: #e8e4dc;
    line-height: 1;
    margin: 0;
    letter-spacing: -0.01em;
}
.page-tag {
    font-family: 'Playfair Display', serif;
    font-style: italic;
    font-size: 1.35rem;
    color: #c9a96e;
    margin: 0.6rem 0 1.6rem;
}
.eyebrow {
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.14em;
    color: #555;
    text-transform: uppercase;
    margin-bottom: 1.4rem;
}
.live-dot {
    height: 6px; width: 6px;
    background: #4ab87a;
    border-radius: 50%;
    display: inline-block;
    margin-right: 8px;
    animation: pulse 1.8s infinite;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.25} }
.hero-sub {
    color: #999;
    font-size: 0.92rem;
    max-width: 680px;
    line-height: 1.65;
    margin: 0.8rem 0 2rem;
}
.card {
    background: #0d0d14;
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 6px;
    padding: 1.2rem 1.4rem;
}
.card-title {
    font-family: 'DM Mono', monospace;
    color: #c9a96e;
    font-size: 0.65rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 0.55rem;
}
.card-body { color: #b8b4ac; font-size: 0.88rem; line-height: 1.6; }
.pill {
    display: inline-block;
    background: rgba(201,169,110,0.06);
    border: 1px solid rgba(201,169,110,0.18);
    color: #c9a96e;
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    padding: 0.3rem 0.75rem;
    border-radius: 20px;
    margin: 0.18rem;
    letter-spacing: 0.04em;
}
.stat-card {
    background: #0d0d14;
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 6px;
    padding: 1.1rem 1.3rem;
}
.stat-num { font-family: 'DM Mono', monospace; font-size: 1.9rem; color: #c9a96e; line-height: 1; }
.stat-lbl { font-family: 'DM Mono', monospace; font-size: 0.62rem; color: #555; text-transform: uppercase; letter-spacing: 0.08em; margin-top: 0.3rem; }
.conn-strip { font-family: 'DM Mono', monospace; font-size: 0.7rem; color: #444; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 1.2rem; margin-top: 2.5rem; letter-spacing: 0.04em; }
.ghost-card { background: rgba(74,158,255,0.04); border: 1px solid rgba(74,158,255,0.15); border-radius: 6px; padding: 1.2rem 1.4rem; margin-top: 0.6rem; }
.terminal-title { font-family: 'Playfair Display', serif; font-size: 1.6rem; font-weight: 700; color: #e8e4dc; margin: 0; letter-spacing: -0.01em; }
.terminal-sub { font-family: 'DM Mono', monospace; font-size: 0.65rem; color: #444; letter-spacing: 0.08em; text-transform: uppercase; margin-top: 0.15rem; }
.section-label { font-family: 'DM Mono', monospace; font-size: 0.62rem; color: #444; text-transform: uppercase; letter-spacing: 0.12em; margin-bottom: 0.5rem; margin-top: 1.2rem; }
.total-row { font-family: 'DM Mono', monospace; font-size: 0.82rem; color: #888; background: #0d0d14; border: 1px solid rgba(255,255,255,0.05); border-radius: 6px; padding: 0.75rem 1.1rem; margin-top: 0.7rem; }
.iv-box { background: #0d0d14; border: 1px solid rgba(201,169,110,0.2); border-radius: 6px; padding: 1.6rem; }
.iv-big { font-family: 'DM Mono', monospace; font-size: 2.8rem; color: #c9a96e; line-height: 1; margin: 0.4rem 0 1rem; }
.iv-row { font-family: 'DM Mono', monospace; font-size: 0.82rem; color: #bbb; display: flex; justify-content: space-between; padding: 0.4rem 0; border-bottom: 1px solid rgba(255,255,255,0.04); }
.foot { font-family: 'DM Mono', monospace; font-size: 0.62rem; color: #3a3a3a; line-height: 1.6; border-top: 1px solid rgba(255,255,255,0.04); padding-top: 1.2rem; margin-top: 3rem; letter-spacing: 0.03em; }
</style>
"""


st.markdown(CSS, unsafe_allow_html=True)

# ============================================================ SESSION STATE
for k, v in [('page','home'),('surface_key',None),('surface_data',{}),('iv_result',None),('cur',None)]:
    if k not in st.session_state:
        st.session_state[k] = v


# ============================================================ HOMEPAGE
def homepage():
    st.markdown('<div class="eyebrow"><span class="live-dot"></span>Black-Scholes Engine &nbsp;·&nbsp; 3D Greek Surfaces &nbsp;·&nbsp; IV Solver &nbsp;·&nbsp; P&L Simulator</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-title">Black Scholes Desk</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-tag">The math behind every options trade.</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Black-Scholes isn\'t just a formula — it\'s a 5-dimensional surface. Visualize how option price, Delta, Gamma, Theta, and Vega evolve across spot price and time simultaneously. The math engine powering StratEdge (Day 22), fully exposed.</div>', unsafe_allow_html=True)

    cols = st.columns(4)
    stats = [("5","Greeks computed"),("5 × 3D","surfaces"),("scipy","IV solver"),("∞","P&L scenarios")]
    for c, (n, l) in zip(cols, stats):
        c.markdown(f'<div class="stat-card"><div class="stat-num">{n}</div><div class="stat-lbl">{l}</div></div>', unsafe_allow_html=True)

    st.markdown('<div style="height:1.5rem"></div>', unsafe_allow_html=True)
    pills = ["Price Surface","Delta","Gamma","Theta","Vega","IV Solver","P&L Sim"]
    st.markdown("".join(f'<span class="pill">{p}</span>' for p in pills), unsafe_allow_html=True)
    st.markdown('<div style="height:1.5rem"></div>', unsafe_allow_html=True)

    features = [
        ("Price Surface",    "Watch premium decay across spot and time in 3D."),
        ("Delta Surface",    "Directional sensitivity from OTM to ITM, smoothed by time."),
        ("Gamma Surface",    "The gamma knife — why expiry-day moves destroy sellers."),
        ("Theta Surface",    "The seller's edge: exponential decay near expiry."),
        ("IV Solver",        "Back-solve implied volatility via scipy brentq."),
        ("P&L Simulator",   "Model spot moves, time passage, and IV shifts together."),
    ]
    fc = st.columns(3)
    for i, (t, d) in enumerate(features):
        fc[i % 3].markdown(f'<div class="card" style="margin-bottom:0.75rem;"><div class="card-title">{t}</div><div class="card-body">{d}</div></div>', unsafe_allow_html=True)

    st.markdown('<div style="height:1rem"></div>', unsafe_allow_html=True)
    if st.button("→  Launch Black Scholes Desk", use_container_width=False):
        st.session_state.page = 'terminal'
        st.rerun()

    st.markdown('<div class="conn-strip">Week 4 Derivatives Suite — StratEdge (Day 22) → Black Scholes Desk (Day 23) → PathLab Monte Carlo (Day 24)</div>', unsafe_allow_html=True)


# ============================================================ TERMINAL
def terminal():
    # ---- Clean header row ----
    hcol1, hcol2 = st.columns([5, 1])
    with hcol1:
        st.markdown('<div class="terminal-title">Black Scholes Desk</div>', unsafe_allow_html=True)
        st.markdown('<div class="terminal-sub">Black-Scholes Engine · 3D Greek Surfaces · IV Solver · P&L Simulator</div>', unsafe_allow_html=True)
    with hcol2:
        st.markdown('<div style="padding-top:0.4rem"></div>', unsafe_allow_html=True)
        if st.button("← Home", use_container_width=True):
            st.session_state.page = 'home'
            st.rerun()

    st.markdown('<div style="height:0.6rem"></div>', unsafe_allow_html=True)

    t1, t2, t3, t4, t5 = st.tabs(["Pricer", "3D Surfaces", "IV Solver", "P&L Sim", "BS Explained"])

    # ================================================================ TAB 1 — PRICER
    with t1:
        left, right = st.columns([1, 1], gap="large")

        with left:
            st.markdown('<div class="section-label">Instrument</div>', unsafe_allow_html=True)
            underlying = st.radio("Underlying", list(UNDERLYINGS.keys()), horizontal=True, label_visibility="collapsed")
            u = UNDERLYINGS[underlying]

            st.markdown('<div class="section-label">Option Type</div>', unsafe_allow_html=True)
            option_type = st.radio("Option Type", ["call","put"], horizontal=True,
                                   format_func=str.upper, label_visibility="collapsed")

            st.markdown('<div class="section-label" style="margin-top:1rem;">Spot Price</div>', unsafe_allow_html=True)
            S = st.number_input("Spot Price", value=float(u["spot"]),
                                step=float(u["strike_gap"]), min_value=1.0, label_visibility="collapsed",
                                key=f"spot_{underlying}")

            st.markdown('<div class="section-label">Strike Price</div>', unsafe_allow_html=True)
            atm = round(S / u["strike_gap"]) * u["strike_gap"]
            K = st.number_input("Strike Price", value=float(atm),
                                step=float(u["strike_gap"]), min_value=1.0, label_visibility="collapsed",
                                key=f"strike_{underlying}")

            st.markdown('<div class="section-label">Days to Expiry</div>', unsafe_allow_html=True)
            dte = st.slider("DTE", 1, 90, 21, label_visibility="collapsed")

        with right:
            st.markdown('<div class="section-label">Implied Volatility (%)</div>', unsafe_allow_html=True)
            iv = st.slider("IV", 5.0, 80.0, float(u["typical_iv"]), step=0.5, label_visibility="collapsed",
                           key=f"iv_{underlying}")

            st.markdown('<div class="section-label">Risk-Free Rate (%)</div>', unsafe_allow_html=True)
            rate = st.slider("Rate", 4.0, 10.0, 6.5, step=0.1, label_visibility="collapsed")

            st.markdown('<div class="section-label" style="margin-top:1rem;">Lot Size</div>', unsafe_allow_html=True)
            lot_size = st.number_input("Lot Size", value=int(u["lot_size"]),
                                       step=1, min_value=1, label_visibility="collapsed",
                                       key=f"lot_size_{underlying}")

            st.markdown('<div class="section-label">Number of Lots</div>', unsafe_allow_html=True)
            lots = st.number_input("Lots", value=1, min_value=1,
                                   step=1, label_visibility="collapsed")

        # ---- Compute ----
        T = dte / 365.0
        g = all_greeks(S, K, T, rate / 100, iv / 100, option_type)
        units = lot_size * lots

        st.markdown('<div style="height:0.5rem"></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-label">Greeks</div>', unsafe_allow_html=True)
        mc = st.columns(6)
        mc[0].metric("Price",  f"₹{g['price']:.2f}")
        mc[1].metric("Delta",  f"{g['delta']:.4f}")
        mc[2].metric("Gamma",  f"{g['gamma']:.5f}")
        mc[3].metric("Theta",  f"₹{g['theta']:.2f}")
        mc[4].metric("Vega",   f"₹{g['vega']:.2f}")
        mc[5].metric("Rho",    f"₹{g['rho']:.2f}")

        st.markdown(
            f'<div class="total-row">Total position: '
            f'<b style="color:#c9a96e;">₹{g["price"]:.2f}</b> per unit '
            f'× {lot_size} lot size × {lots} lots = '
            f'<b style="color:#4ab87a;">₹{g["price"]*units:,.0f}</b> total premium'
            f'</div>', unsafe_allow_html=True)

        # ---- Interpretation cards ----
        st.markdown('<div style="height:0.5rem"></div>', unsafe_allow_html=True)
        moneyness = (S - K) / K * 100 if option_type == 'call' else (K - S) / K * 100
        if abs(S - K) / K < 0.005:   status = "ATM"
        elif moneyness > 0:           status = "ITM"
        else:                         status = "OTM"
        be = K + g['price'] if option_type == 'call' else K - g['price']

        pc = st.columns(2, gap="medium")
        pc[0].markdown(
            f'<div class="card"><div class="card-title">Position Summary</div>'
            f'<div class="card-body">'
            f'This <b style="color:#e8e4dc;">{option_type.upper()}</b> on <b style="color:#e8e4dc;">{underlying}</b> '
            f'with {dte} days to expiry is <b style="color:#c9a96e;">{status}</b>.<br><br>'
            f'{"In" if status=="ITM" else "Out of" if status=="OTM" else "At"} the money '
            f'by <b>{abs(moneyness):.2f}%</b> from spot.<br>'
            f'Breakeven at expiry: <b style="color:#e8e4dc;">₹{be:,.0f}</b>'
            f'</div></div>', unsafe_allow_html=True)
        pc[1].markdown(
            f'<div class="card"><div class="card-title">Greeks in Plain English</div>'
            f'<div class="card-body">'
            f'<b style="color:#c9a96e;">Delta</b>&nbsp; '
            f'{"Gains" if g["delta"]>=0 else "Loses"} ₹{abs(g["delta"]*units):,.0f} per 1-pt {underlying} move.<br><br>'
            f'<b style="color:#c9a96e;">Theta</b>&nbsp; '
            f'Loses ₹{abs(g["theta"]*units):,.0f} per day from time decay.<br><br>'
            f'<b style="color:#c9a96e;">Vega</b>&nbsp; '
            f'Gains/loses ₹{abs(g["vega"]*units):,.0f} per 1% IV move.'
            f'</div></div>', unsafe_allow_html=True)

        # ---- d1/d2 always-visible card ----
        if g['d1'] is not None:
            d1v = round(g['d1'], 4)
            d2v = round(g['d2'], 4)
            nd1 = round(float(norm.cdf(g['d1'])), 4)
            nd2 = round(float(norm.cdf(g['d2'])), 4)
            st.markdown(
                '<div class="card" style="margin-top:0.8rem;">'
                '<div class="card-title">d₁ · d₂ · N(d₁) · N(d₂)</div>'
                '<div style="display:grid;grid-template-columns:1fr 1fr;gap:0.8rem;margin-top:0.3rem;">'
                '<div style="font-family:DM Mono,monospace;font-size:0.78rem;color:#b0a898;line-height:1.8;">'
                f'd₁ &nbsp;= &nbsp;<span style="color:#c9a96e;font-size:1rem;">{d1v}</span><br>'
                f'd₂ &nbsp;= &nbsp;<span style="color:#c9a96e;font-size:1rem;">{d2v}</span>'
                '</div>'
                '<div style="font-family:DM Mono,monospace;font-size:0.78rem;color:#b0a898;line-height:1.8;">'
                f'N(d₁) = <span style="color:#4ab87a;font-size:1rem;">{nd1}</span><br>'
                f'N(d₂) = <span style="color:#4ab87a;font-size:1rem;">{nd2}</span>'
                '</div>'
                '</div>'
                '<div style="margin-top:0.6rem;font-family:DM Mono,monospace;font-size:0.65rem;color:#555;">'
                'N(d₁) ≈ delta · N(d₂) = risk-adjusted probability of expiring in the money'
                '</div></div>',
                unsafe_allow_html=True
            )
        # Save state for other tabs
        st.session_state.cur = dict(
            underlying=underlying, S=S, K=K, dte=dte, T=T,
            iv=iv, rate=rate, option_type=option_type,
            lot_size=lot_size, lots=lots,
            price=g['price'], d1=g['d1'], d2=g['d2'])

    cur = st.session_state.get('cur')

    # ================================================================ TAB 2 — 3D SURFACES
    with t2:
        if not cur:
            st.info("Set parameters in the Pricer tab first.")
        else:
            skey = f"{cur['K']}_{cur['rate']}_{cur['iv']}_{cur['option_type']}"
            if st.session_state.surface_key != skey:
                with st.spinner("Computing surfaces — this takes a few seconds..."):
                    st.session_state.surface_data = {}
                    for m in ['price','delta','gamma','theta','vega']:
                        st.session_state.surface_data[m] = generate_surface(
                            cur['K'], cur['rate']/100, cur['iv']/100, cur['option_type'], m)
                    st.session_state.surface_key = skey

            if st.button("↺  Re-render with current inputs"):
                generate_surface.clear()
                st.session_state.surface_key = None
                st.rerun()

            stabs = st.tabs(["💰 Price","📐 Delta","⚡ Gamma","⏰ Theta","🌊 Vega"])
            for tab, m in zip(stabs, ['price','delta','gamma','theta','vega']):
                with tab:
                    x, y, z = st.session_state.surface_data[m]
                    cfg = SURFACE_CONFIGS[m]
                    fig = make_surface_fig(x, y, z, cfg['title'], COLORSCALES[m], cfg['zlabel'])
                    st.plotly_chart(fig, use_container_width=True)
                    st.caption("Click and drag to rotate · Scroll to zoom · Double-click to reset view")
                    st.markdown(f'<div class="card"><div class="card-title">Plain English</div><div class="card-body">{cfg["plain_english"]}</div></div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="ghost-card"><div class="card-title">The Intuition</div><div class="card-body">{cfg["ghost"]}</div></div>', unsafe_allow_html=True)

    # ================================================================ TAB 3 — IV SOLVER
    with t3:
        if not cur:
            st.info("Set parameters in the Pricer tab first.")
        else:
            ivc = st.columns([1, 1], gap="large")
            with ivc[0]:
                st.markdown('<div class="section-label">Market Premium (₹)</div>', unsafe_allow_html=True)
                mkt = st.number_input("Market Premium", value=float(round(cur['price'], 2)),
                                      step=1.0, min_value=0.01, label_visibility="collapsed")
                st.caption(f"{cur['underlying']}  ·  spot ₹{cur['S']:,.0f}  ·  strike ₹{cur['K']:,.0f}  ·  {cur['dte']}d  ·  {cur['option_type'].upper()}")
                st.markdown('<div style="height:0.5rem"></div>', unsafe_allow_html=True)
                solve = st.button("Solve for IV  →")

            with ivc[1]:
                if solve:
                    siv = implied_volatility(mkt, cur['S'], cur['K'], cur['T'], cur['rate']/100, cur['option_type'])
                    sig = f"{cur['S']}_{cur['K']}_{cur['dte']}_{cur['rate']}_{cur['option_type']}"
                    st.session_state.iv_result = (siv, mkt, sig)

                # Invalidate if Pricer params changed since last solve
                res = st.session_state.iv_result
                cur_sig = f"{cur['S']}_{cur['K']}_{cur['dte']}_{cur['rate']}_{cur['option_type']}"
                if res and res[2] != cur_sig:
                    st.session_state.iv_result = None
                    res = None
                    st.caption("⚠ Inputs changed — click Solve to recompute IV.")

                if res:
                    siv, mkt_p, _ = res
                    if siv is None:
                        st.markdown('<div class="iv-box"><div class="card-title">Result</div><div class="card-body" style="color:#e05c6c;">No solution — price is below intrinsic value or outside the solvable range (0.1% – 1000%).</div></div>', unsafe_allow_html=True)
                    else:
                        diff = siv - cur['iv']
                        if abs(diff) < 1.0:   status_iv = "Fairly Priced"
                        elif diff > 1.0:      status_iv = "RICH"
                        else:                 status_iv = "CHEAP"
                        be_move = siv / 100 * np.sqrt(cur['T']) * 100
                        status_color = '#e0a04a' if status_iv == 'Fairly Priced' else ('#e05c6c' if status_iv == 'RICH' else '#4ab87a')
                        st.markdown(
                            f'<div class="iv-box">'
                            f'<div class="card-title">Implied Volatility</div>'
                            f'<div class="iv-big">{siv:.1f}%</div>'
                            f'<div class="iv-row"><span>Your input IV</span><span>{cur["iv"]:.1f}%</span></div>'
                            f'<div class="iv-row"><span>IV premium</span><span>{diff:+.1f}%</span></div>'
                            f'<div class="iv-row"><span>Status</span><span style="color:{status_color};">{status_iv}</span></div>'
                            f'<div class="iv-row"><span>Breakeven move</span><span>±{be_move:.1f}% at expiry</span></div>'
                            f'</div>', unsafe_allow_html=True)
                        if status_iv == 'RICH':
                            note = "Market pricing more uncertainty than your baseline IV. Option is expensive relative to assumption."
                        elif status_iv == 'CHEAP':
                            note = "Market pricing less uncertainty than your baseline IV. Option is cheap relative to assumption."
                        else:
                            note = "Market price consistent with your assumed IV."
                        st.caption(f"scipy.optimize.brentq · guaranteed convergence · {note}")

    # ================================================================ TAB 4 — P&L SIM
    with t4:
        if not cur:
            st.info("Set parameters in the Pricer tab first.")
        else:
            S, K, dte, T   = cur['S'], cur['K'], cur['dte'], cur['T']
            iv, rate, ot   = cur['iv'], cur['rate'], cur['option_type']
            entry, units   = cur['price'], cur['lot_size'] * cur['lots']

            sc = st.columns(3, gap="medium")
            sc[0].markdown('<div class="section-label">Spot Move %</div>', unsafe_allow_html=True)
            spot_move   = sc[0].slider("Spot Move", -15.0, 15.0, 0.0,
                            step=0.5, label_visibility="collapsed", format="%.1f%%")
            sc[1].markdown('<div class="section-label">Days Passed</div>', unsafe_allow_html=True)
            days_passed = sc[1].slider("Days Passed", 0, dte, 0,
                            label_visibility="collapsed")
            sc[2].markdown('<div class="section-label">IV Change %</div>', unsafe_allow_html=True)
            iv_change   = sc[2].slider("IV Change", -10.0, 10.0, 0.0,
                            step=0.5, label_visibility="collapsed", format="%.1f%%")

            spot_range = np.linspace(S * 0.85, S * 1.15, 200)
            T_rem = max((dte - days_passed) / 365.0, 0)

            def pnl_line(arr, Tr, ivv):
                return [(black_scholes(s, K, Tr, rate/100, ivv/100, ot) - entry) * units for s in arr]

            l1 = pnl_line(spot_range, T,     iv)
            l2 = pnl_line(spot_range, T_rem, iv)
            l3 = pnl_line(spot_range, T_rem, max(0.5, iv + iv_change))

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=spot_range, y=l1,
                name="At Entry", line=dict(color='#c9a96e', width=2)))
            fig.add_trace(go.Scatter(x=spot_range, y=l2,
                name=f"After {days_passed}d", line=dict(color='#4a9eff', width=2, dash='dash')))
            fig.add_trace(go.Scatter(x=spot_range, y=l3,
                name=f"After {days_passed}d + IV {iv_change:+.1f}%",
                line=dict(color='#e0a04a', width=2, dash='dot')))
            fig.add_hline(y=0, line=dict(color='rgba(255,255,255,0.15)', dash='dash', width=1))
            fig.add_vline(x=S, line=dict(color='#c9a96e', dash='dash', width=1))
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                height=460, margin=dict(l=0, r=0, t=20, b=0),
                showlegend=True,
                legend=dict(font=dict(color='#888', family='DM Mono', size=10),
                            bgcolor='rgba(0,0,0,0)', bordercolor='rgba(255,255,255,0.06)', borderwidth=1),
                font=dict(family='DM Mono', color='#888'),
                xaxis=dict(title='Spot Price', gridcolor='rgba(255,255,255,0.04)',
                           zerolinecolor='rgba(255,255,255,0.06)'),
                yaxis=dict(title='P&L (₹)', gridcolor='rgba(255,255,255,0.04)',
                           zerolinecolor='rgba(255,255,255,0.06)'))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

            spot_scn = S * (1 + spot_move / 100)
            iv_scn   = max(0.5, iv + iv_change)  # floor at 0.5% — sigma<=0 breaks BS
            new_price = black_scholes(spot_scn, K, T_rem, rate/100, iv_scn/100, ot)
            pos_pnl  = (new_price - entry) * units
            ret      = (new_price - entry) / entry * 100 if entry > 0 else 0
            color    = '#4ab87a' if pos_pnl >= 0 else '#e05c6c'
            st.markdown(
                f'<div class="total-row">'
                f'If {cur["underlying"]} moves to <b style="color:#e8e4dc;">₹{spot_scn:,.0f}</b> '
                f'in {days_passed} days with IV at {iv_scn:.1f}% —&nbsp; '
                f'P&L: <b style="color:{color};">₹{pos_pnl:,.0f}</b>'
                f'&nbsp;&nbsp;|&nbsp;&nbsp;'
                f'Return on premium: <b style="color:{color};">{ret:+.1f}%</b>'
                f'</div>', unsafe_allow_html=True)

    # ================================================================ TAB 5 — BS EXPLAINED
    with t5:
        st.latex(r'C = S \cdot N(d_1) - K \cdot e^{-rT} \cdot N(d_2)')
        st.latex(r'P = K \cdot e^{-rT} \cdot N(-d_2) - S \cdot N(-d_1)')
        st.latex(r'd_1 = \frac{\ln(S/K)+(r+\sigma^2/2)\cdot T}{\sigma\sqrt{T}}, \quad d_2 = d_1 - \sigma\sqrt{T}')

        st.markdown('<div style="height:0.8rem"></div>', unsafe_allow_html=True)
        if cur:
            _nm  = cur['underlying']
            _s   = f"\u20b9{cur['S']:,.0f}"
            _k   = f"\u20b9{cur['K']:,.0f}"
            _dte = cur['dte']
            _T   = cur['T']
            _r   = cur['rate']
            _iv  = cur['iv']
            _mon = abs(cur['S']-cur['K'])/cur['K']
            _mstr = "ATM" if _mon < 0.005 else ("ITM" if (cur['S']-cur['K'])*(1 if cur['option_type']=='call' else -1)>0 else "OTM")
            ctx_S   = f"{_nm} spot at {_s}"
            ctx_K   = f"Selected strike {_k}  ({_mstr})"
            ctx_T   = f"{_dte} days = {_dte}/365 = {_T:.4f} yrs"
            ctx_r   = f"Rate set to {_r:.1f}%  (= {_r/100:.3f} in formula)"
            ctx_sig = f"IV set to {_iv:.1f}%  (= {_iv/100:.3f} in formula)"
        else:
            ctx_S   = "Index spot price (e.g. Nifty at 23,500)"
            ctx_K   = "Your chosen strike price"
            ctx_T   = "Time to expiry in years (21d = 0.0575)"
            ctx_r   = "India 10Y G-Sec rate, e.g. 6.5% = 0.065"
            ctx_sig = "India VIX / 100 (e.g. 15 VIX = 0.15)"
        vardefs = [
            ("S",    "Spot price",         ctx_S),
            ("K",    "Strike price",       ctx_K),
            ("T",    "Time in years",      ctx_T),
            ("r",    "Risk-free rate",     ctx_r),
            ("\u03c3",  "Implied Volatility", ctx_sig),
            ("N(x)", "Normal CDF",         "Probability \u2264 x under standard normal"),
        ]
        vc = st.columns(2, gap="medium")
        for i, (v, m, ctx) in enumerate(vardefs):
            vc[i%2].markdown(
                f'<div class="card" style="margin-bottom:0.6rem;">'
                f'<div class="card-title">{v} — {m}</div>'
                f'<div class="card-body">{ctx}</div></div>', unsafe_allow_html=True)

        if cur and cur['d1'] is not None:
            st.markdown('<div style="height:0.5rem"></div>', unsafe_allow_html=True)
            st.markdown('<div class="section-label">Live values from Pricer</div>', unsafe_allow_html=True)
            st.code(
                f"d1 = {cur['d1']:.4f}    N(d1) = {norm.cdf(cur['d1']):.4f}\n"
                f"d2 = {cur['d2']:.4f}    N(d2) = {norm.cdf(cur['d2']):.4f}"
            )

        st.markdown('<div style="height:0.5rem"></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-label">Assumptions & Limitations</div>', unsafe_allow_html=True)
        limitations = [
            ("Constant Volatility",
             "BS assumes IV doesn't change. Reality: IV smile and skew exist — OTM puts on Nifty trade at higher IV than ATM. Use this as a baseline, not gospel."),
            ("Log-Normal Returns",
             "Assumes normally distributed returns. Reality: markets have fat tails — crashes happen more often than the model predicts."),
            ("Continuous Trading",
             "Assumes you can hedge continuously. Reality: gaps, circuit breakers, and liquidity constraints exist."),
            ("No Dividends",
             "For Nifty, use continuous dividend yield (~1.2%) for more accurate pricing. BS ignores this by default."),
            ("European Style",
             "Indian index options (Nifty, BankNifty) ARE European-style — no early exercise. BS is exactly applicable here. Stock options are American-style and require binomial or other models."),
        ]
        for lt, ld in limitations:
            st.markdown(
                f'<div class="card" style="margin-bottom:0.6rem;">'
                f'<div class="card-title">⚠ {lt}</div>'
                f'<div class="card-body">{ld}</div></div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="foot">Black Scholes Desk · Day 23 · 30 Days of AI Finance · '
        'Black-Scholes assumes European-style options and constant volatility. '
        'Indian index options (Nifty/BankNifty) are European-style — model is exactly applicable. '
        'For educational purposes only. Not investment advice.</div>',
        unsafe_allow_html=True)


# ============================================================ ROUTER
if st.session_state.page == 'home':
    homepage()
else:
    terminal()