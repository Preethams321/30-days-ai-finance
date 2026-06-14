"""
MacroShock — Interactive Macro Shock Simulator for Indian Markets
Day 14 / 30 Days of AI Finance

No LLM API used. All coefficients are hardcoded from verified historical
research (sources cited inline). Live baselines are fetched via yfinance
with a silent fallback to hardcoded defaults if the fetch fails.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ════════════════════════════════════════════════════════════════
# PAGE CONFIG (must be first Streamlit call)
# ════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="MacroShock — Indian Macro Shock Simulator",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ════════════════════════════════════════════════════════════════
# DARK THEME — CSS INJECTION (forced, always on)
# ════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700;800&family=Syne:wght@400;500;600;700;800&family=DM+Mono:wght@400;500&display=swap');

:root {
    --bg: #09090e;
    --card: #111118;
    --gold: #c9a96e;
    --green: #4ab87a;
    --red: #e05c6c;
    --amber: #e0a04a;
    --ink: #f0ede7;
    --muted: #9b9890;
    --faint: #5d5b54;
    --border: #1f1f29;
}

html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"],
[data-testid="stToolbar"], [data-testid="stSidebar"], .main, .block-container {
    background-color: var(--bg) !important;
}

[data-testid="stHeader"] { background-color: rgba(0,0,0,0) !important; }

* { font-family: 'Syne', sans-serif; }

h1, h2, h3, h4, h5, h6 {
    font-family: 'Playfair Display', serif !important;
    color: var(--ink) !important;
    font-weight: 700 !important;
}

p, span, label, .stMarkdown, div[data-testid="stMarkdownContainer"] {
    color: #cfcdc8;
}

hr { border-color: var(--border) !important; }

/* ---- Metric widgets ---- */
[data-testid="stMetricValue"] {
    font-family: 'DM Mono', monospace !important;
    color: var(--gold) !important;
}
[data-testid="stMetricLabel"] {
    font-family: 'Syne', sans-serif !important;
    color: var(--muted) !important;
}

/* ---- Buttons ---- */
.stButton > button {
    background-color: var(--card);
    color: var(--ink);
    border: 1px solid var(--border);
    border-radius: 10px;
    font-family: 'Syne', sans-serif;
    font-weight: 600;
    transition: all 0.18s ease;
    padding: 0.55rem 1rem;
}
.stButton > button:hover {
    border-color: var(--gold);
    color: var(--gold);
    transform: translateY(-1px);
}
.stButton > button[kind="primary"] {
    background-color: rgba(201,169,110,0.14);
    border: 1px solid var(--gold);
    color: var(--gold);
}
.stButton > button[kind="primary"]:hover {
    background-color: rgba(201,169,110,0.22);
}

/* ---- Sliders ---- */
[data-testid="stSlider"] [data-baseweb="slider"] > div > div {
    background: var(--border) !important;
}
[data-testid="stSlider"] [role="slider"] {
    background-color: var(--gold) !important;
    border-color: var(--gold) !important;
}
[data-testid="stTickBar"] { display: none; }

/* ---- Captions ---- */
[data-testid="stCaptionContainer"], .stCaption { color: var(--muted) !important; }

/* ---- Custom cards ---- */
.ms-card {
    background-color: var(--card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.1rem 1.3rem;
    margin-bottom: 0.9rem;
    transition: transform 0.18s ease, border-color 0.18s ease;
}
.ms-card:hover {
    transform: translateY(-2px);
    border-color: #2c2c3a;
}
.ms-card-gold    { border-left: 4px solid var(--gold); }
.ms-card-pos     { border-left: 4px solid var(--green); }
.ms-card-neg     { border-left: 4px solid var(--red); }
.ms-card-neutral { border-left: 4px solid var(--amber); }

.ms-label {
    font-size: 0.78rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.25rem;
}
.ms-value {
    font-family: 'DM Mono', monospace;
    font-size: 1.55rem;
    font-weight: 500;
    line-height: 1.3;
}
.ms-sub {
    font-size: 0.8rem;
    color: var(--faint);
    margin-top: 0.25rem;
}
.ms-pos     { color: var(--green); }
.ms-neg     { color: var(--red); }
.ms-neutral { color: var(--amber); }
.ms-gold    { color: var(--gold); }

.ms-ghost {
    background-color: rgba(201,169,110,0.06);
    border-left: 3px solid var(--gold);
    padding: 0.65rem 0.95rem;
    border-radius: 8px;
    font-size: 0.88rem;
    font-style: italic;
    color: #d8d4cc;
    margin: 0.4rem 0 1.1rem 0;
}

.ms-tag {
    font-family: 'DM Mono', monospace;
    color: var(--gold);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    font-size: 0.78rem;
    margin-bottom: 0.6rem;
}

.ms-hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 3.4rem;
    font-weight: 800;
    color: var(--ink);
    margin: 0.1rem 0 0.4rem 0;
    line-height: 1.05;
}

.ms-topval {
    font-family: 'DM Mono', monospace;
    color: var(--gold);
    font-size: 1.05rem;
    font-weight: 500;
}
.ms-toplabel {
    font-size: 0.7rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

.ms-footer {
    text-align: center;
    color: var(--faint);
    font-size: 0.74rem;
    margin-top: 2rem;
    line-height: 1.6;
    padding: 1rem 0 0.5rem 0;
}

.ms-badge {
    font-family: 'DM Mono', monospace;
    font-size: 0.78rem;
    font-weight: 500;
    white-space: nowrap;
}
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════
# BASELINE DATA FETCH — OPTION B HYBRID
# ════════════════════════════════════════════════════════════════
@st.cache_data(ttl=300)
def fetch_baselines():
    """
    Fetch current baseline values via yfinance.
    If any fetch fails, use hardcoded fallbacks silently.
    Never show error to user — just use fallback.

    Note on Nifty P/E and India CPI:
    - There's no free live feed for either. Nifty P/E is instead *derived* as
      price / EPS, where EPS (≈ ₹1,068, implied by a Nifty level of 23,500 at a
      P/E of 22.0) is treated as a slowly-moving fundamental. So the P/E figure
      still tracks live Nifty price moves even without a live P/E feed.
    - India CPI has no derivation shortcut, so it stays a static last-known
      reading. The UI labels it with the month it's from so it isn't presented
      as live.
    """
    NIFTY_EPS_BASELINE = 23500 / 22.0  # ≈ ₹1,068.18 trailing EPS implied by the baseline P/E

    defaults = {
        "crude_wti": 85.0,      # $/barrel — fallback, mid-June 2026. Crude spiked to ~$110
                                 # during the 2026 West Asia Conflict (Apr-May) but has since
                                 # fallen ~25% to an 8-week low on US-Iran de-escalation hopes.
        "us10y": 4.57,          # % — approx June 2026
        "usdinr": 95.70,        # ₹ per USD — approx June 2026
        "india_cpi": 3.5,       # % — last reported reading, not live (see note above)
        "india_cpi_asof": "Apr'26",
        "nifty": 23500,         # Nifty 50 level
        "nifty_pe": 22.0,       # derived below from the (possibly live) Nifty level
        "india10y": 6.86,       # India 10Y G-Sec yield %
    }
    try:
        import yfinance as yf

        # Crude WTI
        try:
            df = yf.download("CL=F", period="2d", interval="1d", progress=False, auto_adjust=True)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = [c[0] for c in df.columns]
                defaults["crude_wti"] = round(float(df['Close'].iloc[-1]), 2)
        except Exception:
            pass

        # US 10Y yield
        try:
            df = yf.download("^TNX", period="2d", interval="1d", progress=False, auto_adjust=True)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = [c[0] for c in df.columns]
                defaults["us10y"] = round(float(df['Close'].iloc[-1]), 2)
        except Exception:
            pass

        # USD/INR
        try:
            df = yf.download("USDINR=X", period="2d", interval="1d", progress=False, auto_adjust=True)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = [c[0] for c in df.columns]
                defaults["usdinr"] = round(float(df['Close'].iloc[-1]), 2)
        except Exception:
            pass

        # Nifty 50
        try:
            df = yf.download("^NSEI", period="2d", interval="1d", progress=False, auto_adjust=True)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = [c[0] for c in df.columns]
                defaults["nifty"] = round(float(df['Close'].iloc[-1]), 0)
        except Exception:
            pass

        # India 10Y G-Sec
        try:
            df = yf.download("^IN10Y", period="2d", interval="1d", progress=False, auto_adjust=True)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = [c[0] for c in df.columns]
                defaults["india10y"] = round(float(df['Close'].iloc[-1]), 2)
        except Exception:
            pass

    except Exception:
        pass

    # Derive Nifty P/E from whatever Nifty level we ended up with (live or fallback),
    # so the P/E figure isn't permanently frozen even though there's no live P/E feed.
    defaults["nifty_pe"] = round(defaults["nifty"] / NIFTY_EPS_BASELINE, 1)

    return defaults


# ════════════════════════════════════════════════════════════════
# VERIFIED HISTORICAL COEFFICIENTS
# ════════════════════════════════════════════════════════════════

# ════════════════════════════════════════════════════════
# SHOCK 1: CRUDE OIL PRICE SHOCK
# All sourced from RBI research paper (Ghosh & Tomar, 2019),
# Business Standard, ICRA, 360 ONE Capital, Sahi.com research
# ════════════════════════════════════════════════════════
CRUDE_COEFFICIENTS = {
    # Source: RBI Staff Study "Impact of Crude Price Shock on India's CAD,
    # Inflation and Fiscal Deficit" — Ghosh & Tomar
    "import_bill_per_10usd_bn": 13.5,        # $13-14bn added to import bill per $10/bbl rise
    "cpi_per_10usd_bps": 49,                 # +49bps CPI per $10/bbl rise (RBI study, conservative)
    "cad_gdp_per_10usd_pct": 0.4,            # CAD widens 0.35-0.5% of GDP per $10/bbl (B.Standard)
    "gdp_impact_per_10usd_bps": -35,         # -20 to -40bps GDP per $10/bbl (HDFC/CARE ratings)
    "fiscal_deficit_per_10usd_bps": 43,      # +43bps fiscal deficit if zero pass-through (RBI)
    # Source: Business Standard March 2026, Sahi.com
    "inr_depreciation_per_10usd": 0.8,       # ~₹0.8 per $10/bbl crude rise (historical avg)
    # India imports 85-88% of crude — confirmed by multiple sources
    "import_dependence_pct": 86,
}

CRUDE_SECTOR_IMPACT = {
    "OMCs (HPCL/BPCL/IOC)": {
        "direction": "negative",
        "severity": "high",
        "reason": "Under-recoveries widen when crude rises without retail price hike. Margins compressed.",
        "plain_english": "Oil marketing companies lose money when crude rises faster than petrol/diesel prices. Either they bleed or prices go up at the pump."
    },
    "IT Services": {
        "direction": "positive",
        "severity": "low",
        "reason": "Indirect beneficiary — crude rise weakens rupee, boosting dollar revenue conversion.",
        "plain_english": "IT companies earn in dollars. When crude pushes the rupee down, same dollar revenue converts to more rupees — a quiet tailwind."
    },
    "Auto": {
        "direction": "negative",
        "severity": "medium",
        "reason": "Higher fuel costs reduce consumer discretionary spend and vehicle demand. Input costs (steel, plastics) also rise.",
        "plain_english": "When petrol is expensive, people think twice about buying a new car. And the car itself costs more to make."
    },
    "Aviation": {
        "direction": "negative",
        "severity": "high",
        "reason": "ATF (aviation turbine fuel) is 30-40% of airline operating costs. Jet fuel tracks crude directly.",
        "plain_english": "Fuel is an airline's biggest expense. When crude doubles, so does their cost structure."
    },
    "Paints & Chemicals": {
        "direction": "negative",
        "severity": "medium",
        "reason": "Crude is a key feedstock for paints, adhesives, and chemical products. Input cost inflation.",
        "plain_english": "Crude oil is the raw material for paints, plastics, and industrial chemicals. Higher crude = higher input costs."
    },
    "Pharma": {
        "direction": "neutral",
        "severity": "low",
        "reason": "Some API raw materials are crude-linked but sector largely insulated. Rupee depreciation helps exporters.",
        "plain_english": "Pharma is relatively protected — most of their cost structure isn't directly tied to oil."
    },
    "FMCG": {
        "direction": "negative",
        "severity": "low",
        "reason": "Packaging and logistics costs rise. Rural demand weakens if fuel prices hit household budgets.",
        "plain_english": "Higher petrol prices eat into rural household budgets, reducing spending on everyday goods."
    },
    "Infrastructure/Capital Goods": {
        "direction": "negative",
        "severity": "medium",
        "reason": "Fuel and logistics are significant construction costs. Project costs inflate.",
        "plain_english": "Building roads, ports, and factories needs a lot of fuel. Higher crude = higher project costs = squeezed margins."
    },
}

# ════════════════════════════════════════════════════════
# SHOCK 2: US 10Y YIELD SHOCK
# Source: Business Standard (Krishna Kant, May 2025),
# Systematix Institutional Equity, RBI data,
# 2013 Taper Tantrum data, 2022 Fed hike cycle data
# ════════════════════════════════════════════════════════
US10Y_COEFFICIENTS = {
    "india10y_passthrough_pct": 45,     # 45% passthrough — India 10Y moves ~45bps per 100bps US10Y
    "nifty_pe_compression_per_100bps": 1.8,   # ~1.8 P/E points per 100bps US10Y rise
    "inr_depreciation_per_100bps": 2.3,       # ₹2.3 per 100bps US10Y rise
    "fii_outflow_per_100bps_cr": 15000,       # ~₹15,000 Cr net FPI outflow per 100bps (monthly, stress)
    "spread_decade_avg_bps": 410,      # 2010-2020 average US10Y-India10Y spread (B.Standard)
    "spread_2022_bps": 447,            # Spread in July 2022
    # Note: the *current* spread is computed live from baselines (india10y - us10y)
    # rather than hardcoded — see render_us10y().
}

US10Y_SECTOR_IMPACT = {
    "Banks & NBFCs": {
        "direction": "mixed",
        "severity": "medium",
        "reason": "MTM losses on bond portfolios (banks hold significant G-Sec). But higher yields improve NIM over time as lending rates reprice upward.",
        "plain_english": "Banks hold lots of government bonds. When yields rise, bond prices fall — that's an immediate paper loss. But over time, they can charge borrowers more, which helps profits."
    },
    "IT Services": {
        "direction": "positive",
        "severity": "medium",
        "reason": "Rupee weakens as US10Y rises (capital outflows). Every 1% rupee fall adds 30-50bps to IT operating margins. Source: Kotak, Nomura analyst estimates.",
        "plain_english": "Rising US yields push FII money out of India, weakening the rupee. For IT companies earning in dollars, a weaker rupee means more rupees per dollar — a direct margin boost."
    },
    "Real Estate": {
        "direction": "negative",
        "severity": "high",
        "reason": "India home loan rates lag India10Y by 6-9 months. Higher rates = higher EMIs = lower demand for housing.",
        "plain_english": "Home loan rates follow government bond yields. When yields rise, EMIs go up. When EMIs go up, fewer people can afford homes."
    },
    "Auto": {
        "direction": "negative",
        "severity": "medium",
        "reason": "Vehicle loans are rate-sensitive. Dealers finance inventory at higher costs. Consumer EMI affordability reduces.",
        "plain_english": "Most car and two-wheeler purchases are financed. Higher rates mean higher monthly payments — fewer sales."
    },
    "Pharma (Exporters)": {
        "direction": "positive",
        "severity": "low",
        "reason": "Rupee depreciation from capital outflows helps pharma exporters — same dollar revenues convert to more rupees.",
        "plain_english": "Pharma exports earn in dollars. A weaker rupee means better realisation in rupee terms."
    },
    "Capital Goods/Infra": {
        "direction": "negative",
        "severity": "medium",
        "reason": "Higher borrowing costs for large infrastructure projects. Govt borrowing cost rises — potential fiscal constraint on capex.",
        "plain_english": "Infrastructure projects are funded with debt. Higher rates make big projects more expensive to finance."
    },
    "FMCG": {
        "direction": "neutral",
        "severity": "low",
        "reason": "Defensive sector. Low direct rate sensitivity. May see marginal benefit from FII rotation into defensives during yield spike.",
        "plain_english": "People buy soap and biscuits regardless of interest rates. FMCG is a safe harbour when everything else sells off."
    },
    "Gold (not a sector but key asset)": {
        "direction": "negative",
        "severity": "medium",
        "reason": "Classic inverse relationship. Gold/real-yield correlation -0.82 (Erb & Harvey, PIMCO). Note: correlation weakened 2022-24 due to central bank gold buying.",
        "plain_english": "When US bonds pay more, gold becomes less attractive — it pays no interest. Money moves to bonds. Gold usually falls. (This relationship has weakened recently due to central bank buying.)"
    },
}

# ════════════════════════════════════════════════════════
# SHOCK 3: USD/INR SHOCK (rupee depreciates)
# Source: Indmoney.com, Business Standard, Kotak MF,
# Multiple IT sector analyst reports, RBI data
# ════════════════════════════════════════════════════════
USDINR_COEFFICIENTS = {
    "it_margin_per_1pct_inr_fall_bps": 40,      # 30-50bps avg, use midpoint 40bps
    "import_cost_amplification_pct": 1.0,        # 1% INR fall = 1% more rupees for same $ import
}

USDINR_SECTOR_IMPACT = {
    "IT Services": {
        "direction": "positive",
        "severity": "high",
        "reason": "Every 1% rupee fall adds ~30-50bps to EBIT margins (Kotak/Nomura estimates). Top 6 IT firms saw 40-320bps margin boost from rupee in Q4FY26 (MStock research April 2026).",
        "plain_english": "IT is the biggest winner when the rupee falls. They bill in dollars, pay salaries in rupees. Same dollar revenue = more rupee profit. The math is direct."
    },
    "Pharma Exporters": {
        "direction": "positive",
        "severity": "medium",
        "reason": "70%+ of Indian pharma revenue is export-driven (US, Europe). Rupee fall boosts realisation.",
        "plain_english": "Indian pharma sells to American patients in dollars. When the rupee falls, the same drug sale earns more in rupee terms."
    },
    "Textile/Garment Exporters": {
        "direction": "positive",
        "severity": "medium",
        "reason": "Makes Indian textiles cheaper for foreign buyers, improving competitiveness and volumes.",
        "plain_english": "A weaker rupee makes Indian clothes cheaper for buyers in the US and Europe — helps orders and margins."
    },
    "Oil & Gas Importers (OMCs)": {
        "direction": "negative",
        "severity": "high",
        "reason": "Crude is dollar-denominated. Every rupee fall increases import bill directly. No natural hedge.",
        "plain_english": "India buys crude in dollars. When rupee weakens, the same barrel of oil costs more rupees. Pure pain for refiners."
    },
    "Capital Goods (Import-heavy)": {
        "direction": "negative",
        "severity": "medium",
        "reason": "Machinery and component imports become more expensive. Project costs inflate.",
        "plain_english": "If you're building a factory with imported machines, a weaker rupee makes every machine more expensive."
    },
    "Real Estate": {
        "direction": "negative",
        "severity": "low",
        "reason": "Import-linked construction materials (steel, cement inputs) cost more. Marginal impact.",
        "plain_english": "Some construction materials are imported. A weaker rupee makes them pricier, nudging up project costs."
    },
    "FMCG": {
        "direction": "mixed",
        "severity": "low",
        "reason": "Companies like HUL import raw materials (palm oil). Costs rise. But rural sentiment improves if farm exports benefit.",
        "plain_english": "HUL and others import ingredients. Higher input costs squeeze margins. But if exports pick up, rural income rises and spending improves."
    },
    "Aviation": {
        "direction": "negative",
        "severity": "high",
        "reason": "ATF priced in USD. Aircraft leases in USD. When rupee falls, both costs spike simultaneously.",
        "plain_english": "Airlines pay for fuel and planes in dollars. When the rupee weakens, their two biggest costs rise automatically."
    },
}

# ════════════════════════════════════════════════════════
# SHOCK 4: INDIA CPI SURPRISE
# Source: RBI Monetary Policy history 2022-2026,
# ICRA (Aditi Nayar analysis), Arthgyaan, Shriram Finance repo rate history
# ════════════════════════════════════════════════════════
CPI_COEFFICIENTS = {
    "rbi_response_threshold_cpi": 6.0,    # CPI above 6% — hike highly probable
    "rbi_response_lag_months": 3,          # avg 3 months before repo rate response
    "repo_rate_response_per_100bps_cpi": 32,   # bps repo hike per 100bps CPI above 4% target
    "india10y_per_100bps_cpi": 55,        # India 10Y rises ~55bps per 100bps CPI surprise
    "nifty_pe_per_100bps_cpi": -1.2,      # P/E compresses ~1.2x per 100bps CPI surprise
}

CPI_SECTOR_IMPACT = {
    "Banks (Lenders)": {
        "direction": "mixed",
        "severity": "medium",
        "reason": "Higher CPI → higher repo rate → NIM improves on floating rate loans BUT bond portfolio MTM losses, and credit costs may rise if growth slows.",
        "plain_english": "Banks can charge borrowers more (good). But their bond holdings lose value (bad). Net effect depends on how quickly they reprice."
    },
    "Real Estate": {
        "direction": "negative",
        "severity": "high",
        "reason": "Higher CPI → RBI rate hike → higher home loan rates → lower demand. Direct and quick transmission.",
        "plain_english": "When inflation rises, RBI raises rates. When rates rise, home loans get expensive. When home loans get expensive, fewer people buy homes."
    },
    "NBFCs": {
        "direction": "negative",
        "severity": "high",
        "reason": "Higher borrowing costs compress spreads. Floating rate liabilities reprice faster than assets in some NBFCs.",
        "plain_english": "NBFCs borrow to lend. When interest rates rise, their cost of funds goes up — but they can't always pass it on immediately."
    },
    "FMCG": {
        "direction": "negative",
        "severity": "medium",
        "reason": "High CPI = high food inflation → real purchasing power of households falls → volume growth slows.",
        "plain_english": "When inflation is high, ₹500 buys less. People cut back on branded goods. FMCG volumes suffer."
    },
    "Auto": {
        "direction": "negative",
        "severity": "medium",
        "reason": "Inflation reduces disposable income. Rate hike makes vehicle loans costlier. Double impact on demand.",
        "plain_english": "High inflation + high interest rates = the worst combination for auto sales. Less money, more expensive loans."
    },
    "Gold": {
        "direction": "positive",
        "severity": "medium",
        "reason": "Gold is the classic inflation hedge. Indian households buy gold when inflation rises.",
        "plain_english": "When prices rise, people trust gold more than paper money. Gold demand historically spikes during high-inflation periods in India."
    },
    "IT Services": {
        "direction": "neutral",
        "severity": "low",
        "reason": "Domestic inflation has low direct impact on export-oriented IT sector. Global demand and rupee matter more.",
        "plain_english": "IT companies sell to foreign clients — Indian inflation doesn't directly affect their business."
    },
    "Infrastructure": {
        "direction": "negative",
        "severity": "medium",
        "reason": "Construction cost inflation + higher borrowing costs + potential government fiscal squeeze on capex if deficit pressures mount.",
        "plain_english": "When everything costs more to build and loans are more expensive, infrastructure projects slow down."
    },
}

# ════════════════════════════════════════════════════════
# SCENARIO PRESETS — 5 historical events
# ════════════════════════════════════════════════════════
HISTORICAL_SCENARIOS = {
    "2013 Taper Tantrum": {
        "shock_type": "us10y",
        "delta": 130,   # bps — US10Y rose from ~1.6% to ~2.9%
        "context": "Fed announced tapering of QE in May 2013. FPI pulled ₹51,000 Cr from Indian debt. India was in the 'Fragile Five'.",
        "outcome": "Nifty fell ~10%. INR went from ₹54 to ₹68 (a ~20% fall in rupee value). RBI had to raise emergency rates."
    },
    "2022 Fed Rate Hike Cycle": {
        "shock_type": "us10y",
        "delta": 300,   # bps — US10Y rose from ~1.5% to ~4.5%
        "context": "Fed hiked 525bps in 2022-23. US10Y rose 300bps in one year. India was more resilient than 2013.",
        "outcome": "INR fell 10% (₹75 to ₹83). Nifty fell 17% peak to trough. FPI equity outflows significant."
    },
    "2022 Russia-Ukraine Crude Shock": {
        "shock_type": "crude",
        "delta": 40,    # $/barrel — Brent spiked from $75 to $115+
        "context": "Russia invaded Ukraine in Feb 2022. Brent crude spiked 54% in weeks. India's import bill surged.",
        "outcome": "CPI hit 7.8% (April 2022). RBI did emergency 40bps off-cycle hike in May 2022. INR fell 8%."
    },
    "2026 West Asia Conflict": {
        "shock_type": "crude",
        "delta": 30,    # $/barrel — from ~$80 to $110+
        "context": "West Asia conflict disrupted Strait of Hormuz (35% of global seaborne crude). Crude hit $110+ April-May 2026.",
        "outcome": "CPI projected 5.1% for FY27. RBI held rates. INR hit record low ₹96.82 by May 2026. FPI outflows $13.7bn."
    },
    "2020 COVID Demand Shock": {
        "shock_type": "crude",
        "delta": -55,   # $/barrel — Brent fell from $65 to $10 briefly
        "context": "COVID-19 demand collapse. WTI went briefly negative (-$37). Brent fell to $10-15.",
        "outcome": "Massive relief for India's CAD. RBI cut repo from 5.15% to 4.0%. Nifty recovered 90% in 12 months."
    },
}


# ════════════════════════════════════════════════════════════════
# HELPER / RENDER FUNCTIONS
# ════════════════════════════════════════════════════════════════

def metric_card(label, value, sublabel="", color_class="ms-gold"):
    st.markdown(f"""
    <div class="ms-card">
        <div class="ms-label">{label}</div>
        <div class="ms-value {color_class}">{value}</div>
        <div class="ms-sub">{sublabel}</div>
    </div>
    """, unsafe_allow_html=True)


def ghost_box(text):
    st.markdown(f'<div class="ms-ghost"><b>Plain English:</b> {text}</div>', unsafe_allow_html=True)


def context_box(text):
    st.markdown(f'<div class="ms-ghost">{text}</div>', unsafe_allow_html=True)


def sector_card(name, info):
    color_map = {"positive": "ms-card-pos", "negative": "ms-card-neg",
                  "neutral": "ms-card-neutral", "mixed": "ms-card-neutral"}
    badge_map = {
        "positive": ("▲ Positive", "ms-pos"),
        "negative": ("▼ Negative", "ms-neg"),
        "neutral": ("● Neutral", "ms-neutral"),
        "mixed": ("◆ Mixed", "ms-neutral"),
    }
    badge_text, badge_color = badge_map.get(info["direction"], ("●", "ms-neutral"))
    card_class = color_map.get(info["direction"], "ms-card-neutral")
    severity = info["severity"].capitalize()

    st.markdown(f"""
    <div class="ms-card {card_class}">
        <div style="display:flex;justify-content:space-between;align-items:baseline;gap:0.5rem;">
            <div style="font-family:'Playfair Display',serif;font-size:1.05rem;color:#f0ede7;">{name}</div>
            <div class="ms-badge {badge_color}">{badge_text}</div>
        </div>
        <div class="ms-sub" style="margin-top:0;">Severity: {severity}</div>
        <div style="font-size:0.85rem;color:#cfcdc8;margin-top:0.4rem;">{info['reason']}</div>
    </div>
    """, unsafe_allow_html=True)
    ghost_box(info["plain_english"])


def before_after_chart(title, before, after, unit="", fmt="{:.2f}", labels=("Now", "Under this shock")):
    delta = after - before
    bar_color = "#4ab87a" if delta >= 0 else "#e05c6c"
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=list(labels),
        y=[before, after],
        marker_color=["#6b6a73", bar_color],
        text=[fmt.format(before) + unit, fmt.format(after) + unit],
        textposition="outside",
        textfont=dict(family="DM Mono, monospace", color="#e8e6e3", size=14),
        width=[0.45, 0.45],
    ))
    fig.update_layout(
        title=dict(text=title, font=dict(family="Playfair Display, serif", color="#f0ede7", size=16)),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        font=dict(family="Syne, sans-serif", color="#cfcdc8"),
        margin=dict(t=55, b=20, l=10, r=10),
        height=300,
    )
    fig.update_xaxes(color="#9b9890", showgrid=False)
    fig.update_yaxes(color="#9b9890", gridcolor="#1f1f29", zeroline=False)
    st.plotly_chart(fig, width="stretch")


def calc_emi(principal, annual_rate_pct, months):
    r = annual_rate_pct / 100 / 12
    if r == 0:
        return principal / months
    return principal * r * (1 + r) ** months / ((1 + r) ** months - 1)


def sign(x):
    return "+" if x >= 0 else ""


# ════════════════════════════════════════════════════════════════
# SESSION STATE INIT
# ════════════════════════════════════════════════════════════════
defaults_state = {
    "page": "home",
    "shock_type": "crude",
    "crude_delta": 0,
    "us10y_delta": 0,
    "usdinr_delta": 0.0,
    "cpi_delta": 0,
    "active_preset": None,
}
for k, v in defaults_state.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ════════════════════════════════════════════════════════════════
# HOMEPAGE
# ════════════════════════════════════════════════════════════════
def homepage(baselines):
    st.markdown('<div class="ms-tag">30 Days of AI Finance · Day 14</div>', unsafe_allow_html=True)
    st.markdown('<div class="ms-hero-title">MacroShock</div>', unsafe_allow_html=True)
    st.markdown(
        '<p style="font-size:1.05rem;color:#9b9890;max-width:680px;">'
        'An interactive macro shock simulator for Indian markets. Pick a shock, '
        'set the magnitude, and see the estimated cascading impact on Indian '
        'sectors and macro indicators — grounded in 2013-2026 historical patterns.'
        '</p>', unsafe_allow_html=True
    )

    cols = st.columns(4)
    stats = [("4", "Macro Shocks"), ("8", "Sectors per Shock"),
             ("2013–26", "Data Window"), ("RBI · ICRA", "Sourced From")]
    for col, (val, label) in zip(cols, stats):
        with col:
            st.markdown(f"""
            <div class="ms-card ms-card-gold" style="text-align:center;">
                <div class="ms-value ms-gold">{val}</div>
                <div class="ms-sub">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("### The Four Shocks")

    features = [
        ("Crude Oil Price Shock", f"Baseline ≈ ${baselines['crude_wti']:.0f}/bbl", "−$40 to +$60",
         "Ripples through the import bill, CPI, CAD, GDP growth, the rupee, and 8 sectors from OMCs to aviation."),
        ("US 10Y Yield Shock", f"Baseline ≈ {baselines['us10y']:.2f}%", "−200 to +300 bps",
         "Drives India 10Y yields, Nifty valuations, FII flows, and the rupee — echoes of 2013 and 2022."),
        ("USD/INR Rate Shock", f"Baseline ≈ ₹{baselines['usdinr']:.2f}", "−₹10 to +₹20",
         "IT margins, import costs, and export competitiveness move directly with the rupee."),
        ("India CPI Surprise", f"Baseline ≈ {baselines['india_cpi']:.1f}% ({baselines['india_cpi_asof']})", "−200 to +300 bps",
         "Triggers RBI rate response, bond yields, EMI changes on home loans, and equity valuations."),
    ]

    cols = st.columns(2)
    for i, (title, base, rng, desc) in enumerate(features):
        with cols[i % 2]:
            st.markdown(f"""
            <div class="ms-card ms-card-gold">
                <div style="font-family:'Playfair Display',serif;font-size:1.15rem;color:#f0ede7;">{title}</div>
                <div class="ms-topval" style="margin:0.35rem 0;">{base} &nbsp;·&nbsp; {rng}</div>
                <div style="font-size:0.85rem;color:#9b9890;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    _, mid, _ = st.columns([1, 1.2, 1])
    with mid:
        if st.button("Launch Simulator →", width="stretch", type="primary"):
            st.session_state.page = "terminal"
            st.rerun()

    st.markdown("""
    <div class="ms-footer">
    MacroShock · Day 14 · 30 Days of AI Finance · Historical pattern estimates from 2013-2026 data
    (RBI, Business Standard, ICRA, PPAC). Not investment advice. Correlations may break during
    structural regime shifts.
    </div>
    """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════
# TERMINAL — TOPBAR, SHOCK SELECTOR, SLIDER, PRESETS
# ════════════════════════════════════════════════════════════════
def terminal_controls(baselines):
    # ---- Topbar ----
    top = st.columns([2.4, 1, 1, 1, 1, 0.6, 0.6])
    with top[0]:
        st.markdown('<div style="font-family:\'Playfair Display\',serif;font-size:1.7rem;'
                     'color:#f0ede7;padding-top:0.2rem;">⚡ MacroShock</div>', unsafe_allow_html=True)
    with top[1]:
        st.markdown(f'<div class="ms-toplabel">Crude (WTI)</div>'
                     f'<div class="ms-topval">${baselines["crude_wti"]:.1f}</div>', unsafe_allow_html=True)
    with top[2]:
        st.markdown(f'<div class="ms-toplabel">US 10Y</div>'
                     f'<div class="ms-topval">{baselines["us10y"]:.2f}%</div>', unsafe_allow_html=True)
    with top[3]:
        st.markdown(f'<div class="ms-toplabel">USD/INR</div>'
                     f'<div class="ms-topval">₹{baselines["usdinr"]:.2f}</div>', unsafe_allow_html=True)
    with top[4]:
        st.markdown(f'<div class="ms-toplabel">India CPI ({baselines["india_cpi_asof"]})</div>'
                     f'<div class="ms-topval">{baselines["india_cpi"]:.1f}%</div>', unsafe_allow_html=True)
    with top[5]:
        if st.button("↻", help="Refresh live baselines", width="stretch"):
            fetch_baselines.clear()
            st.rerun()
    with top[6]:
        if st.button("⌂", help="Back to home", width="stretch"):
            st.session_state.page = "home"
            st.rerun()

    st.markdown("---")

    # ---- Shock selector ----
    st.markdown("#### Select a shock")
    shock_options = [
        ("crude", "Crude Oil"),
        ("us10y", "US 10Y Yield"),
        ("usdinr", "USD/INR"),
        ("cpi", "India CPI"),
    ]
    cols = st.columns(4)
    for col, (key, label) in zip(cols, shock_options):
        with col:
            btn_type = "primary" if st.session_state.shock_type == key else "secondary"
            if st.button(label, key=f"shockbtn_{key}", width="stretch", type=btn_type):
                st.session_state.shock_type = key
                st.session_state.active_preset = None
                st.rerun()

    # ---- Slider ----
    st.markdown("#### Set the magnitude")
    shock_type = st.session_state.shock_type

    if shock_type == "crude":
        st.session_state.crude_delta = st.slider(
            "Crude oil price shock ($/barrel from baseline)",
            min_value=-40, max_value=60, value=int(st.session_state.crude_delta), step=1,
            format="%+d $/bbl"
        )
        new_val = baselines["crude_wti"] + st.session_state.crude_delta
        st.caption(f"New WTI estimate: **\\${new_val:.1f}/barrel** (baseline \\${baselines['crude_wti']:.1f})")

    elif shock_type == "us10y":
        st.session_state.us10y_delta = st.slider(
            "US 10Y yield shock (bps from baseline)",
            min_value=-200, max_value=300, value=int(st.session_state.us10y_delta), step=5,
            format="%+d bps"
        )
        new_val = baselines["us10y"] + st.session_state.us10y_delta / 100
        st.caption(f"New US 10Y estimate: **{new_val:.2f}%** (baseline {baselines['us10y']:.2f}%)")

    elif shock_type == "usdinr":
        st.session_state.usdinr_delta = st.slider(
            "USD/INR shock (₹ from baseline)",
            min_value=-10.0, max_value=20.0, value=float(st.session_state.usdinr_delta), step=0.5,
            format="%+.1f ₹"
        )
        new_val = baselines["usdinr"] + st.session_state.usdinr_delta
        st.caption(f"New USD/INR estimate: **₹{new_val:.2f}** (baseline ₹{baselines['usdinr']:.2f})")

    elif shock_type == "cpi":
        st.session_state.cpi_delta = st.slider(
            "India CPI surprise (bps from baseline)",
            min_value=-200, max_value=300, value=int(st.session_state.cpi_delta), step=5,
            format="%+d bps"
        )
        new_val = baselines["india_cpi"] + st.session_state.cpi_delta / 100
        st.caption(f"New India CPI estimate: **{new_val:.2f}%** (baseline {baselines['india_cpi']:.1f}%)")

    # ---- Preset scenario buttons ----
    st.markdown("#### Historical scenario presets")
    preset_cols = st.columns(5)
    for col, (name, scenario) in zip(preset_cols, HISTORICAL_SCENARIOS.items()):
        with col:
            if st.button(name, key=f"preset_{name}", width="stretch"):
                st.session_state.shock_type = scenario["shock_type"]
                if scenario["shock_type"] == "crude":
                    st.session_state.crude_delta = scenario["delta"]
                elif scenario["shock_type"] == "us10y":
                    st.session_state.us10y_delta = scenario["delta"]
                st.session_state.active_preset = name
                st.rerun()

    if st.session_state.active_preset:
        scenario = HISTORICAL_SCENARIOS[st.session_state.active_preset]
        st.markdown(f"""
        <div class="ms-card ms-card-gold">
            <div class="ms-tag" style="margin-bottom:0.3rem;">Preset active: {st.session_state.active_preset}</div>
            <div style="font-size:0.85rem;color:#cfcdc8;"><b>What happened:</b> {scenario['context']}</div>
            <div style="font-size:0.85rem;color:#cfcdc8;margin-top:0.3rem;"><b>Outcome:</b> {scenario['outcome']}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")


# ════════════════════════════════════════════════════════════════
# IMPACT DASHBOARDS — ONE PER SHOCK
# ════════════════════════════════════════════════════════════════

def render_crude(baselines):
    delta = st.session_state.crude_delta
    c = CRUDE_COEFFICIENTS
    unit = delta / 10

    import_bill = unit * c["import_bill_per_10usd_bn"]
    cpi_bps = unit * c["cpi_per_10usd_bps"]
    cad_pct = unit * c["cad_gdp_per_10usd_pct"]
    gdp_bps = unit * c["gdp_impact_per_10usd_bps"] + 0.0
    inr_change = unit * c["inr_depreciation_per_10usd"]
    fd_bps = unit * c["fiscal_deficit_per_10usd_bps"]

    new_cpi = baselines["india_cpi"] + cpi_bps / 100
    new_usdinr = baselines["usdinr"] + inr_change
    new_crude = baselines["crude_wti"] + delta

    st.markdown("### Macro impact — Crude Oil Price Shock")
    st.markdown(
        f'<div class="ms-tag">Shock: {sign(delta)}{delta} $/bbl → new WTI ≈ ${new_crude:.1f}</div>',
        unsafe_allow_html=True
    )

    cols = st.columns(3)
    with cols[0]:
        metric_card("Import bill change", f"{sign(import_bill)}{import_bill:.1f} $bn",
                     "Estimated annual change in crude import cost",
                     "ms-neg" if import_bill > 0 else ("ms-pos" if import_bill < 0 else "ms-gold"))
    with cols[1]:
        metric_card("CPI impact", f"{sign(cpi_bps)}{cpi_bps:.0f} bps",
                     f"New headline CPI estimate: {new_cpi:.2f}%",
                     "ms-neg" if cpi_bps > 0 else ("ms-pos" if cpi_bps < 0 else "ms-gold"))
    with cols[2]:
        metric_card("Current account deficit", f"{sign(cad_pct)}{cad_pct:.2f}% of GDP",
                     "Estimated change in CAD as a share of GDP",
                     "ms-neg" if cad_pct > 0 else ("ms-pos" if cad_pct < 0 else "ms-gold"))

    cols = st.columns(3)
    with cols[0]:
        metric_card("GDP growth impact", f"{gdp_bps:+.0f} bps",
                     "Estimated drag/boost to real GDP growth",
                     "ms-neg" if gdp_bps < 0 else ("ms-pos" if gdp_bps > 0 else "ms-gold"))
    with cols[1]:
        metric_card("Rupee impact", f"{sign(inr_change)}₹{inr_change:.2f}",
                     f"New USD/INR estimate: ₹{new_usdinr:.2f}",
                     "ms-neg" if inr_change > 0 else ("ms-pos" if inr_change < 0 else "ms-gold"))
    with cols[2]:
        metric_card("Fiscal deficit (zero pass-through)", f"{fd_bps:+.0f} bps",
                     "If government absorbs the price rise via subsidy, instead of passing it to consumers",
                     "ms-neg" if fd_bps > 0 else ("ms-pos" if fd_bps < 0 else "ms-gold"))

    ghost_box(
        f"India imports about {c['import_dependence_pct']}% of the crude it uses. A move of "
        f"{sign(delta)}{delta}/barrel ripples through fuel prices, the rupee, inflation, and "
        f"the government's budget — all roughly at once."
    )

    before_after_chart("India CPI — current vs. under this shock", baselines["india_cpi"], new_cpi, unit="%", fmt="{:.2f}")

    st.markdown("### Sector impact")
    sector_cols = st.columns(2)
    for i, (name, info) in enumerate(CRUDE_SECTOR_IMPACT.items()):
        with sector_cols[i % 2]:
            sector_card(name, info)

    st.markdown("### Historical comparison — what happened last time")
    matches = [(n, s) for n, s in HISTORICAL_SCENARIOS.items() if s["shock_type"] == "crude"]
    cols = st.columns(len(matches))
    for col, (name, scenario) in zip(cols, matches):
        with col:
            st.markdown(f"""
            <div class="ms-card ms-card-gold">
                <div style="font-family:'Playfair Display',serif;font-size:1rem;color:#f0ede7;">{name}</div>
                <div class="ms-topval" style="font-size:0.85rem;margin:0.2rem 0;">{scenario['delta']:+d} $/bbl</div>
                <div style="font-size:0.8rem;color:#9b9890;margin-top:0.3rem;">{scenario['context']}</div>
                <div style="font-size:0.8rem;color:#cfcdc8;margin-top:0.3rem;"><b>Outcome:</b> {scenario['outcome']}</div>
            </div>
            """, unsafe_allow_html=True)


def render_us10y(baselines):
    delta = st.session_state.us10y_delta
    c = US10Y_COEFFICIENTS

    india10y_change = delta * c["india10y_passthrough_pct"] / 100
    pe_change = (delta / 100) * (-c["nifty_pe_compression_per_100bps"]) + 0.0
    new_pe = baselines["nifty_pe"] + pe_change
    nifty_est = new_pe * (baselines["nifty"] / baselines["nifty_pe"])
    inr_change = (delta / 100) * c["inr_depreciation_per_100bps"]
    fii_change = (delta / 100) * (-c["fii_outflow_per_100bps_cr"]) + 0.0

    new_india10y = baselines["india10y"] + india10y_change / 100
    new_usdinr = baselines["usdinr"] + inr_change
    new_us10y = baselines["us10y"] + delta / 100
    current_spread_bps = (baselines["india10y"] - baselines["us10y"]) * 100

    st.markdown("### Macro impact — US 10Y Yield Shock")
    st.markdown(
        f'<div class="ms-tag">Shock: {delta:+d} bps → new US 10Y ≈ {new_us10y:.2f}%</div>',
        unsafe_allow_html=True
    )
    st.caption(
        f"Current India-US 10Y spread ≈ {current_spread_bps:.0f}bps — for reference, the "
        f"2010-2020 average was ~{c['spread_decade_avg_bps']}bps, and it widened to "
        f"~{c['spread_2022_bps']}bps in July 2022."
    )

    cols = st.columns(3)
    with cols[0]:
        metric_card("India 10Y G-Sec", f"{india10y_change:+.0f} bps",
                     f"New yield estimate: {new_india10y:.2f}% (45% passthrough)",
                     "ms-neg" if india10y_change > 0 else ("ms-pos" if india10y_change < 0 else "ms-gold"))
    with cols[1]:
        metric_card("Nifty P/E", f"{pe_change:+.2f}x",
                     f"New P/E ≈ {new_pe:.1f}x (from {baselines['nifty_pe']:.1f}x)",
                     "ms-neg" if pe_change < 0 else ("ms-pos" if pe_change > 0 else "ms-gold"))
    with cols[2]:
        nifty_pct = (nifty_est / baselines["nifty"] - 1) * 100
        metric_card("Nifty 50 estimate", f"{nifty_est:,.0f}",
                     f"{sign(nifty_pct)}{nifty_pct:.1f}% from baseline {baselines['nifty']:,.0f}",
                     "ms-neg" if nifty_pct < 0 else ("ms-pos" if nifty_pct > 0 else "ms-gold"))

    cols = st.columns(2)
    with cols[0]:
        metric_card("Rupee impact", f"{sign(inr_change)}₹{inr_change:.2f}",
                     f"New USD/INR estimate: ₹{new_usdinr:.2f}",
                     "ms-neg" if inr_change > 0 else ("ms-pos" if inr_change < 0 else "ms-gold"))
    with cols[1]:
        metric_card("FII flow impact", f"₹{fii_change:,.0f} Cr",
                     "Estimated net FPI flow change in a stress month (negative = outflow)",
                     "ms-neg" if fii_change < 0 else ("ms-pos" if fii_change > 0 else "ms-gold"))

    context_box(
        "Historical context: in the 2013 Taper Tantrum, US 10Y rose roughly 130bps and the rupee "
        "fell about 20% in value (USD/INR moved from ₹54 to ₹68). In 2022, US 10Y rose roughly "
        "300bps but the rupee fell only around 10% (₹75 to ₹83) — a sign of stronger Indian "
        "fundamentals the second time around. <i>The chart below applies the shock size set above "
        "to today's live Nifty level — it is not a record of where Nifty actually traded back "
        "then.</i>"
    )

    before_after_chart("Nifty 50 — current level vs. estimate under this shock", baselines["nifty"], nifty_est, unit="", fmt="{:,.0f}")

    st.markdown("### Sector impact")
    sector_cols = st.columns(2)
    for i, (name, info) in enumerate(US10Y_SECTOR_IMPACT.items()):
        with sector_cols[i % 2]:
            sector_card(name, info)

    st.markdown("### Historical comparison — what happened last time")
    matches = [(n, s) for n, s in HISTORICAL_SCENARIOS.items() if s["shock_type"] == "us10y"]
    cols = st.columns(len(matches))
    for col, (name, scenario) in zip(cols, matches):
        with col:
            st.markdown(f"""
            <div class="ms-card ms-card-gold">
                <div style="font-family:'Playfair Display',serif;font-size:1rem;color:#f0ede7;">{name}</div>
                <div class="ms-topval" style="font-size:0.85rem;margin:0.2rem 0;">{scenario['delta']:+d} bps</div>
                <div style="font-size:0.8rem;color:#9b9890;margin-top:0.3rem;">{scenario['context']}</div>
                <div style="font-size:0.8rem;color:#cfcdc8;margin-top:0.3rem;"><b>Outcome:</b> {scenario['outcome']}</div>
            </div>
            """, unsafe_allow_html=True)


def render_usdinr(baselines):
    delta = st.session_state.usdinr_delta
    c = USDINR_COEFFICIENTS

    new_usdinr = baselines["usdinr"] + delta
    shock_pct = (delta / baselines["usdinr"]) * 100
    it_margin_bps = shock_pct * c["it_margin_per_1pct_inr_fall_bps"]
    import_cost_pct = shock_pct * c["import_cost_amplification_pct"]

    # Illustrative annual fuel-bill example, based on the crude cost embedded in petrol
    annual_petrol_litres = 1000
    litres_per_barrel = 159
    crude_cost_per_litre_base = (baselines["crude_wti"] / litres_per_barrel) * baselines["usdinr"]
    crude_cost_per_litre_new = (baselines["crude_wti"] / litres_per_barrel) * new_usdinr
    annual_fuel_change = (crude_cost_per_litre_new - crude_cost_per_litre_base) * annual_petrol_litres

    st.markdown("### Macro impact — USD/INR Shock")
    direction_word = "weakens" if delta > 0 else ("strengthens" if delta < 0 else "is unchanged")
    st.markdown(
        f'<div class="ms-tag">Shock: {sign(delta)}{delta:.1f} → new USD/INR ≈ ₹{new_usdinr:.2f} (rupee {direction_word})</div>',
        unsafe_allow_html=True
    )

    cols = st.columns(3)
    with cols[0]:
        metric_card("USD/INR move", f"{sign(shock_pct)}{shock_pct:.2f}%",
                     f"New rate: ₹{new_usdinr:.2f} (baseline ₹{baselines['usdinr']:.2f})",
                     "ms-neg" if shock_pct > 0 else ("ms-pos" if shock_pct < 0 else "ms-gold"))
    with cols[1]:
        metric_card("IT sector margin impact", f"{it_margin_bps:+.0f} bps",
                     "Estimated EBIT margin change for export-oriented IT firms",
                     "ms-pos" if it_margin_bps > 0 else ("ms-neg" if it_margin_bps < 0 else "ms-gold"))
    with cols[2]:
        metric_card("Import cost change", f"{sign(import_cost_pct)}{import_cost_pct:.2f}%",
                     "Rupee cost of dollar-denominated imports (crude, machinery, etc.)",
                     "ms-neg" if import_cost_pct > 0 else ("ms-pos" if import_cost_pct < 0 else "ms-gold"))

    if delta != 0:
        verb = "adds" if annual_fuel_change >= 0 else "removes roughly"
        ghost_box(
            f"A move of {sign(delta)}₹{abs(delta):.1f} on USD/INR {verb} about ₹{abs(annual_fuel_change):,.0f} "
            f"to the annual fuel bill of a household using roughly {annual_petrol_litres:,} litres of petrol "
            f"a year. This is a simplified illustration based only on the crude-oil cost embedded in fuel — "
            f"it doesn't include taxes, duties, refining margins, or OMC pricing decisions, which usually "
            f"dominate the pump price."
        )
    else:
        ghost_box(
            f"At the current baseline, a household using roughly {annual_petrol_litres:,} litres of petrol "
            f"a year has a crude-cost component of about ₹{crude_cost_per_litre_base * annual_petrol_litres:,.0f} "
            f"per year embedded in its fuel bill. Move the slider to see how this shifts with USD/INR."
        )

    before_after_chart("IT sector margin impact (bps)", 0, it_margin_bps, unit=" bps", fmt="{:+.0f}")

    st.markdown("### Sector impact")
    sector_cols = st.columns(2)
    for i, (name, info) in enumerate(USDINR_SECTOR_IMPACT.items()):
        with sector_cols[i % 2]:
            sector_card(name, info)

    st.markdown("### Historical comparison — what happened last time")
    st.markdown(f"""
    <div class="ms-card ms-card-gold">
        <div style="font-family:'Playfair Display',serif;font-size:1rem;color:#f0ede7;">No direct preset for USD/INR shocks</div>
        <div style="font-size:0.85rem;color:#cfcdc8;margin-top:0.4rem;">
        Rupee moves are usually a <i>consequence</i> of crude or US yield shocks rather than standalone events.
        During the 2026 West Asia Conflict (a crude shock), the rupee touched a record low of ₹96.82.
        During the 2013 Taper Tantrum (a US 10Y shock), the rupee fell from roughly ₹54 to ₹68.
        Try those presets above to see the rupee move as part of a broader cascade.
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_cpi(baselines):
    delta = st.session_state.cpi_delta
    c = CPI_COEFFICIENTS

    new_cpi = baselines["india_cpi"] + delta / 100
    repo_response = max(0, (delta / 100) * c["repo_rate_response_per_100bps_cpi"])
    india10y_change = (delta / 100) * c["india10y_per_100bps_cpi"]
    new_india10y = baselines["india10y"] + india10y_change / 100
    pe_change = (delta / 100) * c["nifty_pe_per_100bps_cpi"] + 0.0
    new_pe = baselines["nifty_pe"] + pe_change
    nifty_est = new_pe * (baselines["nifty"] / baselines["nifty_pe"])

    # Home loan EMI example — ₹50L, 20-year tenure
    # Baseline floating home-loan rate assumed at ~8.6% (representative current rate, not a coefficient
    # cited above — used only to make the repo-rate response concrete for a borrower)
    baseline_loan_rate = 8.6
    new_loan_rate = baseline_loan_rate + repo_response / 100
    principal, months = 5_000_000, 240
    emi_old = calc_emi(principal, baseline_loan_rate, months)
    emi_new = calc_emi(principal, new_loan_rate, months)
    emi_change = emi_new - emi_old

    rbi_outlook = "Hike likely at next MPC (Aug 2026)" if new_cpi > c["rbi_response_threshold_cpi"] else "Hold likely"

    st.markdown("### Macro impact — India CPI Surprise")
    st.markdown(
        f'<div class="ms-tag">Shock: {delta:+d} bps → new India CPI ≈ {new_cpi:.2f}%</div>',
        unsafe_allow_html=True
    )

    cols = st.columns(3)
    with cols[0]:
        metric_card("RBI repo response (est.)", f"{repo_response:+.0f} bps",
                     f"Typical lag before response: ~{c['rbi_response_lag_months']} months",
                     "ms-neg" if repo_response > 0 else "ms-gold")
    with cols[1]:
        metric_card("India 10Y G-Sec", f"{india10y_change:+.0f} bps",
                     f"New yield estimate: {new_india10y:.2f}%",
                     "ms-neg" if india10y_change > 0 else ("ms-pos" if india10y_change < 0 else "ms-gold"))
    with cols[2]:
        nifty_pct = (nifty_est / baselines["nifty"] - 1) * 100
        metric_card("Nifty P/E & level", f"{pe_change:+.2f}x",
                     f"New P/E ≈ {new_pe:.1f}x → Nifty est. {nifty_est:,.0f} ({sign(nifty_pct)}{nifty_pct:.1f}%)",
                     "ms-neg" if pe_change < 0 else ("ms-pos" if pe_change > 0 else "ms-gold"))

    cols = st.columns(2)
    with cols[0]:
        metric_card("MPC outlook", rbi_outlook,
                     f"Response threshold: CPI > {c['rbi_response_threshold_cpi']:.1f}%",
                     "ms-neg" if "Hike" in rbi_outlook else "ms-gold")
    with cols[1]:
        metric_card("Home loan EMI (₹50L, 20yr)", f"{sign(emi_change)}₹{emi_change:,.0f}/month",
                     f"₹{emi_old:,.0f} → ₹{emi_new:,.0f}/month, assuming rate moves "
                     f"{baseline_loan_rate:.1f}% → {new_loan_rate:.2f}%",
                     "ms-neg" if emi_change > 0 else ("ms-pos" if emi_change < 0 else "ms-gold"))

    if repo_response > 0:
        ghost_box(
            f"If inflation surprises by {delta:+d}bps, history suggests the RBI eventually moves the "
            f"repo rate by roughly a third of that, with a 2-3 month lag. On a ₹50 lakh, 20-year home "
            f"loan, that could mean paying about ₹{emi_change:,.0f} more per month once your bank "
            f"reprices the loan."
        )
    else:
        ghost_box(
            f"A CPI surprise of {delta:+d}bps is below the level that historically triggers an RBI "
            f"rate hike, so no repo response is modelled here — your EMI on a ₹50 lakh, 20-year home "
            f"loan would be unaffected by this alone."
        )

    before_after_chart("India 10Y G-Sec yield — current vs. under this shock", baselines["india10y"], new_india10y,
                        unit="%", fmt="{:.2f}")

    context_box(
        "Historical context: in 2022, CPI hit 7.8% and the RBI hiked the repo rate by 250bps over "
        "nine months. The Nifty fell roughly 17% peak to trough during that tightening cycle. "
        "<i>The chart below applies the shock size set above to today's live India 10Y yield — it "
        "is not a record of where yields actually traded back then.</i>"
    )

    st.markdown("### Sector impact")
    sector_cols = st.columns(2)
    for i, (name, info) in enumerate(CPI_SECTOR_IMPACT.items()):
        with sector_cols[i % 2]:
            sector_card(name, info)

    st.markdown("### Historical comparison — what happened last time")
    st.markdown("""
    <div class="ms-card ms-card-gold">
        <div style="font-family:'Playfair Display',serif;font-size:1rem;color:#f0ede7;">No direct preset for standalone CPI shocks</div>
        <div style="font-size:0.85rem;color:#cfcdc8;margin-top:0.4rem;">
        In practice, India's biggest CPI surprises have usually been driven by crude oil shocks.
        The 2022 Russia-Ukraine Crude Shock preset shows CPI hitting 7.8% and the RBI responding with
        an emergency off-cycle hike. Try that preset to see the full cascade.
        </div>
    </div>
    """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════
# MAIN ROUTING
# ════════════════════════════════════════════════════════════════
baselines = fetch_baselines()

if st.session_state.page == "home":
    homepage(baselines)
else:
    terminal_controls(baselines)

    shock_type = st.session_state.shock_type
    if shock_type == "crude":
        render_crude(baselines)
    elif shock_type == "us10y":
        render_us10y(baselines)
    elif shock_type == "usdinr":
        render_usdinr(baselines)
    elif shock_type == "cpi":
        render_cpi(baselines)

    st.markdown("""
    <div class="ms-footer">
    MacroShock · Day 14 · 30 Days of AI Finance · Historical pattern estimates from 2013-2026 data
    (RBI, Business Standard, ICRA, PPAC). Not investment advice. Correlations may break during
    structural regime shifts.
    </div>
    """, unsafe_allow_html=True)