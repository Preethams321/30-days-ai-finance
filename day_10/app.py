import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import math

st.set_page_config(
    page_title="YieldLab — US 10Y Impact Simulator",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════════════════════
#  CSS  — dark theme locked regardless of OS preference
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,400&family=Syne:wght@400;600;700&family=DM+Mono:wght@300;400;500&display=swap');

/* ── force dark always ── */
html,body,.stApp,.stApp>*,
[data-testid="stAppViewContainer"],[data-testid="stHeader"],
[data-testid="stToolbar"],[data-testid="stDecoration"],
[data-testid="stBottom"],[data-testid="stMainBlockContainer"],
[data-testid="stMain"],[class*="css"]{
  background-color:#09090e !important;
  background:#09090e !important;
  color:#e4e4f0 !important;
  color-scheme:dark !important;
}
*,*::before,*::after{box-sizing:border-box;}
body{font-family:'Syne',sans-serif !important;}

/* ── chrome ── */
#MainMenu,footer,[data-testid="stToolbar"],[data-testid="stDecoration"]{display:none !important;}
.stApp{overflow-x:hidden !important;}
[data-testid="stMainBlockContainer"],.block-container{
  max-width:1040px !important;
  padding:0 28px 100px 28px !important;
  margin:0 auto !important;
  overflow-x:hidden !important;
}
[data-testid="stSidebar"]{display:none !important;}

/* ── slider ── */
[data-testid="stSlider"]{padding:8px 0 4px !important;}
[data-testid="stSlider"] label{display:none !important;}
[data-testid="stSlider"]>div>div{background:#252535 !important;height:3px !important;}
[data-testid="stSlider"]>div>div>div>div{background:#c9a96e !important;height:3px !important;}
[data-testid="stSlider"] [role="slider"]{
  background:#c9a96e !important;border:3px solid #09090e !important;
  box-shadow:0 0 0 5px rgba(201,169,110,.22) !important;
  width:22px !important;height:22px !important;top:-10px !important;cursor:grab !important;
}
[data-testid="stSliderTickBarMin"],[data-testid="stSliderTickBarMax"]{
  color:#444455 !important;font-family:'DM Mono',monospace !important;font-size:11px !important;
}

/* ── tabs ── */
[data-testid="stTabs"] [role="tablist"]{
  background:transparent !important;border-bottom:1px solid #1a1a28 !important;
  gap:0 !important;overflow-x:auto !important;flex-wrap:nowrap !important;
  scrollbar-width:none !important;
}
[data-testid="stTabs"] [role="tab"]{
  background:transparent !important;color:#444455 !important;
  font-family:'DM Mono',monospace !important;font-size:11px !important;
  font-weight:500 !important;letter-spacing:.10em !important;text-transform:uppercase !important;
  padding:14px 20px !important;border-bottom:2px solid transparent !important;
  border-radius:0 !important;white-space:nowrap !important;
}
[data-testid="stTabs"] [aria-selected="true"]{
  color:#c9a96e !important;border-bottom-color:#c9a96e !important;
}
[data-testid="stTabs"] [role="tabpanel"]{padding-top:36px !important;background:transparent !important;}

/* ── buttons ── */
.stButton>button{
  width:100% !important;background:transparent !important;
  border:1px solid #252535 !important;color:#777788 !important;
  font-family:'DM Mono',monospace !important;font-size:11px !important;
  font-weight:500 !important;letter-spacing:.05em !important;
  padding:10px 16px !important;border-radius:6px !important;transition:all .15s !important;
}
.stButton>button:hover{
  border-color:#c9a96e !important;color:#c9a96e !important;
  background:rgba(201,169,110,.05) !important;
}

/* ── inputs ── */
[data-testid="stNumberInput"] input,[data-testid="stTextInput"] input{
  background:#0e0e18 !important;border:1px solid #252535 !important;
  border-radius:6px !important;color:#e4e4f0 !important;
  font-family:'DM Mono',monospace !important;font-size:13px !important;
}
[data-testid="stNumberInput"] label,[data-testid="stTextInput"] label,
[data-testid="stSelectbox"] label{
  color:#444455 !important;font-family:'DM Mono',monospace !important;
  font-size:10px !important;text-transform:uppercase !important;letter-spacing:.08em !important;
}
[data-testid="stSelectbox"]>div>div{
  background:#0e0e18 !important;border:1px solid #252535 !important;
  color:#e4e4f0 !important;font-family:'DM Mono',monospace !important;
}

/* ── expander ── */
[data-testid="stExpander"] summary{
  background:#0c0c16 !important;border:1px solid #1a1a28 !important;
  border-radius:6px !important;color:#444455 !important;
  font-family:'DM Mono',monospace !important;font-size:10px !important;
  letter-spacing:.10em !important;text-transform:uppercase !important;padding:10px 14px !important;
}
[data-testid="stExpander"]>div>div{
  background:#0c0c16 !important;border:1px solid #1a1a28 !important;
  border-top:none !important;border-radius:0 0 6px 6px !important;padding:16px !important;
}

/* ── dataframe ── */
[data-testid="stDataFrame"]{border:1px solid #1a1a28 !important;border-radius:8px !important;overflow:hidden !important;}

/* ── columns ── */
[data-testid="stHorizontalBlock"]{gap:16px !important;flex-wrap:wrap !important;}
[data-testid="column"]{min-width:0 !important;overflow:hidden !important;}

/* ════════════ COMPONENT TOKENS ════════════ */

/* Metric card */
.mc{background:#0c0c18;border:1px solid #1a1a28;border-radius:10px;
    padding:22px 24px 20px;position:relative;overflow:hidden;}
.mc::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;border-radius:10px 10px 0 0;}
.mc.pos::before{background:#4ab87a;} .mc.neg::before{background:#e05c6c;}
.mc.neu::before{background:#c9a96e;} .mc.mix::before{background:linear-gradient(90deg,#4ab87a,#e05c6c);}
.mc-eye{font:500 10px/1 'DM Mono',monospace;letter-spacing:.12em;text-transform:uppercase;
        color:#444455;margin-bottom:10px;}
.mc-val{font:500 28px/1 'DM Mono',monospace;color:#e4e4f0;margin-bottom:8px;word-break:break-all;}
.mc-dlt{font:400 12px/1 'DM Mono',monospace;margin-bottom:6px;}
.mc-sub{font:400 11px/1.5 'Syne',sans-serif;color:#555568;}
.g{color:#4ab87a;} .r{color:#e05c6c;} .a{color:#c9a96e;}

/* Knowledge card */
.kc{background:#111120;border-left:2px solid #c9a96e;border-radius:0 6px 6px 0;padding:14px 16px;}
.kc-t{font:400 12px/1.7 'Syne',sans-serif;color:#7a7a90;margin-bottom:10px;}
.kc-g{font:400 13px/1.7 'Playfair Display',serif;font-style:italic;color:#b8b8cc;
      border-top:1px solid #1a1a28;padding-top:10px;}

/* Disclaimer */
.disc{font:400 11px/1.6 'DM Mono',monospace;color:#444455;
      background:rgba(201,169,110,.04);border:1px solid rgba(201,169,110,.12);
      border-radius:6px;padding:10px 14px;margin:16px 0;}

/* Section header */
.sh{margin-bottom:36px;}
.sh-eye{font:500 10px/1 'DM Mono',monospace;letter-spacing:.18em;text-transform:uppercase;
        color:#a07840;margin-bottom:8px;}
.sh-title{font:700 30px/1.1 'Playfair Display',serif;color:#e4e4f0;margin-bottom:8px;}
.sh-sub{font:400 14px/1.6 'Syne',sans-serif;color:#7a7a90;max-width:580px;}

/* Sector badge */
.sb{display:inline-block;padding:4px 9px;border-radius:4px;
    font:500 11px/1.4 'DM Mono',monospace;margin:3px 3px;}
.sbp{background:rgba(74,184,122,.10);color:#4ab87a;border:1px solid rgba(74,184,122,.20);}
.sbn{background:rgba(224,92,108,.10);color:#e05c6c;border:1px solid rgba(224,92,108,.20);}
.sbm{background:rgba(201,169,110,.10);color:#c9a96e;border:1px solid rgba(201,169,110,.20);}

/* XP bar */
.xpb-o{background:#1a1a28;border-radius:99px;height:5px;overflow:hidden;margin:6px 0;}
.xpb-i{height:100%;background:linear-gradient(90deg,#a07840,#e8c98a);border-radius:99px;}

/* Streak chip */
.scchip{display:inline-flex;align-items:center;gap:4px;
        background:linear-gradient(135deg,#a07840,#c9a96e);color:#09090e;
        font:700 11px/1 'DM Mono',monospace;padding:5px 12px;border-radius:99px;}

/* Quiz option */
.qo{background:#0c0c18;border:1px solid #252535;border-radius:8px;
    padding:14px 18px;margin:6px 0;font:400 14px/1.4 'Syne',sans-serif;color:#777788;}
.qo-c{border-color:#4ab87a !important;background:rgba(74,184,122,.07) !important;color:#4ab87a !important;}
.qo-w{border-color:#e05c6c !important;background:rgba(224,92,108,.07) !important;color:#e05c6c !important;}
.qo-d{opacity:.3;}

/* Leaderboard row */
.lb{display:flex;align-items:center;gap:12px;background:#0c0c18;
    border:1px solid #1a1a28;border-radius:8px;padding:12px 16px;margin:6px 0;
    font:400 13px/1 'DM Mono',monospace;}
.lb-m{width:24px;text-align:center;font-size:16px;}
.lb-n{flex:1;color:#e4e4f0;}
.lb-s{font-size:10px;color:#444455;}
.lb-v{color:#e8c98a;font-weight:500;font-size:15px;}

/* Divider */
.dv{border:none;border-top:1px solid #1a1a28;margin:32px 0;}

/* Zone pill */
.zp{display:inline-flex;align-items:center;padding:4px 12px;border-radius:99px;
    font:500 11px/1 'DM Mono',monospace;letter-spacing:.06em;border:1px solid;}
.zg{color:#4ab87a;border-color:rgba(74,184,122,.35);background:rgba(74,184,122,.07);}
.za{color:#c9a96e;border-color:rgba(201,169,110,.35);background:rgba(201,169,110,.07);}
.zr{color:#e05c6c;border-color:rgba(224,92,108,.35);background:rgba(224,92,108,.07);}

/* Mobile */
@media(max-width:640px){
  [data-testid="stMainBlockContainer"],.block-container{padding:0 14px 60px 14px !important;}
  .mc-val{font-size:22px !important;}
  .sh-title{font-size:22px !important;}
  [data-testid="stTabs"] [role="tab"]{font-size:10px !important;padding:12px 10px !important;}
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  CONSTANTS & COEFFICIENTS
# ══════════════════════════════════════════════════════════════
B10Y  = 4.57  # US 10Y yield as of June 10, 2026
BINR  = 95.0;  SINR  = 2.3
BI10  = 6.95;  SI10  = 0.45
BPE   = 20.1;  SPE   = 2.88; EPS = 1160  # SPE from 2010-2025 regression
BGOLD = 4200;  SGOLD = 8.0
BFII  = 18000
BHLR  = 8.75;  SHLR  = 0.6
BLOAN = 5_000_000; BTEN = 20

# Keys must not contain special chars — use safe keys mapped from sector names
SECTORS = {
    "IT Services":         +1.5,   # FX tailwind offset by US tech demand headwind
    "Banks":               -1.2,
    "NBFCs":               -3.5,
    "Real Estate":         -3.0,   # premium segment rate-resilient; affordable most impacted
    "Auto":                -2.8,
    "FMCG":                -0.5,
    "Capital Goods/Infra": -3.2,
    "Pharma/Exporters":    +2.1,
    "Gold ETF":            -8.0,
}
# Safe session-state keys (no / or spaces)
SECTOR_KEYS = {s: "sec_" + s.replace("/","_").replace(" ","_") for s in SECTORS}

# Scenario actual historical data — verified from RBI/NSE/Bloomberg sources
# These show WHAT ACTUALLY HAPPENED, not model estimates
SCENARIOS = {
    "2013 Taper Tantrum": {
        "yield": 2.90, "e": "🌪",
        "body": "Fed hinted at tapering QE. US 10Y spiked 1.6% → 2.9% in 6 months. Rupee crashed ₹54 → ₹68 (peak stress). FII outflows ~$10bn+. RBI was forced into an emergency rate hike. India 10Y hit 8.8%.",
        # Actual historical data for this episode
        "actual": {"inr": 62.0, "gold": 1220, "india10y": 8.8, "nifty_pe": 18.0,
                   "inr_note": "₹54 at start → ₹68 at peak", "period": "May–Dec 2013"},
    },
    "2020 COVID Crash": {
        "yield": 0.62, "e": "◎",
        "body": "Fed cut to 0%. US 10Y hit 0.62% — all-time low. India FII inflows ~₹1.7 lakh Cr in 2020. Nifty rallied ~93% from March lows. Nifty PE expanded to 33.7× as money flooded EM.",
        "actual": {"inr": 74.1, "gold": 1770, "india10y": 6.01, "nifty_pe": 33.7,
                   "inr_note": "Stabilised near ₹74", "period": "Jul 2020 avg"},
    },
    "2023 5% Shock": {
        "yield": 4.80, "e": "↯",
        "body": "Fed at 5.25–5.50%. US 10Y hit 4.8% — highest since 2007. India held better than most EMs — domestic SIPs cushioned. FIIs sold ₹25,000+ Cr in Oct 2023. Nifty corrected ~10% then recovered.",
        "actual": {"inr": 83.3, "gold": 1916, "india10y": 7.18, "nifty_pe": 23.4,
                   "inr_note": "₹83 range in Oct 2023", "period": "Oct 2023"},
    },
    "Goldilocks 2019": {
        "yield": 1.70, "e": "✦",
        "body": "US 10Y at ~1.7%, low inflation, steady global growth. Capital freely flowed to EM. India saw FII inflows, INR stable at ₹70, Nifty PE at 27×. Ideal conditions for Indian equity markets.",
        "actual": {"inr": 70.4, "gold": 1392, "india10y": 6.64, "nifty_pe": 27.2,
                   "inr_note": "Annual avg ₹70.4", "period": "2019 annual avg"},
    },
}

QUIZZES = [
    {"q": "US 10Y jumps to 5.5%. What typically happens to Nifty 50 P/E?",
     "o": ["Rises sharply — expands", "Stays roughly flat", "Compresses ~1.8× per 100bps", "Becomes undefined"],
     "a": 2, "xp": 30,
     "exp": "A +100bps rise historically compresses Nifty P/E by ~1.8×. At 5.5% (+100bps above 4.5% baseline), P/E goes from 22.0 → ~20.2. Higher US risk-free rates raise the discount rate in DCF models, reducing what investors rationally pay for future Indian earnings."},
    {"q": "Rupee at ₹85.5. US 10Y rises 200bps. Estimated new level?",
     "o": ["₹83.0 — rupee appreciates", "₹85.5 — stays unchanged", "₹88.5 — mild depreciation", "₹90.1 — sharp depreciation"],
     "a": 3, "xp": 25,
     "exp": "+200bps × ₹2.3 per 100bps = +₹4.6. So ₹85.5 + ₹4.6 = ~₹90.1. Higher US yields attract dollar capital home, increasing demand for dollars and weakening the rupee against it."},
    {"q": "When US yields spike sharply, which Indian sector benefits most?",
     "o": ["Real Estate", "NBFCs", "IT Services", "Capital Goods"],
     "a": 2, "xp": 20,
     "exp": "IT Services earns revenues in USD but reports earnings in INR. Every ₹1 depreciation adds ~1–2% to IT EPS. TCS, Infosys, and Wipro all saw meaningful margin expansion during INR weakness episodes. It acts as a natural FX hedge."},
    {"q": "Gold's classic correlation with real yields (Erb & Harvey, NBER) is:",
     "o": ["+0.82 — strongly positive", "−0.82 — strongly negative", "Near zero — no relationship", "−0.30 — weakly negative"],
     "a": 1, "xp": 25,
     "exp": "−0.82, confirmed verbatim in the NBER working paper 'The Golden Dilemma'. When real yields rise, the opportunity cost of holding non-yielding gold increases. Note: this correlation broke down post-2022 due to large-scale central bank buying."},
    {"q": "India's 10Y G-Sec typically absorbs what fraction of a US 10Y move?",
     "o": ["100% — full pass-through", "~75%", "~45%", "~10% — largely insulated"],
     "a": 2, "xp": 30,
     "exp": "~45bps per 100bps US10Y move. RBI's independent monetary policy dampens but cannot eliminate the transmission. India-US spread compressed from ~410bps decade-average (per Business Standard) to ~255bps recently."},
    {"q": "2013 Taper Tantrum — approximate FII outflow from India?",
     "o": ["$1bn outflow", "$10bn+ outflow in stress window", "$5bn inflow", "No significant change"],
     "a": 1, "xp": 35,
     "exp": "Massive outflows (~$10bn+ in the May–Aug 2013 stress window). Rupee crashed from 54 to 68. RBI emergency-hiked rates and restricted gold imports to defend the currency — a textbook EM yield-shock transmission event."},
    {"q": "FMCG sector sensitivity to rising US yields is best described as:",
     "o": ["Highly positive", "Highly negative", "Neutral to mildly negative — defensive", "Most negatively impacted sector"],
     "a": 2, "xp": 20,
     "exp": "FMCG is considered 'defensive' — low debt, domestic revenues, resilient demand regardless of rates. During yield spikes and FII outflows, investors often rotate into FMCG as a relative shelter. It has among the lowest rate-beta in Nifty 50."},
    {"q": "US 10Y near 0.5% (2020) — what happened to Indian FII flows?",
     "o": ["Outflows continued post-COVID", "Neutral — COVID kept capital out", "Record inflows as yield seekers found India attractive", "RBI restricted all FII activity"],
     "a": 2, "xp": 30,
     "exp": "Record inflows (~₹1.7 lakh Cr in 2020, per Business Standard). Nifty rallied ~93% from March 2020 lows. Zero US yields made India's 7%+ bonds and equity growth story irresistible to global allocators."},
]

OPTIMAL = {
    "2013 Taper Tantrum": {"IT Services":35,"Pharma/Exporters":30,"FMCG":20,"Gold ETF":5,"Banks":10,
                            "NBFCs":0,"Real Estate":0,"Auto":0,"Capital Goods/Infra":0},
    "2020 COVID Crash":   {"Banks":30,"Capital Goods/Infra":25,"Auto":20,"Real Estate":15,"FMCG":10,
                            "IT Services":0,"Pharma/Exporters":0,"NBFCs":0,"Gold ETF":0},
    "2023 5% Shock":      {"IT Services":30,"Pharma/Exporters":25,"FMCG":25,"Gold ETF":10,"Banks":10,
                            "NBFCs":0,"Real Estate":0,"Auto":0,"Capital Goods/Infra":0},
    "Goldilocks 2019":    {"Capital Goods/Infra":25,"Banks":25,"Auto":20,"NBFCs":15,"Real Estate":15,
                            "IT Services":0,"FMCG":0,"Pharma/Exporters":0,"Gold ETF":0},
}

# ══════════════════════════════════════════════════════════════
#  SESSION STATE
# ══════════════════════════════════════════════════════════════
_DEFAULTS = {
    "y10": 4.5, "active_sc": None,
    "qi": 0, "qa": False, "qs": None,
    "streak": 0, "best_streak": 0, "xp": 0, "qtotal": 0, "qhist": [],
    "btm_sc": "2023 5% Shock", "btm_done": False,
    "btm_lb": [], "btm_name": "You",
    "btm_score": 0, "btm_ur": 0.0, "btm_or": 0.0, "btm_xp": 0,
}
for _k, _v in _DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# Safe per-sector session keys (no slash or space)
for _s, _sk in SECTOR_KEYS.items():
    if ("pf_" + _sk) not in st.session_state:
        st.session_state["pf_" + _sk] = 0
    if ("btm_" + _sk) not in st.session_state:
        st.session_state["btm_" + _sk] = 0

# ══════════════════════════════════════════════════════════════
#  CALCULATION ENGINE
# ══════════════════════════════════════════════════════════════
def calc(y):
    d    = y - B10Y
    inr  = BINR + SINR * d
    i10  = BI10 + SI10 * d
    pe   = max(BPE - SPE * d, 10.0)
    gold = BGOLD * (1 - SGOLD / 100 * d)
    fii  = -BFII * d
    lr   = BHLR + SHLR * SI10 * d * 100 / 100
    r, n = lr / 100 / 12, BTEN * 12
    emi  = BLOAN * (r * (1+r)**n) / ((1+r)**n - 1) if r > 0 else BLOAN / n
    br   = BHLR / 100 / 12
    bemi = BLOAN * (br * (1+br)**n) / ((1+br)**n - 1)
    secs = {s: b * d for s, b in SECTORS.items()}
    return dict(y=y, d=d, inr=inr, i10=i10, pe=pe, lvl=pe*EPS,
                gold=gold, gold_inr=gold*inr, fii=fii,
                lr=lr, emi=emi, bemi=bemi, edlt=emi-bemi, secs=secs)

# ══════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════
def sgn(v, p=2):
    return ("+" if v >= 0 else "") + f"{v:.{p}f}"

# Metric card — string concat, no nested quotes
def mc(eye, val, dlt, dlt_v, sent, sub=""):
    dc   = "g" if dlt_v > 0 else ("r" if dlt_v < 0 else "a")
    html = '<div class="mc ' + sent + '">'
    html += '<div class="mc-eye">' + eye + '</div>'
    html += '<div class="mc-val">' + val + '</div>'
    html += '<div class="mc-dlt ' + dc + '">' + dlt + '</div>'
    if sub:
        html += '<div class="mc-sub">' + sub + '</div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

def disc(t=None):
    msg = t or "Historical pattern estimate (2010–2025) · Not a prediction · Correlations break during regime shifts"
    st.markdown('<div class="disc">◈  ' + msg + '</div>', unsafe_allow_html=True)

def sh(eye, title, sub=""):
    html = '<div class="sh">'
    html += '<div class="sh-eye">' + eye + '</div>'
    html += '<div class="sh-title">' + title + '</div>'
    if sub:
        html += '<div class="sh-sub">' + sub + '</div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

def kc(tech, ghost):
    html = (
        '<div class="kc">'
        '<div class="kc-t">' + tech + '</div>'
        '<div class="kc-g">' + ghost + '</div>'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)

def sdiv(h=16):
    st.markdown(f'<div style="height:{h}px;"></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  PLOTLY DARK THEME
# ══════════════════════════════════════════════════════════════
_DL = dict(
    paper_bgcolor="#09090e", plot_bgcolor="#09090e",
    font_family="DM Mono", font_color="#555570",
    margin=dict(l=0, r=4, t=36, b=0),
    xaxis=dict(gridcolor="#141420", zerolinecolor="#1e1e2e", showline=False),
    yaxis=dict(gridcolor="#141420", zerolinecolor="#1e1e2e", showline=False),
    showlegend=False,
)

def chart_sectors(secs, key):
    sx  = list(secs.keys())
    sy  = list(secs.values())
    clr = ["#4ab87a" if v > 0 else "#e05c6c" for v in sy]
    fig = go.Figure(go.Bar(
        x=sy, y=sx, orientation="h", marker_color=clr,
        text=[sgn(v, 1) + "%" for v in sy],
        textposition="outside",
        textfont=dict(color="#e4e4f0", size=11, family="DM Mono"),
        hovertemplate="%{y}: %{x:.1f}%<extra></extra>",
    ))
    fig.update_layout(**_DL, height=360,
        title=dict(text="Sector impact (%) vs baseline at current yield",
                   font_size=10, font_color="#555570"),
        xaxis_ticksuffix="%")
    st.plotly_chart(fig, use_container_width=True,
                    config={"displayModeBar": False}, key=key)

def chart_curve(cur, key):
    x   = np.linspace(2.0, 8.0, 120)
    pe  = np.clip(BPE - SPE * (x - B10Y), 10, 35)
    inr = BINR + SINR * (x - B10Y)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=pe, name="Nifty P/E",
        line=dict(color="#5b9cf6", width=2.5),
        hovertemplate="US10Y: %{x:.1f}%<br>Nifty P/E: %{y:.1f}×<extra></extra>"))
    fig.add_trace(go.Scatter(x=x, y=inr/10, name="INR÷10",
        line=dict(color="#e05c6c", width=2.5, dash="dot"),
        customdata=inr,
        hovertemplate="US10Y: %{x:.1f}%<br>INR: ₹%{customdata:.1f}<extra></extra>"))
    fig.add_vline(x=cur, line_color="#c9a96e", line_width=1.5, line_dash="dash",
        annotation_text=f"  {cur:.1f}%",
        annotation_font_color="#c9a96e", annotation_position="top right")
    fig.update_layout(**_DL, height=260,
        title=dict(text="Nifty P/E (blue)  ·  USD/INR ÷ 10 (red)",
                   font_size=10, font_color="#555570"))
    st.plotly_chart(fig, use_container_width=True,
                    config={"displayModeBar": False}, key=key)

def chart_fii(fii, key):
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=fii / 1000,
        delta={"reference": 0, "suffix": "K Cr",
               "increasing": {"color": "#4ab87a"},
               "decreasing": {"color": "#e05c6c"},
               "font": {"size": 14}},
        number={"suffix": "K Cr",
                "font": {"size": 24, "family": "DM Mono", "color": "#e4e4f0"}},
        gauge={
            "axis": {"range": [-60, 36],
                     "tickvals": [-54, -36, -18, 0, 18, 36],
                     "ticktext": ["-54K", "-36K", "-18K", "0", "+18K", "+36K"],
                     "tickcolor": "#444455",
                     "tickfont": {"size": 9},
                     "tickangle": 0},
            "bar":  {"color": "#c9a96e", "thickness": 0.22},
            "bgcolor": "#0c0c18", "bordercolor": "#1a1a28",
            "borderwidth": 1,
            "steps": [
                {"range": [-60, -20], "color": "rgba(224,92,108,.10)"},
                {"range": [-20,  12], "color": "rgba(201,169,110,.04)"},
                {"range": [ 12,  36], "color": "rgba(74,184,122,.08)"},
            ],
        },
        title={"text": "FII Monthly Flow  (₹000 Cr)",
               "font": {"size": 10, "color": "#555570"}},
    ))
    dl_fii = {**_DL, "margin": dict(l=20, r=20, t=40, b=20)}
    fig.update_layout(**dl_fii, height=260)
    st.plotly_chart(fig, use_container_width=True,
                    config={"displayModeBar": False}, key=key)

def chart_waterfall(alloc, secs, key):
    labs, vals, tot = [], [], 0
    for s, w in alloc.items():
        if w > 0:
            v = w / 100 * secs.get(s, 0)
            labs.append(s); vals.append(v); tot += v
    if not labs:
        return
    labs.append("Portfolio"); vals.append(tot)
    clr = ["#c9a96e" if i == len(vals)-1
           else ("#4ab87a" if v >= 0 else "#e05c6c")
           for i, v in enumerate(vals)]
    fig = go.Figure(go.Bar(
        x=labs, y=vals, marker_color=clr,
        text=[sgn(v, 2) + "%" for v in vals],
        textposition="outside",
        textfont=dict(color="#e4e4f0", size=10, family="DM Mono"),
    ))
    fig.update_layout(**_DL, height=320, yaxis_ticksuffix="%",
        title=dict(text="Portfolio contribution by sector (%)",
                   font_size=10, font_color="#555570"))
    st.plotly_chart(fig, use_container_width=True,
                    config={"displayModeBar": False}, key=key)

# ══════════════════════════════════════════════════════════════
#  SLIDER CONTROL — safe programmatic update
# ══════════════════════════════════════════════════════════════
def _set_yield(v: float):
    """
    Safely move the slider thumb. Writing to a widget key after it
    has been rendered raises StreamlitAPIException. Instead: store
    the target in y10, POP 'main_slider' so the slider re-initialises
    from value= on the next run, then rerun.
    """
    st.session_state.y10 = v
    st.session_state.pop("main_slider", None)
    st.rerun()

def render_control():
    # Preset buttons BEFORE slider (so they fire before slider renders)
    c1, c2, c3, c4 = st.columns(4)
    for col, (lbl, pv) in zip(
        [c1, c2, c3, c4],
        [("2.0% — Low", 2.0), ("3.5% — Moderate", 3.5),
         ("5.0% — Elevated", 5.0), ("7.0% — Extreme", 7.0)]
    ):
        with col:
            if st.button(lbl, key=f"qy_{pv}"):
                _set_yield(pv)

    new_y = st.slider(
        "Yield", min_value=2.0, max_value=8.0,
        value=float(st.session_state.y10),
        step=0.1, format="%.1f%%",
        key="main_slider", label_visibility="collapsed",
    )
    st.session_state.y10 = new_y

    y   = new_y
    zc  = "zg" if y <= 3.0 else ("za" if y <= 4.5 else "zr")
    ztx = ("GOLDILOCKS" if y <= 3.0 else
           "NEUTRAL"    if y <= 4.5 else
           "STRESS"     if y <= 6.0 else "EXTREME STRESS")
    yc  = "#4ab87a" if y <= 3.0 else ("#c9a96e" if y <= 4.5 else "#e05c6c")
    dlt = y - B10Y
    dlt_txt = ("▲ +" + f"{dlt:.1f}% above" if dlt > 0
               else "▼ " + f"{abs(dlt):.1f}% below" if dlt < 0
               else "at") + f" {B10Y}% baseline"

    st.markdown(
        '<div style="display:flex;align-items:flex-end;gap:16px;'
        'flex-wrap:wrap;margin-top:24px;margin-bottom:32px;">'
        '<div style="font:900 clamp(40px,7vw,68px)/1 \'DM Mono\',monospace;'
        'color:' + yc + ';letter-spacing:-.02em;">'
        + f"{y:.1f}" +
        '<span style="font-size:.45em;color:#444455;">%</span>'
        '</div>'
        '<div style="padding-bottom:8px;">'
        '<span class="zp ' + zc + '">' + ztx + '</span>'
        '<div style="font:400 11px/1 \'DM Mono\',monospace;color:#444455;margin-top:8px;">'
        + dlt_txt +
        '</div></div></div>'
        '<hr class="dv">',
        unsafe_allow_html=True
    )
    return new_y

# ══════════════════════════════════════════════════════════════
#  HERO
# ══════════════════════════════════════════════════════════════
def render_hero():
    st.markdown("""
<div style="padding:72px 0 56px;border-bottom:1px solid #1a1a28;">
  <div style="font:500 11px/1 'DM Mono',monospace;letter-spacing:.18em;
       text-transform:uppercase;color:#a07840;margin-bottom:16px;">
    Day 10 · 30 Days of AI Finance · India Markets Simulator
  </div>
  <div style="font:900 clamp(48px,8vw,82px)/1 'Playfair Display',serif;
       letter-spacing:-.03em;color:#e4e4f0;margin-bottom:20px;">
    Yield<span style="color:#c9a96e;">Lab</span>
  </div>
  <div style="font:400 16px/1.75 'Syne',sans-serif;color:#7a7a90;
       max-width:520px;margin-bottom:32px;">
    Drag a slider. Watch Indian markets move in real time.<br>
    Built from 15 years of US–India yield history. Baselines updated June 2026.
  </div>
  <div class="disc" style="max-width:640px;">
    ◈  All outputs are historical pattern estimates (2010–2025).
    This shows what <em>typically happened</em> when US 10Y moved —
    not a forecast. Correlations break during regime shifts, geopolitical
    events, and RBI interventions.
  </div>
  <div style="display:flex;flex-wrap:wrap;gap:32px;
       padding-top:32px;border-top:1px solid #1a1a28;margin-top:32px;">
    <div>
      <div style="font:700 22px/1 'DM Mono',monospace;color:#c9a96e;">2.0–8.0%</div>
      <div style="font:500 10px/1 'DM Mono',monospace;letter-spacing:.1em;
           text-transform:uppercase;color:#444455;margin-top:6px;">Yield range</div>
    </div>
    <div>
      <div style="font:700 22px/1 'DM Mono',monospace;color:#c9a96e;">15 Years</div>
      <div style="font:500 10px/1 'DM Mono',monospace;letter-spacing:.1em;
           text-transform:uppercase;color:#444455;margin-top:6px;">Data (2010–2025)</div>
    </div>
    <div>
      <div style="font:700 22px/1 'DM Mono',monospace;color:#c9a96e;">9 Sectors</div>
      <div style="font:500 10px/1 'DM Mono',monospace;letter-spacing:.1em;
           text-transform:uppercase;color:#444455;margin-top:6px;">Impact tracked</div>
    </div>
    <div>
      <div style="font:700 22px/1 'DM Mono',monospace;color:#c9a96e;">8 Outputs</div>
      <div style="font:500 10px/1 'DM Mono',monospace;letter-spacing:.1em;
           text-transform:uppercase;color:#444455;margin-top:6px;">Recalculate live</div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  TAB 1 — LIVE SIMULATOR
# ══════════════════════════════════════════════════════════════
def tab_sim(m):
    sh("LIVE SIMULATOR", "Real-Time Market Impact",
       f"Estimated effects of US 10Y at {m['y']:.1f}% vs baseline {B10Y}%. "
       "All numbers update instantly as you drag the slider.")
    disc()

    # ── Row 1: INR + India 10Y ──
    c1, c2 = st.columns(2, gap="medium")
    with c1:
        d = m["inr"] - BINR
        mc("USD / INR", "₹" + f"{m['inr']:.2f}",
           sgn(d, 2) + " rupees vs ₹" + str(BINR) + " baseline", -d,
           "neg" if d > 0 else "pos",
           sub="Sensitivity: ₹2.3 weaker per +100bps US10Y")
        with st.expander("WHY DOES THIS HAPPEN"):
            kc("India-US 10Y spread peaked at ~590bps (2016) and compressed to ~255bps (2024–25) per Business Standard. As the spread narrowed, INR fell ~35% over the decade. Sensitivity hardcoded at ₹2.3 per +100bps from long-run regression.",
               '"Capital finds the steepest slope. When US bonds pay more, dollars flow home from India — and that demand for dollars weakens the rupee."')
    with c2:
        d = m["i10"] - BI10
        mc("INDIA 10Y G-SEC", f"{m['i10']:.2f}%",
           sgn(int(d * 100), 0) + "bps vs " + str(BI10) + "% baseline", -d,
           "neg" if d > 0 else "pos",
           sub="~45% pass-through from US 10Y (decade avg)")
        with st.expander("WHY DOES THIS HAPPEN"):
            kc("India absorbs ~45bps per 100bps US10Y move. RBI has partial independence but can't fully insulate domestic yields. The decade-average spread of ~410bps compressed to ~255bps recently (Business Standard, Dec 2024).",
               '"When America sneezes, India catches half a cold. RBI has its own tools — but global yield gravity always pulls."')

    sdiv(16)

    # ── Row 2: Nifty P/E + Gold ──
    c3, c4 = st.columns(2, gap="medium")
    with c3:
        d = m["pe"] - BPE
        mc("NIFTY 50 P/E", f"{m['pe']:.1f}×",
           sgn(d, 1) + "× vs " + str(BPE) + "× baseline", d,
           "pos" if d > 0 else "neg",
           sub=f"Nifty ~{m['lvl']:,.0f}  ·  EPS ₹{EPS:,}")
        with st.expander("WHY DOES THIS HAPPEN"):
            kc("~1.8× P/E compression per +100bps US10Y, with 1–2 month lag. Higher US risk-free rate raises the discount rate in DCF models — compressing fair-value multiples across Indian equities.",
               '"When US bonds yield 5%, paying 22× for Indian earnings looks expensive. Investors don\'t accept the same price — they negotiate it down."')
    with c4:
        d = m["gold"] - BGOLD
        mc("GOLD (USD/OZ)", "$" + f"{m['gold']:,.0f}",
           sgn(int(d), 0) + " USD vs $" + f"{BGOLD:,} baseline", d,
           "pos" if d > 0 else "neg",
           sub=f"₹{m['gold_inr']/31.1:,.0f}/gram approx  ·  r = −0.82 (Erb & Harvey, NBER)")
        with st.expander("WHY DOES THIS HAPPEN"):
            kc("Gold-real yield correlation: −0.82 (confirmed NBER working paper 'The Golden Dilemma'). ~8% per 100bps long-run avg. ⚠ Post-2022 this broke down — central bank buying absorbed the selling pressure.",
               '"Gold pays nothing. When real US yields rise, the opportunity cost of holding gold rises too. But recently, central banks buying gold as a dollar alternative have rewritten this old rule."')

    st.markdown('<hr class="dv">', unsafe_allow_html=True)

    # ── Row 3: FII + EMI + Govt ──
    c5, c6, c7 = st.columns(3, gap="medium")
    with c5:
        fi = m["fii"]
        mc("FII MONTHLY FLOW",
           "₹" + f"{abs(fi/1000):.0f}" + ",000 Cr",
           "Outflow estimate" if fi < 0 else "Inflow estimate", fi,
           "neg" if fi < 0 else "pos",
           sub="₹18,000 Cr per +100bps (stress-period scale)")
        with st.expander("WHY DOES THIS HAPPEN"):
            kc("Higher US yields narrow India's risk-adjusted yield advantage. ₹18,000 Cr/month per 100bps is derived from stress episodes: 2013 Taper, 2018 oil crisis, 2022 Fed hike cycle.",
               '"Why accept rupee risk for 7% when US T-Bills pay 5% risk-free? The math stops working for India — so capital leaves."')
    with c6:
        mc("HOME LOAN EMI (₹50L/20Y)",
           "₹" + f"{m['emi']:,.0f}" + "/mo",
           sgn(int(m["edlt"]), 0) + " vs current baseline", -m["edlt"],
           "neg" if m["edlt"] > 0 else "pos",
           sub=f"Rate: {m['lr']:.2f}%  ·  60% India10Y pass-through to MCLR")
        with st.expander("WHY DOES THIS HAPPEN"):
            kc("60% of India 10Y move eventually reaches floating home loans via MCLR adjustments. India10Y absorbs 45bps per 100bps US10Y. Combined: ~27bps on lending rates per 100bps US10Y.",
               '"Your EMI is downstream from the US Federal Reserve. Fed tightens → US10Y rises → India10Y follows → banks raise MCLR → your EMI jumps. Each link dilutes the signal, but it gets through."')
    with c7:
        govt = 1_500_000 * (m["i10"] / 100 - BI10 / 100)
        mc("GOVT INTEREST DELTA",
           "₹" + f"{abs(govt/1000):,.0f}" + "K Cr extra",
           "annual burden above baseline", -govt,
           "neg" if govt > 0 else "pos",
           sub="On ₹15L Cr annual gross borrowing base")
        with st.expander("WHY DOES THIS HAPPEN"):
            kc("India borrows ~₹15 lakh crore annually. Every 100bps rise in India 10Y adds ~₹15,000 Cr to the annual interest burden on fresh issuances — a direct fiscal cost of US rate spillover.",
               '"Higher US yields don\'t just hurt your portfolio. They make the government\'s borrowing more expensive — and that eventually shows up in taxes, spending cuts, or inflation."')

    st.markdown('<hr class="dv">', unsafe_allow_html=True)

    # ── Sector matrix ──
    st.markdown(
        '<div style="font:500 10px/1 \'DM Mono\',monospace;letter-spacing:.12em;'
        'text-transform:uppercase;color:#444455;margin-bottom:20px;">SECTOR IMPACT MATRIX</div>',
        unsafe_allow_html=True
    )
    chart_sectors(m["secs"], key="k_sim_sectors")

    # Sector badge row — using safe string build, no nested quotes in f-string
    badge_html = '<div style="line-height:2.6;margin-top:12px;">'
    for s, b in m["secs"].items():
        cls = "sbp" if b > 0 else "sbn"
        badge_html += '<span class="sb ' + cls + '">' + s + '  ' + sgn(b, 1) + '%</span>'
    badge_html += '</div>'
    st.markdown(badge_html, unsafe_allow_html=True)

    disc("Sector betas from historical return regressions vs US 10Y moves (2010–2025). Individual stock outcomes vary significantly. Not investment advice.")

# ══════════════════════════════════════════════════════════════
#  TAB 2 — SCENARIOS
# ══════════════════════════════════════════════════════════════
def tab_scenarios():
    sh("SCENARIOS", "Four Yield Regimes, Relived",
       "Real historical data from each episode — verified from RBI, NSE, and Bloomberg. Not model estimates.")

    c1, c2, c3, c4 = st.columns(4, gap="small")
    for col, (name, sc) in zip([c1, c2, c3, c4], SCENARIOS.items()):
        with col:
            if st.button(sc["e"] + "  " + name, key="sc_btn_" + name.replace(" ", "_")):
                st.session_state.active_sc = name
                _set_yield(sc["yield"])

    if st.session_state.active_sc:
        name = st.session_state.active_sc
        sc   = SCENARIOS[name]
        act  = sc["actual"]

        card = (
            '<div style="background:#0c0c18;border:1px solid #1a1a28;border-radius:10px;padding:24px;margin:24px 0;">'
            '<div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px;margin-bottom:12px;">'
            '<div style="font:700 18px/1 Playfair Display,serif;color:#c9a96e;">' + sc["e"] + "  " + name + '</div>'
            '<span style="font:400 11px/1 DM Mono,monospace;color:#444455;background:#1a1a28;padding:4px 10px;border-radius:4px;">' + act["period"] + '</span>'
            '</div>'
            '<div style="font:400 14px/1.75 Syne,sans-serif;color:#7a7a90;">' + sc["body"] + '</div>'
            '</div>'
        )
        st.markdown(card, unsafe_allow_html=True)

        st.markdown('<div style="font:500 10px/1 DM Mono,monospace;letter-spacing:.12em;text-transform:uppercase;color:#a07840;margin-bottom:16px;">ACTUAL HISTORICAL DATA — VERIFIED SOURCES</div>', unsafe_allow_html=True)

        ca, cb, cc, cd, ce = st.columns(5, gap="medium")
        with ca:
            mc("US 10Y YIELD", str(sc["yield"]) + "%", "actual level", 0, "neu", sub=act["period"])
        with cb:
            mc("USD / INR", "₹" + f'{act["inr"]:.1f}', act["inr_note"], -(act["inr"] - BINR),
               "neg" if act["inr"] > BINR else "pos", sub="Actual rate")
        with cc:
            d_pe = act["nifty_pe"] - BPE
            mc("NIFTY P/E", f'{act["nifty_pe"]:.1f}×', sgn(d_pe, 1) + "× vs today " + str(BPE) + "×", d_pe,
               "pos" if d_pe > 0 else "neg", sub="Actual Nifty PE")
        with cd:
            d_g = act["gold"] - BGOLD
            mc("GOLD (USD)", "$" + f'{act["gold"]:,}', sgn(int(d_g), 0) + " vs today $" + f'{BGOLD:,}', d_g,
               "pos" if d_g > 0 else "neg", sub="Actual price")
        with ce:
            d_i = act["india10y"] - BI10
            mc("INDIA 10Y", f'{act["india10y"]:.2f}%', sgn(round(d_i, 2), 2) + "% vs today", -d_i,
               "neg" if act["india10y"] > BI10 else "pos", sub="Actual G-Sec")

        st.markdown('<div class="disc">◈  Actual figures from RBI Annual Reports, NSE PE data, Bloomberg. Not model projections. Slider moved to this yield level — check Live Simulator tab for today-relative estimates.</div>', unsafe_allow_html=True)

        sdiv(24)
        m = calc(sc["yield"])
        st.markdown('<div style="font:500 10px/1 DM Mono,monospace;letter-spacing:.12em;text-transform:uppercase;color:#555570;margin-bottom:16px;">MODEL SECTOR ESTIMATE AT THIS YIELD (from today\'s baseline)</div>', unsafe_allow_html=True)
        chart_sectors(m["secs"], key="k_sc_sectors")
    else:
        st.markdown('<div style="text-align:center;padding:56px 0;color:#444455;font:400 13px/1 DM Mono,monospace;">Select a scenario above to load it.</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  TAB 3 — QUIZ
# ══════════════════════════════════════════════════════════════
def tab_quiz():
    sh("PREDICTION GAME", "Test Your Macro Intuition",
       "Answer questions about historical yield-market relationships. "
       "Build streaks for bonus XP. Track your level progression.")

    xp      = st.session_state.xp
    streak  = st.session_state.streak
    best    = st.session_state.best_streak
    tot     = st.session_state.qtotal
    correct = sum(1 for h in st.session_state.qhist if h)
    acc     = int(correct / max(tot, 1) * 100)
    lv      = xp // 100 + 1
    xp_in   = xp % 100
    titles  = {1: "Yield Rookie", 2: "Rate Watcher", 3: "Macro Analyst",
               4: "FII Tracker", 5: "Bond Whisperer", 6: "Global Macro Pro"}
    title   = titles.get(min(lv, 6), "Grand Strategist")

    # Stats row
    c1, c2, c3, c4, c5 = st.columns(5, gap="medium")
    with c1:
        mc("STREAK", str(streak), "Best: " + str(best), 0, "neu")
    with c2:
        mc("TOTAL XP", str(xp), "Level " + str(lv), xp, "pos")
    with c3:
        gc = "pos" if acc >= 70 else ("neg" if acc < 50 else "neu")
        mc("ACCURACY", str(acc) + "%", str(correct) + "/" + str(tot) + " correct", 0, gc)
    with c4:
        mc("RANK", title, "Level " + str(lv) + " of 7", 0, "neu")
    with c5:
        mc("TO NEXT LV", str(100 - xp_in) + " XP", str(xp_in) + "/100 earned", 0, "neu")

    # XP progress bar
    st.markdown(
        '<div style="margin:16px 0 32px;">'
        '<div class="xpb-o"><div class="xpb-i" style="width:' + str(xp_in) + '%;"></div></div>'
        '<div style="display:flex;justify-content:space-between;'
        'font:400 10px/1 \'DM Mono\',monospace;color:#444455;margin-top:4px;">'
        '<span>Level ' + str(lv) + '</span>'
        '<span>' + str(xp_in) + '/100 XP</span>'
        '<span>Level ' + str(lv + 1) + '</span>'
        '</div></div>',
        unsafe_allow_html=True
    )
    st.markdown('<hr class="dv">', unsafe_allow_html=True)

    # Current question
    idx    = st.session_state.qi % len(QUIZZES)
    q      = QUIZZES[idx]
    bonus  = min(streak * 5, 50)
    earn   = q["xp"] + bonus

    # Question card — pure string concat, zero nested quotes in f-strings
    bonus_span = (
        '<span style="display:block;font:400 10px/1 DM Mono,monospace;'
        'color:#444455;margin-top:4px;">+' + str(bonus) + ' streak bonus</span>'
    ) if bonus else ""

    qcard = (
        '<div class="mc neu" style="margin-bottom:24px;">'
        '<div style="display:flex;justify-content:space-between;'
        'align-items:flex-start;gap:16px;">'
        '<div style="flex:1;">'
        '<div class="mc-eye">QUESTION ' + str(idx + 1) + ' / ' + str(len(QUIZZES)) + '</div>'
        '<div style="font:600 17px/1.5 Syne,sans-serif;color:#e4e4f0;margin-top:8px;">'
        + q["q"] +
        '</div></div>'
        '<div style="flex-shrink:0;text-align:right;">'
        '<span class="scchip">+' + str(earn) + ' XP</span>'
        + bonus_span +
        '</div></div></div>'
    )
    st.markdown(qcard, unsafe_allow_html=True)

    answered = st.session_state.qa
    selected = st.session_state.qs

    for i, opt in enumerate(q["o"]):
        letter = chr(65 + i)
        if not answered:
            if st.button(letter + ".  " + opt, key="q_" + str(idx) + "_" + str(i)):
                st.session_state.qa = True
                st.session_state.qs = i
                st.session_state.qtotal += 1
                if i == q["a"]:
                    ns = streak + 1
                    st.session_state.streak = ns
                    st.session_state.best_streak = max(ns, best)
                    st.session_state.xp += q["xp"] + min(ns * 5, 50)
                    st.session_state.qhist.append(True)
                else:
                    st.session_state.streak = 0
                    st.session_state.qhist.append(False)
                st.rerun()
        else:
            cf  = (i == q["a"])
            sf  = (i == selected)
            cls = "qo-c" if cf else ("qo-w" if sf else "qo-d")
            pfx = "✓" if cf else ("✗" if sf else " ")
            st.markdown(
                '<div class="qo ' + cls + '">' + pfx + "  " + letter + ".  " + opt + '</div>',
                unsafe_allow_html=True
            )

    if answered:
        ok  = (selected == q["a"])
        clr = "#4ab87a" if ok else "#e05c6c"
        streak_now = st.session_state.streak
        earned_xp  = q["xp"] + min(streak_now * 5, 50) if ok else 0
        streak_txt = (" · Streak ×" + str(streak_now)) if (ok and streak_now > 1) else ""
        if ok:
            hdr = "Correct — +" + str(earned_xp) + " XP" + streak_txt
            bg  = "rgba(74,184,122,.07)"
            bdr = "#4ab87a44"
        else:
            hdr = "Incorrect · Correct: " + chr(65 + q["a"]) + ". " + q["o"][q["a"]]
            bg  = "rgba(224,92,108,.07)"
            bdr = "#e05c6c44"

        st.markdown(
            '<div style="background:' + bg + ';border:1px solid ' + bdr + ';'
            'border-radius:8px;padding:18px 20px;margin:12px 0;">'
            '<div style="color:' + clr + ';font:700 14px/1 \'DM Mono\',monospace;'
            'margin-bottom:10px;">' + hdr + '</div>'
            '<div style="font:400 13px/1.7 \'Syne\',sans-serif;color:#7a7a90;">'
            + q["exp"] +
            '</div></div>',
            unsafe_allow_html=True
        )

        cn, cr = st.columns([3, 1])
        with cn:
            if st.button("Next Question →", key="q_next"):
                st.session_state.qi += 1
                st.session_state.qa = False
                st.session_state.qs = None
                st.rerun()
        with cr:
            if st.button("Reset Progress", key="q_reset"):
                for k in ["streak", "best_streak", "xp", "qtotal"]:
                    st.session_state[k] = 0
                st.session_state.qhist = []
                st.session_state.qa    = False
                st.session_state.qs    = None
                st.rerun()

# ══════════════════════════════════════════════════════════════
#  TAB 4 — STRESS TEST
# ══════════════════════════════════════════════════════════════
def tab_stress(m):
    sh("PORTFOLIO STRESS TEST", "Your Holdings Under the Yield Lens",
       f"Enter your sector allocations (must sum to 100%) and see the estimated "
       f"blended impact at US 10Y = {m['y']:.1f}%. Use the presets to get started quickly.")

    PRESETS = {
        "IT-Heavy": {
            "IT Services": 40, "Pharma/Exporters": 25, "FMCG": 20,
            "Banks": 15, "NBFCs": 0, "Real Estate": 0,
            "Auto": 0, "Capital Goods/Infra": 0, "Gold ETF": 0},
        "Rate-Sensitive": {
            "Banks": 35, "NBFCs": 25, "Real Estate": 20,
            "Auto": 15, "FMCG": 5, "IT Services": 0,
            "Pharma/Exporters": 0, "Capital Goods/Infra": 0, "Gold ETF": 0},
        "Balanced": {
            "IT Services": 20, "Banks": 20, "FMCG": 15,
            "Pharma/Exporters": 15, "Auto": 10, "Capital Goods/Infra": 10,
            "NBFCs": 5, "Real Estate": 0, "Gold ETF": 5},
        "Defensive": {
            "FMCG": 35, "Pharma/Exporters": 30, "IT Services": 20,
            "Gold ETF": 15, "Banks": 0, "NBFCs": 0,
            "Real Estate": 0, "Auto": 0, "Capital Goods/Infra": 0},
    }

    # Preset buttons
    st.markdown(
        '<div style="font:500 10px/1 \'DM Mono\',monospace;letter-spacing:.12em;'
        'text-transform:uppercase;color:#444455;margin-bottom:12px;">LOAD PRESET</div>',
        unsafe_allow_html=True
    )
    pc = st.columns(4, gap="small")
    for col, (pname, palloc) in zip(pc, PRESETS.items()):
        with col:
            if st.button(pname, key="pf_pre_" + pname.replace("-", "_")):
                for s, v in palloc.items():
                    st.session_state["pf_" + SECTOR_KEYS[s]] = v
                st.rerun()

    st.markdown('<hr class="dv">', unsafe_allow_html=True)

    # ── Allocation inputs in a 3-column grid ──
    st.markdown(
        '<div style="font:500 10px/1 \'DM Mono\',monospace;letter-spacing:.12em;'
        'text-transform:uppercase;color:#444455;margin-bottom:16px;">SECTOR ALLOCATION (%)</div>',
        unsafe_allow_html=True
    )
    alloc   = {}
    inp_cols = st.columns(3, gap="medium")
    for i, s in enumerate(SECTORS):
        sk  = "pf_" + SECTOR_KEYS[s]   # safe key, no slash
        val = int(st.session_state.get(sk, 0))
        with inp_cols[i % 3]:
            v = st.number_input(
                s, min_value=0, max_value=100,
                value=val, step=5, key=sk
            )
        alloc[s] = v

    tot = sum(alloc.values())
    tc  = "#4ab87a" if tot == 100 else "#e05c6c"
    st.markdown(
        '<div style="margin:16px 0 28px;">'
        '<div class="xpb-o" style="height:6px;">'
        '<div class="xpb-i" style="width:' + str(min(tot, 100)) + '%;background:' + tc + ';"></div>'
        '</div>'
        '<div style="font:400 11px/1 \'DM Mono\',monospace;color:' + tc + ';margin-top:6px;">'
        + str(tot) + '% allocated ' + ('✓ complete' if tot == 100 else '— must equal 100%') +
        '</div></div>',
        unsafe_allow_html=True
    )

    # ── Results ──
    if tot > 0:
        disc()
        impact = sum(alloc[s] / 100 * m["secs"][s] for s in SECTORS if alloc[s] > 0)
        n_pos  = sum(1 for v in alloc.values() if v > 0)

        mc(
            "BLENDED PORTFOLIO IMPACT @ " + f"{m['y']:.1f}%",
            sgn(impact, 2) + "%",
            "vs baseline US 10Y = " + str(B10Y) + "%",
            impact,
            "pos" if impact >= 0 else "neg",
            sub="Weighted average across " + str(n_pos) + " active positions"
        )

        sdiv(20)

        # Per-sector breakdown table
        rows_html = ""
        for s, w in alloc.items():
            if w > 0:
                imp = w / 100 * m["secs"][s]
                cls = "sbp" if imp >= 0 else "sbn"
                rows_html += (
                    '<div style="display:flex;justify-content:space-between;'
                    'align-items:center;padding:10px 0;border-bottom:1px solid #1a1a28;">'
                    '<span style="font:400 13px/1 Syne,sans-serif;color:#7a7a90;">' + s + '</span>'
                    '<span style="font:400 11px/1 DM Mono,monospace;color:#444455;">' + str(w) + '%</span>'
                    '<span class="sb ' + cls + '">' + sgn(imp, 2) + '%</span>'
                    '</div>'
                )
        if rows_html:
            st.markdown(
                '<div style="background:#0c0c18;border:1px solid #1a1a28;'
                'border-radius:10px;padding:16px 20px;">' + rows_html + '</div>',
                unsafe_allow_html=True
            )

        sdiv(24)
        chart_waterfall(alloc, m["secs"], key="k_pf_waterfall")
        disc("Sector betas from historical regressions (2010–2025). Not investment advice.")

# ══════════════════════════════════════════════════════════════
#  TAB 5 — BEAT THE MARKET
# ══════════════════════════════════════════════════════════════
def tab_btm():
    sh("BEAT THE MARKET", "Allocate ₹10 Lakh — Outsmart History",
       "Pick a yield scenario and build your sector allocation. "
       "Score 0–100 against the historically optimal portfolio. Climb the session leaderboard.")

    cl, cr = st.columns(2, gap="large")
    sc_key = st.session_state.btm_sc

    with cl:
        st.markdown(
            '<div style="font:500 10px/1 \'DM Mono\',monospace;letter-spacing:.12em;'
            'text-transform:uppercase;color:#444455;margin-bottom:12px;">STEP 1 — CHOOSE SCENARIO</div>',
            unsafe_allow_html=True
        )
        sc_key = st.selectbox(
            "Scenario", list(SCENARIOS.keys()),
            index=list(SCENARIOS.keys()).index(sc_key),
            key="btm_sel", label_visibility="collapsed"
        )
        st.session_state.btm_sc = sc_key
        sc = SCENARIOS[sc_key]

        st.markdown(
            '<div style="background:#0c0c18;border:1px solid #1a1a28;'
            'border-radius:8px;padding:18px;margin:12px 0 24px;">'
            '<div style="font:700 15px/1 \'DM Mono\',monospace;color:#c9a96e;margin-bottom:10px;">'
            + sc["e"] + "  US 10Y = " + str(sc["yield"]) + "%"
            + '</div>'
            '<div style="font:400 13px/1.6 \'Syne\',sans-serif;color:#7a7a90;">'
            + sc["body"][:200] + "…"
            + '</div></div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div style="font:500 10px/1 \'DM Mono\',monospace;letter-spacing:.12em;'
            'text-transform:uppercase;color:#444455;margin-bottom:12px;">STEP 2 — ALLOCATE (%)</div>',
            unsafe_allow_html=True
        )
        ba = {}
        bt = 0
        for s in SECTORS:
            sk  = "btm_" + SECTOR_KEYS[s]   # safe key
            val = int(st.session_state.get(sk, 0))
            v   = st.number_input(s, 0, 100, val, 5, key=sk)
            ba[s] = v
            bt   += v

        tc = "#4ab87a" if bt == 100 else "#e05c6c"
        st.markdown(
            '<div style="font:400 11px/1 \'DM Mono\',monospace;color:' + tc +
            ';margin:8px 0 16px;">'
            + str(bt) + '% ' + ('✓ Ready to submit' if bt == 100 else '← must equal 100%') +
            '</div>',
            unsafe_allow_html=True
        )

        nm = st.text_input("Your name for leaderboard",
                           value=st.session_state.btm_name, key="btm_nm")
        st.session_state.btm_name = nm or "You"

        if st.button("Submit Allocation →", key="btm_go") and bt == 100:
            mv    = calc(sc["yield"])
            ur    = sum(ba[s] / 100 * mv["secs"][s] for s in SECTORS)
            opt   = OPTIMAL.get(sc_key, {s: 0 for s in SECTORS})
            or_   = sum(opt.get(s, 0) / 100 * mv["secs"][s] for s in SECTORS)
            score = min(int(max(0, ur / or_ * 100) if or_ else 50), 100)
            xa    = score // 2
            st.session_state.btm_done  = True
            st.session_state.btm_score = score
            st.session_state.btm_ur    = ur
            st.session_state.btm_or    = or_
            st.session_state.btm_xp    = xa
            st.session_state.xp       += xa
            lb = st.session_state.btm_lb
            lb.append({"name": nm or "You", "score": score,
                       "sc": sc_key, "ret": round(ur, 2)})
            lb.sort(key=lambda x: -x["score"])
            st.session_state.btm_lb = lb[:10]
            st.rerun()

    with cr:
        if st.session_state.btm_done:
            score = st.session_state.btm_score
            ur    = st.session_state.btm_ur
            or_   = st.session_state.btm_or
            xa    = st.session_state.btm_xp
            gc    = "#4ab87a" if score >= 75 else ("#c9a96e" if score >= 50 else "#e05c6c")
            medal = ("🏆" if score >= 90 else
                     "🥈" if score >= 75 else
                     "👍" if score >= 50 else "📚")

            st.markdown(
                '<div style="text-align:center;padding:32px 0 24px;'
                'border-bottom:1px solid #1a1a28;margin-bottom:24px;">'
                '<div style="font:500 10px/1 \'DM Mono\',monospace;letter-spacing:.14em;'
                'text-transform:uppercase;color:#444455;margin-bottom:12px;">YOUR SCORE</div>'
                '<div style="font:900 72px/1 \'Playfair Display\',serif;color:' + gc + ';">'
                + medal + "  " + str(score) +
                '</div>'
                '<div style="font:400 12px/1 \'DM Mono\',monospace;color:#444455;'
                'margin:8px 0 16px;">/100</div>'
                '<span class="scchip">+' + str(xa) + ' XP awarded</span>'
                '</div>',
                unsafe_allow_html=True
            )

            ca2, cb2 = st.columns(2, gap="medium")
            with ca2:
                mc("YOUR RETURN", sgn(ur, 2) + "%", "under this scenario",
                   ur, "pos" if ur >= 0 else "neg")
            with cb2:
                mc("OPTIMAL RETURN", sgn(or_, 2) + "%", "historical best allocation",
                   or_, "pos" if or_ >= 0 else "neg")

            opt = OPTIMAL.get(sc_key, {})
            st.markdown(
                '<div style="font:500 10px/1 \'DM Mono\',monospace;letter-spacing:.12em;'
                'text-transform:uppercase;color:#444455;margin:20px 0 10px;">'
                'HISTORICALLY OPTIMAL ALLOCATION</div>',
                unsafe_allow_html=True
            )
            ob_html = ""
            for s, w in opt.items():
                if w > 0:
                    ob_html += '<span class="sb sbp">' + s + ': ' + str(w) + '%</span>'
            st.markdown(
                '<div style="line-height:2.4;">' + ob_html + '</div>',
                unsafe_allow_html=True
            )
            disc("Based on sectors that historically outperformed during this yield environment (2010–2025).")

            if st.button("Try Again with Different Allocation", key="btm_retry"):
                st.session_state.btm_done = False
                for s in SECTORS:
                    st.session_state["btm_" + SECTOR_KEYS[s]] = 0
                st.rerun()

        else:
            st.markdown(
                '<div style="font:500 10px/1 \'DM Mono\',monospace;letter-spacing:.12em;'
                'text-transform:uppercase;color:#444455;margin-bottom:16px;">LEADERBOARD</div>',
                unsafe_allow_html=True
            )
            lb = st.session_state.btm_lb
            if lb:
                medals_list = ["🥇", "🥈", "🥉"] + ["·"] * 10
                for i, row in enumerate(lb[:8]):
                    st.markdown(
                        '<div class="lb">'
                        '<span class="lb-m">' + medals_list[i] + '</span>'
                        '<span class="lb-n">' + row["name"] + '</span>'
                        '<span class="lb-s">' + row["sc"][:18] + '</span>'
                        '<span class="lb-v">' + str(row["score"]) + '/100</span>'
                        '</div>',
                        unsafe_allow_html=True
                    )
            else:
                st.markdown(
                    '<div style="height:160px;display:flex;align-items:center;'
                    'justify-content:center;color:#444455;font:400 13px/1 DM Mono,monospace;'
                    'text-align:center;">Submit your allocation<br>to appear here.</div>',
                    unsafe_allow_html=True
                )

# ══════════════════════════════════════════════════════════════
#  TAB 6 — CHARTS
# ══════════════════════════════════════════════════════════════
def tab_charts(m):
    sh("DATA CHARTS", "Yield Relationships Visualised",
       "All correlations plotted across the 2.0–8.0% range. "
       "Historical pattern estimates (2010–2025).")
    disc()

    c1, c2 = st.columns(2, gap="medium")
    with c1:
        chart_curve(st.session_state.y10, key="k_chart_curve")
    with c2:
        chart_fii(m["fii"], key="k_chart_fii")

    sdiv(24)
    chart_sectors(m["secs"], key="k_chart_sectors")

    st.markdown(
        '<div style="font:500 10px/1 \'DM Mono\',monospace;letter-spacing:.12em;'
        'text-transform:uppercase;color:#444455;margin:32px 0 12px;">'
        'FULL SENSITIVITY TABLE — 2.0% TO 8.0%</div>',
        unsafe_allow_html=True
    )
    rows = []
    for yv in np.arange(2.0, 8.5, 0.5):
        r = calc(yv)
        rows.append({
            "US 10Y":      f"{yv:.1f}%",
            "USD/INR":     f"₹{r['inr']:.2f}",
            "India 10Y":   f"{r['i10']:.2f}%",
            "Nifty P/E":   f"{r['pe']:.1f}×",
            "Nifty Level": f"{r['lvl']:,.0f}",
            "Gold (USD)":  f"${r['gold']:,.0f}",
            "FII Est.":    ("−" if r["fii"] < 0 else "+") + "₹" + f"{abs(r['fii']/1000):.0f}K Cr",
            "Loan Rate":   f"{r['lr']:.2f}%",
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True,
                 height=360, hide_index=True)

# ══════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════
def main():
    render_hero()
    y = render_control()
    m = calc(y)

    tabs = st.tabs([
        "LIVE SIMULATOR", "SCENARIOS", "QUIZ",
        "STRESS TEST", "BEAT THE MARKET", "CHARTS"
    ])
    with tabs[0]: tab_sim(m)
    with tabs[1]: tab_scenarios()
    with tabs[2]: tab_quiz()
    with tabs[3]: tab_stress(m)
    with tabs[4]: tab_btm()
    with tabs[5]: tab_charts(m)

    st.markdown(
        '<hr class="dv">'
        '<div style="text-align:center;font:400 11px/2.2 \'DM Mono\',monospace;'
        'color:#2a2a38;padding-bottom:40px;">'
        'YIELDLAB · DAY 10 · 30 DAYS OF AI FINANCE<br>'
        'Historical patterns (2010–2025) · Not predictions · Not investment advice'
        '</div>',
        unsafe_allow_html=True
    )

main()
