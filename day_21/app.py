import streamlit as st
import plotly.graph_objects as go
import numpy as np
import copy

st.set_page_config(
    page_title="LinkDesk — Day 21 | 30 Days of AI Finance",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── FORCE DARK EVERYWHERE — light/dark mode proof ───────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400;1,700&family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&display=swap');

/* Nuclear dark mode — overrides Streamlit light/dark both */
html, body, [data-testid="stApp"], .stApp,
[data-testid="stMain"], .main,
[data-testid="stVerticalBlock"],
[data-testid="stTabsContent"],
[data-testid="stHeader"],
.block-container, section[data-testid="stSidebar"],
[data-theme="light"], [data-theme="dark"],
:root {
    background-color: #09090e !important;
    color: #e8e4dc !important;
}

/* Wipe streamlit's default text colours */
.stMarkdown, .stMarkdown p, .stMarkdown li,
[data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li {
    color: #b0ac9f !important;
    font-family: 'Syne', sans-serif !important;
}

/* Headings */
h1,h2,h3,h4,h5,h6,
.stMarkdown h1,.stMarkdown h2,.stMarkdown h3 {
    color: #e8e4dc !important;
    font-family: 'Playfair Display', serif !important;
}

/* Widget labels — must be light on dark */
label, [data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] span {
    color: #b0ac9f !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 0.8rem !important;
}

/* Radio buttons — fix gold-on-gold bug: style text only, not container */
[data-testid="stRadio"] label { color: #c8c4bc !important; font-family: 'Syne', sans-serif !important; font-size: 0.84rem !important; }
[data-testid="stRadio"] p { color: #c8c4bc !important; font-family: 'Syne', sans-serif !important; }
[data-testid="stRadio"] span { color: #c8c4bc !important; }

/* Tabs */
[data-testid="stTabs"] button {
    color: #555566 !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 0.75rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    border: none !important;
    background: transparent !important;
    padding: 0.5rem 0.8rem !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: #c9a96e !important;
    border-bottom: 2px solid #c9a96e !important;
    background: transparent !important;
}
[data-testid="stTabs"] [data-testid="stTabsTabList"] {
    border-bottom: 1px solid #1e1e2a !important;
    background: transparent !important;
    gap: 0 !important;
}

/* Sliders */
[data-testid="stSlider"] > div > div > div { background: #3a5a7a !important; }
[data-testid="stSlider"] p { color: #b0ac9f !important; }

/* Primary buttons */
.stButton > button {
    background: linear-gradient(135deg, #c9a96e, #e8ca90) !important;
    color: #09090e !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 4px !important;
    padding: 0.55rem 1.2rem !important;
    letter-spacing: 0.04em !important;
    font-size: 0.85rem !important;
}
/* Force button text dark — Streamlit injects <p>/<span> that inherit body color */
.stButton > button p,
.stButton > button span,
.stButton > button div,
[data-testid="baseButton-secondary"] p,
[data-testid="baseButton-secondary"] span,
[data-testid="baseButton-primary"] p,
[data-testid="baseButton-primary"] span {
    color: #09090e !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
}
.stButton > button:hover { opacity: 0.88 !important; }

/* Download button */
[data-testid="stDownloadButton"] > button {
    background: linear-gradient(135deg, #1a3a5a, #3a5a7a) !important;
    color: #e8e4dc !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    border: 1px solid #3a5a7a !important;
    border-radius: 4px !important;
    width: 100% !important;
    padding: 0.7rem !important;
    font-size: 0.85rem !important;
}

/* Selectbox */
[data-testid="stSelectbox"] > div > div {
    background: #111118 !important;
    color: #e8e4dc !important;
    border: 1px solid #1e1e2a !important;
    font-family: 'DM Mono', monospace !important;
}

/* Metrics */
[data-testid="stMetric"] {
    background: #111118 !important;
    border: 1px solid #1e1e2a !important;
    border-radius: 8px !important;
    padding: 0.9rem 1rem !important;
}
[data-testid="stMetricValue"] {
    color: #c9a96e !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 1.35rem !important;
}
[data-testid="stMetricLabel"] {
    color: #666677 !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 0.7rem !important;
}
[data-testid="stMetricDelta"] {
    color: #4ab87a !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.72rem !important;
}

/* Divider */
hr { border-color: #1e1e2a !important; margin: 0.6rem 0 !important; }

/* Hide branding */
#MainMenu, footer, header, [data-testid="stDecoration"] { visibility: hidden !important; display: none !important; }

/* ── FINANCIAL TABLES ─────────────────────────────────── */
.tbl-wrap { overflow-x: auto; -webkit-overflow-scrolling: touch; border-radius: 8px; border: 1px solid #1a1a28; }
.fin-table {
    width: 100%; border-collapse: collapse;
    font-family: 'DM Mono', monospace; font-size: 0.85rem;
    background: #0c0c14;
}
.fin-table th {
    background: #0f0f1c !important; color: #8888aa !important;
    text-align: right; padding: 10px 14px;
    font-family: 'Syne', sans-serif; font-weight: 700;
    letter-spacing: 0.06em; font-size: 0.72rem; text-transform: uppercase;
    border-bottom: 2px solid #1e1e30; white-space: nowrap;
}
.fin-table th:first-child { text-align: left; min-width: 180px; }
.fin-table td {
    padding: 8px 14px; text-align: right;
    color: #ccc8c0 !important; border-bottom: 1px solid #131320;
    white-space: nowrap; font-size: 0.85rem;
}
.fin-table td:first-child { text-align: left; color: #e8e4dc !important; font-weight: 500; }
.fin-table tbody tr:nth-child(even) td { background: rgba(255,255,255,0.014); }
.fin-table tr:hover td { background: rgba(201,169,110,0.05) !important; }
.fin-table .sh { background: #11111e !important; }
.fin-table .sh td {
    color: #5a7a9a !important; font-weight: 700; font-size: 0.67rem;
    text-transform: uppercase; letter-spacing: 0.1em;
    font-family: 'Syne', sans-serif !important;
    padding: 5px 14px !important; border-top: 1px solid #1a1a2c;
}
.fin-table .hc { color: #3a5a70 !important; }
.fin-table .sub td { color: #e8ca80 !important; font-weight: 700; border-top: 1px solid #252535; font-size: 0.87rem !important; background: rgba(201,169,110,0.035) !important; }
.fin-table .sub td:first-child { color: #e8ca80 !important; }
.fin-table .tot td { color: #f0e8c0 !important; font-weight: 800; border-top: 2px solid #3a5a7a; font-size: 0.89rem !important; background: rgba(58,90,122,0.1) !important; letter-spacing: 0.02em; }
.fin-table .tot td:first-child { color: #f0e8c0 !important; }
.fin-table .mrg td { color: #3d6050 !important; font-size: 0.74rem !important; font-style: italic; padding: 3px 14px !important; }
.fin-table .pos { color: #5ac88a !important; }
.fin-table .neg { color: #e06878 !important; }
.fin-table .chk { color: #5ac88a !important; font-weight: 700; }

/* ── COMPONENT STYLES ─────────────────────────────────── */
.ghost-block {
    background: rgba(58,90,122,0.07);
    border-left: 3px solid #2a4a6a;
    padding: 0.9rem 1.1rem;
    border-radius: 0 6px 6px 0;
    margin: 1rem 0;
}
.ghost-block .gl {
    color: #2a4a6a !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 0.62rem !important; font-weight: 700 !important;
    letter-spacing: 0.14em !important; text-transform: uppercase !important;
    margin-bottom: 0.35rem !important; display: block;
}
.ghost-block p {
    color: #9a9690 !important; font-size: 0.83rem !important;
    line-height: 1.65 !important; margin: 0 !important;
    font-family: 'Syne', sans-serif !important;
}

.pill {
    display: inline-block;
    background: rgba(58,90,122,0.18);
    border: 1px solid rgba(58,90,122,0.35);
    border-radius: 20px; padding: 3px 11px; margin: 3px;
    font-family: 'Syne', sans-serif; font-size: 0.67rem;
    font-weight: 700; color: #4a7a9a !important;
    letter-spacing: 0.07em; text-transform: uppercase;
}

.feat-card {
    background: #111118; border: 1px solid #191924;
    border-radius: 10px; padding: 1.2rem; margin-bottom: 0.7rem;
    min-height: 120px;
}
.feat-card:hover { border-color: #2a4a6a; }
.feat-card .fi { font-size: 1.3rem; margin-bottom: 0.5rem; display: block; }
.feat-card .ft { color: #c9a96e !important; font-family: 'Syne', sans-serif !important; font-weight: 700 !important; font-size: 0.82rem !important; margin-bottom: 0.35rem !important; display: block; }
.feat-card .fd { color: #555566 !important; font-size: 0.75rem !important; line-height: 1.5 !important; font-family: 'Syne', sans-serif !important; }

.week-strip {
    background: rgba(26,58,90,0.25);
    border: 1px solid rgba(58,90,122,0.25);
    border-radius: 8px; padding: 0.7rem 1rem;
    text-align: center; margin: 1.2rem 0;
}

/* Text input dark styling */
[data-testid="stTextInput"] input {
    background: #111118 !important;
    color: #e8e4dc !important;
    border: 1px solid #2a2a3a !important;
    border-radius: 4px !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.84rem !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: #3a5a7a !important;
    box-shadow: 0 0 0 1px #3a5a7a !important;
}
[data-testid="stTextInput"] label {
    color: #8888a0 !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 0.76rem !important;
}

/* Number input dark styling */
[data-testid="stNumberInput"] input {
    background: #111118 !important;
    color: #e8e4dc !important;
    border: 1px solid #2a2a3a !important;
    border-radius: 4px !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.84rem !important;
}
[data-testid="stNumberInput"] input:focus { border-color: #c9a96e !important; box-shadow: 0 0 0 1px rgba(201,169,110,0.3) !important; }
[data-testid="stNumberInput"] label { color: #8888a0 !important; font-family: 'Syne', sans-serif !important; font-size: 0.76rem !important; }
[data-testid="stNumberInput"] button { background: #1a1a28 !important; border-color: #2a2a3a !important; color: #8888a0 !important; }

/* Mobile responsive */
@media (max-width: 768px) {
    .block-container { padding: 0.5rem 0.8rem !important; }
    .fin-table { font-size: 0.68rem !important; }
    .fin-table td, .fin-table th { padding: 5px 7px !important; }
    .feat-card { min-height: unset; }
}
</style>
""", unsafe_allow_html=True)

# ─── CONSTANTS & MODEL ───────────────────────────────────────────────────────
YEARS = ["Y0 (Base)", "Y1", "Y2", "Y3", "Y4", "Y5"]

DEFAULT_ASSUMPTIONS = {
    "rev_growth":  [0.12, 0.11, 0.10, 0.09, 0.08],
    "cogs_pct":    [0.70, 0.695, 0.69, 0.685, 0.68],
    "rd_pct":      [0.010]*5,
    "sga_pct":     [0.098, 0.095, 0.093, 0.091, 0.090],
    "da_pct":      [0.048, 0.047, 0.046, 0.045, 0.044],
    "capex_pct":   [0.072, 0.068, 0.065, 0.062, 0.060],
    "tax_rate":    0.25, "interest_rate": 0.090,
    "rec_days":    65,   "inv_days": 77, "pay_days": 61,
    "debt_repay":  25.0, "min_cash": 40.0,
    "y0_rev":      600.0,   # Y0 base revenue — user-editable in custom mode
}

Y0 = {
    "revenue":600.0,"cogs":-426.0,"gross":174.0,"rd":-6.0,"sga":-60.0,
    "ebitda":108.0,"da":-30.0,"ebit":78.0,"interest":-18.0,"other_inc":2.0,
    "ebt":62.0,"tax":-15.5,"net_income":46.5,"cash":45.0,"receivables":108.0,
    "inventory":90.0,"prepaid":8.0,"net_ppe":330.0,"gross_ppe":510.0,
    "accum_dep":-180.0,"intangibles":20.0,"payables":71.0,"accrued":18.0,
    "current_debt":25.0,"lt_debt":150.0,"deferred_tax":12.0,"share_capital":50.0,
    "retained_earn":275.0,"total_assets":601.0,
    "operating_cf":79.0,"investing_cf":-30.0,"financing_cf":-25.0,
    "beg_cash":20.0,"end_cash":45.0,
}

def build_model(assumptions=None):
    a = assumptions or DEFAULT_ASSUMPTIONS

    # ── Y0 base — scale all BS items proportionally if y0_rev changed ─────
    base_rev = a.get("y0_rev", Y0["revenue"])
    scale    = base_rev / Y0["revenue"]  # e.g. 2.0 for ₹1200 Cr company

    # Scaled Y0 balance sheet starting points
    y0_rec   = Y0["receivables"] * scale
    y0_inv   = Y0["inventory"]   * scale
    y0_pay   = Y0["payables"]    * scale
    y0_cash  = Y0["cash"] * scale
    cash_plug= max(0.0, a["min_cash"] - y0_cash)  # if min_cash > scaled seed, plug equity
    y0_cash  = max(a["min_cash"], y0_cash)
    y0_gppe  = Y0["gross_ppe"]   * scale
    y0_adep  = abs(Y0["accum_dep"]) * scale
    y0_prep  = Y0["prepaid"]     * scale
    y0_intg  = Y0["intangibles"] * scale
    y0_dft   = Y0["deferred_tax"]* scale
    y0_acc   = Y0["accrued"]     * scale
    y0_sc    = Y0["share_capital"]* scale
    y0_re    = Y0["retained_earn"]* scale + cash_plug  # absorb min_cash top-up
    y0_debt  = (Y0["lt_debt"] + Y0["current_debt"]) * scale

    # ── Income Statement ───────────────────────────────────────────────────
    revenue = [base_rev]
    for gr in a["rev_growth"]: revenue.append(revenue[-1]*(1+gr))
    revenue = revenue[1:]
    cogs    = [-r*a["cogs_pct"][i] for i,r in enumerate(revenue)]
    gross   = [r+c for r,c in zip(revenue,cogs)]
    rd      = [-r*a["rd_pct"][i] for i,r in enumerate(revenue)]
    sga     = [-r*a["sga_pct"][i] for i,r in enumerate(revenue)]
    ebitda  = [g+rd_+s for g,rd_,s in zip(gross,rd,sga)]
    da      = [-r*a["da_pct"][i] for i,r in enumerate(revenue)]
    ebit    = [e+d for e,d in zip(ebitda,da)]

    # ── Debt Schedule ──────────────────────────────────────────────────────
    debt_op = [y0_debt]
    for _ in range(5): debt_op.append(max(0,debt_op[-1]-a["debt_repay"]))
    debt_cl = debt_op[1:]; debt_op = debt_op[:-1]
    debt_avg= [(o+c)/2 for o,c in zip(debt_op,debt_cl)]
    interest= [-avg*a["interest_rate"] for avg in debt_avg]
    other_inc = [1.0*scale]*5
    ebt     = [e+i_+o for e,i_,o in zip(ebit,interest,other_inc)]
    tax     = [min(0,-e*a["tax_rate"]) for e in ebt]
    ni      = [e+t for e,t in zip(ebt,tax)]

    # ── PP&E Schedule ──────────────────────────────────────────────────────
    gppe_op = [y0_gppe]
    capex   = [r*a["capex_pct"][i] for i,r in enumerate(revenue)]
    for c in capex: gppe_op.append(gppe_op[-1]+c)
    gppe_cl = gppe_op[1:]; gppe_op = gppe_op[:-1]
    ad_op   = [y0_adep]
    da_ch   = [abs(d) for d in da]
    for d in da_ch: ad_op.append(ad_op[-1]+d)
    ad_cl   = ad_op[1:]; ad_op = ad_op[:-1]
    net_ppe = [g-a_ for g,a_ in zip(gppe_cl,ad_cl)]

    # ── Working Capital ────────────────────────────────────────────────────
    cogs_abs= [abs(c) for c in cogs]
    rec     = [r/365*a["rec_days"] for r in revenue]
    inv     = [c/365*a["inv_days"] for c in cogs_abs]
    pay     = [c/365*a["pay_days"] for c in cogs_abs]
    nwc     = [r+i-p for r,i,p in zip(rec,inv,pay)]
    nwc0    = [y0_rec + y0_inv - y0_pay] + nwc
    dnwc    = [-(nwc0[i+1]-nwc0[i]) for i in range(5)]

    # ── Balance Sheet items ────────────────────────────────────────────────
    acc     = [r*0.03 for r in revenue]
    dft     = [y0_dft*(1.03**(i+1)) for i in range(5)]
    prep    = [y0_prep]*5
    intang  = [y0_intg]*5
    # actual_repay = cash actually paid = min(repay, opening balance)
    actual_repay = [min(a["debt_repay"], max(0.0, op)) for op in debt_op]
    # cd (BS current portion) = what will be repaid next period = min(repay, closing balance)
    # This ensures cd + ltd == closing debt on the balance sheet exactly
    cd      = [min(a["debt_repay"], cl) for cl in debt_cl]
    ltd     = [max(0.0, cl - c) for cl, c in zip(debt_cl, cd)]
    sc      = [y0_sc]*5
    re_op   = [y0_re]
    for i in range(4): re_op.append(re_op[-1]+ni[i])
    re      = [ro+n for ro,n in zip(re_op,ni)]

    # ── Cash Flow ──────────────────────────────────────────────────────────
    d_dft   = [dft[i]-(y0_dft if i==0 else dft[i-1]) for i in range(5)]
    d_acc   = [acc[i]-(y0_acc if i==0 else acc[i-1]) for i in range(5)]
    ocf     = [n+dc+dn+dd+da_ for n,dc,dn,dd,da_ in zip(ni,da_ch,dnwc,d_dft,d_acc)]
    icf     = [-c for c in capex]
    fcf     = [-r for r in actual_repay]  # actual cash out for debt repayment

    beg=[y0_cash]; end=[]; cf_plug=[0.0]*5
    for i in range(5):
        natural = beg[-1] + ocf[i] + icf[i] + fcf[i]
        ec = max(a["min_cash"], natural)
        cf_plug[i] = max(0.0, ec - natural)  # implicit equity injection to meet min_cash
        end.append(ec); beg.append(ec)
    beg=beg[:-1]

    # Adjust retained earnings — absorb cumulative cash plugs so BS stays balanced
    cum_plug = 0.0
    re_adj = []
    for i in range(5):
        cum_plug += cf_plug[i]
        re_adj.append(re[i] + cum_plug)
    re = re_adj

    ca  = [e+r+i+p for e,r,i,p in zip(end,rec,inv,prep)]
    ta  = [c+n+ig for c,n,ig in zip(ca,net_ppe,intang)]
    cl  = [p+a_+c for p,a_,c in zip(pay,acc,cd)]
    tl  = [c+l+d for c,l,d in zip(cl,ltd,dft)]
    te  = [s+r for s,r in zip(sc,re)]
    tle = [l+e for l,e in zip(tl,te)]
    chk = [t-l for t,l in zip(ta,tle)]
    fcff= [o+abs(i_)*(1-a["tax_rate"]) for o,i_ in zip(ocf,interest)]
    fcfe= [o+i+f for o,i,f in zip(ocf,icf,fcf)]

    return {
        "years": YEARS[1:],
        "income": {"revenue":revenue,"cogs":cogs,"gross":gross,"rd":rd,"sga":sga,
                   "ebitda":ebitda,"da":da,"ebit":ebit,"interest":interest,
                   "other_inc":[1.0]*5,"ebt":ebt,"tax":tax,"net_income":ni,
                   "gross_margin":[g/r for g,r in zip(gross,revenue)],
                   "ebitda_margin":[e/r for e,r in zip(ebitda,revenue)],
                   "ebit_margin":[e/r for e,r in zip(ebit,revenue)],
                   "net_margin":[n/r for n,r in zip(ni,revenue)]},
        "ppe":  {"gross_open":gppe_op,"capex":capex,"gross_close":gppe_cl,
                 "accum_open":ad_op,"da_charge":da_ch,"accum_close":ad_cl,"net_ppe":net_ppe},
        "debt": {"opening":debt_op,"repayment":[-r for r in actual_repay],
                 "closing":debt_cl,"avg":debt_avg,"interest":interest},
        "wc":   {"receivables":rec,"inventory":inv,"payables":pay,"nwc":nwc,"delta_nwc":dnwc},
        "bs":   {"cash":end,"receivables":rec,"inventory":inv,"prepaid":prep,
                 "current_assets":ca,"net_ppe":net_ppe,"intangibles":intang,
                 "total_assets":ta,"payables":pay,"accrued":acc,"current_debt":cd,
                 "current_liab":cl,"lt_debt":ltd,"deferred_tax":dft,"total_liab":tl,
                 "share_capital":sc,"retained_earn":re,"total_equity":te,
                 "total_le":tle,"check":chk},
        "cf":   {"net_income":ni,"da_addback":da_ch,"delta_nwc":dnwc,
                 "d_deferred_tax":d_dft,"d_accrued":d_acc,"operating_cf":ocf,
                 "investing_cf":icf,"financing_cf":fcf,"beg_cash":beg,
                 "end_cash":end,"fcff":fcff,"fcfe":fcfe},
        "ratios":{"roe":[n/e for n,e in zip(ni,te)],
                  "roa":[n/a_ for n,a_ in zip(ni,ta)],
                  "roce":[e/(t-c) for e,t,c in zip(ebit,ta,cl)],
                  "nd_ebitda":[(l+c-e)/eb for l,c,e,eb in zip(ltd,cd,end,ebitda)],
                  "int_cov":[eb/abs(i_) for eb,i_ in zip(ebitda,interest)],
                  "fcff":fcff,"fcfe":fcfe,
                  "capex_rev":[c/r for c,r in zip(capex,revenue)],
                  "ocf_ebitda":[o/e for o,e in zip(ocf,ebitda)]}
    }

# ─── HELPERS ─────────────────────────────────────────────────────────────────
def dark_layout(**extra):
    d = dict(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='DM Mono, monospace', color='#9a9aaa', size=13),
        xaxis=dict(gridcolor='#161622', linecolor='#1e1e2a', tickfont=dict(color='#8888a0',size=12)),
        yaxis=dict(gridcolor='#161622', linecolor='#1e1e2a', tickfont=dict(color='#8888a0',size=12)),
        margin=dict(l=8,r=8,t=40,b=16), showlegend=False,
        height=340,
    )
    for k,v in extra.items():
        if k in d and isinstance(d[k],dict) and isinstance(v,dict):
            d[k].update(v)
        else:
            d[k]=v
    return d

def cr(v, d=1): return f"₹{v:.{d}f}"
def pct(v, d=1): return f"{v*100:.{d}f}%"

def _td(v, cls="", neg_red=True, gold=False, green=False):
    color=""
    if gold: color="color:#c9a96e;"
    elif green: color="color:#4ab87a;"
    elif neg_red and v < 0: color="color:#e05c6c;"
    return f"<td class='{cls}' style='{color}'>{cr(v)}</td>"

def tbl_wrap(html): return f"<div class='tbl-wrap'>{html}</div>"

# ─── SESSION STATE ────────────────────────────────────────────────────────────
if "page" not in st.session_state: st.session_state.page = "home"
if "model" not in st.session_state: st.session_state.model = build_model()
if "custom_a" not in st.session_state: st.session_state.custom_a = copy.deepcopy(DEFAULT_ASSUMPTIONS)
if "company_name" not in st.session_state: st.session_state.company_name = "Arjun Steel & Engineering Ltd"
if "custom_mode" not in st.session_state: st.session_state.custom_mode = False

# ─── HOME PAGE ───────────────────────────────────────────────────────────────
def render_home():
    st.markdown("""
    <div style='margin-top:1.5rem;'>
      <span style='color:#2a4a6a;font-family:Syne,sans-serif;font-size:0.68rem;font-weight:700;letter-spacing:0.14em;text-transform:uppercase;'>
        <span style='color:#4ab87a;'>●</span>&nbsp; INCOME STATEMENT &nbsp;·&nbsp; BALANCE SHEET &nbsp;·&nbsp; CASH FLOW &nbsp;·&nbsp; FULLY LINKED
      </span>
    </div>
    <div style='margin:1.8rem 0 1.4rem;'>
      <div style='font-family:"Playfair Display",serif;font-size:clamp(2.4rem,5.5vw,4.2rem);font-weight:700;color:#e8e4dc;line-height:1.06;'>
        The <em style='color:#c9a96e;'>foundation.</em>
      </div>
      <div style='font-family:Syne,sans-serif;font-size:1rem;color:#888880;margin-top:0.9rem;max-width:580px;line-height:1.75;'>
        The 3-Statement Model — starting point for every DCF, LBO, and Comps ever built.
        Fully integrated. Balance sheet verified.
        <span style='color:#c9a96e;'>Week 3 closer.</span>
      </div>
    </div>
    <div style='display:flex;gap:2rem;flex-wrap:wrap;padding:0.9rem 0;border-top:1px solid #191924;border-bottom:1px solid #191924;margin-bottom:1.2rem;'>
      <div><div style='font-family:"DM Mono",monospace;font-size:1.35rem;color:#c9a96e;'>3</div><div style='font-family:Syne,sans-serif;font-size:0.62rem;color:#444455;letter-spacing:0.1em;text-transform:uppercase;'>Linked Statements</div></div>
      <div><div style='font-family:"DM Mono",monospace;font-size:1.35rem;color:#c9a96e;'>6</div><div style='font-family:Syne,sans-serif;font-size:0.62rem;color:#444455;letter-spacing:0.1em;text-transform:uppercase;'>Schedules</div></div>
      <div><div style='font-family:"DM Mono",monospace;font-size:1.35rem;color:#4ab87a;'>✓</div><div style='font-family:Syne,sans-serif;font-size:0.62rem;color:#444455;letter-spacing:0.1em;text-transform:uppercase;'>BS Verified</div></div>
      <div><div style='font-family:"DM Mono",monospace;font-size:1.35rem;color:#c9a96e;'>514</div><div style='font-family:Syne,sans-serif;font-size:0.62rem;color:#444455;letter-spacing:0.1em;text-transform:uppercase;'>Excel Formulas</div></div>
      <div><div style='font-family:"DM Mono",monospace;font-size:1.35rem;color:#c9a96e;'>5yr</div><div style='font-family:Syne,sans-serif;font-size:0.62rem;color:#444455;letter-spacing:0.1em;text-transform:uppercase;'>Horizon</div></div>
    </div>
    """, unsafe_allow_html=True)

    pills = ["Income Statement","Balance Sheet","Cash Flow","PP&E Schedule","Debt Schedule","Working Capital"]
    st.markdown("<div style='margin:0.8rem 0;'>"+"".join(f"<span class='pill'>{p}</span>" for p in pills)+"</div>", unsafe_allow_html=True)

    features = [
        ("📊","Income Statement","Revenue → COGS → Gross Profit → EBITDA → EBIT → Net Income. Five-year projection with margin expansion and operating leverage."),
        ("🏗️","PP&E Roll-forward","Gross PP&E + Capex each period. Accumulated depreciation builds year by year. Net PP&E feeds the balance sheet directly."),
        ("💳","Debt Schedule","Opening → mandatory repayment → closing. Average debt drives interest expense, which flows into the income statement."),
        ("⚙️","Working Capital","Receivables, inventory, payables — driven by days assumptions. Delta NWC hits operating cash flow as a source or drag."),
        ("💵","Cash Flow","Indirect method: NI + D&A + ΔNWC = Operating CF. Less capex = Investing. Less repayment = Financing. Ending cash → balance sheet."),
        ("✅","Balance Sheet Check","Assets = Liabilities + Equity in all 5 periods. CHECK = 0.00 every year. A model that actually balances."),
    ]
    c1, c2, c3 = st.columns(3)
    for i,(icon,title,desc) in enumerate(features):
        with [c1,c2,c3][i%3]:
            st.markdown(f"<div class='feat-card'><span class='fi'>{icon}</span><span class='ft'>{title}</span><span class='fd'>{desc}</span></div>", unsafe_allow_html=True)

    st.markdown("<div style='height:0.8rem;'></div>", unsafe_allow_html=True)
    b1,b2,_= st.columns([1,1,2])
    with b1:
        if st.button("→ Launch LinkDesk", key="hl", use_container_width=True):
            st.session_state.page="terminal"; st.rerun()
    with b2:
        if st.button("→ Custom Assumptions", key="hc", use_container_width=True):
            st.session_state.page="terminal"; st.rerun()

    st.markdown("""
    <div class='week-strip'>
      <span style='font-family:Syne,sans-serif;font-size:0.68rem;font-weight:700;color:#2a4a6a;letter-spacing:0.08em;text-transform:uppercase;'>Week 3 complete →</span>
      <span style='font-family:"DM Mono",monospace;font-size:0.8rem;color:#666677;margin-left:0.6rem;'>
        <span style='color:#c9a96e;'>LBOdesk</span> · <span style='color:#c9a96e;'>DCFdesk</span> · <span style='color:#c9a96e;'>CompsDesk</span> · <span style='color:#4ab87a;font-weight:700;'>LinkDesk</span>
      </span>
    </div>
    <div style='margin-top:2rem;padding-top:0.8rem;border-top:1px solid #111118;text-align:center;'>
      <span style='font-family:Syne,sans-serif;font-size:0.62rem;color:#222233;letter-spacing:0.07em;'>
        LinkDesk · Day 21 · 30 Days of AI Finance · Arjun Steel & Engineering Ltd is fictional · Not investment advice
      </span>
    </div>
    """, unsafe_allow_html=True)


# ─── NAV BAR ─────────────────────────────────────────────────────────────────
def render_nav():
    a,b,c = st.columns([2,6,2])
    with a:
        st.markdown("<div style='font-family:\"Playfair Display\",serif;font-size:1.15rem;color:#c9a96e;padding-top:0.4rem;'>Link<em>Desk</em></div>", unsafe_allow_html=True)
    with b:
        cname = st.session_state.company_name
        mode_label = "Custom Model" if st.session_state.custom_mode else "Fictional"
        st.markdown(f"<div style='text-align:center;padding-top:0.5rem;'><span style='font-family:Syne,sans-serif;font-size:0.65rem;color:#2a4a6a;letter-spacing:0.1em;text-transform:uppercase;'>{cname} · {mode_label} · ₹ Crores</span></div>", unsafe_allow_html=True)
    with c:
        if st.button("← Home", key="nh"): st.session_state.page="home"; st.rerun()


# ─── TAB 1: OVERVIEW ─────────────────────────────────────────────────────────
def tab_overview():
    m = st.session_state.model
    inc, cf, rat = m["income"], m["cf"], m["ratios"]

    # Mode toggle — simple and clean
    mode = st.radio("", ["Demo — Arjun Steel Base Case", "Custom Assumptions"],
                    key="mode_radio", horizontal=True, label_visibility="collapsed")

    if "Custom" in mode:
        st.session_state.custom_mode = True
        a = st.session_state.custom_a
        st.markdown("<div style='height:0.4rem;'></div>", unsafe_allow_html=True)
        # Company name input
        inp_c1, inp_c2, _ = st.columns([2,1,3])
        with inp_c1:
            new_name = st.text_input("Company Name", value=st.session_state.company_name, key="co_name_input", placeholder="e.g. Tata Steel Ltd")
            if new_name != st.session_state.company_name:
                st.session_state.company_name = new_name
        with inp_c2:
            new_y0 = st.number_input("Y0 Revenue (₹ Cr)", min_value=1.0, max_value=500000.0,
                value=float(a.get("y0_rev", 600.0)), step=50.0, format="%.0f", key="y0_rev_input")
            a["y0_rev"] = new_y0
        st.markdown("<span style='font-family:Syne,sans-serif;font-size:0.68rem;color:#2a4a6a;text-transform:uppercase;letter-spacing:0.1em;font-weight:700;'>Assumptions</span>", unsafe_allow_html=True)

        c1,c2,c3 = st.columns(3)
        with c1:
            st.markdown("<div style='font-family:Syne,sans-serif;font-size:0.7rem;color:#444455;margin-bottom:0.3rem;'>Revenue Growth %</div>", unsafe_allow_html=True)
            for i in range(5):
                a["rev_growth"][i] = st.slider(f"Y{i+1}", 0.0, 30.0, a["rev_growth"][i]*100, 0.5, key=f"rg{i}", label_visibility="visible") / 100
        with c2:
            st.markdown("<div style='font-family:Syne,sans-serif;font-size:0.7rem;color:#444455;margin-bottom:0.3rem;'>COGS % of Revenue</div>", unsafe_allow_html=True)
            for i in range(5):
                a["cogs_pct"][i] = st.slider(f"Y{i+1} ", 55.0, 85.0, a["cogs_pct"][i]*100, 0.5, key=f"cg{i}", label_visibility="visible") / 100
            a["interest_rate"] = st.slider("Interest Rate %", 4.0, 15.0, a["interest_rate"]*100, 0.25, key="ir") / 100
            a["tax_rate"] = st.slider("Tax Rate %", 15.0, 35.0, a["tax_rate"]*100, 0.5, key="tr") / 100
        with c3:
            st.markdown("<div style='font-family:Syne,sans-serif;font-size:0.7rem;color:#444455;margin-bottom:0.3rem;'>Capex & Working Capital</div>", unsafe_allow_html=True)
            for i in range(5):
                a["capex_pct"][i] = st.slider(f"Y{i+1}  ", 2.0, 15.0, a["capex_pct"][i]*100, 0.25, key=f"cp{i}", label_visibility="visible") / 100
            a["rec_days"] = st.slider("Receivable Days", 30, 120, int(a["rec_days"]), 1, key="rd")
            a["inv_days"] = st.slider("Inventory Days",  30, 150, int(a["inv_days"]), 1, key="id")
            a["pay_days"] = st.slider("Payable Days",    20, 100, int(a["pay_days"]), 1, key="pd")
            a["debt_repay"] = st.slider("Debt Repay ₹Cr", 10.0, 50.0, a["debt_repay"], 2.5, key="dr")

        if st.button("⟳  Recalculate", key="rcalc"):
            st.session_state.model = build_model(a); st.rerun()
        m = st.session_state.model
        inc, cf, rat = m["income"], m["cf"], m["ratios"]
    else:
        st.session_state.custom_mode = False
        st.session_state.company_name = "Arjun Steel & Engineering Ltd"
        st.session_state.model = build_model()
        m = st.session_state.model
        inc, cf, rat = m["income"], m["cf"], m["ratios"]

    st.markdown("<div style='height:0.6rem;'></div>", unsafe_allow_html=True)

    # KPI strip
    k1,k2,k3,k4,k5 = st.columns(5)
    a_k = st.session_state.custom_a if st.session_state.custom_mode else DEFAULT_ASSUMPTIONS
    y0_base_k = a_k.get("y0_rev", Y0["revenue"])
    cagr = (inc["revenue"][-1]/y0_base_k)**0.2 - 1
    with k1: st.metric("Revenue Y5", f"₹{inc['revenue'][-1]:.0f} Cr", f"{cagr*100:.1f}% CAGR")
    y0_ebm_k = Y0['ebitda']/Y0['revenue']  # always use original margins for delta (structural)
    with k2: st.metric("EBITDA Margin Y5", pct(inc["ebitda_margin"][-1]), f"+{(inc['ebitda_margin'][-1]-y0_ebm_k)*100:.1f}pp")
    with k3: st.metric("Net Income Y5", f"₹{inc['net_income'][-1]:.0f} Cr", f"vs ₹{Y0['net_income']:.0f} Cr Y0")
    with k4: st.metric("Operating CF Y5", f"₹{cf['operating_cf'][-1]:.0f} Cr")
    with k5:
        nd = rat["nd_ebitda"][-1]
        st.metric("Net Debt/EBITDA", f"{nd:.2f}x", "Net cash" if nd<0 else "")

    # Revenue chart
    st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)
    rev_all = [y0_base_k] + inc["revenue"]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=YEARS, y=rev_all,
        marker_color=["#1a3a5a"]+["#3a5a7a"]*5,
        marker_line_color=["#c9a96e"]*6, marker_line_width=1,
        text=[f"₹{v:.0f}" for v in rev_all], textposition="outside",
        textfont=dict(color="#c9a96e", size=11, family="DM Mono"),
    ))
    cagr_label = f"5Y CAGR: {cagr*100:.1f}%"
    fig.add_annotation(x=4.5, y=max(rev_all)*1.1, text=cagr_label, showarrow=False,
        font=dict(color="#4ab87a",size=11,family="Syne"),
        bgcolor="rgba(74,184,122,0.08)", bordercolor="#4ab87a", borderwidth=1, borderpad=5)
    fig.update_layout(**dark_layout(
        title=dict(text="Revenue (₹ Crores)", font=dict(color="#555566",size=11,family="Syne"),x=0),
        yaxis=dict(showgrid=True,gridcolor="#161622",tickfont=dict(color="#555566",size=10)),
    ))
    st.plotly_chart(fig, use_container_width=True, key="rev_chart")

    a_cur = st.session_state.custom_a if st.session_state.custom_mode else DEFAULT_ASSUMPTIONS
    y0r_ov = a_cur.get("y0_rev", Y0["revenue"])
    st.markdown(f"""<div class='ghost-block'>
      <span class='gl'>/ghost</span>
      <p>Revenue grows from ₹{y0r_ov:.0f} Cr to ₹{inc['revenue'][-1]:.0f} Cr over five years. EBITDA margins expand as fixed costs spread over a larger revenue base — operating leverage. Every assumption you move flows through all three statements simultaneously. That's what makes this a <em>model</em> rather than a spreadsheet.</p>
    </div>""", unsafe_allow_html=True)


# ─── TAB 2: INCOME STATEMENT ─────────────────────────────────────────────────
def tab_income():
    m = st.session_state.model
    inc = m["income"]
    yrs = m["years"]

    # Dynamic Y0 values — scale from base_rev if custom mode
    a_cur = st.session_state.custom_a if st.session_state.custom_mode else DEFAULT_ASSUMPTIONS
    y0_base = a_cur.get("y0_rev", Y0["revenue"])
    sc = y0_base / Y0["revenue"]
    # Scaled Y0 P&L values for the Y0 Hist column
    y0d = {
        "revenue": y0_base,
        "cogs":    Y0["cogs"]    * sc,
        "gross":   Y0["gross"]   * sc,
        "rd":      Y0["rd"]      * sc,
        "sga":     Y0["sga"]     * sc,
        "ebitda":  Y0["ebitda"]  * sc,
        "da":      Y0["da"]      * sc,
        "ebit":    Y0["ebit"]    * sc,
        "interest":Y0["interest"]* sc,
        "other_inc":Y0["other_inc"]* sc,
        "ebt":     Y0["ebt"]     * sc,
        "tax":     Y0["tax"]     * sc,
        "net_income":Y0["net_income"]*sc,
    }

    hdr = "<thead><tr><th>₹ Crores</th><th style='color:#2a4a6a;'>Y0 Hist</th>" + "".join(f"<th>{y}</th>" for y in yrs) + "</tr></thead>"

    def row(label, y0v, vals, cls="", color_fn=None):
        y0td = f"<td style='color:#2a4a6a;'>{cr(y0v)}</td>"
        tds = ""
        for v in vals:
            style = ""
            if color_fn: style = f"color:{color_fn(v)};"
            elif v < 0: style = "color:#e05c6c;"
            tds += f"<td style='{style}'>{cr(v)}</td>"
        return f"<tr class='{cls}'><td>{label}</td>{y0td}{tds}</tr>"

    def mrow(label, y0m, vals):
        y0td = f"<td style='color:#333344;font-style:italic;'>{pct(y0m)}</td>"
        tds = "".join(f"<td style='color:#333344;font-style:italic;'>{pct(v)}</td>" for v in vals)
        return f"<tr class='mrg'><td style='padding-left:1.2rem;color:#333344;font-size:0.7rem;'>{'↳ Margin'}</td>{y0td}{tds}</tr>"

    def gold(v): return "#c9a96e"
    def green(v): return "#4ab87a"

    html = f"""<table class='fin-table'>{hdr}<tbody>
    <tr class='sh'><td colspan='7'>Revenue</td></tr>
    {row('Revenue', y0d['revenue'], inc['revenue'], color_fn=lambda v:'#e8e4dc')}
    <tr class='sh'><td colspan='7'>Cost of Goods Sold</td></tr>
    {row('COGS', y0d['cogs'], inc['cogs'])}
    {row('Gross Profit', y0d['gross'], inc['gross'], cls='sub', color_fn=gold)}
    {mrow('', y0d['gross']/y0d['revenue'], inc['gross_margin'])}
    <tr class='sh'><td colspan='7'>Operating Expenses</td></tr>
    {row('R&D', y0d['rd'], inc['rd'])}
    {row('SG&A', y0d['sga'], inc['sga'])}
    {row('EBITDA', y0d['ebitda'], inc['ebitda'], cls='sub', color_fn=gold)}
    {mrow('', y0d['ebitda']/y0d['revenue'], inc['ebitda_margin'])}
    {row('D&A', y0d['da'], inc['da'])}
    {row('EBIT', y0d['ebit'], inc['ebit'], cls='sub', color_fn=gold)}
    {mrow('', y0d['ebit']/y0d['revenue'], inc['ebit_margin'])}
    <tr class='sh'><td colspan='7'>Below the Line</td></tr>
    {row('Interest Expense', y0d['interest'], inc['interest'])}
    {row('Other Income', y0d['other_inc'], [v*sc for v in [1.0]*5], color_fn=lambda v:'#b0ac9f')}
    {row('EBT', y0d['ebt'], inc['ebt'], cls='sub', color_fn=gold)}
    {row('Tax', y0d['tax'], inc['tax'])}
    {row('Net Income', y0d['net_income'], inc['net_income'], cls='tot', color_fn=green)}
    {mrow('', y0d['net_income']/y0d['revenue'], inc['net_margin'])}
    </tbody></table>"""

    st.markdown(tbl_wrap(html), unsafe_allow_html=True)
    st.markdown("<div style='height:0.8rem;'></div>", unsafe_allow_html=True)

    # Dual axis chart — Y0 bar uses actual base_rev (scaled)
    rev_all = [y0_base] + inc["revenue"]
    ebm_all = [y0d['ebitda']/y0d['revenue']] + inc["ebitda_margin"]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=YEARS, y=rev_all, name="Revenue",
        marker_color=["#1a3a5a"]+["#3a5a7a"]*5, yaxis="y1"))
    fig.add_trace(go.Scatter(x=YEARS, y=[v*100 for v in ebm_all], name="EBITDA Margin %",
        line=dict(color="#c9a96e",width=2.5), mode="lines+markers",
        marker=dict(size=5,color="#c9a96e"), yaxis="y2"))
    fig.update_layout(**dark_layout(
        title=dict(text="Revenue (₹ Cr) + EBITDA Margin", font=dict(color="#555566",size=11,family="Syne"),x=0),
        yaxis=dict(gridcolor="#161622",tickfont=dict(color="#555566",size=10)),
        yaxis2=dict(overlaying="y",side="right",ticksuffix="%",
                    tickfont=dict(color="#c9a96e",size=10),showgrid=False),
        showlegend=True,
        legend=dict(font=dict(color="#555566",size=10),bgcolor="rgba(0,0,0,0)",x=0.01,y=0.99),
    ))
    st.plotly_chart(fig, use_container_width=True, key="is_chart")

    a_used = st.session_state.custom_a if st.session_state.custom_mode else DEFAULT_ASSUMPTIONS
    y0r = a_used.get("y0_rev", Y0["revenue"])
    cagr_is = (inc['revenue'][-1]/y0r)**0.2 - 1
    y0_ebm = (Y0['ebitda']/Y0['revenue'])*100
    st.markdown(f"""<div class='ghost-block'>
      <span class='gl'>/ghost</span>
      <p>Revenue compounds at {cagr_is*100:.1f}% CAGR — ₹{y0r:.0f} Cr to ₹{inc['revenue'][-1]:.0f} Cr. EBITDA margins expand from {y0_ebm:.0f}% to {inc['ebitda_margin'][-1]*100:.0f}% as operating leverage kicks in. Net income grows to ₹{inc['net_income'][-1]:.0f} Cr — earnings power that is compounding, not eroding.</p>
    </div>""", unsafe_allow_html=True)


# ─── TAB 3: BALANCE SHEET ────────────────────────────────────────────────────
def tab_bs():
    m = st.session_state.model
    bs = m["bs"]
    yrs = m["years"]

    # Year selector + balance check inline
    yr_col, chk_col = st.columns([2,5])
    with yr_col:
        yr_sel = st.selectbox("Inspect year", ["All"]+yrs, key="bs_yr")
    with chk_col:
        chk = bs["check"]
        max_err = max(abs(c) for c in chk)
        if max_err < 0.01:
            st.markdown(f"<div style='background:rgba(74,184,122,0.07);border:1px solid rgba(74,184,122,0.2);border-radius:6px;padding:0.6rem 1rem;margin-top:0.4rem;'><span style='font-family:\"DM Mono\",monospace;font-size:0.82rem;color:#4ab87a;font-weight:700;'>✅ Assets = L+E in all 5 periods &nbsp;·&nbsp; CHECK = 0.0000</span></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='background:rgba(224,92,108,0.07);border:1px solid rgba(224,92,108,0.2);border-radius:6px;padding:0.6rem 1rem;margin-top:0.4rem;'><span style='font-family:\"DM Mono\",monospace;font-size:0.82rem;color:#e05c6c;font-weight:700;'>❌ CHECK ERROR: {max_err:.4f}</span></div>", unsafe_allow_html=True)

    if yr_sel != "All":
        idx = yrs.index(yr_sel)
        ta = bs["total_assets"][idx]; tle = bs["total_le"][idx]
        st.markdown(f"<div style='font-family:\"DM Mono\",monospace;font-size:0.85rem;color:#b0ac9f;margin:0.5rem 0 0.8rem;'>Assets <span style='color:#c9a96e;'>{cr(ta)}</span> = L+E <span style='color:#c9a96e;'>{cr(tle)}</span> <span style='color:#4ab87a;'>✅</span></div>", unsafe_allow_html=True)

    y0ca = Y0["cash"]+Y0["receivables"]+Y0["inventory"]+Y0["prepaid"]
    y0cl = Y0["payables"]+Y0["accrued"]+Y0["current_debt"]
    y0tl = y0cl+Y0["lt_debt"]+Y0["deferred_tax"]
    y0eq = Y0["share_capital"]+Y0["retained_earn"]

    hdr = "<thead><tr><th>₹ Crores</th><th style='color:#2a4a6a;'>Y0 Hist</th>"+"".join(f"<th>{y}</th>" for y in yrs)+"</tr></thead>"

    def brow(label, y0v, key, cls=""):
        vals = bs[key]
        y0td = f"<td style='color:#2a4a6a;'>{cr(y0v)}</td>"
        tds = "".join(f"<td>{cr(v)}</td>" for v in vals)
        return f"<tr class='{cls}'><td>{label}</td>{y0td}{tds}</tr>"

    def bsum(label, y0v, vals, cls="sub", color="#c9a96e"):
        y0td = f"<td style='color:#2a4a6a;'>{cr(y0v)}</td>"
        tds = "".join(f"<td style='color:{color};font-weight:600;'>{cr(v)}</td>" for v in vals)
        return f"<tr class='{cls}'><td><b>{label}</b></td>{y0td}{tds}</tr>"

    html = f"""<table class='fin-table'>{hdr}<tbody>
    <tr class='sh'><td colspan='7'>ASSETS</td></tr>
    <tr class='sh'><td colspan='7' style='padding-left:1rem;'>Current Assets</td></tr>
    {brow('Cash & Equivalents', Y0['cash'], 'cash')}
    {brow('Accounts Receivable', Y0['receivables'], 'receivables')}
    {brow('Inventory', Y0['inventory'], 'inventory')}
    {brow('Prepaid & Other', Y0['prepaid'], 'prepaid')}
    {bsum('Total Current Assets', y0ca, bs['current_assets'])}
    <tr class='sh'><td colspan='7' style='padding-left:1rem;'>Non-Current Assets</td></tr>
    {brow('Net PP&E', Y0['net_ppe'], 'net_ppe')}
    {brow('Intangibles', Y0['intangibles'], 'intangibles')}
    {bsum('TOTAL ASSETS', Y0['total_assets'], bs['total_assets'], cls='tot', color='#e8ca90')}
    <tr class='sh'><td colspan='7'>LIABILITIES</td></tr>
    <tr class='sh'><td colspan='7' style='padding-left:1rem;'>Current Liabilities</td></tr>
    {brow('Accounts Payable', Y0['payables'], 'payables')}
    {brow('Accrued Liabilities', Y0['accrued'], 'accrued')}
    {brow('Current Portion — Debt', Y0['current_debt'], 'current_debt')}
    {bsum('Total Current Liabilities', y0cl, bs['current_liab'])}
    <tr class='sh'><td colspan='7' style='padding-left:1rem;'>Non-Current Liabilities</td></tr>
    {brow('Long-Term Debt', Y0['lt_debt'], 'lt_debt')}
    {brow('Deferred Tax Liability', Y0['deferred_tax'], 'deferred_tax')}
    {bsum('Total Liabilities', y0tl, bs['total_liab'])}
    <tr class='sh'><td colspan='7'>EQUITY</td></tr>
    {brow('Share Capital', Y0['share_capital'], 'share_capital')}
    {brow('Retained Earnings', Y0['retained_earn'], 'retained_earn')}
    {bsum('Total Equity', y0eq, bs['total_equity'])}
    {bsum('TOTAL L + E', y0tl+y0eq, bs['total_le'], cls='tot', color='#e8ca90')}
    <tr class='sh'><td colspan='7'>CHECK</td></tr>
    <tr><td style='color:#4ab87a;font-family:"DM Mono",monospace;'>Assets − (L+E)</td>
      <td style='color:#2a4a6a;'>0.00</td>
      {"".join(f'<td class=\"chk\">{v:.4f}</td>' for v in bs['check'])}
    </tr></tbody></table>"""

    st.markdown(tbl_wrap(html), unsafe_allow_html=True)
    st.markdown("<div style='height:0.8rem;'></div>", unsafe_allow_html=True)

    # Asset composition chart
    rev_all_c = [Y0["cash"]]+bs["cash"]
    rev_all_r = [Y0["receivables"]]+bs["receivables"]
    rev_all_i = [Y0["inventory"]]+bs["inventory"]
    rev_all_p = [Y0["net_ppe"]]+bs["net_ppe"]
    rev_all_o = [Y0["prepaid"]+Y0["intangibles"]]+[bs["prepaid"][i]+bs["intangibles"][i] for i in range(5)]
    fig = go.Figure()
    for label,vals,color in [("Cash",rev_all_c,"#4ab87a"),("Receivables",rev_all_r,"#c9a96e"),
                               ("Inventory",rev_all_i,"#e0a04a"),("Net PP&E",rev_all_p,"#3a5a7a"),("Other",rev_all_o,"#333344")]:
        fig.add_trace(go.Bar(x=YEARS,y=vals,name=label,marker_color=color))
    fig.update_layout(**dark_layout(
        barmode="stack",
        title=dict(text="Total Assets Composition (₹ Crores)",font=dict(color="#555566",size=11,family="Syne"),x=0),
        showlegend=True,
        legend=dict(font=dict(color="#666677",size=10),bgcolor="rgba(0,0,0,0)",orientation="h",y=-0.18),
    ))
    st.plotly_chart(fig, use_container_width=True, key="bs_chart")

    st.markdown(f"""<div class='ghost-block'>
      <span class='gl'>/ghost</span>
      <p>The balance sheet has to balance — it's an accounting identity. Net debt falls from ₹130 Cr to a net cash position by Y5 as operating cash flows retire the term loan. PP&E grows from ₹330 Cr to ₹{bs['net_ppe'][-1]:.0f} Cr — the company is investing in productive capacity while simultaneously de-levering.</p>
    </div>""", unsafe_allow_html=True)


# ─── TAB 4: CASH FLOW ────────────────────────────────────────────────────────
def tab_cf():
    m = st.session_state.model
    cf = m["cf"]; inc = m["income"]
    yrs = m["years"]

    hdr = "<thead><tr><th>₹ Crores</th><th style='color:#2a4a6a;'>Y0 Hist</th>"+"".join(f"<th>{y}</th>" for y in yrs)+"</tr></thead>"

    def crow(label, y0v, vals, pos_color="#b0ac9f"):
        y0td = f"<td style='color:#2a4a6a;'>{cr(y0v)}</td>"
        tds = "".join(f"<td style='color:{'#e05c6c' if v<0 else pos_color};'>{cr(v)}</td>" for v in vals)
        return f"<tr><td>{label}</td>{y0td}{tds}</tr>"

    def csub(label, y0v, vals, color="#c9a96e"):
        y0td = f"<td style='color:#2a4a6a;'>{cr(y0v)}</td>"
        tds = "".join(f"<td style='color:{color};font-weight:600;'>{cr(v)}</td>" for v in vals)
        return f"<tr class='sub'><td><b>{label}</b></td>{y0td}{tds}</tr>"

    html = f"""<table class='fin-table'>{hdr}<tbody>
    <tr class='sh'><td colspan='7'>OPERATING ACTIVITIES</td></tr>
    {crow('Net Income', Y0['net_income'], cf['net_income'], pos_color="#b0ac9f")}
    {crow('+ D&A Add-back', abs(Y0['da']), cf['da_addback'], pos_color="#b0ac9f")}
    {crow('Δ Net Working Capital', 0.0, cf['delta_nwc'])}
    {crow('Δ Deferred Tax', 0.0, cf['d_deferred_tax'], pos_color="#b0ac9f")}
    {crow('Δ Accruals', 0.0, cf['d_accrued'], pos_color="#b0ac9f")}
    {csub('Operating Cash Flow', Y0['operating_cf'], cf['operating_cf'], color="#c9a96e")}
    <tr class='sh'><td colspan='7'>INVESTING ACTIVITIES</td></tr>
    {crow('Capital Expenditure', Y0['investing_cf'], cf['investing_cf'])}
    {csub('Investing Cash Flow', Y0['investing_cf'], cf['investing_cf'], color="#e05c6c")}
    <tr class='sh'><td colspan='7'>FINANCING ACTIVITIES</td></tr>
    {crow('Debt Repayment', Y0['financing_cf'], cf['financing_cf'])}
    {csub('Financing Cash Flow', Y0['financing_cf'], cf['financing_cf'], color="#e05c6c")}
    <tr class='sh'><td colspan='7'>CASH POSITION</td></tr>
    {crow('Beginning Cash', Y0['beg_cash'], cf['beg_cash'], pos_color="#b0ac9f")}
    <tr class='tot'><td><b>Ending Cash</b></td><td style='color:#2a4a6a;'>{cr(Y0['end_cash'])}</td>
      {"".join(f'<td style=\"color:#4ab87a;font-weight:700;\">{cr(v)}</td>' for v in cf['end_cash'])}
    </tr>
    <tr class='sh'><td colspan='7'>FREE CASH FLOW</td></tr>
    <tr><td><b>FCFF</b> <span style='color:#333344;font-size:0.7rem;'>(to Firm)</span></td><td style='color:#2a4a6a;'>—</td>
      {"".join(f'<td style=\"color:#c9a96e;font-weight:600;\">{cr(v)}</td>' for v in cf['fcff'])}
    </tr>
    <tr><td><b>FCFE</b> <span style='color:#333344;font-size:0.7rem;'>(to Equity)</span></td><td style='color:#2a4a6a;'>—</td>
      {"".join(f'<td style=\"color:#4ab87a;font-weight:600;\">{cr(v)}</td>' for v in cf['fcfe'])}
    </tr>
    </tbody></table>"""

    st.markdown(tbl_wrap(html), unsafe_allow_html=True)
    st.markdown("<div style='height:0.8rem;'></div>", unsafe_allow_html=True)

    fig = go.Figure()
    fig.add_trace(go.Bar(x=m["years"],y=cf["operating_cf"],name="Operating CF",marker_color="#4ab87a"))
    fig.add_trace(go.Bar(x=m["years"],y=cf["investing_cf"],name="Investing CF",marker_color="#e05c6c"))
    fig.add_trace(go.Bar(x=m["years"],y=cf["financing_cf"],name="Financing CF",marker_color="#e0a04a"))
    fig.add_trace(go.Scatter(x=m["years"],y=cf["fcff"],name="FCFF",
        line=dict(color="#c9a96e",width=2.5,dash="dash"),mode="lines+markers",marker=dict(size=5)))
    fig.update_layout(**dark_layout(
        barmode="group",
        title=dict(text="Cash Flow Breakdown + FCFF (₹ Crores)",font=dict(color="#555566",size=11,family="Syne"),x=0),
        showlegend=True,
        legend=dict(font=dict(color="#666677",size=10),bgcolor="rgba(0,0,0,0)",orientation="h",y=-0.18),
    ))
    st.plotly_chart(fig, use_container_width=True, key="cf_chart")

    st.markdown(f"""<div class='ghost-block'>
      <span class='gl'>Technical</span>
      <p>FCFF = Operating CF + Interest×(1−Tax). In Y1: ₹{cf['operating_cf'][0]:.1f} Cr + ₹{abs(inc['interest'][0]):.1f}×0.75 = ₹{cf['fcff'][0]:.1f} Cr. Grows to ₹{cf['fcff'][-1]:.1f} Cr by Y5 as margins expand and working capital needs stabilise.</p>
    </div>
    <div class='ghost-block'>
      <span class='gl'>/ghost</span>
      <p>FCFF is the cash the business generates before it repays lenders — enterprise-level cash flow. A DCF model discounts it to get company value. FCFE is what's left for equity holders after the bank gets paid. Both grow every year. That's a business becoming more valuable, not less.</p>
    </div>""", unsafe_allow_html=True)


# ─── TAB 5: SCHEDULES ────────────────────────────────────────────────────────
def tab_schedules():
    m = st.session_state.model
    ppe, debt, wc = m["ppe"], m["debt"], m["wc"]
    yrs = m["years"]

    s1,s2,s3 = st.tabs(["PP&E Roll-forward","Debt Schedule","Working Capital"])

    with s1:
        hdr = "<thead><tr><th>₹ Crores</th><th style='color:#2a4a6a;'>Y0</th>"+"".join(f"<th>{y}</th>" for y in yrs)+"</tr></thead>"
        html = f"""<table class='fin-table'>{hdr}<tbody>
        <tr class='sh'><td colspan='7'>GROSS PP&E</td></tr>
        <tr><td>Opening Gross PP&E</td><td style='color:#2a4a6a;'>{cr(Y0['gross_ppe'])}</td>{"".join(f'<td>{cr(v)}</td>' for v in ppe['gross_open'])}</tr>
        <tr><td>  + Capex</td><td style='color:#2a4a6a;'>30.0</td>{"".join(f'<td style=\"color:#c9a96e;\">{cr(v)}</td>' for v in ppe['capex'])}</tr>
        <tr class='sub'><td><b>Closing Gross PP&E</b></td><td style='color:#2a4a6a;'>{cr(Y0['gross_ppe'])}</td>{"".join(f'<td style=\"color:#c9a96e;\">{cr(v)}</td>' for v in ppe['gross_close'])}</tr>
        <tr class='sh'><td colspan='7'>ACCUMULATED DEPRECIATION</td></tr>
        <tr><td>Opening Accum. Dep.</td><td style='color:#2a4a6a;'>{cr(abs(Y0['accum_dep']))}</td>{"".join(f'<td>{cr(v)}</td>' for v in ppe['accum_open'])}</tr>
        <tr><td>  + D&A Charge</td><td style='color:#2a4a6a;'>{cr(abs(Y0['da']))}</td>{"".join(f'<td>{cr(v)}</td>' for v in ppe['da_charge'])}</tr>
        <tr class='sub'><td><b>Closing Accum. Dep.</b></td><td style='color:#2a4a6a;'>{cr(abs(Y0['accum_dep']))}</td>{"".join(f'<td>{cr(v)}</td>' for v in ppe['accum_close'])}</tr>
        <tr class='tot'><td><b>Net PP&E</b></td><td style='color:#2a4a6a;'>{cr(Y0['net_ppe'])}</td>{"".join(f'<td style=\"color:#c9a96e;font-weight:700;\">{cr(v)}</td>' for v in ppe['net_ppe'])}</tr>
        </tbody></table>"""
        st.markdown(tbl_wrap(html), unsafe_allow_html=True)
        st.markdown("<div style='height:0.8rem;'></div>", unsafe_allow_html=True)

        g_all=[Y0["gross_ppe"]]+ppe["gross_close"]; n_all=[Y0["net_ppe"]]+ppe["net_ppe"]
        fig=go.Figure()
        fig.add_trace(go.Bar(x=YEARS,y=g_all,name="Gross PP&E",marker_color="#1a3a5a"))
        fig.add_trace(go.Bar(x=YEARS,y=n_all,name="Net PP&E",marker_color="#3a5a7a"))
        fig.update_layout(**dark_layout(barmode="group",title=dict(text="Gross vs Net PP&E (₹ Crores)",font=dict(color="#555566",size=11,family="Syne"),x=0),showlegend=True,legend=dict(font=dict(color="#666677",size=10),bgcolor="rgba(0,0,0,0)")))
        st.plotly_chart(fig,use_container_width=True,key="ppe_chart")
        st.markdown(f"""<div class='ghost-block'><span class='gl'>/ghost</span><p>Arjun Steel invests ₹{ppe['capex'][0]:.0f}–{ppe['capex'][-1]:.0f} Cr per year in equipment. Net PP&E grows more slowly than gross PP&E — the gap is accumulated depreciation building up. That gap tells you how aged the asset base is. If it keeps widening without capex, the productive base is eroding.</p></div>""", unsafe_allow_html=True)

    with s2:
        hdr = "<thead><tr><th>₹ Crores</th><th style='color:#2a4a6a;'>Y0</th>"+"".join(f"<th>{y}</th>" for y in yrs)+"</tr></thead>"
        html = f"""<table class='fin-table'>{hdr}<tbody>
        <tr class='sh'><td colspan='7'>DEBT SCHEDULE</td></tr>
        <tr><td>Opening Debt Balance</td><td style='color:#2a4a6a;'>{cr(Y0['lt_debt']+Y0['current_debt'])}</td>{"".join(f'<td>{cr(v)}</td>' for v in debt['opening'])}</tr>
        <tr><td>  Mandatory Repayment</td><td style='color:#e05c6c;'>{cr(Y0['financing_cf'])}</td>{"".join(f'<td style=\"color:#e05c6c;\">{cr(v)}</td>' for v in debt['repayment'])}</tr>
        <tr class='sub'><td><b>Closing Debt Balance</b></td><td style='color:#2a4a6a;'>{cr(Y0['lt_debt']+Y0['current_debt'])}</td>{"".join(f'<td style=\"color:#c9a96e;\">{cr(v)}</td>' for v in debt['closing'])}</tr>
        <tr><td>Average Debt Balance</td><td style='color:#2a4a6a;'>—</td>{"".join(f'<td>{cr(v)}</td>' for v in debt['avg'])}</tr>
        <tr class='tot'><td><b>Interest Expense (9.0%)</b></td><td style='color:#2a4a6a;'>{cr(Y0['interest'])}</td>{"".join(f'<td style=\"color:#e05c6c;font-weight:700;\">{cr(v)}</td>' for v in debt['interest'])}</tr>
        </tbody></table>"""
        st.markdown(tbl_wrap(html), unsafe_allow_html=True)
        st.markdown("<div style='height:0.8rem;'></div>", unsafe_allow_html=True)

        d_all=[Y0["lt_debt"]+Y0["current_debt"]]+debt["closing"]
        i_all=[abs(Y0["interest"])]+[abs(v) for v in debt["interest"]]
        fig=go.Figure()
        fig.add_trace(go.Bar(x=YEARS,y=d_all,name="Total Debt",marker_color="#1a3a5a"))
        fig.add_trace(go.Scatter(x=YEARS,y=i_all,name="Interest Expense",line=dict(color="#e05c6c",width=2.5),mode="lines+markers",marker=dict(size=5),yaxis="y2"))
        fig.update_layout(**dark_layout(title=dict(text="Debt Balance + Interest Expense",font=dict(color="#555566",size=11,family="Syne"),x=0),yaxis2=dict(overlaying="y",side="right",tickfont=dict(color="#e05c6c",size=10),showgrid=False),showlegend=True,legend=dict(font=dict(color="#666677",size=10),bgcolor="rgba(0,0,0,0)")))
        st.plotly_chart(fig,use_container_width=True,key="debt_chart")
        st.markdown(f"""<div class='ghost-block'><span class='gl'>/ghost</span><p>₹25 Cr repaid per year — total debt falls from ₹175 Cr to ₹{debt['closing'][-1]:.0f} Cr by Y5. Interest drops from ₹{abs(Y0['interest']):.0f} Cr to ₹{abs(debt['interest'][-1]):.1f} Cr. Lower debt → lower interest → higher net income → more cash to repay debt. A self-reinforcing loop.</p></div>""", unsafe_allow_html=True)

    with s3:
        hdr = "<thead><tr><th>₹ Crores</th><th style='color:#2a4a6a;'>Y0</th>"+"".join(f"<th>{y}</th>" for y in yrs)+"</tr></thead>"
        y0nwc=Y0["receivables"]+Y0["inventory"]-Y0["payables"]
        html = f"""<table class='fin-table'>{hdr}<tbody>
        <tr class='sh'><td colspan='7'>WORKING CAPITAL</td></tr>
        <tr><td>Accounts Receivable</td><td style='color:#2a4a6a;'>{cr(Y0['receivables'])}</td>{"".join(f'<td>{cr(v)}</td>' for v in wc['receivables'])}</tr>
        <tr><td>Inventory</td><td style='color:#2a4a6a;'>{cr(Y0['inventory'])}</td>{"".join(f'<td>{cr(v)}</td>' for v in wc['inventory'])}</tr>
        <tr><td>Accounts Payable</td><td style='color:#2a4a6a;'>{cr(Y0['payables'])}</td>{"".join(f'<td style=\"color:#e05c6c;\">{cr(v)}</td>' for v in wc['payables'])}</tr>
        <tr class='sub'><td><b>Net Working Capital</b></td><td style='color:#2a4a6a;'>{cr(y0nwc)}</td>{"".join(f'<td style=\"color:#c9a96e;\">{cr(v)}</td>' for v in wc['nwc'])}</tr>
        <tr class='tot'><td><b>Δ NWC (CF impact)</b></td><td style='color:#2a4a6a;'>—</td>{"".join(f'<td style=\"color:{"#4ab87a" if v>=0 else "#e05c6c"};font-weight:700;\">{cr(v)}</td>' for v in wc['delta_nwc'])}</tr>
        </tbody></table>"""
        st.markdown(tbl_wrap(html), unsafe_allow_html=True)
        st.markdown("<div style='height:0.8rem;'></div>", unsafe_allow_html=True)

        r_all=[Y0["receivables"]]+wc["receivables"]; i_all=[Y0["inventory"]]+wc["inventory"]; p_all=[Y0["payables"]]+wc["payables"]
        fig=go.Figure()
        fig.add_trace(go.Scatter(x=YEARS,y=r_all,name="Receivables",line=dict(color="#c9a96e",width=2),mode="lines+markers",marker=dict(size=5)))
        fig.add_trace(go.Scatter(x=YEARS,y=i_all,name="Inventory",line=dict(color="#e0a04a",width=2),mode="lines+markers",marker=dict(size=5)))
        fig.add_trace(go.Scatter(x=YEARS,y=p_all,name="Payables",line=dict(color="#e05c6c",width=2),mode="lines+markers",marker=dict(size=5)))
        fig.update_layout(**dark_layout(title=dict(text="Working Capital Trends (₹ Crores)",font=dict(color="#555566",size=11,family="Syne"),x=0),showlegend=True,legend=dict(font=dict(color="#666677",size=10),bgcolor="rgba(0,0,0,0)")))
        st.plotly_chart(fig,use_container_width=True,key="wc_chart")
        st.markdown(f"""<div class='ghost-block'><span class='gl'>/ghost</span><p>NWC grows with the business — receivables and inventory scale with revenue. Each year, the NWC build is a modest cash drag as Arjun Steel extends credit to customers and holds more stock than it defers to suppliers. Positive Δ NWC in the CF statement means NWC shrank (cash source). Negative means NWC grew (cash use).</p></div>""", unsafe_allow_html=True)


# ─── TAB 6: RATIOS & DOWNLOAD ────────────────────────────────────────────────
def tab_ratios():
    m = st.session_state.model
    rat = m["ratios"]; inc = m["income"]; cf = m["cf"]
    yrs = m["years"]

    lc, rc = st.columns([3,2])

    with lc:
        # Margins
        gm=[Y0["gross"]/Y0["revenue"]]+inc["gross_margin"]
        ebm=[Y0["ebitda"]/Y0["revenue"]]+inc["ebitda_margin"]
        nm=[Y0["net_income"]/Y0["revenue"]]+inc["net_margin"]
        fig=go.Figure()
        for label,vals,color in [("Gross Margin",gm,"#c9a96e"),("EBITDA Margin",ebm,"#4ab87a"),("Net Margin",nm,"#3a5a7a")]:
            fig.add_trace(go.Scatter(x=YEARS,y=[v*100 for v in vals],name=label,line=dict(width=2),mode="lines+markers",marker=dict(size=4)))
        fig.update_layout(**dark_layout(title=dict(text="Profitability Margins (%)",font=dict(color="#555566",size=11,family="Syne"),x=0),yaxis=dict(ticksuffix="%"),showlegend=True,legend=dict(font=dict(color="#666677",size=10),bgcolor="rgba(0,0,0,0)",orientation="h",y=-0.22)))
        st.plotly_chart(fig,use_container_width=True,key="marg_chart")

        # Returns
        roe=[None]+rat["roe"]; roa=[None]+rat["roa"]; roce=[None]+rat["roce"]
        fig2=go.Figure()
        for label,vals,color in [("ROE",roe,"#c9a96e"),("ROA",roa,"#4ab87a"),("ROCE",roce,"#3a5a7a")]:
            fig2.add_trace(go.Scatter(x=YEARS,y=[v*100 if v else None for v in vals],name=label,line=dict(width=2),mode="lines+markers",marker=dict(size=4)))
        fig2.update_layout(**dark_layout(title=dict(text="Returns — ROE / ROA / ROCE (%)",font=dict(color="#555566",size=11,family="Syne"),x=0),yaxis=dict(ticksuffix="%"),showlegend=True,legend=dict(font=dict(color="#666677",size=10),bgcolor="rgba(0,0,0,0)",orientation="h",y=-0.22)))
        st.plotly_chart(fig2,use_container_width=True,key="ret_chart")

        # Credit
        fig3=go.Figure()
        fig3.add_trace(go.Bar(x=yrs[1:],y=rat["nd_ebitda"][1:],name="Net Debt/EBITDA",
            marker_color=["#1a3a5a" if v>0 else "#1a4a2a" for v in rat["nd_ebitda"][1:]]))
        fig3.add_trace(go.Scatter(x=yrs[1:],y=rat["int_cov"][1:],name="Interest Coverage",
            line=dict(color="#c9a96e",width=2.5),mode="lines+markers",marker=dict(size=5),yaxis="y2"))
        fig3.update_layout(**dark_layout(title=dict(text="Credit Metrics",font=dict(color="#555566",size=11,family="Syne"),x=0),
            yaxis2=dict(overlaying="y",side="right",tickfont=dict(color="#c9a96e",size=10),showgrid=False,title=dict(text="Coverage (x)",font=dict(color="#c9a96e",size=10))),
            showlegend=True,legend=dict(font=dict(color="#666677",size=10),bgcolor="rgba(0,0,0,0)",orientation="h",y=-0.22)))
        st.plotly_chart(fig3,use_container_width=True,key="cred_chart")

    with rc:
        st.markdown("<span style='font-family:Syne,sans-serif;font-size:0.68rem;font-weight:700;color:#2a4a6a;letter-spacing:0.12em;text-transform:uppercase;'>Y5 Snapshot</span>", unsafe_allow_html=True)
        st.markdown("<div style='height:0.3rem;'></div>", unsafe_allow_html=True)

        sections = [
            ("PROFITABILITY",[
                ("Gross Margin", pct(inc["gross_margin"][-1])),
                ("EBITDA Margin", pct(inc["ebitda_margin"][-1])),
                ("Net Margin", pct(inc["net_margin"][-1])),
            ]),
            ("RETURNS",[
                ("ROE", pct(rat["roe"][-1])),
                ("ROA", pct(rat["roa"][-1])),
                ("ROCE", pct(rat["roce"][-1])),
            ]),
            ("CREDIT",[
                ("Net Debt/EBITDA", f"{rat['nd_ebitda'][-1]:.2f}x"),
                ("Interest Coverage", f"{rat['int_cov'][-1]:.1f}x"),
            ]),
            ("CASH FLOW",[
                ("OCF/EBITDA", pct(rat["ocf_ebitda"][-1],0)),
                ("Capex/Revenue", pct(rat["capex_rev"][-1])),
                ("FCFF", cr(rat["fcff"][-1])),
                ("FCFE", cr(rat["fcfe"][-1])),
            ]),
        ]
        for section_name, rows in sections:
            st.markdown(f"<div style='font-family:Syne,sans-serif;font-size:0.63rem;font-weight:700;color:#2a4a6a;letter-spacing:0.1em;text-transform:uppercase;margin:0.8rem 0 0.25rem;border-top:1px solid #151520;padding-top:0.5rem;'>{section_name}</div>", unsafe_allow_html=True)
            for label, val in rows:
                st.markdown(f"<div style='display:flex;justify-content:space-between;padding:3px 0;border-bottom:1px solid #111118;'><span style='font-family:\"DM Mono\",monospace;font-size:0.74rem;color:#888880;'>{label}</span><span style='font-family:\"DM Mono\",monospace;font-size:0.74rem;color:#c9a96e;'>{val}</span></div>", unsafe_allow_html=True)

        # Download
        st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
        st.markdown("<span style='font-family:Syne,sans-serif;font-size:0.68rem;font-weight:700;color:#2a4a6a;letter-spacing:0.12em;text-transform:uppercase;'>Excel Template</span>", unsafe_allow_html=True)
        st.markdown("<div style='height:0.3rem;'></div>", unsafe_allow_html=True)
        st.markdown("""<div style='background:#111118;border:1px solid #191924;border-left:3px solid #c9a96e;border-radius:6px;padding:0.9rem;margin-bottom:0.7rem;'>
          <div style='font-family:Syne,sans-serif;font-weight:700;color:#c9a96e;font-size:0.82rem;'>3Statement_Template.xlsx</div>
          <div style='font-family:"DM Mono",monospace;font-size:0.7rem;color:#444455;margin:0.3rem 0;'>9 sheets · 514 formulas · zero errors · BS verified</div>
          <div style='font-family:Syne,sans-serif;font-size:0.72rem;color:#666677;line-height:1.55;'>IS · BS · CF · PP&E · Debt · WC · Assumptions · Ratios · Cover</div>
        </div>""", unsafe_allow_html=True)

        import os
        if os.path.exists("3Statement_Template.xlsx"):
            with open("3Statement_Template.xlsx","rb") as f:
                st.download_button("⬇ Download Excel Template", f,
                    "3Statement_Template.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True, key="xl_dl")
        else:
            st.markdown("<div style='background:rgba(58,90,122,0.08);border:1px solid rgba(58,90,122,0.2);border-radius:5px;padding:0.6rem;text-align:center;'><span style='font-family:Syne,sans-serif;font-size:0.72rem;color:#2a4a6a;'>Place 3Statement_Template.xlsx in app directory to enable download</span></div>", unsafe_allow_html=True)

    st.markdown(f"""<div class='ghost-block'>
      <span class='gl'>/ghost</span>
      <p>By Y5: net cash position, {pct(inc['ebitda_margin'][-1],0)} EBITDA margin, {pct(rat['roe'][-1],0)} ROE, {rat['int_cov'][-1]:.0f}x interest coverage. Margins expanding, debt shrinking, returns improving, cash compounding. The three statements got you here — the ratios just summarise the story the numbers are telling.</p>
    </div>""", unsafe_allow_html=True)


# ─── TERMINAL ────────────────────────────────────────────────────────────────
def render_terminal():
    render_nav()
    st.markdown("<hr>", unsafe_allow_html=True)

    t1,t2,t3,t4,t5,t6 = st.tabs([
        "Overview","Income Statement","Balance Sheet",
        "Cash Flow","Schedules","Ratios & Download"
    ])
    with t1: tab_overview()
    with t2: tab_income()
    with t3: tab_bs()
    with t4: tab_cf()
    with t5: tab_schedules()
    with t6: tab_ratios()

    st.markdown("<div style='margin-top:2rem;padding-top:0.6rem;border-top:1px solid #111118;text-align:center;'><span style='font-family:Syne,sans-serif;font-size:0.6rem;color:#1e1e2e;'>LinkDesk · Day 21 · 30 Days of AI Finance · Arjun Steel is fictional · Not investment advice</span></div>", unsafe_allow_html=True)


# ─── ROUTER ──────────────────────────────────────────────────────────────────
if st.session_state.page == "home":
    render_home()
else:
    render_terminal()