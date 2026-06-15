import re
import numpy as np
import streamlit as st
import plotly.graph_objects as go

from model import run_model, YEAR_0_EBITDA_MARGIN, DA_PCT_REVENUE, CAPEX_PCT_REVENUE, TAX_RATE, HOLD_PERIOD_YEARS
from excel_export import generate_excel

# ═══════════════════════════ CONFIG ═══════════════════════════
st.set_page_config(page_title="LBOdesk", page_icon="📐", layout="wide", initial_sidebar_state="collapsed")

# ═══════════════════════════ THEMES ═══════════════════════════
THEMES = {
    "dark": dict(
        bg="#09090e", card="#111118", card_grad_top="#131320", card_grad_bot="#0d0d14",
        border="#1f1f2b", border2="#181822", border_hover="#3a3a4a",
        gold="#c9a96e", gold_rgb="201,169,110", navy="#3a5a7a", navy_rgb="58,90,122",
        green="#4ab87a", red="#e05c6c",
        ink="#f3ede1", text="#e8e6e1", soft="#c4c1ba", mute="#8a877f", mute2="#6f6c66", faint="#5a5750",
        heat_header_bg="#15151f", btn_text="#09090e", btn_hover="#d9bd8a", feature_navy_num="#6f93b8",
        hl1="#c9a96e", hl2="#f3dcb0",
    ),
    "light": dict(
        bg="#f7f5ef", card="#ffffff", card_grad_top="#ffffff", card_grad_bot="#f2eee3",
        border="#e6e0d2", border2="#ece6d8", border_hover="#cfc7b4",
        gold="#a9824f", gold_rgb="169,130,79", navy="#3a5a7a", navy_rgb="58,90,122",
        green="#2f8f5b", red="#c0394a",
        ink="#211e19", text="#2b2823", soft="#524e47", mute="#8a8278", mute2="#a89f8f", faint="#b0a89a",
        heat_header_bg="#efeadc", btn_text="#211e19", btn_hover="#c2a06a", feature_navy_num="#3a5a7a",
        hl1="#8a6a3c", hl2="#c9a96e",
    ),
}
# Fixed (theme-independent) text colors for heatmap cells, which have their own strong fill colors
HEAT_DARK_TXT = "#15131a"
HEAT_LIGHT_TXT = "#fbf9f5"

CURRENCIES = {
    "₹ (Indian Rupees, Crores)": ("₹ Cr", "₹ Crores"),
    "$ (US Dollars, Millions)": ("$ M", "US$ Millions"),
    "$ (US Dollars, Thousands)": ("$ K", "US$ Thousands"),
    "€ (Euros, Millions)": ("€ M", "€ Millions"),
    "£ (British Pounds, Millions)": ("£ M", "£ Millions"),
}

DEMO = dict(
    company_name="Bharat Precision Components Ltd",
    sector="Auto Ancillary / Precision Manufacturing",
    currency_short="₹ Cr", currency_long="₹ Crores",
    year_zero_revenue=500.0, is_fictional=True,
)

SLIDER_DEFAULTS = dict(entry=8.0, exit=8.0, senior=4.0, sub=1.5, growth=8.0, margin=20.0)


# ═══════════════════════════ SESSION STATE ═══════════════════════════
if "page" not in st.session_state:
    st.session_state.page = "home"
if "theme" not in st.session_state:
    st.session_state.theme = "dark"
for k, v in DEMO.items():
    if k not in st.session_state:
        st.session_state[k] = v
for k, v in SLIDER_DEFAULTS.items():
    if f"s_{k}" not in st.session_state:
        st.session_state[f"s_{k}"] = v

T = THEMES[st.session_state.theme]


# ═══════════════════════════ CSS ═══════════════════════════
CSS_TEMPLATE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;700;900&family=Syne:wght@400;600;700;800&family=DM+Mono:wght@400;500&display=swap');

html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stToolbar"] {
    background-color: @@BG@@ !important;
}
[data-testid="stHeader"] { background: transparent; }
.main .block-container { padding-top: 1.5rem; padding-bottom: 3rem; max-width: 1140px; }

html, body, p, span, div, label, li { font-family: 'Syne', sans-serif; color: @@TEXT@@; }
h1, h2, h3, h4 { font-family: 'Playfair Display', serif !important; }

/* ---------- HERO ---------- */
.badge {
    display: block; width: fit-content; margin: 0 auto 1.6rem;
    border: 1px solid rgba(@@GOLD_RGB@@,0.35); border-radius: 999px;
    padding: 0.4rem 1.2rem; color: @@GOLD@@; letter-spacing: 0.22em; text-transform: uppercase;
    font-size: 0.7rem; font-weight: 800; background: rgba(@@GOLD_RGB@@,0.06);
}
.hero-title {
    text-align: center; font-family: 'Playfair Display', serif; font-weight: 900;
    font-size: 4.8rem; color: @@INK@@; margin: 0; letter-spacing: 0.01em; line-height: 1.05;
    background: linear-gradient(135deg, @@INK@@ 35%, @@GOLD@@ 100%);
    -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;
}
.hero-sub {
    text-align: center; font-size: 1rem; color: @@MUTE2@@; letter-spacing: 0.18em;
    text-transform: uppercase; font-weight: 600; margin: 0.6rem 0 0;
}
.hero-tagline {
    text-align: center; font-size: 1.2rem; color: @@SOFT@@; max-width: 660px;
    margin: 1.6rem auto 0; line-height: 1.7; font-weight: 400;
}

/* ---------- STATS STRIP ---------- */
.stats-strip { display: flex; gap: 1rem; justify-content: center; margin: 3.2rem 0 2.8rem; flex-wrap: wrap; }
.stat-box {
    background: linear-gradient(180deg, @@CARD_GRAD_TOP@@ 0%, @@CARD_GRAD_BOT@@ 100%);
    border: 1px solid @@BORDER@@; border-radius: 10px;
    padding: 1.5rem 2.2rem; text-align: center; min-width: 165px; flex: 1;
    position: relative; overflow: hidden;
}
.stat-box::after {
    content: ''; position: absolute; bottom: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent, @@GOLD@@, transparent);
}
.stat-num { font-family: 'DM Mono', monospace; font-size: 2rem; color: @@INK@@; font-weight: 500; letter-spacing: -0.02em; }
.stat-label { font-size: 0.74rem; color: @@MUTE2@@; margin-top: 0.5rem; letter-spacing: 0.14em; text-transform: uppercase; }

/* ---------- FEATURE GRID ---------- */
.feature-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 1.2rem; margin: 1.2rem 0 2.8rem; }
.feature-card {
    background: @@CARD@@; border: 1px solid @@BORDER@@; border-radius: 12px;
    padding: 1.8rem 2rem; position: relative; transition: border-color 0.2s ease;
}
.feature-card:hover { border-color: @@BORDER_HOVER@@; }
.feature-num {
    font-family: 'DM Mono', monospace; color: @@GOLD@@; font-size: 0.78rem; font-weight: 500;
    letter-spacing: 0.1em; opacity: 0.85; margin-bottom: 0.7rem; display: block;
}
.feature-card.navy .feature-num { color: @@FEATURE_NAVY_NUM@@; }
.feature-card h3 { color: @@INK@@; margin: 0 0 0.6rem 0; font-size: 1.3rem; font-weight: 700; }
.feature-card p { color: @@SOFT@@; font-size: 0.93rem; line-height: 1.7; margin: 0; }
@media (max-width: 800px) { .feature-grid { grid-template-columns: 1fr; } }

/* ---------- NAVBAR ---------- */
.navbar-brand { display: flex; align-items: center; gap: 0.65rem; font-family: 'Playfair Display', serif;
                font-size: 1.35rem; font-weight: 700; color: @@INK@@; }
.navbar-logo { width: 36px; height: 36px; border-radius: 9px; flex-shrink: 0;
               background: linear-gradient(135deg, rgba(@@GOLD_RGB@@,0.22), rgba(@@NAVY_RGB@@,0.22));
               border: 1px solid @@BORDER@@; display: flex; align-items: center; justify-content: center; font-size: 1.15rem; }
.navbar-brand .accent { color: @@GOLD@@; }
.navbar-border { border-bottom: 1px solid @@BORDER@@; margin: 0.2rem 0 2rem; }

/* ---------- EYEBROW LINE ---------- */
.eyebrow-line { display: flex; align-items: center; gap: 0.55rem; color: @@MUTE@@; font-size: 0.74rem;
                letter-spacing: 0.2em; text-transform: uppercase; font-weight: 700; margin-bottom: 1.2rem; }
.eyebrow-dot { width: 7px; height: 7px; border-radius: 50%; background: @@GREEN@@; display: inline-block;
               box-shadow: 0 0 8px @@GREEN@@; flex-shrink: 0; }

/* ---------- HERO TITLE 2 (value-prop headline) ---------- */
.hero-title2 { font-family: 'Playfair Display', serif; font-weight: 900; font-size: 3.6rem;
               line-height: 1.18; color: @@INK@@; margin: 0; }
.hero-title2 .hl {
    background: linear-gradient(135deg, @@HL1@@ 0%, @@HL2@@ 100%);
    -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;
}

/* ---------- PILL ROW ---------- */
.pill-row { display: flex; gap: 0.6rem; flex-wrap: wrap; margin-top: 1.8rem; }
.pill { display: flex; align-items: center; gap: 0.5rem; border: 1px solid @@BORDER@@; background: @@CARD@@;
        border-radius: 999px; padding: 0.5rem 1.1rem; font-size: 0.84rem; color: @@SOFT@@; font-weight: 600; }

/* ---------- INFO BAR ---------- */
.info-bar { display: flex; gap: 2.6rem; align-items: center; flex-wrap: wrap; border: 1px solid @@BORDER@@;
            border-top: 2px solid @@GOLD@@; border-radius: 10px; padding: 1.5rem 1.9rem; margin: 2.4rem 0 2.8rem;
            background: @@CARD@@; }
.info-stat .v { font-family: 'DM Mono', monospace; font-size: 1.55rem; color: @@INK@@; font-weight: 500; }
.info-stat .v.neg { color: @@RED@@; }
.info-stat .l { font-size: 0.68rem; color: @@MUTE2@@; letter-spacing: 0.14em; text-transform: uppercase; margin-top: 0.3rem; }
.info-divider { width: 1px; align-self: stretch; background: @@BORDER@@; }
.info-desc { color: @@SOFT@@; font-size: 0.88rem; line-height: 1.65; flex: 1; min-width: 220px; }
.info-desc b { color: @@INK@@; }

/* ---------- SECTION CARDS ---------- */
.section-card {
    background: @@CARD@@; border: 1px solid @@BORDER@@; border-radius: 12px;
    padding: 1.7rem 1.9rem; margin: 1.4rem 0;
}
.section-title {
    font-family: 'Playfair Display', serif; color: @@GOLD@@; font-size: 1.55rem;
    margin: 0 0 1.1rem 0; padding-bottom: 0.7rem; border-bottom: 1px solid @@BORDER@@;
}
.section-title.navy { color: @@NAVY@@; }
.section-sub { color: @@MUTE@@; font-size: 0.85rem; margin: -0.8rem 0 1.1rem 0; }

/* ---------- GHOST BOX ---------- */
.ghost-box {
    background: rgba(@@NAVY_RGB@@,0.14); border-left: 3px solid @@NAVY@@; border-radius: 6px;
    padding: 0.95rem 1.2rem; margin-top: 1.1rem; font-size: 0.93rem; color: @@SOFT@@; line-height: 1.6;
}
.ghost-label {
    color: @@NAVY@@; font-weight: 800; font-size: 0.72rem; letter-spacing: 0.18em;
    text-transform: uppercase; margin-bottom: 0.4rem; display: block;
}

/* ---------- TABLES ---------- */
.table-scroll { overflow-x: auto; }
table.lbo { width: 100%; border-collapse: collapse; font-family: 'DM Mono', monospace; font-size: 0.86rem; }
table.lbo th { text-align: right; color: @@MUTE@@; font-weight: 500; padding: 0.5rem 0.6rem;
                border-bottom: 1px solid @@BORDER@@; white-space: nowrap; }
table.lbo th:first-child, table.lbo td:first-child {
    text-align: left; font-family: 'Syne', sans-serif; color: @@TEXT@@; font-size: 0.88rem; white-space: nowrap;
}
table.lbo td { text-align: right; padding: 0.42rem 0.6rem; color: @@SOFT@@; border-bottom: 1px solid @@BORDER2@@; white-space: nowrap; }
table.lbo tr.total td { font-weight: 700; color: @@TEXT@@; border-top: 1px solid @@GOLD@@; border-bottom: none; }
table.lbo tr.section-row td {
    color: @@GOLD@@; font-weight: 800; padding-top: 1rem; font-family: 'Syne', sans-serif;
    font-size: 0.78rem; letter-spacing: 0.12em; text-transform: uppercase; border-bottom: none;
}
table.lbo tr.bold td { font-weight: 700; color: @@TEXT@@; }
table.lbo tr.last td { border-bottom: none; }

/* ---------- RETURNS METRICS ---------- */
.returns-grid { display: flex; gap: 2.5rem; justify-content: center; margin: 0.5rem 0 1.2rem; flex-wrap: wrap; }
.returns-metric { text-align: center; }
.returns-value { font-family: 'DM Mono', monospace; font-size: 3.4rem; font-weight: 500; color: @@GREEN@@; line-height: 1; }
.returns-value.neg { color: @@RED@@; }
.returns-label { color: @@MUTE@@; letter-spacing: 0.2em; text-transform: uppercase; font-size: 0.78rem; margin-top: 0.6rem; }

/* ---------- HEATMAP ---------- */
table.heat { border-collapse: collapse; margin: 0 auto; font-family: 'DM Mono', monospace; font-size: 0.85rem; }
table.heat th, table.heat td { padding: 0.65rem 1.05rem; text-align: center; border: 1px solid @@BG@@; border-radius: 4px; white-space: nowrap; }
table.heat th { color: @@MUTE@@; font-weight: 600; background: @@HEAT_HEADER_BG@@; font-size: 0.8rem; }
table.heat th.corner { background: transparent; color: @@MUTE@@; font-size: 0.68rem; font-weight: 700;
                        text-transform: uppercase; letter-spacing: 0.08em; text-align: left; vertical-align: bottom; }

/* ---------- BUTTONS ---------- */
.stButton > button, .stDownloadButton > button {
    background: @@GOLD@@ !important; color: @@BTN_TEXT@@ !important; border: none !important;
    border-radius: 6px !important; font-family: 'Syne', sans-serif !important; font-weight: 700 !important;
    padding: 0.7rem 1.8rem !important; letter-spacing: 0.04em;
    transition: transform 0.1s ease;
}
.stButton > button:hover, .stDownloadButton > button:hover { transform: translateY(-1px); background: @@BTN_HOVER@@ !important; }
.stButton > button p, .stDownloadButton > button p { color: @@BTN_TEXT@@ !important; font-weight: 700 !important; }

/* ---------- SLIDERS ---------- */
[data-testid="stSlider"] [role="slider"] { background-color: @@GOLD@@ !important; }
[data-baseweb="slider"] div[data-testid="stTickBar"] { display: none; }
div[data-testid="stSliderTickBarMin"], div[data-testid="stSliderTickBarMax"] { color: @@MUTE@@; }
.stSlider label p { color: @@SOFT@@ !important; font-size: 0.85rem !important; }

/* ---------- FORM INPUTS ---------- */
[data-testid="stTextInput"] input, [data-testid="stNumberInput"] input {
    background-color: @@CARD@@ !important; color: @@TEXT@@ !important; border: 1px solid @@BORDER@@ !important;
}
[data-baseweb="select"] > div {
    background-color: @@CARD@@ !important; border-color: @@BORDER@@ !important; color: @@TEXT@@ !important;
}
[data-testid="stTextInput"] label p, [data-testid="stNumberInput"] label p, [data-testid="stSelectbox"] label p {
    color: @@SOFT@@ !important;
}
[data-testid="stWidgetLabel"] p { color: @@SOFT@@ !important; }

/* ---------- CONTROL PANEL ---------- */
.control-header { color: @@NAVY@@; font-family: 'Syne', sans-serif; font-weight: 800;
                   letter-spacing: 0.2em; text-transform: uppercase; font-size: 0.78rem; margin-bottom: 0.6rem; }

/* ---------- FOOTER ---------- */
.lbo-footer { text-align: center; color: @@FAINT@@; font-size: 0.78rem; margin-top: 3rem;
              padding-top: 1.4rem; border-top: 1px solid @@BORDER@@; letter-spacing: 0.02em; }

/* hide default streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }

/* ---------- MOBILE ---------- */
@media (max-width: 640px) {
    .main .block-container { padding-left: 0.8rem; padding-right: 0.8rem; padding-top: 1rem; }
    .navbar-brand { font-size: 1.1rem; }
    .navbar-logo { width: 30px; height: 30px; font-size: 1rem; }
    .navbar-border { margin: 0.2rem 0 1.4rem; }
    .eyebrow-line { font-size: 0.62rem; letter-spacing: 0.14em; }
    .hero-title2 { font-size: 2.3rem; }
    .pill { font-size: 0.74rem; padding: 0.4rem 0.85rem; }
    .info-bar { padding: 1.1rem 1.2rem; gap: 1.4rem; }
    .info-divider { display: none; }
    .info-stat .v { font-size: 1.25rem; }
    .hero-title { font-size: 2.7rem; }
    .hero-sub { font-size: 0.7rem; letter-spacing: 0.12em; }
    .hero-tagline { font-size: 0.95rem; margin-top: 1.1rem; }
    .badge { font-size: 0.62rem; padding: 0.35rem 0.9rem; margin-bottom: 1.1rem; }
    .stats-strip { gap: 0.6rem; margin: 2rem 0 1.8rem; }
    .stat-box { min-width: 130px; padding: 1rem 1.2rem; }
    .stat-num { font-size: 1.4rem; }
    .feature-card { padding: 1.3rem 1.4rem; }
    .feature-card h3 { font-size: 1.1rem; }
    .section-card { padding: 1.1rem 1.1rem; }
    .section-title { font-size: 1.25rem; }
    .returns-value { font-size: 2.3rem; }
    .returns-grid { gap: 1.4rem; }
    table.lbo { font-size: 0.72rem; }
    table.lbo th, table.lbo td { padding: 0.32rem 0.4rem; }
    table.heat th, table.heat td { padding: 0.45rem 0.65rem; font-size: 0.72rem; }
}
</style>
"""


def render_css():
    css = CSS_TEMPLATE
    for key, val in T.items():
        css = css.replace(f"@@{key.upper()}@@", str(val))
    st.markdown(css, unsafe_allow_html=True)


render_css()


# ═══════════════════════════ HELPERS ═══════════════════════════
def cr(x):
    return f"{x:,.1f}"


def pct(x):
    return f"{x*100:.1f}%"


def spct(x):
    return f"{x*100:+.1f}%"


def mult(x):
    return f"{x:.2f}x"


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(round(c)))) for c in rgb)


def blend(c1, c2, t):
    t = max(0.0, min(1.0, t))
    a, b = hex_to_rgb(c1), hex_to_rgb(c2)
    return rgb_to_hex(tuple(a[i] + (b[i] - a[i]) * t for i in range(3)))


def text_for_bg(h):
    r, g, b = hex_to_rgb(h)
    return HEAT_DARK_TXT if (0.299 * r + 0.587 * g + 0.114 * b) > 140 else HEAT_LIGHT_TXT


def irr_cell(irr):
    """Returns (bg_color, text_color, display_string) for an IRR sensitivity cell."""
    if irr is None or (isinstance(irr, float) and np.isnan(irr)):
        return T["border"], T["faint"], "N/M"
    p = irr * 100
    if irr < 0:
        bgc = blend(T["navy"], T["red"], irr + 1.0)  # 0 at -100% (navy, "cold"), 1 at 0% (red)
    elif p < 15:
        bgc = T["red"]
    elif p < 25:
        bgc = T["gold"]
    else:
        bgc = T["green"]
    return bgc, text_for_bg(bgc), f"{p:.1f}%"


def slugify(name):
    s = re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_")
    return s or "Company"


def footer():
    if st.session_state.is_fictional:
        disclaimer = (f'LBOdesk · Illustrative example ({st.session_state.company_name} is fictional). '
                       'Assumptions are illustrative — adjust for your own analysis. Not investment advice.')
    else:
        disclaimer = (f'LBOdesk · Model configured for {st.session_state.company_name}. '
                       'Operating assumptions (margins, growth, leverage, WACC) are illustrative defaults — '
                       'replace them with figures specific to this company. Not investment advice.')
    st.markdown(f'<div class="lbo-footer">{disclaimer}</div>', unsafe_allow_html=True)


def theme_toggle():
    label = "☀ Light" if st.session_state.theme == "dark" else "🌙 Dark"
    if st.button(label, key=f"theme_toggle_{st.session_state.page}"):
        st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
        st.rerun()


# ═══════════════════════════ HOME PAGE ═══════════════════════════
def render_home():
    nav_l, nav_r = st.columns([5, 1])
    with nav_l:
        st.markdown(
            '<div class="navbar-brand"><div class="navbar-logo">📐</div>'
            '<div>LBO<span class="accent">desk</span></div></div>',
            unsafe_allow_html=True,
        )
    with nav_r:
        theme_toggle()
    st.markdown('<div class="navbar-border"></div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="eyebrow-line"><span class="eyebrow-dot"></span>'
        'PAPER LBO · CASH SWEEP · ENTRY \u00d7 EXIT SENSITIVITY</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<h1 class="hero-title2">Build the LBO.<br>See the <span class="hl">returns</span>.</h1>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="hero-tagline" style="text-align:left; margin:1.2rem 0 0;">'
        'A fully linked LBO model — the same structure used in private equity interviews and early '
        'deal screening. Set the entry and exit multiples, leverage, growth, and margin assumptions, '
        'and the Sources &amp; Uses, debt paydown, returns, and sensitivity grid recalculate '
        'instantly. Export a formula-driven Excel workbook when you\u2019re ready to take it further.</p>',
        unsafe_allow_html=True,
    )

    st.markdown("""
    <div class="pill-row">
        <div class="pill">💰 Sources &amp; Uses</div>
        <div class="pill">🔁 Cash Sweep Debt Schedule</div>
        <div class="pill">🔍 DCF Cross-Check</div>
        <div class="pill">📊 IRR / MOIC Sensitivity</div>
    </div>
    """, unsafe_allow_html=True)

    # -------- LIVE BASE-CASE INFO BAR --------
    base = run_model(SLIDER_DEFAULTS["entry"], SLIDER_DEFAULTS["exit"], SLIDER_DEFAULTS["senior"],
                      SLIDER_DEFAULTS["sub"], SLIDER_DEFAULTS["growth"] / 100, SLIDER_DEFAULTS["margin"] / 100,
                      year_zero_revenue=DEMO["year_zero_revenue"])
    base_ret = base["returns"]
    irr_cls = "" if base_ret["irr"] >= 0 else "neg"
    moic_cls = "" if base_ret["moic"] >= 0 else "neg"
    leverage0 = (base["senior_debt"] + base["sub_debt"]) / base["year_zero_ebitda"]

    st.markdown(f"""
    <div class="info-bar">
        <div class="info-stat"><div class="v">{mult(SLIDER_DEFAULTS["entry"])}</div><div class="l">Entry Multiple</div></div>
        <div class="info-stat"><div class="v">{mult(SLIDER_DEFAULTS["exit"])}</div><div class="l">Exit Multiple</div></div>
        <div class="info-stat"><div class="v">{mult(leverage0)}</div><div class="l">Total Leverage</div></div>
        <div class="info-divider"></div>
        <div class="info-stat"><div class="v {irr_cls}">{pct(base_ret["irr"])}</div><div class="l">Base Case IRR</div></div>
        <div class="info-stat"><div class="v {moic_cls}">{mult(base_ret["moic"])}</div><div class="l">Base Case MOIC</div></div>
        <div class="info-divider"></div>
        <div class="info-desc">
            <b>Base case, {HOLD_PERIOD_YEARS}-year hold.</b> 3-tranche structure (senior, subordinated,
            sponsor equity) with a 100% cash sweep. Drag the sliders in the model to see how IRR and
            MOIC respond to entry price, exit price, leverage, growth, and margin expansion.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="feature-grid">
        <div class="feature-card">
            <span class="feature-num">01 — Sources &amp; Uses</span>
            <h3>Entry Financing Structure</h3>
            <p>Entry enterprise value, transaction fees, and the financing stack — Senior Debt,
            Subordinated Debt, and Sponsor Equity as the plug. Sources always equal Uses, by
            construction.</p>
        </div>
        <div class="feature-card navy">
            <span class="feature-num">02 — Debt Schedule</span>
            <h3>Cash Sweep Waterfall</h3>
            <p>A year-by-year paydown waterfall: mandatory senior amortization first, then 100% of
            remaining free cash flow sweeps senior debt, then subordinated debt — the engine
            behind LBO returns.</p>
        </div>
        <div class="feature-card">
            <span class="feature-num">03 — DCF Cross-Check</span>
            <h3>Standalone Valuation</h3>
            <p>A reality check on the entry price. Two terminal-value methods — EBITDA exit
            multiple and Gordon Growth perpetuity — discounted at WACC, compared against the
            price being paid.</p>
        </div>
        <div class="feature-card navy">
            <span class="feature-num">04 — Sensitivity</span>
            <h3>IRR / MOIC Grid</h3>
            <p>A live 5×5 grid of entry vs. exit multiples, color-coded so you can see at a glance
            where this deal works — and where it doesn't.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Launch Demo Model →", use_container_width=True):
            for k, v in DEMO.items():
                st.session_state[k] = v
            for k, v in SLIDER_DEFAULTS.items():
                st.session_state[f"s_{k}"] = v
            st.session_state.page = "terminal"
            st.rerun()
    with c2:
        if st.button("Build My Own Model →", use_container_width=True):
            st.session_state.page = "setup"
            st.rerun()

    st.markdown(
        '<p style="text-align:center; color:'
        + T["mute"]
        + '; font-size:0.82rem; margin-top:0.9rem;">'
        'Launch Demo loads a fully worked illustrative example. Build My Own lets you set your '
        'company name, sector, currency, and Year 0 revenue, then tune the same model.</p>',
        unsafe_allow_html=True,
    )

    footer()


# ═══════════════════════════ SETUP PAGE ═══════════════════════════
def render_setup():
    top_l, top_r = st.columns([5, 1])
    with top_l:
        st.markdown('<div class="badge" style="margin:0 0 0.5rem;">Build My Own Model</div>',
                     unsafe_allow_html=True)
        st.markdown('<h2 style="margin:0.2rem 0 0 0;">Set Up Your Company</h2>', unsafe_allow_html=True)
        st.markdown(f'<p style="color:{T["mute"]}; font-size:0.9rem; margin-top:0.3rem;">'
                     'These details drive the labels and Year 0 figures across the model and the '
                     'Excel download. Operating ratios (margins, growth, leverage) stay tunable as '
                     'sliders on the next screen.</p>', unsafe_allow_html=True)
    with top_r:
        theme_toggle()
        if st.button("← Home"):
            st.session_state.page = "home"
            st.rerun()

    st.markdown('<div class="section-card">', unsafe_allow_html=True)

    company_name = st.text_input("Company Name", value=st.session_state.company_name,
                                   placeholder="e.g. Acme Manufacturing Ltd")
    sector = st.text_input("Sector / Industry", value=st.session_state.sector,
                            placeholder="e.g. Industrial Automation")

    c1, c2 = st.columns(2)
    with c1:
        currency_label = st.selectbox("Currency & Unit", list(CURRENCIES.keys()), index=0)
    with c2:
        year_zero_revenue = st.number_input("Year 0 Revenue (LTM)", min_value=0.1, value=float(st.session_state.year_zero_revenue),
                                         step=10.0, format="%.1f")

    currency_short, currency_long = CURRENCIES[currency_label]
    st.markdown(f'<p style="color:{T["mute"]}; font-size:0.82rem; margin-top:-0.4rem;">'
                 f'Figures will be shown as <b>{currency_short}</b> ({currency_long}).</p>',
                 unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    _, c, _ = st.columns([1, 1, 1])
    with c:
        if st.button("Continue to Model →", use_container_width=True):
            st.session_state.company_name = company_name.strip() or "My Company Ltd"
            st.session_state.sector = sector.strip() or "Industry Not Specified"
            st.session_state.currency_short = currency_short
            st.session_state.currency_long = currency_long
            st.session_state.year_zero_revenue = float(year_zero_revenue)
            st.session_state.is_fictional = False
            for k, v in SLIDER_DEFAULTS.items():
                st.session_state[f"s_{k}"] = v
            st.session_state.page = "terminal"
            st.rerun()

    footer()


# ═══════════════════════════ TERMINAL PAGE ═══════════════════════════
def render_terminal():
    company_name = st.session_state.company_name
    sector = st.session_state.sector
    cur_short = st.session_state.currency_short
    cur_long = st.session_state.currency_long
    is_fictional = st.session_state.is_fictional

    top_l, top_r = st.columns([5, 1])
    with top_l:
        st.markdown('<div class="badge" style="margin:0 0 0.5rem;">LBOdesk Terminal</div>',
                     unsafe_allow_html=True)
        st.markdown(f'<h2 style="margin:0.2rem 0 0 0;">{company_name}</h2>', unsafe_allow_html=True)
        st.markdown(f'<p style="color:{T["mute"]}; font-size:0.88rem; margin-top:0.2rem;">'
                     f'{sector} · Illustrative, {cur_long}</p>', unsafe_allow_html=True)
    with top_r:
        theme_toggle()
        if st.button("← Home"):
            st.session_state.page = "home"
            st.rerun()
        if not is_fictional:
            if st.button("Edit Company Info"):
                st.session_state.page = "setup"
                st.rerun()

    # -------- CONTROL PANEL --------
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="control-header">Adjust the deal</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.session_state.s_entry = st.slider("Entry EV / EBITDA", 6.0, 10.0, st.session_state.s_entry, 0.5,
                                               format="%.1fx")
        st.session_state.s_growth = st.slider("Revenue Growth (CAGR)", 4.0, 12.0, st.session_state.s_growth, 0.5,
                                                format="%.1f%%")
    with c2:
        st.session_state.s_exit = st.slider("Exit EV / EBITDA", 6.0, 10.0, st.session_state.s_exit, 0.5,
                                              format="%.1fx")
        st.session_state.s_margin = st.slider("Year 5 EBITDA Margin Target", 16.0, 24.0, st.session_state.s_margin, 0.5,
                                                format="%.1f%%")
    with c3:
        st.session_state.s_senior = st.slider("Senior Debt / EBITDA", 3.0, 5.0, st.session_state.s_senior, 0.25,
                                                format="%.2fx")
        st.session_state.s_sub = st.slider("Subordinated Debt / EBITDA", 0.5, 2.5, st.session_state.s_sub, 0.25,
                                            format="%.2fx")

    if st.button("Reset to defaults"):
        for k, v in SLIDER_DEFAULTS.items():
            st.session_state[f"s_{k}"] = v
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # -------- RUN MODEL --------
    entry_m = st.session_state.s_entry
    exit_m = st.session_state.s_exit
    senior_m = st.session_state.s_senior
    sub_m = st.session_state.s_sub
    growth = st.session_state.s_growth / 100
    margin_y5 = st.session_state.s_margin / 100
    year_zero_revenue = st.session_state.year_zero_revenue

    r = run_model(entry_m, exit_m, senior_m, sub_m, growth, margin_y5, year_zero_revenue=year_zero_revenue)
    om, ds, wacc, dcf, ret = r["om"], r["debt_schedule"], r["wacc"], r["dcf"], r["returns"]
    total_debt0 = r["senior_debt"] + r["sub_debt"]
    year_zero_ebitda = r["year_zero_ebitda"]

    # ═══════════════════════ 1. SOURCES & USES ═══════════════════════
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Sources &amp; Uses</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-sub">{cur_long}, at entry (Year 0)</div>', unsafe_allow_html=True)

    su_html = f"""
    <div class="table-scroll"><table class="lbo">
    <tr><th></th><th>{cur_short}</th></tr>
    <tr class="section-row"><td colspan="2">Uses of Funds</td></tr>
    <tr><td>Entry Enterprise Value ({mult(entry_m)} EBITDA)</td><td>{cr(r["entry_ev"])}</td></tr>
    <tr><td>Transaction Fees (2.0%)</td><td>{cr(r["fees"])}</td></tr>
    <tr class="total"><td>Total Uses</td><td>{cr(r["total_uses"])}</td></tr>
    <tr class="section-row"><td colspan="2">Sources of Funds</td></tr>
    <tr><td>Senior Debt ({mult(senior_m)} EBITDA)</td><td>{cr(r["senior_debt"])}</td></tr>
    <tr><td>Subordinated Debt ({mult(sub_m)} EBITDA)</td><td>{cr(r["sub_debt"])}</td></tr>
    <tr><td>Sponsor Equity (Plug)</td><td>{cr(r["sponsor_equity"])}</td></tr>
    <tr class="total"><td>Total Sources</td><td>{cr(r["total_uses"])}</td></tr>
    </table></div>
    """
    st.markdown(su_html, unsafe_allow_html=True)

    leverage = total_debt0 / year_zero_ebitda
    eq_pct = r["sponsor_equity"] / r["total_uses"]
    st.markdown(f"""
    <div class="ghost-box">
        <span class="ghost-label">What this means</span>
        We're paying {cr(r["entry_ev"])} {cur_short} for a company with {cr(year_zero_ebitda)} {cur_short} of
        EBITDA — that's {mult(entry_m)} the company's annual earnings, before {cr(r["fees"])} {cur_short}
        of deal fees on top. To fund it, lenders put up {cr(total_debt0)} {cur_short}
        ({mult(leverage)} EBITDA of total leverage), and the sponsor writes a check for the rest:
        {cr(r["sponsor_equity"])} {cur_short}, or {pct(eq_pct)} of the total bill. The less equity the
        sponsor needs, the harder the debt is working for them.
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ═══════════════════════ 2. OPERATING MODEL ═══════════════════════
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Operating Model</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-sub">{cur_long} · Year 0 = entry (LTM) · unlevered, standalone build</div>', unsafe_allow_html=True)

    y0_da = year_zero_revenue * DA_PCT_REVENUE
    y0_ebit = year_zero_ebitda - y0_da
    y0_capex = year_zero_revenue * CAPEX_PCT_REVENUE
    y0_nopat = y0_ebit * (1 - TAX_RATE)

    revenue = [year_zero_revenue] + om["revenue"]
    margins = [YEAR_0_EBITDA_MARGIN] + om["margins"]
    ebitda = [year_zero_ebitda] + om["ebitda"]
    da = [y0_da] + om["da"]
    ebit = [y0_ebit] + om["ebit"]
    capex = [y0_capex] + om["capex"]
    nwc = [None] + om["nwc"]
    nopat = [y0_nopat] + om["nopat"]
    fcff = [None] + om["fcff"]

    years_hdr = "".join(f"<th>Year {i}</th>" for i in range(6))

    def row6(label, vals, fmt=cr, cls=""):
        cells = "".join(f"<td>{('—' if v is None else fmt(v))}</td>" for v in vals)
        return f'<tr class="{cls}"><td>{label}</td>{cells}</tr>'

    om_html = f"""
    <div class="table-scroll"><table class="lbo">
    <tr><th></th>{years_hdr}</tr>
    {row6("Revenue", revenue)}
    {row6("EBITDA Margin %", margins, pct)}
    {row6("EBITDA", ebitda, cr, "bold")}
    {row6("D&amp;A", da)}
    {row6("EBIT", ebit)}
    {row6("Capex", capex)}
    {row6("Incremental NWC Investment", nwc)}
    {row6("NOPAT (EBIT \u00d7 (1-Tax))", nopat)}
    {row6("Unlevered FCF (FCFF)", fcff, cr, "bold last")}
    </table></div>
    """
    st.markdown(om_html, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="ghost-box">
        <span class="ghost-label">What this means</span>
        This is the business on a standalone basis — before any debt or interest enters the picture.
        Revenue grows {pct(growth)} a year while the EBITDA margin expands from {pct(YEAR_0_EBITDA_MARGIN)}
        to {pct(margin_y5)} — that margin expansion is the PE playbook: same top line, more profit falls
        through. EBITDA grows from {cr(year_zero_ebitda)} {cur_short} to {cr(ebitda[-1])} {cur_short} over
        the hold. Unlevered FCF (FCFF) is what's left after tax, capex, and working capital — it's this
        stream that gets discounted in the DCF cross-check below. The Debt Schedule section shows what
        happens once financing is layered on top.
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ═══════════════════════ 3. DEBT SCHEDULE ═══════════════════════
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title navy">Debt Schedule — Cash Sweep</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-sub">{cur_long} · Year 0 = entry position (from Sources &amp; Uses) · Priority: mandatory senior amort → senior sweep → sub debt sweep</div>',
                 unsafe_allow_html=True)

    years_hdr6 = "".join(f"<th>Year {i}</th>" for i in range(0, 6))
    senior_end = [row["senior_end"] for row in ds]
    sub_end = [row["sub_end"] for row in ds]
    total_end = [s + b for s, b in zip(senior_end, sub_end)]
    senior_int = [row["senior_interest"] for row in ds]
    sub_int = [row["sub_interest"] for row in ds]
    total_int = [row["total_interest"] for row in ds]
    net_income = [row["net_income"] for row in ds]
    fcf_levered = [row["fcf_before_sweep"] for row in ds]
    mand = [row["mandatory_amort"] for row in ds]
    sr_sweep = [row["senior_sweep"] for row in ds]
    sub_sweep = [row["sub_sweep"] for row in ds]
    lev = [t / e for t, e in zip(total_end, om["ebitda"])]

    # Year 0 column = opening position at entry, anchoring this table to Sources & Uses above
    senior_balances = [r["senior_debt"]] + senior_end
    sub_balances = [r["sub_debt"]] + sub_end
    total_balances = [total_debt0] + total_end
    lev_with_y0 = [leverage] + lev
    senior_int_y0 = [None] + senior_int
    sub_int_y0 = [None] + sub_int
    total_int_y0 = [None] + total_int
    net_income_y0 = [None] + net_income
    fcf_levered_y0 = [None] + fcf_levered
    mand_y0 = [None] + mand
    sr_sweep_y0 = [None] + sr_sweep
    sub_sweep_y0 = [None] + sub_sweep

    def row6ds(label, vals, fmt=cr, cls=""):
        cells = "".join(f"<td>{('—' if v is None else fmt(v))}</td>" for v in vals)
        return f'<tr class="{cls}"><td>{label}</td>{cells}</tr>'

    ds_html = f"""
    <div class="table-scroll"><table class="lbo">
    <tr><th></th>{years_hdr6}</tr>
    {row6ds("Senior Debt — Ending Balance", senior_balances)}
    {row6ds("Subordinated Debt — Ending Balance", sub_balances)}
    {row6ds("Total Debt — Ending Balance", total_balances, cr, "bold")}
    {row6ds("Total Debt / EBITDA", lev_with_y0, mult)}
    {row6ds("Senior Interest Expense", senior_int_y0)}
    {row6ds("Subordinated Interest Expense", sub_int_y0)}
    {row6ds("Total Interest Expense", total_int_y0, cr, "bold")}
    {row6ds("Net Income (Levered)", net_income_y0)}
    {row6ds("FCF Before Sweep (Levered)", fcf_levered_y0, cr, "bold")}
    {row6ds("Mandatory Senior Amortization", mand_y0)}
    {row6ds("Senior Debt Cash Sweep", sr_sweep_y0)}
    {row6ds("Subordinated Debt Cash Sweep", sub_sweep_y0, cr, "last")}
    </table></div>
    """
    st.markdown(ds_html, unsafe_allow_html=True)

    # stacked area chart
    x = [f"Year {i}" for i in range(6)]
    senior_series = [r["senior_debt"]] + senior_end
    sub_series = [r["sub_debt"]] + sub_end

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=senior_series, mode="lines", stackgroup="one", name="Senior Debt",
                              line=dict(width=0.5, color=T["navy"]), fillcolor=f'rgba({T["navy_rgb"]},0.65)'))
    fig.add_trace(go.Scatter(x=x, y=sub_series, mode="lines", stackgroup="one", name="Subordinated Debt",
                              line=dict(width=0.5, color=T["gold"]), fillcolor=f'rgba({T["gold_rgb"]},0.55)'))
    fig.add_annotation(x=x[2], y=senior_series[2] / 2, text="Senior Debt", showarrow=False,
                        font=dict(family="DM Mono", size=12, color=HEAT_LIGHT_TXT))
    fig.add_annotation(x=x[2], y=senior_series[2] + sub_series[2] / 2, text="Subordinated Debt", showarrow=False,
                        font=dict(family="DM Mono", size=12, color=HEAT_DARK_TXT))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False,
        margin=dict(l=10, r=10, t=20, b=10), height=320,
        font=dict(family="DM Mono, monospace", color=T["soft"], size=11),
        xaxis=dict(gridcolor=T["border"], linecolor=T["border"]),
        yaxis=dict(gridcolor=T["border"], title=cur_short, zeroline=False),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"""
    <div class="ghost-box">
        <span class="ghost-label">What this means</span>
        This is the same business, now with financing layered on. Interest on
        {cr(total_debt0)} {cur_short} of debt eats into pre-tax income, which is why "Net Income
        (Levered)" here is lower than the unlevered NOPAT shown in the Operating Model above.
        "FCF Before Sweep" is what's left after tax, capex, and working capital, on a levered
        basis — and every spare unit of it goes straight to paying down the most senior, most
        expensive debt first, like a snowball. Total debt falls from {cr(total_debt0)} {cur_short} to
        {cr(total_end[-1])} {cur_short} over five years, mostly through senior debt paydown — the
        subordinated tranche only starts getting swept once senior is cleared. Leverage drops from
        {mult(leverage)} to {mult(lev[-1])} EBITDA by exit. That deleveraging, on top of EBITDA
        growth, is a big part of where LBO returns come from.
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ═══════════════════════ 4. DCF CROSS-CHECK ═══════════════════════
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">DCF Cross-Check</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-sub">{cur_long} · does the price we\'re paying make sense on a standalone DCF basis?</div>',
                 unsafe_allow_html=True)

    prem_mult = dcf["implied_ev_multiple"] / r["entry_ev"] - 1
    prem_perp = dcf["implied_ev_perp"] / r["entry_ev"] - 1

    wacc_html = f"""
    <div class="table-scroll"><table class="lbo">
    <tr class="section-row"><td colspan="2">Cost of Capital (WACC)</td></tr>
    <tr><td>Cost of Equity (CAPM: Rf + \u03b2 \u00d7 MRP)</td><td>{pct(wacc["cost_of_equity"])}</td></tr>
    <tr><td>Cost of Debt — Pre-Tax (blended)</td><td>{pct(wacc["cost_of_debt_pretax"])}</td></tr>
    <tr><td>Cost of Debt — Post-Tax</td><td>{pct(wacc["cost_of_debt_posttax"])}</td></tr>
    <tr><td>Equity Weight</td><td>{pct(wacc["equity_weight"])}</td></tr>
    <tr><td>Debt Weight</td><td>{pct(wacc["debt_weight"])}</td></tr>
    <tr class="total last"><td>WACC</td><td>{pct(wacc["wacc"])}</td></tr>
    </table></div>
    """
    st.markdown(wacc_html, unsafe_allow_html=True)

    dcf_html = f"""
    <div class="table-scroll"><table class="lbo">
    <tr class="section-row"><td colspan="3">Implied Enterprise Value (discounted at WACC)</td></tr>
    <tr><th></th><th>Implied EV ({cur_short})</th><th>vs Entry EV</th></tr>
    <tr><td>LBO Entry Enterprise Value</td><td>{cr(r["entry_ev"])}</td><td>—</td></tr>
    <tr><td>Method 1 — EBITDA Exit Multiple</td><td>{cr(dcf["implied_ev_multiple"])}</td><td>{spct(prem_mult)}</td></tr>
    <tr><td>Method 2 — Perpetuity Growth (Gordon Growth)</td><td>{cr(dcf["implied_ev_perp"])}</td><td>{spct(prem_perp)}</td></tr>
    <tr class="last"><td>PV of Unlevered FCF, Years 1\u20135</td><td>{cr(dcf["pv_fcff"])}</td><td></td></tr>
    </table></div>
    """
    st.markdown(dcf_html, unsafe_allow_html=True)

    verdict = "looks attractive" if min(prem_mult, prem_perp) > 0 else "looks rich"
    st.markdown(f"""
    <div class="ghost-box">
        <span class="ghost-label">What this means</span>
        The discount rate, WACC, blends what equity investors require ({pct(wacc["cost_of_equity"])},
        via CAPM) with what lenders charge after the tax shield ({pct(wacc["cost_of_debt_posttax"])}),
        weighted by how the deal is actually financed ({pct(wacc["equity_weight"])} equity,
        {pct(wacc["debt_weight"])} debt) — giving {pct(wacc["wacc"])}. Strip away the leverage
        entirely — on a standalone, unlevered basis, discounting future cash flows at that rate, the
        business is worth somewhere between
        {cr(min(dcf["implied_ev_multiple"], dcf["implied_ev_perp"]))} {cur_short} and
        {cr(max(dcf["implied_ev_multiple"], dcf["implied_ev_perp"]))} {cur_short} by the two methods
        above. We're paying {cr(r["entry_ev"])} {cur_short}. Positive % means the DCF says the entry
        price {verdict} — there's room for upside even before leverage and operational improvements
        are layered on. Negative % would mean we're paying a premium to standalone value.
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ═══════════════════════ 5. RETURNS DASHBOARD ═══════════════════════
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Returns to Sponsor Equity</div>', unsafe_allow_html=True)

    irr_cls = "" if ret["irr"] >= 0 else "neg"
    moic_cls = "" if ret["moic"] >= 0 else "neg"
    st.markdown(f"""
    <div class="returns-grid">
        <div class="returns-metric">
            <div class="returns-value {irr_cls}">{pct(ret["irr"])}</div>
            <div class="returns-label">IRR · {HOLD_PERIOD_YEARS}-Year Hold</div>
        </div>
        <div class="returns-metric">
            <div class="returns-value {moic_cls}">{mult(ret["moic"])}</div>
            <div class="returns-label">MOIC</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    ret_html = f"""
    <div class="table-scroll"><table class="lbo">
    <tr class="section-row"><td colspan="2">Exit Value (Year 5)</td></tr>
    <tr><td>Exit EBITDA</td><td>{cr(om["ebitda"][-1])}</td></tr>
    <tr><td>Exit EV/EBITDA Multiple</td><td>{mult(exit_m)}</td></tr>
    <tr class="bold"><td>Exit Enterprise Value</td><td>{cr(ret["exit_ev"])}</td></tr>
    <tr><td>Exit Net Debt</td><td>{cr(ret["exit_net_debt"])}</td></tr>
    <tr class="last bold"><td>Exit Equity Value</td><td>{cr(ret["exit_equity_value"])}</td></tr>
    <tr class="section-row"><td colspan="2">Sponsor Cash Flows</td></tr>
    <tr><td>Initial Sponsor Equity (Year 0)</td><td>({cr(r["sponsor_equity"])})</td></tr>
    <tr class="last"><td>Exit Equity Value (Year 5)</td><td>{cr(ret["exit_equity_value"])}</td></tr>
    </table></div>
    """
    st.markdown(ret_html, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="ghost-box">
        <span class="ghost-label">What this means</span>
        Put in {cr(r["sponsor_equity"])} {cur_short}, get back {cr(ret["exit_equity_value"])} {cur_short}
        in {HOLD_PERIOD_YEARS} years. That's roughly {mult(ret["moic"])} your money, or about
        {pct(ret["irr"])} a year. The exit equity value comes from EBITDA growing from
        {cr(year_zero_ebitda)} {cur_short} to {cr(om["ebitda"][-1])} {cur_short} and net debt falling from
        {cr(total_debt0)} {cur_short} to {cr(ret["exit_net_debt"])} {cur_short} — notice how much of the
        return comes from paying down debt rather than the business simply growing. That's the leverage
        effect at the heart of every LBO.
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ═══════════════════════ 6. IRR SENSITIVITY GRID ═══════════════════════
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title navy">IRR Sensitivity — Entry × Exit Multiple</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Holds the financing structure and operating assumptions fixed; '
                 'varies only entry and exit EV/EBITDA</div>', unsafe_allow_html=True)

    entry_mults, exit_mults, grid = r["entry_mults"], r["exit_mults"], r["grid"]

    header_cells = "".join(f"<th>{xm:.0f}x</th>" for xm in exit_mults)
    rows_html = ""
    for i, em in enumerate(entry_mults):
        cells = ""
        for j in range(len(exit_mults)):
            bgc, fg, txt = irr_cell(grid[i, j])
            is_base = (abs(em - entry_m) < 1e-9 and abs(exit_mults[j] - exit_m) < 1e-9)
            border = f"border: 2px solid {T['ink']};" if is_base else ""
            cells += f'<td style="background:{bgc}; color:{fg}; {border}">{txt}</td>'
        rows_html += f'<tr><th>{em:.0f}x</th>{cells}</tr>'

    heat_html = f"""
    <table class="heat">
    <tr><th class="corner">Entry ↓ / Exit →</th>{header_cells}</tr>
    {rows_html}
    </table>
    """
    st.markdown(f'<div class="table-scroll">{heat_html}</div>', unsafe_allow_html=True)
    st.markdown(
        f'<p style="text-align:center; color:{T["faint"]}; font-size:0.78rem; margin-top:0.6rem;">'
        f'<span style="color:{T["red"]}">■</span> &lt;15% &nbsp; '
        f'<span style="color:{T["gold"]}">■</span> 15–25% &nbsp; '
        f'<span style="color:{T["green"]}">■</span> &gt;25% &nbsp; '
        f'<span style="color:{T["navy"]}">■</span> deeply negative &nbsp; '
        f'<span style="color:{T["faint"]}">■</span> N/M (not viable) &nbsp; · '
        f'box outline = current slider settings</p>',
        unsafe_allow_html=True,
    )

    st.markdown(f"""
    <div class="ghost-box">
        <span class="ghost-label">What this means</span>
        Rows are the price we pay going in; columns are the price someone pays us coming out. The
        debt and operating assumptions stay fixed at your current slider settings — only entry and
        exit multiples move. Move down a row (pay more to get in) and IRR falls, because the same
        debt now has to be financed with more sponsor equity. Move right (sell for more) and IRR
        rises. The base case (highlighted) sits at {mult(entry_m)} entry / {mult(exit_m)} exit, giving
        {pct(ret["irr"])}. "N/M" cells mean the leverage assumed exceeds the purchase price at that
        entry multiple — not a structure any lender would actually fund.
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ═══════════════════════ 7. DOWNLOAD EXCEL ═══════════════════════
    st.markdown('<div class="section-card" style="text-align:center;">', unsafe_allow_html=True)
    st.markdown('<div class="section-title" style="border-bottom:none; text-align:center;">'
                 'Take the Model With You</div>', unsafe_allow_html=True)
    st.markdown(f'<p style="color:{T["soft"]}; max-width:560px; margin:0 auto 1.2rem;">'
                 'Download the full LBO model as an Excel workbook — every cell is a live formula, '
                 'not a hardcoded value. Change any assumption on the Assumptions tab and every other '
                 'tab recalculates: Operating Model, Sources &amp; Uses, Debt Schedule, WACC, DCF '
                 'Cross-Check, and Returns with IRR/MOIC sensitivity grids.</p>',
                 unsafe_allow_html=True)

    excel_buf = generate_excel({
        "entry_ev_ebitda": entry_m, "exit_ev_ebitda": exit_m,
        "senior_debt_mult": senior_m, "sub_debt_mult": sub_m,
        "revenue_growth": growth, "ebitda_margin_year5": margin_y5,
        "company_name": company_name, "sector": sector,
        "currency_short": cur_short, "currency_long": cur_long,
        "year_zero_revenue": year_zero_revenue, "is_fictional": is_fictional,
    })

    _, c, _ = st.columns([1, 1, 1])
    with c:
        st.download_button(
            "Download Excel Template", data=excel_buf,
            file_name=f"LBOdesk_{slugify(company_name)}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)

    footer()


# ═══════════════════════════ ROUTER ═══════════════════════════
if st.session_state.page == "home":
    render_home()
elif st.session_state.page == "setup":
    render_setup()
else:
    render_terminal()