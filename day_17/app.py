"""
CompeteIQ — Day 17 / 30 Days of AI Finance
Competitive intelligence for Indian banking, powered by AI.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import math

from data import (
    COLORS, BANK_COLORS, DEFAULT_CHART_COLORS, DEMO_DATA, SECTOR_PORTER,
    dupont_decomposition, compute_moat_score, moat_breakdown,
    moat_factors_and_summary, normalize_for_radar,
)
from ai_providers import PROVIDERS, normalize_ai_company

# Force layout config
st.set_page_config(page_title="CompeteIQ", page_icon="🏦", layout="wide", initial_sidebar_state="collapsed")

# =========================================================================
# SYSTEM DATA COEFFICIENT DEFINITIONS — Fixed Undefined Global Errors
# =========================================================================
METRIC_DEFS = [
    ("nim_pct", "NIM %", True), ("roa_pct", "ROA %", True), ("roe_pct", "ROE %", True),
    ("cost_to_income_pct", "Cost/Income %", False), ("gnpa_pct", "GNPA %", False),
    ("nnpa_pct", "NNPA %", False), ("crar_pct", "CRAR %", True),
    ("advances_growth_pct", "Advances Growth %", True), ("pbv", "P/BV", True),
]

FORCE_LABELS = {
    "buyer_power": "Buyer Power", "supplier_power": "Supplier Power",
    "threat_of_entry": "Threat of New Entrants", "substitutes": "Threat of Substitutes",
    "rivalry": "Competitive Rivalry",
}

# =========================================================================
# PREMIUM DARK THEME CSS — Matched to LBOdesk Luxe Dark Profile
# =========================================================================
def inject_css():
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Overrides */
    .stApp {{ background-color: #09090e; font-family: 'Inter', sans-serif; }}
    [data-testid="stHeader"] {{ background-color: transparent; }}
    .block-container {{ padding-top: 1.5rem; max-width: 1250px; }}
    
    /* Typography */
    h1, h2, h3, h4 {{ color: #e8e4dc !important; font-family: 'Inter', sans-serif; font-weight: 700; letter-spacing: -0.02em; }}
    p, span, label, div {{ color: #b0ac9f; }}
    
    /* LBOdesk Style Hero Components */
    .lb-tag {{
        color: #c9a96e; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.15em; margin-bottom: 0.5rem;
        display: flex; align-items: center; gap: 6px;
    }}
    .lb-tag::before {{ content: "●"; color: #4ab87a; font-size: 9px; }}
    .lb-hero-title {{ font-size: 52px; font-weight: 700; color: #e8e4dc; line-height: 1.1; letter-spacing: -0.03em; margin-bottom: 10px; }}
    .lb-hero-title span {{ color: #c9a96e; }}
    .lb-hero-desc {{ font-size: 16px; color: #b0ac9f; max-width: 650px; line-height: 1.5; margin-bottom: 2rem; }}
    
    /* Cards Layout */
    .ciq-card {{
        background-color: #111118; border: 1px solid #1e1e28; border-radius: 8px; padding: 20px; margin-bottom: 14px;
    }}
    .ciq-tag {{ color: #666666; font-size: 11px; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 6px; font-weight: 600; }}
    .ciq-tech {{ color: #e8e4dc; font-size: 15px; font-weight: 500; line-height: 1.5; margin-bottom: 6px; }}
    .ciq-plain {{ color: #c9a96e; font-size: 13px; font-style: italic; line-height: 1.4; opacity: 0.95; }}
    
    /* Input Elements Overwrite */
    div[data-testid="stTextInput"] input, div[data-testid="stSelectbox"] div {{
        background-color: #111118 !important; border: 1px solid #1e1e28 !important; color: #e8e4dc !important; border-radius: 6px !important;
    }}
    .stButton button {{
        border-radius: 6px !important; font-weight: 600 !important; background-color: #111118; border: 1px solid #1e1e28; color: #e8e4dc; transition: all 0.2s;
    }}
    .stButton button:hover {{ border-color: #c9a96e; color: #c9a96e; background-color: #111118; }}
    
    /* Tab Layout & High-Contrast Selected Text Overrides */
    div[data-baseweb="tab-list"] {{ background-color: transparent !important; gap: 8px; }}
    button[data-baseweb="tab"] {{
        background-color: #111118 !important; border: 1px solid #1e1e28 !important; border-radius: 20px !important; 
        padding: 6px 16px !important; color: #b0ac9f !important; font-size: 13px !important; height: auto !important;
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        border-color: #c9a96e !important; background-color: #c9a96e !important;
    }}
    button[data-baseweb="tab"][aria-selected="true"] p,
    button[data-baseweb="tab"][aria-selected="true"] span,
    button[data-baseweb="tab"][aria-selected="true"] div {{
        color: #09090e !important; font-weight: 600 !important;
    }}
    hr {{ border-color: #1e1e28; }}
    </style>
    """, unsafe_allow_html=True)


def dark_fig(fig, height=400):
    fig.update_layout(
        paper_bgcolor="#09090e", plot_bgcolor="#111118",
        font=dict(color="#e8e4dc", family="sans-serif"),
        height=height, margin=dict(l=40, r=30, t=50, b=40),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
    )
    fig.update_xaxes(gridcolor="#1e1e28", zerolinecolor="#1e1e28")
    fig.update_yaxes(gridcolor="#1e1e28", zerolinecolor="#1e1e28")
    return fig


def insight_card(technical, plain, tag=None):
    tag_html = f'<div class="ciq-tag">{tag}</div>' if tag else ""
    st.markdown(f"""
    <div class="ciq-card">
        {tag_html}
        <div class="ciq-tech">{technical}</div>
        <div class="ciq-plain">→ {plain}</div>
    </div>
    """, unsafe_allow_html=True)


def bank_color(ticker):
    return BANK_COLORS.get(ticker, DEFAULT_CHART_COLORS[hash(ticker) % len(DEFAULT_CHART_COLORS)])


def fmt_pct(v, decimals=2):
    return "N/A" if v is None else f"{v:.{decimals}f}%"


def fmt_cr(v):
    return "N/A" if v is None else f"₹{v:,.0f} Cr"


# =========================================================================
# SESSION STATE INITIALIZATION
# =========================================================================
if "mode" not in st.session_state:
    st.session_state.mode = None       # 'demo' | 'custom'
if "data" not in st.session_state:
    st.session_state.data = None
if "fetch_error" not in st.session_state:
    st.session_state.fetch_error = None

inject_css()

# =========================================================================
# HOMEPAGE RENDER
# =========================================================================
def render_homepage():
    st.markdown('<div class="lb-tag">COMPETITIVE INTELLIGENCE · DECOMPOSITION · RISK MATRIX</div>', unsafe_allow_html=True)
    st.markdown('<div class="lb-hero-title">CompeteIQ.<br>See the <span>returns.</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="lb-hero-desc">An advanced multi-angle financial mapping framework. Deconstruct operating return dynamics, analyze resource allocation intensities, and evaluate systemic valuation premiums across institutional banking portfolios.</div>', unsafe_allow_html=True)

    st.markdown('<div class="ciq-tag" style="margin-bottom:10px;">Select Execution Engine Mode</div>', unsafe_allow_html=True)
    b1, b2 = st.columns([1.5, 1.5], gap="medium")
    with b1:
        if st.button("⚡ SOURCED BANKING DEMO (FY25)", use_container_width=True):
            st.session_state.mode = "demo"
            st.session_state.data = DEMO_DATA
            st.rerun()
    with b2:
        if st.button("🔍 CUSTOM MULTI-COMPANY ANALYSIS", use_container_width=True):
            st.session_state.mode = "custom"
            st.session_state.data = None
            st.rerun()

    st.markdown("<br><br>", unsafe_allow_html=True)

    # Fixed: Safe string interpolation completely resolving rendering leaking bugs
    html_strip = """
    <div style="background-color: #111118; border: 1px solid #1e1e28; border-radius: 8px; padding: 28px; display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 30px; margin-bottom: 2.5rem;">
        <div style="display: flex; gap: 45px; flex-grow: 1; flex-wrap: wrap; justify-content: flex-start; min-width: 300px;">
            <div style="display: flex; flex-direction: column;">
                <div style="font-size: 32px; font-weight: 700; color: #c9a96e; line-height: 1; margin-bottom: 6px;">5.50x</div>
                <div style="font-size: 10px; color: #666666; text-transform: uppercase; letter-spacing: 0.1em; font-weight: 600;">PEER MEDIAN P/BV</div>
            </div>
            <div style="display: flex; flex-direction: column;">
                <div style="font-size: 32px; font-weight: 700; color: #e8e4dc; line-height: 1; margin-bottom: 6px;">9 Vectors</div>
                <div style="font-size: 10px; color: #666666; text-transform: uppercase; letter-spacing: 0.1em; font-weight: 600;">SYSTEMIC PARAMETERS</div>
            </div>
            <div style="display: flex; flex-direction: column;">
                <div style="font-size: 32px; font-weight: 700; color: #c9a96e; line-height: 1; margin-bottom: 6px;">High-Fidelity</div>
                <div style="font-size: 10px; color: #666666; text-transform: uppercase; letter-spacing: 0.1em; font-weight: 600;">DUPONT ENGINE</div>
            </div>
            <div style="display: flex; flex-direction: column;">
                <div style="font-size: 32px; font-weight: 700; color: #e8e4dc; line-height: 1; margin-bottom: 6px;">0-100</div>
                <div style="font-size: 10px; color: #666666; text-transform: uppercase; letter-spacing: 0.1em; font-weight: 600;">STRUCTURAL RATING INDEX</div>
            </div>
        </div>
        <div style="flex: 1; min-width: 350px; border-left: 1px solid #222230; padding-left: 24px; font-size: 13px; line-height: 1.5; color: #b0ac9f;">
            <b style="color: #e8e4dc; display: block; margin-bottom: 4px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Institutional Environment:</b>
            Multi-stage financial deconstruction verifying asset capacity metrics, liability pricing structures, and systemic bank capitalization. Toggle the execution matrices above to initialize terminal telemetry data maps.
        </div>
    </div>
    """
    st.markdown(html_strip, unsafe_allow_html=True)

    st.markdown('<div class="ciq-tag" style="margin-bottom:15px;">System Analytics Framework</div>', unsafe_allow_html=True)
    f1, f2, f3, f4 = st.columns(4)
    features = [
        ("DuPont Breakdown Matrix", "Isolates ROE composition to trace exactly where yield efficiency emerges."),
        ("Peer Axis Grouping", "Standardizes across core parameters utilizing advanced radar scaling mapping."),
        ("Porter's 5 Forces Model", "Calculates underlying sector entry resistance against intense systemic rivalry."),
        ("Core Moat Classification", "Assigns 0-100 index mapping to quantify durable competitive moats.")
    ]
    for col, (title, desc) in zip([f1, f2, f3, f4], features):
        with col:
            st.markdown(f"""
            <div class="ciq-card" style="min-height:140px; border-left: 2px solid #c9a96e;">
                <b style="color:#e8e4dc; font-size:14px;">{title}</b><br>
                <span style="color:#666666; font-size:12px; display:inline-block; margin-top:8px;">{desc}</span>
            </div>
            """, unsafe_allow_html=True)


# =========================================================================
# SYSTEM WORKSPACES
# =========================================================================
def render_tab_overview():
    if st.session_state.mode == "custom" and st.session_state.data is None:
        render_custom_mode_form()
        return

    data = st.session_state.data
    if data is None:
        st.info("Please execute an operational mode to spin up analytics.")
        return

    st.markdown(f"""
    <div class="ciq-card" style="border-left: 3px solid #c9a96e;">
        <div class="ciq-tag">Sector Profile Context · {data.get('fy', '')}</div>
        <div class="ciq-tech" style="font-size:16px; color:#e8e4dc;">{data.get('sector_overview', '')}</div>
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns(len(data["companies"]))
    for col, co in zip(cols, data["companies"]):
        score = co.get("moat_score") or compute_moat_score(co)
        with col:
            st.markdown(f"""
            <div class="ciq-card" style="border-top: 3px solid {bank_color(co.get('ticker',''))}; min-height: 290px;">
                <span style="font-size:16px; font-weight:700; color:#e8e4dc;">{co['name']}</span><br>
                <span style="color:#666666; font-size:11px; font-weight:600; letter-spacing:0.05em;">{co.get('ticker','')}</span>
                <hr style="margin:12px 0;">
                <div style="font-size:13px; margin-bottom:4px;">ROE: <b style="color:#e8e4dc; float:right;">{fmt_pct(co.get('roe_pct'))}</b></div>
                <div style="font-size:13px; margin-bottom:4px;">NIM: <b style="color:#e8e4dc; float:right;">{fmt_pct(co.get('nim_pct'))}</b></div>
                <div style="font-size:13px; margin-bottom:4px;">GNPA: <b style="color:#e8e4dc; float:right;">{fmt_pct(co.get('gnpa_pct'))}</b></div>
                <div style="font-size:13px; margin-bottom:12px;">P/BV: <b style="color:#e8e4dc; float:right;">{co.get('pbv','N/A')}x</b></div>
                <div style="margin-top:15px; font-size:28px; color:#c9a96e; font-weight:700; line-height:1;">{score}</div>
                <div style="font-size:10px; color:#666666; text-transform:uppercase; font-weight:600; letter-spacing:0.05em;">Moat Score Index</div>
            </div>
            """, unsafe_allow_html=True)


def render_custom_mode_form():
    st.markdown("<h4 style='margin-bottom:20px;'>Configure Customized Target Matrix</h4>", unsafe_allow_html=True)
    cols = st.columns(5)
    names = []
    for i, col in enumerate(cols):
        with col:
            names.append(st.text_input(f"Ticker Target {i+1}", value="", key=f"cname_{i}", placeholder="e.g. HDFCBANK"))

    c1, c2 = st.columns([2, 2])
    with c1:
        provider_label = st.selectbox("Intelligence Extraction Provider Target", list(PROVIDERS.keys()))
    with c2:
        api_key = st.text_input("Bearer Token / Provider API Key", type="password", key="api_key_input")
        
    st.caption("🔒 Security Note: API Credentials processed directly on runtime execution loops without persistent cache layers.")

    if st.button("⚡ INITIATE DATA PROCESSING RUN", type="primary"):
        if not all(names) or not api_key:
            st.warning("Please complete all 5 ticker fields and attach your access key.")
            return
        provider_key, fetch_fn, has_search = PROVIDERS[provider_label]
        with st.spinner("Executing secure pipeline queries..."):
            result = fetch_fn(names, api_key)
        if "error" in result:
            st.session_state.fetch_error = result["error"]
            st.error(f"Pipeline Interruption: {result['error']}")
            return
        try:
            companies = [normalize_ai_company(c) for c in result["companies"]]
            for co in companies:
                if not co.get("moat_score"):
                    co["moat_score"] = compute_moat_score(co)
            data = {
                "sector": "Custom Comparison Set",
                "fy": companies[0].get("fy", "Latest Tracked") if companies else "Latest Tracked",
                "sector_overview": result.get("sector_overview", ""),
                "companies": companies,
                "data_sources": result.get("data_sources", []),
                "porter": _aggregate_porter(companies),
            }
            st.session_state.data = data
            st.session_state.fetch_error = None
            st.rerun()
        except Exception as e:
            st.error(f"Structured Parse Interruption: {e}")


def _aggregate_porter(companies):
    forces = ["buyer_power", "supplier_power", "threat_of_entry", "substitutes", "rivalry"]
    agg = {}
    for f in forces:
        vals = [co.get("porter", {}).get(f) for co in companies if co.get("porter", {}).get(f) is not None]
        agg[f] = round(sum(vals) / len(vals), 1) if vals else 5
    agg["notes"] = {f: "Aggregated across active query runs." for f in forces}
    return agg


def render_tab_dupont(data):
    st.markdown("""
    <div class="ciq-card">
    <b style="font-size:16px; color:#e8e4dc;">High-Fidelity Structure: Multi-Stage DuPont Verification Matrix</b><br>
    <span style="font-size:13px; color:#b0ac9f;">Reconciling fundamental balance lines directly against reported output efficiency vectors. Taller stacked vectors isolate structural leverage dependencies from baseline operational margins.</span>
    </div>
    """, unsafe_allow_html=True)

    rows = dupont_decomposition(data["companies"])
    
    # Chart Visualization
    fig = go.Figure()
    names = [r["name"] for r in rows]
    log_npm = [math.log(max(r["npm"], 0.0001)) for r in rows]
    log_au = [math.log(max(r["au"], 0.0001)) for r in rows]
    log_em = [math.log(max(r["em"], 1.0)) for r in rows]

    fig.add_trace(go.Bar(name="Net Profit Margin Factor (A)", x=names, y=log_npm, marker_color="#c9a96e",
                          customdata=[f"{r['npm']*100:.2f}%" for r in rows],
                          hovertemplate="Margin (A): %{customdata}<extra></extra>"))
    fig.add_trace(go.Bar(name="Asset Utilisation Factor (B)", x=names, y=log_au, marker_color="#3a5a7a",
                          customdata=[f"{r['au']*100:.2f}%" for r in rows],
                          hovertemplate="Utilisation (B): %{customdata}<extra></extra>"))
    fig.add_trace(go.Bar(name="Equity Multiplier Factor (C)", x=names, y=log_em, marker_color="#4ab87a",
                          customdata=[f"{r['em']:.2f}x" for r in rows],
                          hovertemplate="Multiplier (C): %{customdata}<extra></extra>"))
    fig.update_layout(barmode="relative", showlegend=True)
    st.plotly_chart(dark_fig(fig), use_container_width=True)

    st.markdown("<h5>Identity Breakdown Layer: ROE Equation [Reported vs Computed]</h5>", unsafe_allow_html=True)
    identity_rows = []
    for r, co in zip(rows, data["companies"]):
        identity_rows.append({
            "Institution": co["name"],
            "Net Profit (Cr)": fmt_cr(co["net_profit_cr"]),
            "Total Income (Cr)": fmt_cr(co["total_income_cr"]),
            "Net Profit Margin (A)": f"{r['npm']*100:.2f}%",
            "Total Assets (Cr)": fmt_cr(co["total_assets_cr"]),
            "Asset Turnover Ratio (B)": f"{r['au']:.4f}",
            "Net Worth (Cr)": fmt_cr(co["net_worth_cr"]),
            "Equity Multiplier (C)": f"{r['em']:.2f}x",
            "Computed ROE (A*B*C)": f"{r['roe_computed']*100:.2f}%",
            "Reported ROE": fmt_pct(co.get("roe_pct"))
        })
    st.dataframe(pd.DataFrame(identity_rows), use_container_width=True, hide_index=True)

    st.markdown("<h5>Asset Efficiency Layer: Return On Assets (ROA) Identity</h5>", unsafe_allow_html=True)
    roa_rows = []
    for co in data["companies"]:
        computed_roa = (co["net_profit_cr"] / co["total_assets_cr"] * 100) if co["total_assets_cr"] else 0
        roa_rows.append({
            "Institution": co["name"],
            "Net Profit": fmt_cr(co["net_profit_cr"]),
            "Total Sourced Assets": fmt_cr(co["total_assets_cr"]),
            "Computed ROA": f"{computed_roa:.2f}%",
            "Reported ROA Matrix": fmt_pct(co.get("roa_pct"))
        })
    st.dataframe(pd.DataFrame(roa_rows), use_container_width=True, hide_index=True)


def render_tab_peer(data):
    companies = data["companies"]
    norm = normalize_for_radar(companies)

    fig = go.Figure()
    axes = ["NIM", "ROA", "ROE", "GNPA (Inverted)", "CRAR", "Advances Growth"]
    for co in companies:
        n = norm[co["name"]]
        vals = [n["nim_pct"], n["roa_pct"], n["roe_pct"], n["gnpa_pct"], n["crar_pct"], n["growth_pct"]]
        fig.add_trace(go.Scatterpolar(r=vals + [vals[0]], theta=axes + [axes[0]], name=co["name"],
                                       line_color=bank_color(co.get("ticker", "")), fill="toself", opacity=0.15))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100], gridcolor="#1e1e28"),
                                  angularaxis=dict(gridcolor="#1e1e28"), bgcolor="#111118"))
    st.plotly_chart(dark_fig(fig, height=450), use_container_width=True)

    st.markdown("##### Metric Variance Table")
    metric_keys = [k for k, _, _ in METRIC_DEFS]
    metric_labels = [l for _, l, _ in METRIC_DEFS]
    
    z, text = [], []
    for co in companies:
        row_z, row_t = [], []
        for k in metric_keys:
            v = co.get(k)
            row_t.append("N/A" if v is None else f"{v:.2f}")
            row_z.append(v if v is not None else 0)
        z.append(row_z)
        text.append(row_t)

    fig3 = go.Figure(go.Heatmap(
        z=z, x=metric_labels, y=[co["name"] for co in companies],
        text=text, texttemplate="%{text}", colorscale="Viridis", showscale=False
    ))
    st.plotly_chart(dark_fig(fig3, height=350), use_container_width=True)


def render_tab_porter(data):
    porter = data.get("porter", SECTOR_PORTER)
    forces = list(FORCE_LABELS.keys())
    vals = [porter.get(f, 5) for f in forces]
    labels = [FORCE_LABELS[f] for f in forces]

    fig = go.Figure(go.Scatterpolar(r=vals + [vals[0]], theta=labels + [labels[0]], fill="toself",
                                     line_color="#c9a96e", fillcolor="rgba(201,169,110,0.15)"))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 10], gridcolor="#1e1e28"),
                                  bgcolor="#111118"))
    st.plotly_chart(dark_fig(fig, height=420), use_container_width=True)

    notes = porter.get("notes", {})
    for f in forces:
        score = porter.get(f, 5)
        st.markdown(f"""
        <div class="ciq-card">
            <span style="font-weight:600; color:#e8e4dc;">{FORCE_LABELS[f]}</span> 
            <span style="color:#c9a96e; float:right; font-weight:700;">{score} / 10</span>
            <p style="margin-top:8px; font-size:13px; color:#b0ac9f; margin-bottom:0;">{notes.get(f, '')}</p>
        </div>
        """, unsafe_allow_html=True)


def render_tab_moat(data):
    companies = data["companies"]
    
    st.markdown("""
    <div class="ciq-card">
    <b style="font-size:16px; color:#e8e4dc;">System Assessment Level: Comprehensive Franchise Moat Matrix</b><br>
    <span style="font-size:13px; color:#b0ac9f;">Replicating institutional research structural rows. Compiles operational margin spreads, return indices, asset velocity ratios, and capital defenses into a unified comparative baseline.</span>
    </div>
    """, unsafe_allow_html=True)

    moat_matrix = []
    for co in companies:
        score = co.get("moat_score") or compute_moat_score(co)
        npm_calc = (co["net_profit_cr"] / co["total_income_cr"] * 100) if co["total_income_cr"] else 0
        au_calc = (co["total_income_cr"] / co["total_assets_cr"] * 100) if co["total_assets_cr"] else 0
        
        moat_matrix.append({
            "Metric Index Line": co["name"],
            "Net Profit Margin (%)": f"{npm_calc:.2f}%",
            "Asset Velocity / AT (%)": f"{au_calc:.2f}%",
            "Core Net Interest Margin": fmt_pct(co.get("nim_pct")),
            "Operating Cost/Income": fmt_pct(co.get("cost_to_income_pct")),
            "Gross Asset Stress (GNPA)": fmt_pct(co.get("gnpa_pct")),
            "Capital Buffer Ratio (CRAR)": fmt_pct(co.get("crar_pct")),
            "Return on Assets (ROA)": fmt_pct(co.get("roa_pct")),
            "Return on Equity (ROE)": fmt_pct(co.get("roe_pct")),
            "Composite Moat Rating": f"{score} / 100"
        })
        
    df_moat = pd.DataFrame(moat_matrix).set_index("Metric Index Line").T.reset_index()
    df_moat.rename(columns={"index": "Structural Evaluation Parameters"}, inplace=True)
    st.dataframe(df_moat, use_container_width=True, hide_index=True)

    st.markdown("<br><h5>Individual Vulnerability Breakdown Explanations</h5>", unsafe_allow_html=True)
    scored = [(co, co.get("moat_score") or compute_moat_score(co)) for co in companies]
    scored.sort(key=lambda x: -x[1])
    
    for co, score in scored:
        factors, summary = moat_factors_and_summary(co, score)
        with st.expander(f"📊 Structural Deep Dive Layer: {co['name']} — Core Score {score}/100"):
            parts = moat_breakdown(co)
            bdf = pd.DataFrame([{"Factor Parameters": label, "Points Earned": pts, "Max Limit": mx, "Context Line": note} for label, pts, mx, note in parts])
            st.dataframe(bdf, use_container_width=True, hide_index=True)
            insight_card(summary, f"Primary Vectors: {', '.join(factors)}", tag="Core Parameter Analytics")


# =========================================================================
# MAIN CONTROL LOOP
# =========================================================================
def render_terminal():
    data = st.session_state.data
    
    st.markdown('<div class="lb-tag">SYSTEM EXECUTION PANEL ACTIVE</div>', unsafe_allow_html=True)
    st.markdown(f"<h3>Execution Space: Terminal Dashboard ({st.session_state.mode.upper() if st.session_state.mode else ''})</h3>", unsafe_allow_html=True)
    
    tabs = st.tabs(["Overview", "DuPont Analysis Matrix", "Peer Group Vectors", "Porter Pressure Scale", "Comprehensive Moat Assessment"])
    
    with tabs[0]:
        render_tab_overview()
    if data is not None:
        with tabs[1]:
            render_tab_dupont(data)
        with tabs[2]:
            render_tab_peer(data)
        with tabs[3]:
            render_tab_porter(data)
        with tabs[4]:
            render_tab_moat(data)
    else:
        for t in tabs[1:]:
            with t:
                st.info("System Engine idling. Initialize operational telemetry maps in the Primary Overview Workspace tab above.")

    st.markdown("<br><hr>", unsafe_allow_html=True)
    
    if st.button("← ABORT RUN AND RETURN TO TERMINAL HOME"):
        st.session_state.mode = None
        st.session_state.data = None
        st.rerun()


if st.session_state.mode is None:
    render_homepage()
else:
    render_terminal()