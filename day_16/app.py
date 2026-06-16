import streamlit as st
import plotly.graph_objects as go

from model import (
    COMPANY, SCENARIOS, SCENARIO_NAMES,
    dcf_valuation, sensitivity_grid, reverse_dcf,
    WACC_RANGE, TG_RANGE, EXIT_MULT_RANGE, REVERSE_CAGRS,
)

# ═══ CONFIG ═══
st.set_page_config(page_title="DCFdesk | MCX", page_icon="📊",
                   layout="wide", initial_sidebar_state="collapsed")

# ═══ THEMES ═══
THEMES = {
    "dark": dict(
        bg="#09090e", card="#111118", card_grad_top="#131320", card_grad_bot="#0d0d14",
        border="#1f1f2b", border2="#181822", border_hover="#3a3a4a",
        gold="#c9a96e", gold_rgb="201,169,110", navy="#3a5a7a", navy_rgb="58,90,122",
        green="#4ab87a", red="#e05c6c", amber="#e0a04a",
        ink="#f3ede1", text="#e8e6e1", soft="#c4c1ba", mute="#8a877f",
        mute2="#6f6c66", faint="#5a5750",
        heat_header="#15151f", btn_text="#09090e", btn_hover="#d9bd8a",
        hl1="#c9a96e", hl2="#f3dcb0",
        tab_active_bg="#1a1a28",
    ),
    "light": dict(
        bg="#f7f5ef", card="#ffffff", card_grad_top="#ffffff", card_grad_bot="#f2eee3",
        border="#e6e0d2", border2="#ece6d8", border_hover="#cfc7b4",
        gold="#a9824f", gold_rgb="169,130,79", navy="#3a5a7a", navy_rgb="58,90,122",
        green="#2f8f5b", red="#c0394a", amber="#c07a2a",
        ink="#211e19", text="#2b2823", soft="#524e47", mute="#8a8278",
        mute2="#a89f8f", faint="#b0a89a",
        heat_header="#efeadc", btn_text="#211e19", btn_hover="#c2a06a",
        hl1="#8a6a3c", hl2="#c9a96e",
        tab_active_bg="#f0ebe0",
    ),
}
CELL_DARK  = "#15131a"
CELL_LIGHT = "#fbf9f5"

for key, default in [("theme","dark"),("page","home"),("scenario","Base")]:
    if key not in st.session_state:
        st.session_state[key] = default

T = THEMES[st.session_state.theme]

# ═══ CSS ═══
def inject_css():
    css = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;700;900&family=Syne:wght@400;600;700;800&family=DM+Mono:wght@400;500&display=swap');

html,body,.stApp,[data-testid="stAppViewContainer"],[data-testid="stHeader"]{{background-color:{T['bg']} !important;}}
[data-testid="stHeader"]{{background:transparent;}}
.main .block-container{{padding-top:1.4rem;padding-bottom:3rem;max-width:1200px;}}
html,body,p,span,div,label,li{{font-family:'Syne',sans-serif;color:{T['text']};}}
h1,h2,h3,h4{{font-family:'Playfair Display',serif !important;}}

/* NAVBAR */
.nb{{display:flex;align-items:center;gap:.7rem;margin-bottom:.2rem;}}
.nb-logo{{width:36px;height:36px;border-radius:9px;background:linear-gradient(135deg,rgba({T['gold_rgb']},.22),rgba({T['navy_rgb']},.22));border:1px solid {T['border']};display:flex;align-items:center;justify-content:center;font-size:1.1rem;flex-shrink:0;}}
.nb-brand{{font-family:'Playfair Display',serif;font-size:1.35rem;font-weight:700;color:{T['ink']};}}
.nb-brand .acc{{color:{T['gold']};}}
.nb-border{{border-bottom:1px solid {T['border']};margin:.2rem 0 2rem;}}
.nb-ticker{{font-family:'DM Mono',monospace;font-size:.78rem;color:{T['mute']};margin-left:.5rem;letter-spacing:.06em;}}

/* EYEBROW */
.ey{{display:flex;align-items:center;gap:.55rem;color:{T['mute']};font-size:.73rem;letter-spacing:.2em;text-transform:uppercase;font-weight:700;margin-bottom:1.2rem;}}
.ey-dot{{width:7px;height:7px;border-radius:50%;background:{T['green']};box-shadow:0 0 8px {T['green']};flex-shrink:0;}}

/* HERO */
.ht{{font-family:'Playfair Display',serif;font-weight:900;font-size:3.5rem;line-height:1.18;color:{T['ink']};margin:0;}}
.ht .hl{{background:linear-gradient(135deg,{T['hl1']} 0%,{T['hl2']} 100%);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;}}
.htag{{font-size:1.12rem;color:{T['soft']};max-width:700px;margin:1.2rem 0 0;line-height:1.7;}}

/* INFO BAR */
.ib{{display:flex;gap:2rem;align-items:center;flex-wrap:wrap;border:1px solid {T['border']};border-top:2px solid {T['gold']};border-radius:10px;padding:1.4rem 1.8rem;margin:2.2rem 0 2.6rem;background:{T['card']};}}
.is .v{{font-family:'DM Mono',monospace;font-size:1.5rem;color:{T['ink']};font-weight:500;}}
.is .v.dn{{color:{T['red']};}}
.is .v.up{{color:{T['green']};}}
.is .l{{font-size:.67rem;color:{T['mute2']};letter-spacing:.14em;text-transform:uppercase;margin-top:.3rem;}}
.idiv{{width:1px;align-self:stretch;background:{T['border']};}}
.idesc{{color:{T['soft']};font-size:.87rem;line-height:1.65;flex:1;min-width:200px;}}
.idesc b{{color:{T['ink']};}}

/* PILL ROW */
.pr{{display:flex;gap:.55rem;flex-wrap:wrap;margin-top:1.7rem;}}
.pi{{display:flex;align-items:center;gap:.4rem;border:1px solid {T['border']};background:{T['card']};border-radius:999px;padding:.45rem 1rem;font-size:.82rem;color:{T['soft']};font-weight:600;}}

/* FEATURE GRID */
.fg{{display:grid;grid-template-columns:repeat(3,1fr);gap:1.1rem;margin:1.2rem 0 2.6rem;}}
.fc{{background:{T['card']};border:1px solid {T['border']};border-radius:12px;padding:1.6rem 1.7rem;transition:border-color .2s;}}
.fc:hover{{border-color:{T['border_hover']};}}
.fn{{font-family:'DM Mono',monospace;color:{T['gold']};font-size:.75rem;font-weight:500;opacity:.85;margin-bottom:.6rem;display:block;}}
.fc h3{{color:{T['ink']};margin:0 0 .5rem;font-size:1.1rem;font-weight:700;}}
.fc p{{color:{T['soft']};font-size:.89rem;line-height:1.7;margin:0;}}
@media(max-width:900px){{.fg{{grid-template-columns:repeat(2,1fr);}}}}
@media(max-width:600px){{.fg{{grid-template-columns:1fr;}}}}

/* SECTION CARDS */
.sc{{background:{T['card']};border:1px solid {T['border']};border-radius:12px;padding:1.6rem 1.8rem;margin:1.2rem 0;}}
.sct{{font-family:'Playfair Display',serif;color:{T['gold']};font-size:1.4rem;margin:0 0 .9rem;padding-bottom:.6rem;border-bottom:1px solid {T['border']};}}
.sct.nv{{color:{T['navy']};}}
.scs{{color:{T['mute']};font-size:.82rem;margin:-.6rem 0 .9rem;}}

/* GHOST BOX */
.gb{{background:rgba({T['navy_rgb']},.14);border-left:3px solid {T['navy']};border-radius:6px;padding:.9rem 1.2rem;margin-top:1rem;font-size:.9rem;color:{T['soft']};line-height:1.6;}}
.gbl{{color:{T['navy']};font-weight:800;font-size:.7rem;letter-spacing:.18em;text-transform:uppercase;margin-bottom:.35rem;display:block;}}

/* METRIC CARDS */
.mr{{display:flex;gap:.9rem;margin:1rem 0 1.3rem;flex-wrap:wrap;}}
.mc{{background:{T['card']};border:1px solid {T['border']};border-radius:10px;padding:1.1rem 1.4rem 1.55rem;flex:1;min-width:155px;position:relative;overflow:hidden;}}
.mc::after{{content:'';position:absolute;bottom:0;left:0;right:0;height:2px;background:linear-gradient(90deg,transparent,{T['gold']},transparent);}}
.mv{{font-family:'DM Mono',monospace;font-size:1.8rem;font-weight:500;color:{T['ink']};line-height:1;}}
.mv.up{{color:{T['green']};}}
.mv.dn{{color:{T['red']};}}
.ml{{font-size:.7rem;color:{T['mute2']};letter-spacing:.12em;text-transform:uppercase;margin-top:.45rem;}}

/* TABLES */
.ts{{overflow-x:auto;}}
table.t{{width:100%;border-collapse:collapse;font-family:'DM Mono',monospace;font-size:.84rem;}}
table.t th{{text-align:right;color:{T['mute']};font-weight:500;padding:.48rem .6rem;border-bottom:1px solid {T['border']};white-space:nowrap;}}
table.t th:first-child,table.t td:first-child{{text-align:left;font-family:'Syne',sans-serif;color:{T['text']};font-size:.86rem;white-space:nowrap;}}
table.t td{{text-align:right;padding:.38rem .6rem;color:{T['soft']};border-bottom:1px solid {T['border2']};white-space:nowrap;}}
table.t tr.bold td{{font-weight:700;color:{T['ink']};}}
table.t tr.last td{{border-bottom:none;}}
table.t tr.sec td{{color:{T['gold']};font-weight:800;font-size:.78rem;letter-spacing:.14em;text-transform:uppercase;padding-top:1.4rem;padding-bottom:.4rem;border-bottom:1px solid {T['border']};border-top:none;}}

/* HEATMAP */
table.heat{{border-collapse:collapse;margin:0 auto;font-family:'DM Mono',monospace;font-size:.8rem;}}
table.heat th,table.heat td{{padding:.58rem .85rem;text-align:center;border:1px solid {T['bg']};}}
table.heat th{{color:{T['mute']};font-weight:600;background:{T['heat_header']};font-size:.74rem;}}
table.heat th.corner{{background:transparent;color:{T['mute']};font-size:.63rem;font-weight:700;text-transform:uppercase;letter-spacing:.07em;text-align:left;vertical-align:bottom;}}

/* BUTTONS */
.stButton>button,.stDownloadButton>button{{background:{T['gold']} !important;color:{T['btn_text']} !important;border:none !important;border-radius:6px !important;font-family:'Syne',sans-serif !important;font-weight:700 !important;padding:.68rem 1.8rem !important;transition:transform .1s;}}
.stButton>button:hover,.stDownloadButton>button:hover{{transform:translateY(-1px);background:{T['btn_hover']} !important;}}
.stButton>button p,.stDownloadButton>button p{{color:{T['btn_text']} !important;font-weight:700 !important;}}

/* SLIDERS */
[data-testid="stSlider"] [role="slider"]{{background-color:{T['gold']} !important;}}
.stSlider label p{{color:{T['soft']} !important;font-size:.84rem !important;}}

/* TABS */
[data-testid="stTabs"] [role="tablist"]{{gap:.3rem;border-bottom:1px solid {T['border']};}}
[data-testid="stTabs"] [role="tab"]{{font-family:'Syne',sans-serif;font-weight:700;font-size:.82rem;color:{T['mute']};border-radius:6px 6px 0 0;padding:.5rem 1rem;}}
[data-testid="stTabs"] [role="tab"][aria-selected="true"]{{color:{T['gold']};background:{T['tab_active_bg']};}}
[data-testid="stTabsContent"]{{background:{T['bg']} !important;}}

/* FOOTER */
.foot{{text-align:center;color:{T['faint']};font-size:.76rem;margin-top:3rem;padding-top:1.3rem;border-top:1px solid {T['border']};}}

#MainMenu,footer,header{{visibility:hidden;}}

/* MOBILE */
@media(max-width:640px){{
  .main .block-container{{padding-left:.8rem;padding-right:.8rem;}}
  .ht{{font-size:2.3rem;}}
  .htag{{font-size:.93rem;}}
  .ib{{padding:1rem 1.1rem;gap:1.1rem;}}
  .idiv{{display:none;}}
  .is .v{{font-size:1.2rem;}}
  .mv{{font-size:1.4rem;}}
  table.t{{font-size:.72rem;}}
  table.t th,table.t td{{padding:.3rem .35rem;}}
  table.heat th,table.heat td{{padding:.42rem .55rem;font-size:.7rem;}}
}}
</style>"""
    st.markdown(css, unsafe_allow_html=True)

inject_css()

# ═══ HELPERS ═══
def cr(x):   return f"{x:,.1f}"
def pct(x):  return f"{x*100:.1f}%"
def spct(x): return f"{x*100:+.1f}%"
def inr(x):  return f"₹{x:,.0f}"

def price_cls(p):
    if p >= COMPANY["current_price"]: return "up"
    if p < COMPANY["current_price"] * 0.5: return "dn"
    return ""

def upside_cls(u): return "up" if u > 0 else "dn"

def heat_color(price):
    if price is None: return T["border"], T["faint"], "N/M"
    cp = COMPANY["current_price"]
    ratio = price / cp
    if ratio >= 1.0:   bg = T["green"]
    elif ratio >= 0.7: bg = T["amber"]
    elif ratio >= 0.4: bg = T["gold"]
    else:              bg = T["red"]
    r, g, b = int(bg[1:3], 16), int(bg[3:5], 16), int(bg[5:7], 16)
    txt = CELL_DARK if (0.299*r + 0.587*g + 0.114*b) > 130 else CELL_LIGHT
    return bg, txt, f"₹{price:,.0f}"

def theme_toggle():
    label = "☀ Light" if st.session_state.theme == "dark" else "🌙 Dark"
    if st.button(label, key=f"tt_{st.session_state.page}"):
        st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
        st.rerun()

def footer():
    st.markdown(
        f'<div class="foot">DCFdesk · Day 16 · 30 Days of AI Finance · '
        f'Based on publicly available MCX financials (Screener.in, FY26 TTM). '
        f'Not investment advice. All projections are illustrative.</div>',
        unsafe_allow_html=True)

def ghost(text):
    st.markdown(f'<div class="gb"><span class="gbl">What this means</span>{text}</div>',
                unsafe_allow_html=True)

def row6(label, vals, fmt=cr, cls=""):
    cells = "".join(f"<td>{('—' if v is None else fmt(v))}</td>" for v in vals)
    return f'<tr class="{cls}"><td>{label}</td>{cells}</tr>'

# ═══ HOME ═══
def render_home():
    nl, nr = st.columns([5, 1])
    with nl:
        st.markdown(
            f'<div class="nb"><div class="nb-logo">📊</div>'
            f'<div class="nb-brand">DCF<span class="acc">desk</span>'
            f'<span class="nb-ticker">· MCX · NSE</span></div></div>',
            unsafe_allow_html=True)
    with nr:
        theme_toggle()
    st.markdown('<div class="nb-border"></div>', unsafe_allow_html=True)

    st.markdown(
        f'<div class="ey"><span class="ey-dot"></span>'
        f'REAL FINANCIALS · THREE SCENARIOS · DUAL TV · REVERSE DCF</div>',
        unsafe_allow_html=True)
    st.markdown(
        f'<h1 class="ht">Value the exchange.<br>Question the <span class="hl">price.</span></h1>',
        unsafe_allow_html=True)
    st.markdown(
        f'<p class="htag">A three-scenario DCF on MCX — India\'s commodity exchange monopoly '
        f'with 95.9% market share — built from real FY26 financials. Revenue ₹2,302 Cr. '
        f'EBITDA margin 74.7%. Net cash ₹2,944 Cr. The market says ₹2,885/share. '
        f'The DCF has a different view.</p>',
        unsafe_allow_html=True)

    st.markdown(
        '<div class="pr">'
        '<div class="pi">📊 Real MCX Financials</div>'
        '<div class="pi">🐻 Bear / Base / Bull</div>'
        '<div class="pi">📐 WACC via CAPM</div>'
        '<div class="pi">🔁 Dual Terminal Value</div>'
        '<div class="pi">🔥 Sensitivity Grids</div>'
        '<div class="pi">🔍 Reverse DCF</div>'
        '</div>', unsafe_allow_html=True)

    base_r = dcf_valuation("Base")
    tv_pct = base_r["tv_pct_perpetuity"]
    ev_ebitda = COMPANY["implied_market_ev"] / COMPANY["year_zero_ebitda"]

    st.markdown(f"""
    <div class="ib">
        <div class="is"><div class="v">₹{base_r['implied_price']:,.0f}</div><div class="l">Base DCF Price</div></div>
        <div class="is"><div class="v">₹{COMPANY['current_price']:,}</div><div class="l">Market Price</div></div>
        <div class="is"><div class="v dn">{base_r['upside']*100:+.1f}%</div><div class="l">DCF vs Market</div></div>
        <div class="idiv"></div>
        <div class="is"><div class="v">{ev_ebitda:.1f}x</div><div class="l">EV/EBITDA (LTM)</div></div>
        <div class="is"><div class="v">{tv_pct*100:.0f}%</div><div class="l">% from Terminal Value</div></div>
        <div class="idiv"></div>
        <div class="idesc"><b>Even the Base Case implies ₹{base_r['implied_price']:,.0f}</b> — a {abs(base_r['upside']*100):.0f}% discount
        to ₹{COMPANY['current_price']:,}. The market is pricing MCX at {ev_ebitda:.0f}x EBITDA, implying either
        a much higher terminal multiple or growth well beyond the 5-year horizon.</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="fg">
        <div class="fc"><span class="fn">01 — Scenarios</span>
            <h3>Bear / Base / Bull</h3>
            <p>Three independent views on MCX's ADTV growth, margin sustainability, WACC, and terminal assumptions. Switch live.</p>
        </div>
        <div class="fc"><span class="fn">02 — Comparison</span>
            <h3>All Three Side-by-Side</h3>
            <p>Revenue trajectories, EBITDA margins, and implied prices across Bear/Base/Bull on one screen.</p>
        </div>
        <div class="fc"><span class="fn">03 — Sensitivity</span>
            <h3>Two 7×7 Heatmaps</h3>
            <p>WACC × Terminal Growth and WACC × Exit EBITDA Multiple — see every implied price vs ₹2,885 current.</p>
        </div>
        <div class="fc"><span class="fn">04 — Reverse DCF</span>
            <h3>What Does ₹2,885 Imply?</h3>
            <p>Flip the model: what revenue CAGR does the current market price require? The answer is revealing.</p>
        </div>
        <div class="fc"><span class="fn">05 — Football Field</span>
            <h3>Full Price Range</h3>
            <p>All implied prices — Bear/Base/Bull × Perpetuity/Multiple — on one chart against ₹2,885.</p>
        </div>
        <div class="fc"><span class="fn">06 — Data Sources</span>
            <h3>Real Financials</h3>
            <p>FY26 TTM from Screener.in (BSE/NSE filings). Every assumption is labelled and auditable.</p>
        </div>
    </div>""", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Launch DCFdesk →", width='stretch'):
            st.session_state.page = "terminal"
            st.rerun()
    with c2:
        import os
        script_dir = os.path.dirname(os.path.abspath(__file__))
        excel_data = None
        search_names = ["DCFdesk_Template.xlsx", "DCFdesk_MCX.xlsx", "DCFdesk.xlsx"]
        search_dirs  = [script_dir, os.path.join(script_dir, "day_16"), "."]
        for d in search_dirs:
            for fname in search_names:
                fpath = os.path.join(d, fname)
                try:
                    with open(fpath, "rb") as f:
                        excel_data = f.read()
                    break
                except FileNotFoundError:
                    continue
            if excel_data:
                break
        if excel_data:
            st.download_button("⬇ Download Excel Template", data=excel_data,
                               file_name="DCFdesk_MCX.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                               width='stretch')
        else:
            st.button("⬇ Excel not found — place DCFdesk_MCX.xlsx here", disabled=True, width='stretch')

    st.markdown(f'<p style="text-align:center;color:{T["mute"]};font-size:.8rem;margin-top:.8rem;">'
                f'Based on publicly available MCX financials (Screener.in, FY26 TTM). '
                f'Not investment advice.</p>', unsafe_allow_html=True)
    footer()

# ═══ TERMINAL ═══
def render_terminal():
    tl, tr = st.columns([5, 1])
    with tl:
        st.markdown('<div class="ey" style="margin:0 0 .35rem;">DCFdesk Terminal</div>', unsafe_allow_html=True)
        st.markdown(f'<h2 style="margin:.1rem 0 0;">{COMPANY["name"]}</h2>', unsafe_allow_html=True)
        st.markdown(f'<p style="color:{T["mute"]};font-size:.86rem;margin-top:.2rem;">'
                    f'{COMPANY["ticker"]} · {COMPANY["sector"]} · FY26 TTM · ₹ Crores · '
                    f'Current Price ₹{COMPANY["current_price"]:,}/share</p>', unsafe_allow_html=True)
    with tr:
        theme_toggle()
        if st.button("← Home"):
            st.session_state.page = "home"
            st.rerun()

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["📈 Scenarios", "⚖️ Comparison", "🔥 Sensitivity", "🔍 Reverse DCF", "🏈 Football Field"])

    # ═══ TAB 1: SCENARIOS ═══
    with tab1:
        sc_cols = st.columns([1, 1, 1, 3])
        for i, name in enumerate(SCENARIO_NAMES):
            with sc_cols[i]:
                is_active = st.session_state.scenario == name
                col_hex = SCENARIOS[name]["color"]
                txt_hex = "#ffffff" if name == "Bear" else "#09090e"
                if is_active:
                    st.markdown(f"""<style>
                    div[data-testid="column"]:nth-child({i+1}) .stButton button{{
                        background:{col_hex} !important;color:{txt_hex} !important;
                        border:2px solid {col_hex} !important;}}
                    </style>""", unsafe_allow_html=True)
                if st.button(name, key=f"sb_{name}", width='stretch'):
                    st.session_state.scenario = name
                    st.rerun()

        sc = st.session_state.scenario
        s  = SCENARIOS[sc]
        r  = dcf_valuation(sc)

        # Metric cards
        st.markdown(f"""
        <div class="mr">
          <div class="mc"><div class="mv {price_cls(r['implied_price'])}">₹{r['implied_price']:,.0f}</div><div class="ml">Implied Price</div></div>
          <div class="mc"><div class="mv {upside_cls(r['upside'])}">{r['upside']*100:+.1f}%</div><div class="ml">vs ₹{COMPANY['current_price']:,} Current</div></div>
          <div class="mc"><div class="mv">{r['wacc']*100:.2f}%</div><div class="ml">WACC (CAPM)</div></div>
          <div class="mc"><div class="mv">₹{r['avg_implied_ev']:,.0f}</div><div class="ml">Avg Implied EV (₹ Cr)</div></div>
        </div>""", unsafe_allow_html=True)

        st.markdown(f'<p style="color:{s["color"]};font-size:.83rem;font-weight:700;margin-bottom:1rem;">'
                    f'{sc} Case — {s["label"]}</p>', unsafe_allow_html=True)

        # Operating Model
        st.markdown('<div class="sc"><div class="sct">Operating Model — FCFF Build</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="scs">₹ Crores · Y0 = FY26 LTM base · {sc} Case · FCFF = NOPAT + D&amp;A − Capex − ΔNWC</div>', unsafe_allow_html=True)

        yrs_hdr = "".join(f"<th>Y{i}</th>" for i in range(6))
        y0r = COMPANY["year_zero_revenue"]
        y0m = COMPANY["year_zero_ebitda_margin"]
        y0ebitda = COMPANY["year_zero_ebitda"]
        y0da = COMPANY["year_zero_da"]

        rev_all   = [y0r]      + r["revenue"]
        mar_all   = [y0m]      + r["margins"]
        ebd_all   = [y0ebitda] + r["ebitda"]
        ebit_all  = [y0ebitda - y0da] + r["ebit"]
        da_all    = [y0da]     + r["da"]
        nopat_all = [None]     + r["nopat"]
        cap_all   = [None]     + r["capex"]
        nwc_all   = [None]     + r["dnwc"]
        fcff_all  = [None]     + r["fcff"]

        st.markdown(f"""<div class="ts"><table class="t">
        <tr><th></th>{yrs_hdr}</tr>
        {row6("Revenue", rev_all)}
        {row6("EBITDA Margin %", mar_all, pct)}
        {row6("EBITDA", ebd_all, cr, "bold")}
        {row6("D&amp;A", da_all)}
        {row6("EBIT", ebit_all)}
        {row6("Capex", cap_all)}
        {row6("Δ NWC", nwc_all)}
        {row6("NOPAT (EBIT×(1-Tax))", nopat_all)}
        {row6("Unlevered FCF (FCFF)", fcff_all, cr, "bold last")}
        </table></div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Chart 1: Revenue & EBITDA growth trajectory
        years_all = [f"Y{i}" for i in range(6)]
        fig_growth = go.Figure()

        fig_growth.add_trace(go.Bar(
            x=years_all, y=[y0r] + r["revenue"],
            name="Revenue", marker_color=T["navy"],
            opacity=0.85, yaxis="y"))

        fig_growth.add_trace(go.Bar(
            x=years_all, y=[y0ebitda] + r["ebitda"],
            name="EBITDA", marker_color=T["gold"],
            opacity=0.9, yaxis="y"))

        margin_vals = [m * 100 for m in mar_all]
        margin_min = min(margin_vals)
        margin_max = max(margin_vals)

        fig_growth.add_trace(go.Scatter(
            x=years_all, y=margin_vals,
            name="EBITDA Margin %", mode="lines+markers+text",
            line=dict(color=T["green"], width=2.5, dash="dot"),
            marker=dict(size=8, color=T["green"]),
            text=[f"{m:.1f}%" for m in margin_vals],
            textposition="top center",
            textfont=dict(color=T["green"], size=9),
            yaxis="y2"))

        fig_growth.update_layout(
            barmode="group",
            bargap=0.3, bargroupgap=0.05,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=400,
            showlegend=True,
            legend=dict(orientation="h", y=1.13, x=0,
                        font=dict(size=11), bgcolor="rgba(0,0,0,0)"),
            margin=dict(l=60, r=80, t=60, b=40),
            title=f"Revenue &amp; EBITDA Build — {sc} Case",
            title_font=dict(color=T["gold"], size=13),
            font=dict(family="DM Mono, monospace", color=T["soft"], size=11),
            xaxis=dict(gridcolor=T["border"], tickfont=dict(size=12)),
            yaxis=dict(
                gridcolor=T["border"], title="₹ Cr",
                title_font=dict(size=11), side="left"),
            yaxis2=dict(
                title="EBITDA Margin %", side="right",
                overlaying="y", showgrid=False,
                ticksuffix="%", tickfont=dict(size=11),
                # Tight range around actual margin values — no stretching to 0-100%
                range=[margin_min - 8, margin_max + 12],
            ),
        )
        st.plotly_chart(fig_growth, width="stretch")

        # Chart 2: FCFF waterfall (cleaner version)
        st.markdown(f'<p style="color:{T["gold"]};font-family:\'Playfair Display\',serif;font-size:1rem;font-weight:700;margin:.5rem 0 .3rem;">Unlevered Free Cash Flow (FCFF) Build — {sc} Case</p>', unsafe_allow_html=True)

        years = [f"Y{i}" for i in range(1, 6)]
        fig_wf = go.Figure()
        fig_wf.add_trace(go.Bar(name="NOPAT", x=years, y=r["nopat"],
                                marker_color=T["navy"], opacity=0.9,
                                text=[f"₹{v:,.0f}" for v in r["nopat"]],
                                textposition="inside", textfont=dict(color="white", size=9)))
        fig_wf.add_trace(go.Bar(name="+D&A", x=years, y=r["da"],
                                marker_color=T["gold"], opacity=0.8))
        fig_wf.add_trace(go.Bar(name="−Capex", x=years,
                                y=[-c for c in r["capex"]], marker_color=T["red"], opacity=0.75))
        fig_wf.add_trace(go.Bar(name="−ΔNWC", x=years,
                                y=[-n for n in r["dnwc"]], marker_color=T["amber"], opacity=0.75))
        fig_wf.add_trace(go.Scatter(
            name="FCFF", x=years, y=r["fcff"],
            mode="lines+markers+text",
            line=dict(color=T["green"], width=3),
            marker=dict(size=10, color=T["green"], symbol="diamond",
                        line=dict(color=T["bg"], width=2)),
            text=[f"₹{v:,.0f}" for v in r["fcff"]],
            textposition="top center",
            textfont=dict(color=T["green"], size=9)))
        fig_wf.update_layout(
            barmode="relative", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            height=280, showlegend=True,
            legend=dict(orientation="h", y=1.12, font=dict(size=10)),
            margin=dict(l=10, r=10, t=35, b=10),
            font=dict(family="DM Mono, monospace", color=T["soft"], size=11),
            xaxis=dict(gridcolor=T["border"]),
            yaxis=dict(gridcolor=T["border"], title="₹ Cr"),
        )
        st.plotly_chart(fig_wf, width='stretch')

        # DCF Valuation table
        st.markdown('<div class="sc"><div class="sct">DCF Valuation</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="scs">₹ Crores · {sc} Case · MCX has net cash ₹{2944:,} Cr — this ADDS to implied equity value</div>', unsafe_allow_html=True)

        tv_pp = r["tv_pct_perpetuity"] * 100
        tv_pm = r["tv_pct_multiple"] * 100

        # WACC sub-table
        st.markdown(f'<p style="color:{T["gold"]};font-family:\'Playfair Display\',serif;font-size:1.1rem;font-weight:700;margin:0 0 .6rem;">Cost of Capital (WACC)</p>', unsafe_allow_html=True)
        st.markdown(f"""<div class="ts"><table class="t">
        <tr><td>Risk-Free Rate</td><td>{pct(s['risk_free'])}</td></tr>
        <tr><td>Market Risk Premium</td><td>{pct(s['mrp'])}</td></tr>
        <tr><td>Levered Beta</td><td>{s['beta']:.2f}x</td></tr>
        <tr><td>Cost of Equity (CAPM: Rf + β × MRP)</td><td>{pct(r['coe'])}</td></tr>
        <tr><td>Cost of Debt (Post-Tax)</td><td>{pct(r['cod_posttax'])}</td></tr>
        <tr><td>Equity Weight / Debt Weight</td><td>{pct(r['equity_weight'])} / {pct(1-r['equity_weight'])}</td></tr>
        <tr class="bold last"><td>WACC</td><td>{pct(r['wacc'])}</td></tr>
        </table></div>""", unsafe_allow_html=True)

        # Method 1
        st.markdown(f'<p style="color:{T["navy"]};font-family:\'Playfair Display\',serif;font-size:1.1rem;font-weight:700;margin:1.4rem 0 .6rem;">Method 1 — Perpetuity Growth (Gordon Growth)</p>', unsafe_allow_html=True)
        st.markdown(f"""<div class="ts"><table class="t">
        <tr><td>PV of FCFFs (Years 1–5)</td><td>{cr(r['pv_fcffs'])}</td></tr>
        <tr><td>Terminal Growth Rate (g)</td><td>{pct(s['terminal_growth'])}</td></tr>
        <tr><td>Terminal Value (TV = Y5 FCFF × (1+g) / (WACC−g))</td><td>{cr(r['tv_perpetuity'])}</td></tr>
        <tr><td>PV of Terminal Value &nbsp;<span style="color:{T['mute']};font-size:.8rem;">({tv_pp:.0f}% of implied EV)</span></td><td>{cr(r['pv_tv_perpetuity'])}</td></tr>
        <tr class="bold last"><td>Implied EV — Perpetuity Method</td><td>{cr(r['implied_ev_perpetuity'])}</td></tr>
        </table></div>""", unsafe_allow_html=True)

        # Method 2
        st.markdown(f'<p style="color:{T["navy"]};font-family:\'Playfair Display\',serif;font-size:1.1rem;font-weight:700;margin:1.4rem 0 .6rem;">Method 2 — Exit EBITDA Multiple</p>', unsafe_allow_html=True)
        st.markdown(f"""<div class="ts"><table class="t">
        <tr><td>Year 5 EBITDA</td><td>{cr(r['ebitda'][-1])}</td></tr>
        <tr><td>Exit EV / EBITDA Multiple</td><td>{s['exit_ebitda_mult']:.0f}x</td></tr>
        <tr><td>Terminal Value (= Y5 EBITDA × Exit Multiple)</td><td>{cr(r['tv_multiple'])}</td></tr>
        <tr><td>PV of Terminal Value &nbsp;<span style="color:{T['mute']};font-size:.8rem;">({tv_pm:.0f}% of implied EV)</span></td><td>{cr(r['pv_tv_multiple'])}</td></tr>
        <tr class="bold last"><td>Implied EV — Exit Multiple Method</td><td>{cr(r['implied_ev_multiple'])}</td></tr>
        </table></div>""", unsafe_allow_html=True)

        # Bridge
        st.markdown(f'<p style="color:{T["gold"]};font-family:\'Playfair Display\',serif;font-size:1.1rem;font-weight:700;margin:1.4rem 0 .6rem;">Bridge to Equity Value &nbsp;<span style="font-size:.82rem;color:{T["mute"]};font-family:\'Syne\',sans-serif;font-weight:400;">EV + Net Cash = Equity (MCX has no debt)</span></p>', unsafe_allow_html=True)
        st.markdown(f"""<div class="ts"><table class="t">
        <tr><td>Average Implied EV (2 methods)</td><td>{cr(r['avg_implied_ev'])}</td></tr>
        <tr><td>Add: Net Cash (Investments ₹2,949 Cr − Borrowings ₹5 Cr)</td><td style="color:{T['green']}">+{cr(2944)}</td></tr>
        <tr><td>Implied Equity Value</td><td>{cr(r['implied_equity'])}</td></tr>
        <tr><td>Shares Outstanding</td><td>{COMPANY['shares_outstanding']:.1f} Cr</td></tr>
        <tr class="bold"><td>Implied Share Price</td><td>₹{r['implied_price']:,.0f}</td></tr>
        <tr class="bold last"><td>vs Current Price ₹{COMPANY['current_price']:,}/share</td>
            <td style="color:{T['green'] if r['upside']>0 else T['red']};font-size:1.05rem;">{spct(r['upside'])}</td></tr>
        </table></div>""", unsafe_allow_html=True)

        ghost(f"In the {sc} case, a 5-year DCF produces an implied price of ₹{r['implied_price']:,.0f} vs "
              f"the market's ₹{COMPANY['current_price']:,}. Note: MCX has ₹2,944 Cr of net cash on its "
              f"balance sheet, which adds ₹115/share of value on top of the operational DCF. Even so, "
              f"the market is paying a significant premium to this model — implying either a terminal "
              f"multiple well above {s['exit_ebitda_mult']:.0f}x EBITDA or growth beyond Year 5.")
        st.markdown('</div>', unsafe_allow_html=True)

    # ═══ TAB 2: COMPARISON ═══
    with tab2:
        all_r = {sc: dcf_valuation(sc) for sc in SCENARIO_NAMES}

        cols3 = st.columns(3)
        for i, sc in enumerate(SCENARIO_NAMES):
            rv = all_r[sc]
            col = SCENARIOS[sc]["color"]
            with cols3[i]:
                st.markdown(f"""
                <div class="sc" style="border-top:3px solid {col};">
                  <div style="color:{col};font-weight:800;font-size:.8rem;letter-spacing:.12em;margin-bottom:.7rem;">{sc.upper()} CASE</div>
                  <div style="font-family:'DM Mono',monospace;font-size:1.65rem;color:{col};font-weight:500;">₹{rv['implied_price']:,.0f}</div>
                  <div style="font-size:.68rem;color:{T['mute2']};letter-spacing:.12em;text-transform:uppercase;margin:.25rem 0 .7rem;">Implied Price</div>
                  <div style="font-size:.86rem;color:{T['soft']};">WACC: {pct(rv['wacc'])}</div>
                  <div style="font-size:.86rem;color:{T['soft']};">Avg EV: ₹{rv['avg_implied_ev']:,.0f} Cr</div>
                  <div style="font-size:.86rem;color:{T['green'] if rv['upside']>0 else T['red']};font-weight:700;margin-top:.35rem;">{spct(rv['upside'])} vs ₹{COMPANY['current_price']:,}</div>
                  <div style="font-size:.76rem;color:{T['mute']};margin-top:.6rem;line-height:1.5;">{SCENARIOS[sc]['label']}</div>
                </div>""", unsafe_allow_html=True)

        # Implied price bar chart
        prices_list = [all_r[sc]["implied_price"] for sc in SCENARIO_NAMES]
        colors_list = [SCENARIOS[sc]["color"] for sc in SCENARIO_NAMES]
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(x=SCENARIO_NAMES, y=prices_list, marker_color=colors_list,
                                 showlegend=False,
                                 text=[f"₹{p:,.0f}" for p in prices_list],
                                 textposition="outside"))
        fig_bar.add_hline(y=COMPANY["current_price"], line_dash="dash", line_color=T["soft"],
                          annotation_text=f"Market ₹{COMPANY['current_price']:,}",
                          annotation_position="right")
        fig_bar.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=290,
            font=dict(family="DM Mono, monospace", color=T["soft"], size=11),
            margin=dict(l=10, r=90, t=45, b=10),
            title="Implied Share Price by Scenario (₹) vs Current Market",
            title_font=dict(color=T["gold"], size=13),
            xaxis=dict(gridcolor=T["border"]),
            yaxis=dict(gridcolor=T["border"]),
        )
        st.plotly_chart(fig_bar, width='stretch')

        # Revenue trajectory
        y_labels = [f"Y{i}" for i in range(6)]
        fig_rev = go.Figure()
        for sc in SCENARIO_NAMES:
            rv = all_r[sc]
            fig_rev.add_trace(go.Scatter(
                x=y_labels, y=[COMPANY["year_zero_revenue"]] + rv["revenue"],
                name=sc, mode="lines+markers",
                line=dict(color=SCENARIOS[sc]["color"], width=2),
                marker=dict(size=6)))
        fig_rev.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=260,
            font=dict(family="DM Mono, monospace", color=T["soft"], size=11),
            margin=dict(l=10, r=10, t=40, b=10),
            title="Revenue Trajectory (₹ Cr) from FY26 Base of ₹2,302 Cr",
            title_font=dict(color=T["gold"], size=13),
            showlegend=True, legend=dict(orientation="h", y=1.12),
            xaxis=dict(gridcolor=T["border"]),
            yaxis=dict(gridcolor=T["border"]),
        )
        st.plotly_chart(fig_rev, width='stretch')

        # EBITDA margin chart
        fig_margin = go.Figure()
        for sc in SCENARIO_NAMES:
            rv = all_r[sc]
            fig_margin.add_trace(go.Scatter(
                x=y_labels,
                y=[COMPANY["year_zero_ebitda_margin"]] + rv["margins"],
                name=sc, mode="lines+markers",
                line=dict(color=SCENARIOS[sc]["color"], width=2),
                marker=dict(size=6)))
        fig_margin.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=260,
            font=dict(family="DM Mono, monospace", color=T["soft"], size=11),
            margin=dict(l=10, r=10, t=40, b=10),
            title="EBITDA Margin Trajectory from FY26 Base of 74.7%",
            title_font=dict(color=T["gold"], size=13),
            showlegend=True, legend=dict(orientation="h", y=1.12),
            xaxis=dict(gridcolor=T["border"]),
            yaxis=dict(gridcolor=T["border"], tickformat=".0%"),
        )
        st.plotly_chart(fig_margin, width='stretch')

        ghost(f"The spread — Bear ₹{prices_list[0]:,.0f} to Bull ₹{prices_list[2]:,.0f} — shows a "
              f"₹{prices_list[2]-prices_list[0]:,.0f} range of outcomes from the same starting point. "
              f"Even the most optimistic case (Bull ₹{prices_list[2]:,.0f}) is still "
              f"{abs(all_r['Bull']['upside']*100):.0f}% below ₹{COMPANY['current_price']:,}. "
              f"The key variable isn't margins (MCX is structurally high-margin as a monopoly exchange) "
              f"— it's the terminal multiple and whether you believe commodity derivatives volumes "
              f"sustain at post-upgrade levels.")

    # ═══ TAB 3: SENSITIVITY ═══
    with tab3:
        base_wacc_val = dcf_valuation("Base")["wacc"]
        base_tg_val   = SCENARIOS["Base"]["terminal_growth"]
        base_em_val   = SCENARIOS["Base"]["exit_ebitda_mult"]

        st.markdown('<div class="sc"><div class="sct">Grid 1 — WACC × Terminal Growth Rate</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="scs">Implied Share Price (₹) · Base FCFFs · Perpetuity Method · '
                    f'Current ₹{COMPANY["current_price"]:,} · Green = at/above current</div>', unsafe_allow_html=True)

        g1 = sensitivity_grid(WACC_RANGE, TG_RANGE, "terminal_growth")
        hdr1 = "".join(f"<th>{g*100:.1f}%</th>" for g in TG_RANGE)
        rows1 = ""
        for i, wacc in enumerate(WACC_RANGE):
            brow = abs(wacc - round(base_wacc_val, 3)) < 0.006
            cells = ""
            for j, tg in enumerate(TG_RANGE):
                bg, fg, txt = heat_color(g1[i][j])
                is_base = brow and abs(tg - base_tg_val) < 0.003
                border = f"border:2px solid {T['ink']};" if is_base else ""
                cells += f'<td style="background:{bg};color:{fg};{border}">{txt}</td>'
            rows1 += f'<tr><th>{wacc*100:.1f}%</th>{cells}</tr>'

        st.markdown(f'<div class="ts"><table class="heat"><tr><th class="corner">WACC↓/g→</th>{hdr1}</tr>{rows1}</table></div>',
                    unsafe_allow_html=True)
        st.markdown(f'<p style="text-align:center;color:{T["faint"]};font-size:.76rem;margin-top:.6rem;">'
                    f'<span style="color:{T["green"]}">■</span> ≥₹{COMPANY["current_price"]:,} &nbsp; '
                    f'<span style="color:{T["amber"]}">■</span> ₹{int(COMPANY["current_price"]*0.7):,}–{COMPANY["current_price"]:,} &nbsp; '
                    f'<span style="color:{T["gold"]}">■</span> ₹{int(COMPANY["current_price"]*0.4):,}–{int(COMPANY["current_price"]*0.7):,} &nbsp; '
                    f'<span style="color:{T["red"]}">■</span> below &nbsp; · outline = base case</p>',
                    unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="sc"><div class="sct">Grid 2 — WACC × Exit EBITDA Multiple</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="scs">Implied Share Price (₹) · Base FCFFs · Exit Multiple Method · '
                    f'Multiples reflect premium exchange valuations globally</div>', unsafe_allow_html=True)

        g2 = sensitivity_grid(WACC_RANGE, EXIT_MULT_RANGE, "exit_multiple")
        hdr2 = "".join(f"<th>{m:.0f}x</th>" for m in EXIT_MULT_RANGE)
        rows2 = ""
        for i, wacc in enumerate(WACC_RANGE):
            brow = abs(wacc - round(base_wacc_val, 3)) < 0.006
            cells = ""
            for j, em in enumerate(EXIT_MULT_RANGE):
                bg, fg, txt = heat_color(g2[i][j])
                is_base = brow and abs(em - base_em_val) < 0.5
                border = f"border:2px solid {T['ink']};" if is_base else ""
                cells += f'<td style="background:{bg};color:{fg};{border}">{txt}</td>'
            rows2 += f'<tr><th>{wacc*100:.1f}%</th>{cells}</tr>'

        st.markdown(f'<div class="ts"><table class="heat"><tr><th class="corner">WACC↓/EV/EBITDA→</th>{hdr2}</tr>{rows2}</table></div>',
                    unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        ghost(f"MCX currently trades at {COMPANY['implied_market_ev']/COMPANY['year_zero_ebitda']:.1f}x LTM EBITDA "
              f"(EV ₹{COMPANY['implied_market_ev']:,.0f} Cr ÷ EBITDA ₹{COMPANY['year_zero_ebitda']:,} Cr). "
              f"To justify ₹{COMPANY['current_price']:,} in the sensitivity grids, you need either a terminal "
              f"EBITDA multiple above 40x (rare even for exchange monopolies) or a very low discount rate. "
              f"The market's implicit assumption is that MCX sustains 70%+ EBITDA margins at much higher "
              f"revenue — a bet on structural commodity volume growth in India.")

    # ═══ TAB 4: REVERSE DCF ═══
    with tab4:
        # Hardcoded at Base case terminal growth (5%) — no slider, consistent with model
        BASE_TG = SCENARIOS["Base"]["terminal_growth"]  # 5.0%
        rdcf = reverse_dcf(REVERSE_CAGRS, terminal_growth_override=BASE_TG)
        cagrs  = [x["cagr"] for x in rdcf]
        prices = [x["implied_price"] for x in rdcf]
        evs    = [x["implied_ev"] for x in rdcf]
        mkt_ev = COMPANY["implied_market_ev"]

        crossover = next((x for x in rdcf if x["implied_price"] >= COMPANY["current_price"]), None)
        max_case  = rdcf[-1]

        st.markdown(f"""
        <div class="sc">
          <div class="sct nv">Reverse DCF — What Does ₹{COMPANY['current_price']:,} Imply?</div>
          <div class="scs">Base Case margins, WACC {r['wacc']*100:.1f}%, terminal growth {BASE_TG*100:.0f}% ·
          Revenue CAGR tested from {REVERSE_CAGRS[0]*100:.0f}% to {REVERSE_CAGRS[-1]*100:.0f}%</div>
          <div style="display:flex;gap:1.5rem;flex-wrap:wrap;margin:1rem 0;">
            <div class="mc" style="flex:1;min-width:160px;">
              <div class="mv">₹{COMPANY['current_price']:,}</div><div class="ml">Current Market Price</div>
            </div>
            <div class="mc" style="flex:1;min-width:160px;">
              <div class="mv">₹{mkt_ev:,.0f} Cr</div><div class="ml">Implied Market EV</div>
            </div>
            <div class="mc" style="flex:1;min-width:160px;">
              <div class="mv" style="color:{T['amber']}">
                {'~' + str(int(crossover['cagr']*100)) + '%' if crossover else '>' + str(int(max_case['cagr']*100)) + '%'}
              </div>
              <div class="ml">CAGR to justify ₹{COMPANY['current_price']:,}</div>
            </div>
            <div class="mc" style="flex:1;min-width:160px;">
              <div class="mv">{BASE_TG*100:.0f}%</div><div class="ml">Terminal Growth Assumed</div>
            </div>
          </div>
        </div>""", unsafe_allow_html=True)

        # Chart — implied price curve with market price line and crossover annotation
        fig_r = go.Figure()
        fig_r.add_trace(go.Scatter(
            x=[c * 100 for c in cagrs], y=prices,
            mode="lines+markers", name="Implied Price",
            line=dict(color=T["gold"], width=3),
            marker=dict(size=9, color=T["gold"],
                        line=dict(color=T["bg"], width=2))))

        # Shade below market price in red, above in green
        fig_r.add_hrect(y0=0, y1=COMPANY["current_price"],
                        fillcolor=T["red"], opacity=0.06, layer="below", line_width=0)
        fig_r.add_hrect(y0=COMPANY["current_price"], y1=max(prices) * 1.2,
                        fillcolor=T["green"], opacity=0.06, layer="below", line_width=0)
        fig_r.add_hline(y=COMPANY["current_price"], line_dash="dash",
                        line_color=T["green"], line_width=1.5,
                        annotation_text=f"₹{COMPANY['current_price']:,} Market Price",
                        annotation_position="right",
                        annotation_font_color=T["green"], annotation_font_size=11)

        # Mark crossover point if it exists
        if crossover:
            fig_r.add_vline(x=crossover["cagr"] * 100, line_dash="dot",
                            line_color=T["amber"], line_width=1.5,
                            annotation_text=f"{crossover['cagr']*100:.0f}% CAGR crossover",
                            annotation_position="top left",
                            annotation_font_color=T["amber"], annotation_font_size=11)

        fig_r.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=340,
            font=dict(family="DM Mono, monospace", color=T["soft"], size=11),
            margin=dict(l=10, r=120, t=45, b=40),
            title=f"Implied Share Price vs Revenue CAGR · Base Margins · g={BASE_TG*100:.0f}%",
            title_font=dict(color=T["gold"], size=13),
            xaxis=dict(gridcolor=T["border"], title="Revenue CAGR (%, Y1–Y5)",
                       ticksuffix="%"),
            yaxis=dict(gridcolor=T["border"], title="Implied Price (₹)",
                       tickprefix="₹"),
            showlegend=False,
        )
        st.plotly_chart(fig_r, width='stretch')

        # Table
        table_rows = "".join(
            f'<tr{"" if x["vs_market"] < 0 else " class=bold"}>'
            f'<td>{x["cagr"]*100:.0f}%</td>'
            f'<td>{cr(x["implied_ev"])}</td>'
            f'<td>₹{x["implied_price"]:,.0f}</td>'
            f'<td style="color:{T["green"] if x["vs_market"]>=0 else T["red"]};font-weight:{"700" if x["vs_market"]>=0 else "400"}">'
            f'{"+" if x["vs_market"]>=0 else ""}{cr(x["vs_market"])}</td></tr>'
            for x in rdcf
        )

        if crossover:
            insight = (f"At Base case margins and {BASE_TG*100:.0f}% terminal growth, the current market "
                       f"price of ₹{COMPANY['current_price']:,} is justified at roughly "
                       f"{crossover['cagr']*100:.0f}% revenue CAGR over 5 years. "
                       f"MCX grew revenue 107% in FY26 — but that was a rebound year after the platform "
                       f"migration. Sustaining {crossover['cagr']*100:.0f}%+ CAGR from this elevated base "
                       f"requires commodity volumes to keep compounding. Either you believe in the "
                       f"structural long-term growth of Indian commodity markets, or the stock is priced "
                       f"for perfection.")
        else:
            insight = (f"Even at {max_case['cagr']*100:.0f}% revenue CAGR — far above any realistic "
                       f"5-year forecast — the DCF produces ₹{max_case['implied_price']:,.0f} vs the "
                       f"market's ₹{COMPANY['current_price']:,}. At {BASE_TG*100:.0f}% terminal growth, "
                       f"the market is pricing MCX on value well beyond the 5-year explicit period — "
                       f"likely years 6–15 of sustained commodity volume growth as India's derivatives "
                       f"market deepens. The current price is a long-duration, high-conviction bet.")

        st.markdown(f"""
        <div class="sc">
          <div class="sct nv">Results — Implied EV &amp; Price at Each Revenue CAGR</div>
          <div class="scs">Base Case margins and WACC · Terminal growth {BASE_TG*100:.0f}% ·
          Market EV = ₹{mkt_ev:,.0f} Cr · Positive "vs Market EV" = CAGR justifies current price</div>
          <div class="ts"><table class="t">
            <tr><th>Revenue CAGR (Y1–Y5)</th><th>Implied EV (₹ Cr)</th>
                <th>Implied Price</th><th>vs Market EV (₹ Cr)</th></tr>
            {table_rows}
          </table></div>
          <div class="gb"><span class="gbl">What this means</span>{insight}</div>
        </div>""", unsafe_allow_html=True)

    # ═══ TAB 5: FOOTBALL FIELD ═══
    with tab5:
        all_r5 = {sc: dcf_valuation(sc) for sc in SCENARIO_NAMES}

        st.markdown('<div class="sc"><div class="sct">Football Field — Full Implied Price Range</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="scs">All methods × all scenarios · ₹/share · '
                    f'vs current market price ₹{COMPANY["current_price"]:,}</div>', unsafe_allow_html=True)

        y_labels_ff = []
        prices_ff   = []
        colors_ff   = []
        for sc in SCENARIO_NAMES:
            rv = all_r5[sc]
            col = SCENARIOS[sc]["color"]
            p_perp = (rv["implied_ev_perpetuity"] - COMPANY["net_debt"]) / COMPANY["shares_outstanding"]
            p_mult = (rv["implied_ev_multiple"]   - COMPANY["net_debt"]) / COMPANY["shares_outstanding"]
            for label, price in [
                (f"{sc} — Perpetuity Growth",    p_perp),
                (f"{sc} — Exit EBITDA Multiple", p_mult),
                (f"{sc} — Average (Used)",        rv["implied_price"]),
            ]:
                y_labels_ff.append(label)
                prices_ff.append(price)
                colors_ff.append(col)

        fig_ff = go.Figure()
        fig_ff.add_trace(go.Bar(x=prices_ff, y=y_labels_ff, orientation="h",
                                marker_color=colors_ff, showlegend=False,
                                text=[f"₹{p:,.0f}" for p in prices_ff],
                                textposition="outside"))
        fig_ff.add_vline(x=COMPANY["current_price"], line_dash="dash", line_color=T["soft"],
                         annotation_text=f"Market ₹{COMPANY['current_price']:,}",
                         annotation_position="top right")
        fig_ff.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=420,
            font=dict(family="DM Mono, monospace", color=T["soft"], size=10),
            margin=dict(l=10, r=100, t=20, b=10),
            xaxis=dict(gridcolor=T["border"], title="Implied Share Price (₹)"),
            yaxis=dict(gridcolor=T["border"]),
        )
        st.plotly_chart(fig_ff, width='stretch')

        # Summary table
        st.markdown('<div class="ts"><table class="t"><tr><th></th><th>Bear</th><th>Base</th><th>Bull</th><th>Current</th></tr>', unsafe_allow_html=True)
        rows_ff = [
            ("Implied Price (Avg)", "implied_price"),
            ("Implied EV — Perpetuity", "implied_ev_perpetuity"),
            ("Implied EV — Exit Multiple", "implied_ev_multiple"),
            ("WACC", "wacc"),
            ("Upside / (Downside)", "upside"),
        ]
        for label, key in rows_ff:
            vals = []
            for sc in SCENARIO_NAMES:
                v = all_r5[sc][key]
                if key == "wacc": vals.append(pct(v))
                elif key == "upside":
                    vals.append(f'<span style="color:{T["green"] if v>0 else T["red"]}">{spct(v)}</span>')
                elif key == "implied_price": vals.append(f"₹{v:,.0f}")
                else: vals.append(cr(v))
            curr = ("₹2,885" if key == "implied_price"
                    else cr(COMPANY["implied_market_ev"]) if "ev" in key.lower()
                    else "—")
            td = "".join(f"<td>{v}</td>" for v in vals)
            st.markdown(f'<tr><td>{label}</td>{td}<td>{curr}</td></tr>', unsafe_allow_html=True)
        st.markdown('</table></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        ghost(f"Every single scenario — Bear (₹{all_r5['Bear']['implied_price']:,.0f}), "
              f"Base (₹{all_r5['Base']['implied_price']:,.0f}), Bull (₹{all_r5['Bull']['implied_price']:,.0f}) "
              f"— sits below the current market price of ₹{COMPANY['current_price']:,}. "
              f"This doesn't mean MCX is a sell — exchange monopolies are often valued on "
              f"optionality, regulatory moat, and long-term volume compounding that a 5-year DCF "
              f"cannot capture. But it does mean the current price requires you to believe in the "
              f"bull case on every single assumption simultaneously, with no margin of safety.")

        footer()

# ═══ ROUTER ═══
if st.session_state.page == "home":
    render_home()
else:
    render_terminal()
