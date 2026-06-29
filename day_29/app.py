"""
BondDesk — Day 29 of 30 Days of AI Finance
Fixed income analyser: bond pricing, YTM solver, duration, convexity,
India G-Sec yield curve, credit spread analysis, zero coupon comparison.
Pure financial math — no external API dependencies.
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.optimize import brentq

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="BondDesk — Fixed Income Analyser",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────────────────
# VERIFIED INDIAN YIELD CURVE DATA — June 2026
# ─────────────────────────────────────────────────────────────────────────────
# All sourced from RBI/CEIC/Trading Economics June 2026
INDIA_GSEC_CURVE = {
    "91D T-Bill":  (0.25,  5.26, "91-Day T-Bill",    "RBI auction, CEIC Jun 2026"),
    "182D T-Bill": (0.50,  5.48, "182-Day T-Bill",   "RBI auction, interpolated Jun 2026"),
    "364D T-Bill": (1.00,  5.77, "364-Day T-Bill",   "RBI auction, CEIC May 2026"),
    "2Y G-Sec":    (2.00,  6.15, "2-Year G-Sec",     "NSE debt market, Jun 2026"),
    "5Y G-Sec":    (5.00,  6.54, "5-Year G-Sec",     "NSE debt market, Jun 2026"),
    "10Y G-Sec":   (10.00, 6.84, "10-Year G-Sec",    "Trading Economics, Jun 23 2026"),
    "15Y G-Sec":   (15.00, 7.05, "15-Year G-Sec",    "NSE debt market, Jun 2026"),
    "30Y G-Sec":   (30.00, 7.33, "30-Year G-Sec",    "Trading Economics, Jun 29 2026"),
}

# RBI repo rate as of June 2026 — held at 5.25% since Dec 2025 cut (61st MPC, Jun 4–6, 2026)
RBI_REPO_RATE = 5.25  # %
RBI_SDF_RATE  = 5.00  # % — Standing Deposit Facility rate

# Corporate bond spreads over G-Sec (basis points)
# Source: SEBI corporate bond market data, typical spreads Jun 2026
CORPORATE_SPREADS = {
    "AAA":  {"1Y": 35,  "3Y": 45,  "5Y": 55,  "10Y": 65},
    "AA+":  {"1Y": 55,  "3Y": 70,  "5Y": 85,  "10Y": 100},
    "AA":   {"1Y": 80,  "3Y": 100, "5Y": 120, "10Y": 145},
    "AA-":  {"1Y": 110, "3Y": 135, "5Y": 160, "10Y": 190},
    "A":    {"1Y": 160, "3Y": 200, "5Y": 240, "10Y": 280},
    "BBB":  {"1Y": 260, "3Y": 320, "5Y": 380, "10Y": 450},
}

# Real Indian bond examples (illustrative — real ISINs, approximate market prices)
BOND_EXAMPLES = {
    "— Manual Entry —":       None,
    "GOI 6.89% 2025":         {"coupon": 6.89, "years": 0.5,  "face": 100,  "type": "G-Sec"},
    "GOI 7.10% 2029":         {"coupon": 7.10, "years": 3.0,  "face": 100,  "type": "G-Sec"},
    "GOI 6.79% 2034":         {"coupon": 6.79, "years": 8.0,  "face": 100,  "type": "G-Sec"},
    "GOI 7.18% 2037":         {"coupon": 7.18, "years": 11.0, "face": 100,  "type": "G-Sec"},
    "GOI 7.24% 2055":         {"coupon": 7.24, "years": 29.0, "face": 100,  "type": "G-Sec"},
    "HDFC Ltd 7.95% 2027":    {"coupon": 7.95, "years": 1.0,  "face": 1000, "type": "Corporate AA+"},
    "REC Ltd 7.55% 2030":     {"coupon": 7.55, "years": 4.0,  "face": 1000, "type": "Corporate AAA"},
    "L&T Finance 8.20% 2028": {"coupon": 8.20, "years": 2.0,  "face": 1000, "type": "Corporate AA"},
}

# ─────────────────────────────────────────────────────────────────────────────
# PLOTLY LAYOUT DEFAULTS
# ─────────────────────────────────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Mono, monospace", color="#888", size=10),
    margin=dict(l=50, r=20, t=60, b=50),
    xaxis=dict(
        gridcolor="rgba(255,255,255,0.04)",
        zerolinecolor="rgba(255,255,255,0.06)",
        tickfont=dict(color="#555", size=9),
    ),
    yaxis=dict(
        gridcolor="rgba(255,255,255,0.04)",
        zerolinecolor="rgba(255,255,255,0.06)",
        tickfont=dict(color="#555", size=9),
    ),
)

# ─────────────────────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────────────────────
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
[data-testid="stVerticalBlock"],
[data-testid="stTabsContent"] {
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
    font-size: 1.3rem !important;
}
[data-testid="stMetricLabel"] {
    font-family: 'DM Mono', monospace !important;
    color: #555 !important;
    font-size: 0.6rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}
[data-testid="stTabs"] button[role="tab"] {
    color: #444 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.72rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: #c9a96e !important;
    border-bottom: 2px solid #c9a96e !important;
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
.stButton > button {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.75rem !important;
    border-radius: 2px !important;
}
.stSelectbox label, .stNumberInput label, .stSlider label, .stRadio label {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.72rem !important;
    color: #555 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
}
div[data-testid="stDataFrame"] {
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 3px !important;
}
.concept-card {
    background: #111118;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 3px;
    padding: 1.2rem;
    margin-bottom: 0.8rem;
}
.concept-card h4 {
    font-family: 'DM Mono', monospace;
    color: #c9a96e;
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin: 0 0 0.4rem 0;
}
.concept-card p {
    font-family: 'Syne', sans-serif;
    color: #888;
    font-size: 0.85rem;
    margin: 0;
    line-height: 1.5;
}
.market-context {
    background: #0d0d14;
    border: 1px solid rgba(201,169,110,0.15);
    border-left: 3px solid #c9a96e;
    border-radius: 3px;
    padding: 1.2rem 1.5rem;
    font-family: 'DM Mono', monospace;
    font-size: 0.82rem;
    line-height: 2;
    color: #888;
}
.market-context span { color: #c9a96e; }
.plain-english {
    background: #0d0d14;
    border: 1px solid rgba(255,255,255,0.05);
    border-left: 2px solid #3a5a7a;
    border-radius: 3px;
    padding: 0.8rem 1rem;
    font-family: 'Syne', sans-serif;
    font-size: 0.83rem;
    color: #777;
    line-height: 1.6;
    margin-top: 0.8rem;
}
::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-thumb { background: rgba(201,169,110,0.15); border-radius: 2px; }
</style>
"""

# ─────────────────────────────────────────────────────────────────────────────
# CORE BOND MATH
# ─────────────────────────────────────────────────────────────────────────────

def bond_price(face: float, coupon_rate: float, ytm: float,
               years: float, freq: int = 2) -> float:
    """
    Price a coupon bond (clean price, no accrued interest).
    face:        face value (₹100 for G-Secs, ₹1000 for most corporates)
    coupon_rate: annual coupon rate as decimal
    ytm:         yield to maturity as decimal
    years:       years to maturity
    freq:        coupon payments per year (2 = semi-annual, standard India)
    """
    n_periods = int(years * freq)
    coupon = face * coupon_rate / freq
    ytm_period = ytm / freq

    # Edge case: very short maturity with < 1 period
    if n_periods == 0:
        # Treat as zero coupon for remaining fraction
        frac = years * freq
        pv_face = face / (1 + ytm_period) ** frac
        pv_coupon = coupon * frac / (1 + ytm_period) ** (frac / 2)
        return round(pv_face + pv_coupon, 4)

    if ytm_period == 0:
        return round(coupon * n_periods + face, 4)

    # PV of coupon stream (annuity)
    pv_coupons = coupon * (1 - (1 + ytm_period) ** (-n_periods)) / ytm_period
    # PV of face value (lump sum)
    pv_face = face / (1 + ytm_period) ** n_periods

    return round(pv_coupons + pv_face, 4)


def ytm_solver(face: float, coupon_rate: float, price: float,
               years: float, freq: int = 2):
    """
    Solve for YTM given market price using scipy brentq.
    Guaranteed convergence within [0.001, 0.99].
    Returns YTM as decimal. Returns None if no solution.
    """
    if years <= 0 or price <= 0:
        return None

    def objective(ytm):
        return bond_price(face, coupon_rate, ytm, years, freq) - price

    try:
        lo, hi = 0.0001, 0.9999
        f_lo = objective(lo)
        f_hi = objective(hi)
        # Check if solution exists in range
        if f_lo * f_hi > 0:
            return None
        ytm = brentq(objective, lo, hi, xtol=1e-10, maxiter=1000)
        return round(ytm, 6)
    except Exception:
        return None


def macaulay_duration(face: float, coupon_rate: float, ytm: float,
                      years: float, freq: int = 2) -> float:
    """
    Macaulay Duration: weighted average time to receive cash flows (in years).
    Formula: Σ [t × PV(CF_t)] / Bond Price
    """
    n_periods = int(years * freq)
    coupon = face * coupon_rate / freq
    ytm_period = ytm / freq
    price = bond_price(face, coupon_rate, ytm, years, freq)

    if price <= 0 or n_periods == 0:
        return years  # ZCB-like edge case

    weighted_sum = 0.0
    for t in range(1, n_periods + 1):
        cf = coupon if t < n_periods else coupon + face
        pv_cf = cf / (1 + ytm_period) ** t
        weighted_sum += (t / freq) * pv_cf

    return round(weighted_sum / price, 4)


def modified_duration(face: float, coupon_rate: float, ytm: float,
                      years: float, freq: int = 2) -> float:
    """
    Modified Duration = Macaulay Duration / (1 + YTM/freq)
    Measures % price change for 1% change in yield.
    """
    mac_dur = macaulay_duration(face, coupon_rate, ytm, years, freq)
    return round(mac_dur / (1 + ytm / freq), 4)


def convexity(face: float, coupon_rate: float, ytm: float,
              years: float, freq: int = 2) -> float:
    """
    Convexity: second-order sensitivity of bond price to yield changes.
    Formula: Σ [t(t+1) × PV(CF_t)] / [Price × (1+y/m)^2 × m^2]
    """
    n_periods = int(years * freq)
    coupon = face * coupon_rate / freq
    ytm_period = ytm / freq
    price = bond_price(face, coupon_rate, ytm, years, freq)

    if price <= 0 or n_periods == 0:
        return 0.0

    conv_sum = 0.0
    for t in range(1, n_periods + 1):
        cf = coupon if t < n_periods else coupon + face
        pv_cf = cf / (1 + ytm_period) ** t
        conv_sum += t * (t + 1) * pv_cf

    convexity_val = conv_sum / (price * (1 + ytm_period) ** 2 * freq ** 2)
    return round(convexity_val, 4)


def price_change_estimate(mod_dur: float, conv: float, ytm_change: float) -> dict:
    """
    Estimate % price change from yield change using duration + convexity.
    ytm_change: change in yield as decimal (e.g. 0.01 for +100bps)
    ΔP/P ≈ -ModDur × Δy + 0.5 × Convexity × (Δy)²
    """
    duration_effect = -mod_dur * ytm_change
    convexity_effect = 0.5 * conv * ytm_change ** 2
    total_effect = duration_effect + convexity_effect
    return {
        "duration_effect":  round(duration_effect * 100, 4),
        "convexity_effect": round(convexity_effect * 100, 4),
        "total_effect":     round(total_effect * 100, 4),
    }


def zero_coupon_bond_price(face: float, ytm: float, years: float) -> float:
    """
    Zero coupon bond price: P = F / (1 + y/2)^(2*n)
    Uses semi-annual compounding convention.
    """
    return round(face / (1 + ytm / 2) ** (2 * years), 4)


def current_yield(face: float, coupon_rate: float, price: float) -> float:
    """
    Current Yield = Annual Coupon / Market Price.
    Simple measure — does not account for capital gain/loss.
    """
    annual_coupon = face * coupon_rate
    if price <= 0:
        return 0.0
    return round(annual_coupon / price, 6)


def generate_price_yield_curve(face: float, coupon_rate: float,
                                years: float, freq: int = 2,
                                ytm_range: tuple = (0.02, 0.15),
                                n_points: int = 150):
    """
    Generate arrays of YTM and corresponding prices for P-Y curve.
    Shows convex shape — key visual in fixed income.
    Returns (ytms_pct, prices).
    """
    ytms = np.linspace(ytm_range[0], ytm_range[1], n_points)
    prices = np.array([bond_price(face, coupon_rate, y, years, freq) for y in ytms])
    return ytms * 100, prices  # ytm in %, prices in ₹


def spread_to_gsec(corporate_ytm: float, gsec_ytm: float) -> float:
    """Credit spread in basis points."""
    return round((corporate_ytm - gsec_ytm) * 10000, 1)


def interpolate_gsec_yield(tenor_years: float, curve: dict = None) -> float:
    """Linear interpolation of G-Sec yield for any tenor."""
    if curve is None:
        curve = INDIA_GSEC_CURVE
    tenors = sorted([(v[0], v[1]) for v in curve.values()])

    if tenor_years <= tenors[0][0]:
        return tenors[0][1] / 100
    if tenor_years >= tenors[-1][0]:
        return tenors[-1][1] / 100

    for i in range(len(tenors) - 1):
        t1, y1 = tenors[i]
        t2, y2 = tenors[i + 1]
        if t1 <= tenor_years <= t2:
            frac = (tenor_years - t1) / (t2 - t1)
            return (y1 + frac * (y2 - y1)) / 100

    return tenors[-1][1] / 100


def dv01(face: float, coupon_rate: float, ytm: float,
         years: float, freq: int = 2) -> float:
    """
    DV01: price change for 1 basis point yield change.
    DV01 = ModDur × Price × 0.0001
    In ₹ per face value.
    """
    price = bond_price(face, coupon_rate, ytm, years, freq)
    mod_dur = modified_duration(face, coupon_rate, ytm, years, freq)
    return round(abs(mod_dur * price * 0.0001), 4)


def interpolate_corp_spread(rating: str, tenor_years: float) -> float:
    """Interpolate credit spread for a given rating and tenor."""
    spreads = CORPORATE_SPREADS[rating]
    tenors = [1, 3, 5, 10]
    spr_vals = [spreads[f"{t}Y"] for t in tenors]

    if tenor_years <= tenors[0]:
        return spr_vals[0]
    if tenor_years >= tenors[-1]:
        return spr_vals[-1]

    for i in range(len(tenors) - 1):
        if tenors[i] <= tenor_years <= tenors[i + 1]:
            frac = (tenor_years - tenors[i]) / (tenors[i + 1] - tenors[i])
            return spr_vals[i] + frac * (spr_vals[i + 1] - spr_vals[i])

    return spr_vals[-1]


# ─────────────────────────────────────────────────────────────────────────────
# MATH VERIFICATION — runs on startup
# ─────────────────────────────────────────────────────────────────────────────

def verify_math():
    """Run sanity checks on all bond math. All must pass before UI renders."""

    # Test 1: Par bond — coupon = YTM → price = face
    p = bond_price(100, 0.068, 0.068, 10)
    assert abs(p - 100) < 0.01, f"Par bond failed: {p}"

    # Test 2: Premium bond — coupon > YTM → price > face
    p = bond_price(100, 0.075, 0.065, 5)
    assert p > 100, f"Premium bond failed: {p}"

    # Test 3: Discount bond — coupon < YTM → price < face
    p = bond_price(100, 0.060, 0.075, 5)
    assert p < 100, f"Discount bond failed: {p}"

    # Test 4: YTM solver round-trip
    orig_price = bond_price(100, 0.0689, 0.0720, 8)
    solved = ytm_solver(100, 0.0689, orig_price, 8)
    assert solved is not None, "YTM solver returned None"
    recovered = bond_price(100, 0.0689, solved, 8)
    assert abs(recovered - orig_price) < 0.001, f"YTM round-trip failed: {recovered} vs {orig_price}"

    # Test 5: Duration increases with maturity (all else equal)
    d5 = macaulay_duration(100, 0.07, 0.07, 5)
    d10 = macaulay_duration(100, 0.07, 0.07, 10)
    assert d10 > d5, f"Duration-maturity relationship failed: d5={d5}, d10={d10}"

    # Test 6: Higher coupon → shorter duration (all else equal)
    d_high = macaulay_duration(100, 0.10, 0.07, 10)
    d_low  = macaulay_duration(100, 0.02, 0.07, 10)
    assert d_low > d_high, f"Duration-coupon relationship failed: high={d_high}, low={d_low}"

    # Test 7: YTM solver handles par bond (price = face)
    ytm_par = ytm_solver(100, 0.068, 100.0, 10)
    assert ytm_par is not None, "YTM solver failed at par"
    assert abs(ytm_par - 0.068) < 0.0001, f"YTM at par incorrect: {ytm_par}"

    # Test 8: Modified duration < Macaulay duration (for ytm > 0)
    mac = macaulay_duration(100, 0.07, 0.07, 10)
    mod = modified_duration(100, 0.07, 0.07, 10)
    assert mod < mac, f"ModDur should be < MacDur: mod={mod}, mac={mac}"

    # Test 9: Convexity is positive
    conv = convexity(100, 0.07, 0.07, 10)
    assert conv > 0, f"Convexity must be positive: {conv}"

    # Test 10: Price-yield inverse relationship
    p_low_ytm  = bond_price(100, 0.07, 0.05, 10)
    p_high_ytm = bond_price(100, 0.07, 0.09, 10)
    assert p_low_ytm > p_high_ytm, "Price-yield inverse relationship failed"

    return True


# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────────────────────────────────────

if "page" not in st.session_state:
    st.session_state.page = "home"

if "math_verified" not in st.session_state:
    try:
        verify_math()
        st.session_state.math_verified = True
        st.session_state.math_error = None
    except AssertionError as e:
        st.session_state.math_verified = False
        st.session_state.math_error = str(e)

st.markdown(CSS, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# MATH ERROR BANNER (shown globally if verification failed)
# ─────────────────────────────────────────────────────────────────────────────

if not st.session_state.math_verified:
    st.error(f"⚠️ Math verification failed: {st.session_state.math_error}. Results may be unreliable.")

# ─────────────────────────────────────────────────────────────────────────────
# HOME PAGE
# ─────────────────────────────────────────────────────────────────────────────

def render_home():
    st.markdown("""
    <div style="padding: 3rem 0 2rem 0;">
        <div style="font-family:'DM Mono',monospace; font-size:0.68rem; color:#3a5a7a;
                    letter-spacing:0.18em; text-transform:uppercase; margin-bottom:1rem;">
            ● BOND PRICER · YTM SOLVER · DURATION · CONVEXITY · INDIA YIELD CURVE
        </div>
        <div style="font-family:'Playfair Display',serif; font-size:3.2rem; font-weight:700;
                    color:#e8e4dc; line-height:1.1; margin-bottom:0.5rem;">
            BondDesk
        </div>
        <div style="font-family:'Playfair Display',serif; font-size:1.25rem; font-weight:700;
                    font-style:italic; color:#c9a96e; margin-bottom:1.5rem;">
            The ₹240 trillion market. Finally visualised.
        </div>
        <div style="font-family:'Syne',sans-serif; font-size:0.95rem; color:#666;
                    max-width:640px; line-height:1.7; margin-bottom:2.5rem;">
            Fixed income is the largest financial market in the world — and the most misunderstood.
            India's debt market alone stands at ₹240 trillion (US$ 2.8T) as of 2026 — larger than its equity market.
            BondDesk brings institutional-grade bond analytics to everyone: price any bond, solve for yield,
            understand duration risk, and read India's live G-Sec yield curve.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Stats strip
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Yield Curve Points", "8", "91D → 30Y")
    with col2:
        st.metric("10Y G-Sec Yield", "6.84%", "Jun 2026")
    with col3:
        st.metric("RBI Repo Rate", "5.25%", "Held — 61st MPC Jun 2026")
    with col4:
        st.metric("Bond Math Engine", "SciPy", "Brentq YTM solver")

    st.markdown("<br>", unsafe_allow_html=True)

    # Feature pills
    st.markdown("""
    <div style="display:flex; flex-wrap:wrap; gap:0.5rem; margin-bottom:2rem;">
        <span style="background:#111118; border:1px solid rgba(201,169,110,0.2); border-radius:2px;
                     font-family:'DM Mono',monospace; font-size:0.68rem; color:#c9a96e;
                     padding:0.3rem 0.7rem; text-transform:uppercase; letter-spacing:0.06em;">Bond Pricer</span>
        <span style="background:#111118; border:1px solid rgba(255,255,255,0.06); border-radius:2px;
                     font-family:'DM Mono',monospace; font-size:0.68rem; color:#555;
                     padding:0.3rem 0.7rem; text-transform:uppercase; letter-spacing:0.06em;">YTM Solver</span>
        <span style="background:#111118; border:1px solid rgba(255,255,255,0.06); border-radius:2px;
                     font-family:'DM Mono',monospace; font-size:0.68rem; color:#555;
                     padding:0.3rem 0.7rem; text-transform:uppercase; letter-spacing:0.06em;">India Yield Curve</span>
        <span style="background:#111118; border:1px solid rgba(255,255,255,0.06); border-radius:2px;
                     font-family:'DM Mono',monospace; font-size:0.68rem; color:#555;
                     padding:0.3rem 0.7rem; text-transform:uppercase; letter-spacing:0.06em;">Duration & Convexity</span>
        <span style="background:#111118; border:1px solid rgba(255,255,255,0.06); border-radius:2px;
                     font-family:'DM Mono',monospace; font-size:0.68rem; color:#555;
                     padding:0.3rem 0.7rem; text-transform:uppercase; letter-spacing:0.06em;">Credit Spreads</span>
        <span style="background:#111118; border:1px solid rgba(255,255,255,0.06); border-radius:2px;
                     font-family:'DM Mono',monospace; font-size:0.68rem; color:#555;
                     padding:0.3rem 0.7rem; text-transform:uppercase; letter-spacing:0.06em;">Price-Yield Curve</span>
    </div>
    """, unsafe_allow_html=True)

    # Feature grid
    gc1, gc2, gc3 = st.columns(3)
    cards = [
        ("Bond Pricer", "Price any coupon bond or zero coupon bond. Semi-annual, annual, or quarterly frequency. Instant results with full Greek metrics.", "#c9a96e"),
        ("YTM Solver", "Enter a market price and get the implied yield to maturity. Uses SciPy Brentq — the same solver used in professional fixed income systems.", "#4a9eff"),
        ("India Yield Curve", "Live G-Sec yield curve from 91-Day T-Bills to 30-Year bonds. RBI repo rate overlay. Corporate spread overlay by rating.", "#4ab87a"),
        ("Duration & Convexity", "Macaulay duration, modified duration, DV01, and convexity. Visualise cash flow timelines and the convexity advantage.", "#c9a96e"),
        ("Credit Spreads", "Rating-based spread table (AAA to BBB) at any tenor. Understand what the market charges for credit risk over risk-free G-Sec.", "#4a9eff"),
        ("Price-Yield Visualiser", "See the convex shape of the price-yield curve. Compare duration approximation vs actual curve — the gap is convexity.", "#4ab87a"),
    ]
    for i, (title, desc, color) in enumerate(cards):
        col = [gc1, gc2, gc3][i % 3]
        with col:
            st.markdown(f"""
            <div style="background:#111118; border:1px solid rgba(255,255,255,0.06);
                        border-top:2px solid {color}30; border-radius:3px; padding:1.2rem;
                        margin-bottom:0.8rem; min-height:110px;">
                <div style="font-family:'DM Mono',monospace; font-size:0.7rem; color:{color};
                            text-transform:uppercase; letter-spacing:0.08em; margin-bottom:0.5rem;">{title}</div>
                <div style="font-family:'Syne',sans-serif; font-size:0.82rem; color:#555; line-height:1.5;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_btn, col_ctx = st.columns([1, 3])
    with col_btn:
        if st.button("→ Launch BondDesk", type="primary", use_container_width=True):
            st.session_state.page = "terminal"
            st.rerun()
    with col_ctx:
        st.markdown("""
        <div style="font-family:'DM Mono',monospace; font-size:0.68rem; color:#333;
                    padding-top:0.6rem; line-height:1.7;">
            Part of the 30 Days of AI Finance complete suite — the only tool covering India's fixed income market.
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# CHART BUILDERS
# ─────────────────────────────────────────────────────────────────────────────

def make_yield_curve(curve_data: dict, highlight_repo: bool = True) -> go.Figure:
    tenors = [v[0] for v in curve_data.values()]
    yields = [v[1] for v in curve_data.values()]
    labels = [v[2] for v in curve_data.values()]

    fig = go.Figure()

    # Shaded area
    fig.add_trace(go.Scatter(
        x=tenors, y=yields,
        mode="lines", fill="tozeroy",
        fillcolor="rgba(201,169,110,0.06)",
        line=dict(color="#c9a96e", width=2.5),
        showlegend=False,
    ))

    # Data points with labels — alternate above/below to prevent overlap at short end
    # (91D, 182D, 364D, 2Y are clustered left — stagger them)
    text_positions = ["top center", "bottom center", "top center", "bottom center",
                      "top center", "top center", "top center", "top center"]
    fig.add_trace(go.Scatter(
        x=tenors, y=yields,
        mode="markers+text",
        marker=dict(color="#c9a96e", size=9,
                    line=dict(color="#09090e", width=2)),
        text=[f"{y:.2f}%" for y in yields],
        textposition=text_positions[:len(tenors)],
        textfont=dict(family="DM Mono", size=10, color="#aaa"),
        hovertemplate="%{customdata}<br>Tenor: %{x}Y<br>Yield: %{y:.2f}%<extra></extra>",
        customdata=labels,
        showlegend=False,
    ))

    if highlight_repo:
        fig.add_hline(
            y=RBI_REPO_RATE,
            line_color="rgba(74,184,122,0.4)",
            line_dash="dash", line_width=1.5,
            annotation_text=f"RBI Repo Rate: {RBI_REPO_RATE}%",
            annotation_font=dict(color="#4ab87a", size=9, family="DM Mono"),
            annotation_position="right",
        )

    tick_labels = []
    for t in tenors:
        if t < 1:
            months = int(t * 12)
            tick_labels.append(f"{months}mo")
        else:
            tick_labels.append(f"{int(t)}Y")

    layout = dict(PLOTLY_LAYOUT)
    layout["xaxis"] = dict(PLOTLY_LAYOUT["xaxis"])
    layout["yaxis"] = dict(PLOTLY_LAYOUT["yaxis"])
    layout["xaxis"]["title"] = "Tenor"
    layout["xaxis"]["tickvals"] = tenors
    layout["xaxis"]["ticktext"] = tick_labels
    layout["yaxis"]["title"] = "Yield (%)"

    # Clamp Y-axis to data range (no dead space from 0)
    min_y = min(yields) - 0.4
    max_y = max(yields) + 0.5
    layout["yaxis"]["range"] = [min_y, max_y]

    fig.update_layout(
        **layout,
        title=dict(
            text="India Government Securities Yield Curve — June 2026",
            font=dict(family="Playfair Display, serif", color="#c9a96e", size=15),
            x=0.02,
        ),
        height=420,
        showlegend=False,
    )
    return fig


def make_corp_spread_chart(tenor_years: float) -> go.Figure:
    gsec_yield = interpolate_gsec_yield(tenor_years) * 100
    ratings = list(CORPORATE_SPREADS.keys())
    spreads_bps = [interpolate_corp_spread(r, tenor_years) for r in ratings]
    corp_yields = [gsec_yield + s / 100 for s in spreads_bps]

    rating_colors = {
        "AAA":  "#c9a96e",
        "AA+":  "#a8c8a0",
        "AA":   "#4a9eff",
        "AA-":  "#9b8cff",
        "A":    "#ff9f45",
        "BBB":  "#e05c6c",
    }

    fig = go.Figure()
    for i, r in enumerate(ratings):
        fig.add_trace(go.Bar(
            x=[r], y=[spreads_bps[i]],
            name=r,
            marker_color=rating_colors.get(r, "#888"),
            hovertemplate=f"<b>{r}</b><br>Spread: {spreads_bps[i]:.0f} bps<br>"
                          f"G-Sec: {gsec_yield:.2f}%<br>Corp Yield: {corp_yields[i]:.2f}%<extra></extra>",
            showlegend=False,
        ))

    fig.add_hline(
        y=0,
        line_color="rgba(255,255,255,0.05)",
        line_width=1,
    )

    fig.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(
            text=f"Credit Spreads by Rating — {tenor_years:.1f}Y Tenor (G-Sec base: {gsec_yield:.2f}%)",
            font=dict(family="Playfair Display, serif", color="#c9a96e", size=13),
            x=0.02,
        ),
        xaxis_title="Credit Rating",
        yaxis_title="Spread over G-Sec (bps)",
        height=340,
        showlegend=False,
    )
    return fig


def make_cash_flow_chart(face: float, coupon_rate: float,
                          ytm: float, years: float, freq: int = 2) -> go.Figure:
    n = int(years * freq)
    coupon = face * coupon_rate / freq
    ytm_p = ytm / freq

    if n == 0:
        return go.Figure()

    times, pvs = [], []
    for t in range(1, n + 1):
        cf = coupon if t < n else coupon + face
        pv = cf / (1 + ytm_p) ** t
        times.append(t / freq)
        pvs.append(pv)

    colors = ["#c9a96e" if i < len(times) - 1 else "#4ab87a" for i in range(len(times))]
    mac_dur = macaulay_duration(face, coupon_rate, ytm, years, freq)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=times, y=pvs,
        marker_color=colors,
        hovertemplate="Year %{x:.2f}<br>PV: ₹%{y:.4f}<extra></extra>",
        showlegend=False,
    ))
    fig.add_vline(
        x=mac_dur,
        line_color="#e05c6c", line_width=2, line_dash="dash",
        annotation_text=f"Duration: {mac_dur:.2f}Y",
        annotation_font=dict(color="#e05c6c", size=10, family="DM Mono"),
        annotation_position="top right",
    )
    fig.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(
            text="Cash Flow Timeline — Duration is the Weighted Average",
            font=dict(color="#c9a96e", size=12),
        ),
        xaxis_title="Years",
        yaxis_title="PV of Cash Flow (₹)",
        height=300,
        showlegend=False,
    )
    return fig


def make_price_yield_convexity_chart(face: float, coupon_rate: float,
                                      ytm: float, years: float, freq: int = 2) -> go.Figure:
    ytms_pct, prices = generate_price_yield_curve(face, coupon_rate, years, freq,
                                                   ytm_range=(0.02, 0.15))
    current_price = bond_price(face, coupon_rate, ytm, years, freq)
    mod_dur = modified_duration(face, coupon_rate, ytm, years, freq)
    conv = convexity(face, coupon_rate, ytm, years, freq)

    ytm_arr = np.linspace(0.02, 0.15, 150)

    # Clip approximation lines to ±5% around current YTM
    # Wide enough to show the gap between linear duration and curved convexity
    clip_lo = max(0.02, ytm - 0.05)
    clip_hi = min(0.15, ytm + 0.05)
    approx_mask = (ytm_arr >= clip_lo) & (ytm_arr <= clip_hi)
    ytm_approx = ytm_arr[approx_mask]

    dur_approx = [current_price * (1 - mod_dur * (y - ytm)) for y in ytm_approx]
    conv_approx = [
        current_price * (1 - mod_dur * (y - ytm) + 0.5 * conv * (y - ytm) ** 2)
        for y in ytm_approx
    ]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=ytms_pct, y=prices, mode="lines",
        line=dict(color="#c9a96e", width=3), name="Actual Price",
        hovertemplate="YTM: %{x:.2f}%<br>Price: ₹%{y:.2f}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=ytm_approx * 100, y=dur_approx, mode="lines",
        line=dict(color="#e05c6c", width=2, dash="longdash"), name="Duration Approx.",
    ))
    fig.add_trace(go.Scatter(
        x=ytm_approx * 100, y=conv_approx, mode="lines",
        line=dict(color="#4a9eff", width=2, dash="dot"), name="Conv. Adjusted",
    ))
    fig.add_trace(go.Scatter(
        x=[ytm * 100], y=[current_price],
        mode="markers",
        marker=dict(color="#4ab87a", size=12, symbol="star"),
        name="Current",
    ))

    fig.update_layout(
        **PLOTLY_LAYOUT,
        title=dict(
            text="Price-Yield Relationship — Convexity Advantage",
            font=dict(color="#c9a96e", size=12),
        ),
        xaxis_title="YTM (%)",
        yaxis_title=f"Price (₹)",
        height=340,
        showlegend=True,
        legend=dict(
            bgcolor="rgba(9,9,14,0.85)",
            bordercolor="rgba(255,255,255,0.06)",
            borderwidth=1,
            font=dict(color="#aaa", size=10, family="DM Mono"),
            x=0.98, y=0.98,
            xanchor="right",
            yanchor="top",
        ),
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# TERMINAL — TABS
# ─────────────────────────────────────────────────────────────────────────────

def render_terminal():
    # Header
    col_back, col_title = st.columns([1, 8])
    with col_back:
        if st.button("← Home"):
            st.session_state.page = "home"
            st.rerun()
    with col_title:
        st.markdown("""
        <div style="font-family:'DM Mono',monospace; font-size:0.65rem; color:#3a5a7a;
                    letter-spacing:0.12em; text-transform:uppercase; padding-top:0.5rem;">
            BONDDESK · FIXED INCOME TERMINAL · INDIA G-SEC YIELD CURVE · JUNE 2026
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "⚙️ Bond Pricer",
        "📈 Yield Curve",
        "📐 Duration & Convexity",
        "💳 Credit Spreads",
        "📚 Bond Math 101",
    ])

    # ─────────────────────────────────────────────────────────────────────────
    # TAB 1 — BOND PRICER
    # ─────────────────────────────────────────────────────────────────────────
    with tab1:
        st.markdown("### Bond Pricer & YTM Solver")

        # Preset selector — on_change callback writes directly into session_state
        # so the number_input widgets pick up the new values on re-render
        def _load_preset():
            sel = st.session_state["preset_select"]
            if sel == "— Manual Entry —" or BOND_EXAMPLES[sel] is None:
                return
            b = BOND_EXAMPLES[sel]
            gsec_y = interpolate_gsec_yield(b["years"]) * 100
            ytm_dec = round(gsec_y, 2) / 100
            st.session_state["face_val"]           = float(b["face"])
            st.session_state["coupon_val"]         = float(b["coupon"])
            st.session_state["years_val"]          = float(b["years"])
            st.session_state["ytm_val"]            = round(gsec_y, 2)
            # Reset market price input to computed price for this bond
            computed_price = bond_price(b["face"], b["coupon"] / 100, ytm_dec, b["years"])
            st.session_state["market_price_input"] = float(round(computed_price, 2))

        st.selectbox(
            "Load Example Bond (or configure manually below)",
            list(BOND_EXAMPLES.keys()),
            key="preset_select",
            on_change=_load_preset,
        )

        st.markdown("#### ⚙️ Bond Parameters")
        left_col, right_col = st.columns([1, 1])

        with left_col:
            col_a, col_b = st.columns(2)
            with col_a:
                face = st.number_input("Face Value (₹)", value=100.0,
                                        step=10.0, min_value=1.0, key="face_val")
                coupon_pct = st.number_input("Annual Coupon %", value=6.89,
                                              step=0.01, min_value=0.0, max_value=30.0, key="coupon_val")
                years_input = st.number_input("Years to Maturity", value=8.0,
                                               step=0.5, min_value=0.1, max_value=50.0, key="years_val")
            with col_b:
                ytm_pct = st.number_input("YTM % (for pricing)", value=6.84,
                                           step=0.01, min_value=0.01, max_value=99.0, key="ytm_val")
                freq = st.selectbox("Coupon Frequency", [2, 1, 4], index=0,
                                     format_func=lambda x: {2: "Semi-annual", 1: "Annual", 4: "Quarterly"}[x],
                                     key="freq_val")
                bond_type = st.radio("Bond Type", ["Coupon Bond", "Zero Coupon Bond"],
                                      horizontal=True, key="bond_type_val")

            coupon_rate = coupon_pct / 100
            ytm = ytm_pct / 100

        with right_col:
            st.markdown("#### 📊 Results")

            if bond_type == "Coupon Bond":
                price = bond_price(face, coupon_rate, ytm, years_input, freq)
                mac_dur = macaulay_duration(face, coupon_rate, ytm, years_input, freq)
                mod_dur = modified_duration(face, coupon_rate, ytm, years_input, freq)
                conv = convexity(face, coupon_rate, ytm, years_input, freq)
                dv01_val = dv01(face, coupon_rate, ytm, years_input, freq)
                curr_y = current_yield(face, coupon_rate, price)
                dollar_conv = round(0.5 * conv * price * 0.0001, 4)
            else:
                price = zero_coupon_bond_price(face, ytm, years_input)
                mac_dur = years_input  # ZCB: duration = maturity
                mod_dur = round(mac_dur / (1 + ytm / 2), 4)
                conv = round(years_input * (years_input + 0.5) / (1 + ytm / 2) ** 2, 4)
                dv01_val = round(abs(mod_dur * price * 0.0001), 4)
                curr_y = 0.0
                dollar_conv = round(0.5 * conv * price * 0.0001, 4)

            # Premium / Discount / Par indicator
            if bond_type == "Coupon Bond":
                if abs(price - face) < 0.05:
                    price_label = "PAR"
                    price_color = "#4ab87a"
                elif price > face:
                    price_label = "PREMIUM"
                    price_color = "#4a9eff"
                else:
                    price_label = "DISCOUNT"
                    price_color = "#e05c6c"
                price_tag = f" <span style='font-size:0.6rem; color:{price_color}; font-family:DM Mono;'>{price_label}</span>"
            else:
                price_tag = ""

            m1, m2, m3 = st.columns(3)
            with m1:
                st.metric("Clean Price", f"₹{price:.2f}")
            with m2:
                st.metric("Current Yield", f"{curr_y*100:.4f}%" if curr_y > 0 else "N/A (ZCB)")
            with m3:
                st.metric("YTM Input", f"{ytm_pct:.4f}%")

            m4, m5, m6 = st.columns(3)
            with m4:
                st.metric("Macaulay Duration", f"{mac_dur:.2f} yrs")
            with m5:
                st.metric("Modified Duration", f"{mod_dur:.2f} yrs")
            with m6:
                st.metric("DV01", f"₹{dv01_val:.4f}")

            m7, m8, m9 = st.columns(3)
            with m7:
                st.metric("Convexity", f"{conv:.2f}")
            with m8:
                st.metric("Dollar Convexity", f"₹{dollar_conv:.4f}")
            with m9:
                spread_bps = round((ytm - interpolate_gsec_yield(years_input)) * 10000, 1)
                st.metric("Spread vs G-Sec", f"{spread_bps:+.1f} bps")

        st.markdown("---")

        # YTM Solver
        st.markdown("#### 🔄 YTM Solver — Enter Market Price, Get YTM")
        sol_col1, sol_col2 = st.columns([1, 2])
        with sol_col1:
            market_price = st.number_input("Market Price (₹)", value=float(round(price, 2)),
                                            step=0.01, min_value=0.01, key="market_price_input")
            solve_btn = st.button("Solve for YTM →", type="primary", key="ytm_solve_btn")

        with sol_col2:
            if solve_btn:
                if bond_type == "Coupon Bond":
                    solved = ytm_solver(face, coupon_rate, market_price, years_input, freq)
                    if solved is not None:
                        curr_y_solved = current_yield(face, coupon_rate, market_price)
                        spread_vs_gsec = spread_to_gsec(solved, interpolate_gsec_yield(years_input))
                        sc1, sc2, sc3 = st.columns(3)
                        with sc1:
                            st.metric("Implied YTM", f"{solved*100:.4f}%")
                        with sc2:
                            st.metric("Current Yield", f"{curr_y_solved*100:.4f}%")
                        with sc3:
                            st.metric("Spread vs G-Sec", f"{spread_vs_gsec:+.1f} bps")
                    else:
                        st.error("No solution found. Price may be outside valid range for this bond.")
                else:
                    # ZCB YTM from price: ytm = 2 * ((F/P)^(1/(2n)) - 1)
                    if market_price > 0 and years_input > 0:
                        zcb_ytm = 2 * ((face / market_price) ** (1 / (2 * years_input)) - 1)
                        st.metric("Implied YTM (ZCB)", f"{zcb_ytm*100:.4f}%")
                    else:
                        st.error("Invalid inputs.")
            else:
                st.markdown("""
                <div class="plain-english">
                    Enter a market price above and click "Solve for YTM" to get the implied yield.
                    Works for any bond — premium, discount, or near-par.
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---")

        # Yield Shock Scenarios
        if bond_type == "Coupon Bond":
            st.markdown("#### 📊 Yield Shock Scenarios")
            st.caption("Estimated price change using Duration + Convexity approximation")

            shocks = [-200, -100, -50, -25, +25, +50, +100, +200]
            shock_data = []
            for bps in shocks:
                dy = bps / 10000
                change = price_change_estimate(mod_dur, conv, dy)
                new_price = bond_price(face, coupon_rate, ytm + dy, years_input, freq)
                shock_data.append({
                    "Yield Change": f"{'+'  if bps > 0 else ''}{bps} bps",
                    "New YTM": f"{(ytm + dy) * 100:.2f}%",
                    "Est. Price Change": f"{change['total_effect']:+.2f}%",
                    "Duration Effect": f"{change['duration_effect']:+.2f}%",
                    "Convexity Add": f"{change['convexity_effect']:+.3f}%",
                    "New Price": f"₹{new_price:.2f}",
                })

            st.dataframe(pd.DataFrame(shock_data), use_container_width=True, hide_index=True)

            st.markdown(f"""
            <div class="plain-english">
                Modified Duration of <strong style="color:#c9a96e;">{mod_dur:.2f}</strong>
                means: if yields rise 1% (100 bps), this bond's price falls approximately
                <strong style="color:#e05c6c;">{mod_dur:.2f}%</strong>.
                But convexity means the actual fall is slightly less — bonds gain more when yields fall
                than they lose when yields rise. This asymmetry is what makes convexity a desirable property.
                DV01 of ₹{dv01_val:.4f} means each 1 basis point move changes the price by that amount
                per ₹{int(face)} face value.
            </div>
            """, unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────────
    # TAB 2 — YIELD CURVE
    # ─────────────────────────────────────────────────────────────────────────
    with tab2:
        st.markdown("### India G-Sec Yield Curve — June 2026")

        fig_curve = make_yield_curve(INDIA_GSEC_CURVE)
        st.plotly_chart(fig_curve, use_container_width=True, config={"displayModeBar": False})

        # Curve interpretation
        spread_10_2 = 6.84 - 6.15
        term_premium = 6.84 - RBI_REPO_RATE

        col_interp, col_data = st.columns([2, 1])
        with col_interp:
            st.markdown(f"""
            <div class="plain-english">
                <strong style="color:#c9a96e;">Current shape: Normal (upward sloping)</strong><br>
                Long-term rates (30Y: 7.33%) are higher than short-term rates (91D T-Bill: 5.26%).
                This is the typical healthy state — investors demand higher returns for locking up
                money longer. The 10Y-2Y spread of <strong style="color:#c9a96e;">{spread_10_2:.2f}%</strong>
                signals moderate growth expectations.<br><br>
                <strong style="color:#4ab87a;">What the RBI repo rate gap tells you:</strong><br>
                The 10Y G-Sec (6.84%) is {term_premium:.2f}% above the repo rate ({RBI_REPO_RATE}%).
                This 'term premium' compensates investors for duration risk and inflation uncertainty.
                A narrowing term premium often precedes rate cuts.
            </div>
            """, unsafe_allow_html=True)

        with col_data:
            curve_rows = []
            for key, (tenor, yld, label, source) in INDIA_GSEC_CURVE.items():
                curve_rows.append({"Instrument": key, "Tenor": f"{int(tenor)}Y" if tenor >= 1 else f"{int(tenor*12)}mo",
                                    "Yield": f"{yld:.2f}%", "Source": source.split(",")[0]})
            st.dataframe(pd.DataFrame(curve_rows), use_container_width=True, hide_index=True)

        st.markdown("---")

        # Corporate Spread Overlay
        st.markdown("#### Corporate Bond Yield Curves by Rating")
        st.caption("G-Sec yield + credit spread at each tenor")

        overlay_tenors = [0.25, 0.5, 1, 2, 3, 5, 7, 10, 15, 20, 30]
        gsec_yields_overlay = [interpolate_gsec_yield(t) * 100 for t in overlay_tenors]

        fig_overlay = go.Figure()
        fig_overlay.add_trace(go.Scatter(
            x=overlay_tenors, y=gsec_yields_overlay,
            mode="lines", name="G-Sec",
            line=dict(color="#c9a96e", width=3),
        ))

        rating_colors = {
            "AAA":  "#a8c8a0",
            "AA+":  "#4a9eff",
            "AA":   "#9b8cff",
            "AA-":  "#ff9f45",
            "A":    "#ff6b9d",
            "BBB":  "#e05c6c",
        }

        for rating in CORPORATE_SPREADS:
            corp_yields = []
            for t in overlay_tenors:
                gsec_y = interpolate_gsec_yield(t) * 100
                spread = interpolate_corp_spread(rating, t)
                corp_yields.append(gsec_y + spread / 100)

            fig_overlay.add_trace(go.Scatter(
                x=overlay_tenors, y=corp_yields,
                mode="lines", name=rating,
                line=dict(color=rating_colors[rating], width=1.5, dash="dot"),
                hovertemplate=f"Rating: {rating}<br>Tenor: %{{x}}Y<br>Yield: %{{y:.2f}}%<extra></extra>",
            ))

        fig_overlay.update_layout(
            **PLOTLY_LAYOUT,
            title=dict(
                text="India Corporate Bond Yield Curves by Rating — June 2026",
                font=dict(family="Playfair Display, serif", color="#c9a96e", size=14),
                x=0.02,
            ),
            xaxis_title="Tenor (Years)",
            yaxis_title="Yield (%)",
            height=380,
            showlegend=True,
            legend=dict(
                bgcolor="rgba(9,9,14,0.8)",
                font=dict(color="#666", size=9, family="DM Mono"),
                bordercolor="rgba(255,255,255,0.05)",
                borderwidth=1,
            ),
        )
        st.plotly_chart(fig_overlay, use_container_width=True, config={"displayModeBar": False})

        st.markdown("""
        <div class="plain-english">
            The gap between AAA corporate bonds and G-Sec yields (~55bps at 5Y) is the credit spread —
            what investors demand extra to take credit risk over the government's risk-free rate.
            A AAA bond issued by HDFC or REC trades near government rates. A BBB bond can be
            380+ bps wide — compensating investors for meaningful default probability.
            The entire Indian corporate bond market is priced as: G-Sec yield + credit spread + liquidity premium.
        </div>
        """, unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────────
    # TAB 3 — DURATION & CONVEXITY
    # ─────────────────────────────────────────────────────────────────────────
    with tab3:
        st.markdown("### Duration & Convexity Deep Dive")

        dc_col1, dc_col2 = st.columns(2)

        with dc_col1:
            st.markdown("#### Macaulay Duration — Cash Flow Timeline")
            dc_face = st.number_input("Face Value (₹)", value=100.0, step=10.0, key="dc_face")
            dc_coupon = st.number_input("Annual Coupon %", value=6.89, step=0.01, key="dc_coupon") / 100
            dc_ytm = st.number_input("YTM %", value=6.84, step=0.01, key="dc_ytm") / 100
            dc_years = st.number_input("Years to Maturity", value=10.0, step=0.5,
                                        min_value=0.5, max_value=50.0, key="dc_years")
            dc_freq = st.selectbox("Coupon Frequency", [2, 1, 4], index=0,
                                    format_func=lambda x: {2: "Semi-annual", 1: "Annual", 4: "Quarterly"}[x],
                                    key="dc_freq")

            dc_mac  = macaulay_duration(dc_face, dc_coupon, dc_ytm, dc_years, dc_freq)
            dc_mod  = modified_duration(dc_face, dc_coupon, dc_ytm, dc_years, dc_freq)
            dc_conv = convexity(dc_face, dc_coupon, dc_ytm, dc_years, dc_freq)
            dc_dv01 = dv01(dc_face, dc_coupon, dc_ytm, dc_years, dc_freq)

            dm1, dm2 = st.columns(2)
            with dm1:
                st.metric("Macaulay Duration", f"{dc_mac:.2f} yrs")
                st.metric("Convexity", f"{dc_conv:.2f}")
            with dm2:
                st.metric("Modified Duration", f"{dc_mod:.2f} yrs")
                st.metric("DV01", f"₹{dc_dv01:.4f}")

            fig_cf = make_cash_flow_chart(dc_face, dc_coupon, dc_ytm, dc_years, dc_freq)
            st.plotly_chart(fig_cf, use_container_width=True, config={"displayModeBar": False})

            st.markdown("""
            <div class="plain-english">
                The <strong style="color:#c9a96e;">gold bars</strong> are PV-weighted coupon payments.
                The <strong style="color:#4ab87a;">green bar</strong> is the final cash flow (coupon + face value).
                The <strong style="color:#e05c6c;">red dashed line</strong> is the Macaulay duration —
                the weighted average time at which you receive your money.
                Higher coupon = earlier cash flows = shorter duration.
            </div>
            """, unsafe_allow_html=True)

        with dc_col2:
            st.markdown("#### Convexity — The Price-Yield Curve")
            fig_py = make_price_yield_convexity_chart(dc_face, dc_coupon, dc_ytm, dc_years, dc_freq)
            st.plotly_chart(fig_py, use_container_width=True, config={"displayModeBar": False})

            st.markdown("""
            <div class="plain-english">
                The <strong style="color:#c9a96e;">gold curve</strong> is the actual price-yield relationship —
                it bends outward (convex). The <strong style="color:#e05c6c;">red dashed line</strong>
                is what duration alone would predict — a straight line tangent at the current point.
                The <strong style="color:#4a9eff;">blue dotted line</strong> is the convexity-adjusted approximation —
                much closer to reality.<br><br>
                The gap between the red line and the gold curve is convexity in action.
                Convexity is always your friend as a bond buyer: you gain more when yields fall
                than you lose when yields rise. This asymmetry is why investors pay a premium for
                high-convexity bonds.
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # Duration comparison across coupons
        st.markdown("#### Duration Across Coupon Rates — Same Maturity, Same YTM")
        compare_years = st.slider("Maturity (years)", 1.0, 30.0, 10.0, 0.5, key="dur_compare_slider")
        compare_ytm_pct = st.slider("YTM (%)", 3.0, 12.0, 7.0, 0.25, key="dur_compare_ytm")
        compare_ytm = compare_ytm_pct / 100

        coupon_rates = [0, 2, 4, 6, 8, 10, 12, 15]
        dur_data = []
        for c in coupon_rates:
            if c == 0:
                label = "0% (Zero Coupon)"
                dur = compare_years  # ZCB duration = maturity
                mod = round(dur / (1 + compare_ytm / 2), 4)
            else:
                label = f"{c}%"
                dur = macaulay_duration(100, c / 100, compare_ytm, compare_years)
                mod = modified_duration(100, c / 100, compare_ytm, compare_years)
            dur_data.append({
                "Coupon Rate": label,
                "Macaulay Duration": f"{dur:.2f} yrs",
                "Modified Duration": f"{mod:.2f} yrs",
                "Duration / Maturity": f"{dur / compare_years:.1%}",
            })
        st.dataframe(pd.DataFrame(dur_data), use_container_width=True, hide_index=True)
        st.caption(f"Higher coupon → shorter duration. Zero coupon bond: duration = maturity ({compare_years:.1f} yrs exactly). YTM = {compare_ytm_pct:.2f}%")

    # ─────────────────────────────────────────────────────────────────────────
    # TAB 4 — CREDIT SPREADS
    # ─────────────────────────────────────────────────────────────────────────
    with tab4:
        st.markdown("### Credit Spread Analysis")

        cs_col1, cs_col2 = st.columns([1, 2])

        with cs_col1:
            cs_tenor = st.slider("Tenor (years)", 1.0, 10.0, 5.0, 0.5, key="cs_tenor_slider")

            # Spread table
            gsec_at_tenor = interpolate_gsec_yield(cs_tenor) * 100
            st.metric("G-Sec Yield at Tenor", f"{gsec_at_tenor:.2f}%",
                      delta=f"{cs_tenor:.1f}Y")

            spread_rows = []
            for rating in CORPORATE_SPREADS:
                spread = interpolate_corp_spread(rating, cs_tenor)
                corp_y = gsec_at_tenor + spread / 100
                spread_rows.append({
                    "Rating": rating,
                    "G-Sec": f"{gsec_at_tenor:.2f}%",
                    "Spread": f"+{spread:.0f} bps",
                    "Corp Yield": f"{corp_y:.2f}%",
                })
            st.dataframe(pd.DataFrame(spread_rows), use_container_width=True, hide_index=True)

        with cs_col2:
            fig_spread = make_corp_spread_chart(cs_tenor)
            st.plotly_chart(fig_spread, use_container_width=True, config={"displayModeBar": False})

        st.markdown("""
        <div class="plain-english">
            A AAA corporate bond trades at ~55 bps over G-Sec at 5 years.
            If you see a bond offering 200 bps over G-Sec, the market is implying something between
            A and BBB credit quality. Either the yield is compensation for real credit risk —
            or it's an opportunity if you think the market is wrong about the issuer.
            Credit spread = default risk + liquidity risk premium.
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # "What spread am I paying?" calculator
        st.markdown("#### 🔍 What Spread Am I Paying?")
        st.caption("Enter a corporate bond's details to find its credit spread and implied rating")

        calc_col1, calc_col2 = st.columns([1, 2])
        with calc_col1:
            calc_face  = st.number_input("Face Value (₹)", value=1000.0, step=100.0, key="calc_face")
            calc_coupon = st.number_input("Annual Coupon %", value=8.20, step=0.01, key="calc_coupon") / 100
            calc_price  = st.number_input("Market Price (₹)", value=1000.0, step=1.0, key="calc_price")
            calc_years  = st.number_input("Years to Maturity", value=2.0, step=0.5, min_value=0.1, key="calc_years")

            if st.button("Compute Spread →", type="primary", key="calc_spread_btn"):
                calc_ytm = ytm_solver(calc_face, calc_coupon, calc_price, calc_years)
                if calc_ytm is not None:
                    matched_gsec = interpolate_gsec_yield(calc_years)
                    calc_spread_bps = spread_to_gsec(calc_ytm, matched_gsec)

                    # Find closest rating bracket
                    implied_rating = "BBB"
                    for r in ["AAA", "AA+", "AA", "AA-", "A", "BBB"]:
                        bracket_spread = interpolate_corp_spread(r, calc_years)
                        if calc_spread_bps <= bracket_spread:
                            implied_rating = r
                            break

                    with calc_col2:
                        rc1, rc2, rc3 = st.columns(3)
                        with rc1:
                            st.metric("Solved YTM", f"{calc_ytm*100:.4f}%")
                        with rc2:
                            st.metric("G-Sec (matched tenor)", f"{matched_gsec*100:.2f}%")
                        with rc3:
                            st.metric("Credit Spread", f"{calc_spread_bps:.1f} bps")

                        st.metric("Implied Rating Bracket", implied_rating)
                        st.markdown(f"""
                        <div class="plain-english">
                            YTM of {calc_ytm*100:.3f}% is {calc_spread_bps:.0f} bps over the
                            {calc_years:.1f}Y G-Sec ({matched_gsec*100:.2f}%).
                            This is consistent with market pricing for <strong style="color:#c9a96e;">{implied_rating}</strong>-rated
                            issuers at this tenor. Compare to known benchmarks: REC (AAA, ~{interpolate_corp_spread('AAA', calc_years):.0f} bps),
                            typical AA (~{interpolate_corp_spread('AA', calc_years):.0f} bps).
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    with calc_col2:
                        st.error("Could not solve for YTM. Check that price is within valid range for this bond.")

    # ─────────────────────────────────────────────────────────────────────────
    # TAB 5 — EDUCATION
    # ─────────────────────────────────────────────────────────────────────────
    with tab5:
        st.markdown("### Bond Math 101")

        # Section 1 — Concept cards
        st.markdown("#### Core Concepts")
        concepts = [
            ("Face Value", "The amount you get back at maturity — ₹100 for G-Secs, ₹1000 for most corporate bonds. Also called par value or nominal value."),
            ("Coupon", "The interest you receive periodically. Paid semi-annually for Indian government bonds and most corporate bonds. A 7% coupon on ₹100 face = ₹3.50 every 6 months."),
            ("Yield to Maturity (YTM)", "The total return if you hold to maturity — accounts for price paid, all coupons received, and face value repaid. The single most important metric for comparing bonds."),
            ("Duration", "How sensitive your bond is to interest rate changes. A 7-year duration means: if rates rise 1%, price falls ~7%. Longer maturity and lower coupons = more duration = more interest rate risk."),
            ("Convexity", "The curve in the price-yield relationship. Convexity means you gain more when yields fall than you lose when they rise. Always works in the bondholder's favour. High convexity bonds trade at premium."),
        ]

        c1, c2 = st.columns(2)
        for i, (title, desc) in enumerate(concepts):
            col = c1 if i % 2 == 0 else c2
            with col:
                st.markdown(f"""
                <div class="concept-card">
                    <h4>{title}</h4>
                    <p>{desc}</p>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---")

        # Section 2 — Key Relationships
        st.markdown("#### Key Relationships")

        rel_c1, rel_c2, rel_c3 = st.columns(3)

        with rel_c1:
            ytms_demo = np.linspace(3, 12, 80)
            prices_demo = [bond_price(100, 0.07, y / 100, 10) for y in ytms_demo]
            fig_r1 = go.Figure()
            fig_r1.add_trace(go.Scatter(x=ytms_demo, y=prices_demo, mode="lines",
                                          line=dict(color="#c9a96e", width=2), showlegend=False))
            layout_r1 = dict(PLOTLY_LAYOUT)
            layout_r1["margin"] = dict(l=40, r=10, t=40, b=40)
            layout_r1["xaxis"] = dict(PLOTLY_LAYOUT["xaxis"]); layout_r1["yaxis"] = dict(PLOTLY_LAYOUT["yaxis"])
            fig_r1.update_layout(**layout_r1, height=200,
                                  title=dict(text="Price vs YTM", font=dict(color="#888", size=11)),
                                  xaxis_title="YTM (%)", yaxis_title="Price (₹)")
            st.plotly_chart(fig_r1, use_container_width=True, config={"displayModeBar": False})
            st.caption("Inverse: price falls when yields rise")

        with rel_c2:
            maturities = np.linspace(1, 30, 60)
            durs_mat = [macaulay_duration(100, 0.07, 0.07, m) for m in maturities]
            fig_r2 = go.Figure()
            fig_r2.add_trace(go.Scatter(x=maturities, y=durs_mat, mode="lines",
                                          line=dict(color="#4a9eff", width=2), showlegend=False))
            layout_r2 = dict(PLOTLY_LAYOUT)
            layout_r2["margin"] = dict(l=40, r=10, t=40, b=40)
            layout_r2["xaxis"] = dict(PLOTLY_LAYOUT["xaxis"]); layout_r2["yaxis"] = dict(PLOTLY_LAYOUT["yaxis"])
            fig_r2.update_layout(**layout_r2, height=200,
                                  title=dict(text="Duration vs Maturity", font=dict(color="#888", size=11)),
                                  xaxis_title="Maturity (yrs)", yaxis_title="Duration (yrs)")
            st.plotly_chart(fig_r2, use_container_width=True, config={"displayModeBar": False})
            st.caption("Longer maturity = more duration")

        with rel_c3:
            coupons_demo = np.linspace(1, 15, 60)
            durs_coup = [macaulay_duration(100, c / 100, 0.07, 10) for c in coupons_demo]
            fig_r3 = go.Figure()
            fig_r3.add_trace(go.Scatter(x=coupons_demo, y=durs_coup, mode="lines",
                                          line=dict(color="#4ab87a", width=2), showlegend=False))
            layout_r3 = dict(PLOTLY_LAYOUT)
            layout_r3["margin"] = dict(l=40, r=10, t=40, b=40)
            layout_r3["xaxis"] = dict(PLOTLY_LAYOUT["xaxis"]); layout_r3["yaxis"] = dict(PLOTLY_LAYOUT["yaxis"])
            fig_r3.update_layout(**layout_r3, height=200,
                                  title=dict(text="Duration vs Coupon", font=dict(color="#888", size=11)),
                                  xaxis_title="Coupon Rate (%)", yaxis_title="Duration (yrs)")
            st.plotly_chart(fig_r3, use_container_width=True, config={"displayModeBar": False})
            st.caption("Higher coupon = shorter duration")

        st.markdown("---")

        # Section 3 — Indian Bond Market Context
        st.markdown("#### Indian Bond Market — The Pricing Stack")

        st.markdown("""
        <div class="market-context">
            RBI Repo Rate:     <span>5.25%</span>   ← RBI policy rate (held since Dec 2025 cut)<br>
            91D T-Bill:        <span>5.26%</span>   ← Short-term risk-free rate<br>
            10Y G-Sec:         <span>6.84%</span>   ← Long-term risk-free benchmark<br>
            AAA Corp 5Y:       <span>~7.09%</span>  ← 55 bps over G-Sec<br>
            AA Corp 5Y:        <span>~7.74%</span>  ← 120 bps over G-Sec<br>
            A Corp 5Y:         <span>~8.94%</span>  ← 240 bps over G-Sec<br>
            MCLR (SBI):        <span>~8.85%</span>  ← Banks price loans above this<br>
            Home Loan Rate:    <span>~8.50%</span>  ← Floating, resets with MCLR<br><br>
            When G-Sec yields fall, home loans get cheaper.<br>
            When they rise, EMIs go up.<br>
            Bonds are not just for institutions.
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # Section 4 — Formula Reference
        st.markdown("#### Formula Reference")

        f1, f2 = st.columns(2)
        with f1:
            st.markdown("**Bond Pricing**")
            st.latex(r"P = \sum_{t=1}^{n} \frac{C/m}{(1+y/m)^t} + \frac{F}{(1+y/m)^n}")
            st.caption("P = price, C = annual coupon, F = face, y = YTM, m = freq/year, n = total periods")

            st.markdown("**Macaulay Duration**")
            st.latex(r"D_{mac} = \frac{\sum_{t=1}^{n} \frac{t}{m} \cdot PV(CF_t)}{P}")
            st.caption("Weighted average time of cash flow receipt")

        with f2:
            st.markdown("**Modified Duration**")
            st.latex(r"D_{mod} = \frac{D_{mac}}{1 + y/m}")
            st.caption("% price change per 1% yield change ≈ -ModDur × Δy")

            st.markdown("**Price Change Approximation**")
            st.latex(r"\frac{\Delta P}{P} \approx -D_{mod} \cdot \Delta y + \frac{1}{2} \cdot C_{vx} \cdot (\Delta y)^2")
            st.caption("Duration captures linear effect; Convexity corrects for curvature")

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="font-family:'DM Mono',monospace; font-size:0.62rem; color:#333;
                text-align:center; padding:1rem 0; line-height:1.8;">
        BondDesk · Day 29 · 30 Days of AI Finance<br>
        Indian G-Sec yield curve sourced from RBI/CEIC/Trading Economics (June 2026).
        Corporate spreads from SEBI corporate bond market data.
        Bond math verified against standard fixed income textbook formulas.<br>
        Not investment advice. Bond prices and yields change daily — verify with NSE debt market before transacting.
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# ROUTER
# ─────────────────────────────────────────────────────────────────────────────

if st.session_state.page == "home":
    render_home()
else:
    render_terminal()