"""
CompsDesk — Day 19 · 30 Days of AI Finance
Comparable Company Analysis Engine · Indian IT Sector · FY25
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CompsDesk · Day 19 · 30 Days of AI Finance",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Design tokens ─────────────────────────────────────────────────────────────
COLORS = {
    "bg":         "#09090e",
    "card":       "#111118",
    "card2":      "#16161e",
    "gold":       "#c9a96e",
    "gold_light": "#e8ca90",
    "navy":       "#3a5a7a",
    "navy_dark":  "#1a3a5a",
    "green":      "#4ab87a",
    "red":        "#e05c6c",
    "amber":      "#e0a04a",
    "text1":      "#e8e4dc",
    "text2":      "#b0ac9f",
    "text3":      "#666666",
    "border":     "#2a2a3a",
}

PEER_COLORS = {
    "TCS":                  "#0078D4",
    "Infosys":              "#007CC3",
    "Wipro":                "#7B2D8B",
    "HCL Tech":             "#E31837",
    "Mphasis":              "#1B3A6B",
    "Coforge":              "#F05A28",
    "Meridian Digital Ltd": "#C9A96E",
}

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400;1,700&family=Syne:wght@400;600;700&family=DM+Mono:wght@300;400;500&display=swap');

  [data-testid="stApp"], .stApp,
  [data-testid="stVerticalBlock"],
  [data-testid="stTabsContent"],
  .main, .block-container,
  [data-testid="stMain"] {{
    background-color: {COLORS['bg']} !important;
    color: {COLORS['text1']} !important;
  }}
  .block-container {{ max-width: 1400px; padding: 0 1.5rem 3rem; }}

  h1,h2,h3,h4 {{ font-family:'Syne',sans-serif; color:{COLORS['text1']}; }}
  p,li,label,div {{ color:{COLORS['text1']}; }}

  .stTabs [data-baseweb="tab-list"] {{
    background:{COLORS['card']}; border-bottom:1px solid {COLORS['border']};
    gap:2px; padding:0 8px;
  }}
  .stTabs [data-baseweb="tab"] {{
    background:transparent; color:{COLORS['text2']};
    font-family:'Syne',sans-serif; font-size:0.82rem; font-weight:600;
    letter-spacing:.06em; text-transform:uppercase;
    border-bottom:2px solid transparent; padding:10px 18px;
  }}
  .stTabs [data-baseweb="tab"][aria-selected="true"] {{
    color:{COLORS['gold']}; border-bottom:2px solid {COLORS['gold']};
  }}
  .stTabs [data-baseweb="tab-panel"] {{ background:{COLORS['bg']}; padding-top:1.5rem; }}

  .stButton>button {{
    background:{COLORS['navy']}; color:{COLORS['gold_light']};
    font-family:'Syne',sans-serif; font-weight:600; font-size:0.85rem;
    border:1px solid {COLORS['gold']}44; border-radius:6px;
    padding:10px 22px; transition:all .2s;
  }}
  .stButton>button:hover {{
    background:{COLORS['navy_dark']}; border-color:{COLORS['gold']}99;
    transform:translateY(-1px);
  }}
  .stSelectbox>div>div, .stTextInput>div>div>input, .stTextArea textarea {{
    background:{COLORS['card']} !important; color:{COLORS['text1']} !important;
    border:1px solid {COLORS['border']} !important; border-radius:6px;
  }}
  .stRadio>div {{
    background:{COLORS['card2']}; border-radius:8px; padding:8px 12px;
    border:1px solid {COLORS['border']};
  }}
  .stRadio label {{ font-family:'Syne',sans-serif; font-size:0.85rem; }}
  div[data-testid="stMetricValue"] {{ color:{COLORS['gold']} !important; font-family:'DM Mono',monospace; }}
  div[data-testid="stMetricLabel"] {{ color:{COLORS['text2']} !important; font-size:0.78rem; }}

  /* Download button */
  .stDownloadButton>button {{
    background:{COLORS['navy_dark']}; color:{COLORS['gold_light']};
    font-family:'Syne',sans-serif; font-weight:700;
    border:1px solid {COLORS['gold']}66; border-radius:8px;
    padding:12px 24px; width:100%; font-size:0.9rem;
    transition:all .2s;
  }}
  .stDownloadButton>button:hover {{
    background:{COLORS['gold']}22; border-color:{COLORS['gold']};
  }}
</style>
""", unsafe_allow_html=True)

# ── Data ──────────────────────────────────────────────────────────────────────
PEERS_RAW = [
    ("TCS",      2223, 804300,  361.8,     0, 48908, 255324, 67407, 48797, 134.20, 51.8, 63.0),
    ("Infosys",  1157, 469708,  406.0,     0, 97099, 162990, 38921, 26750,  64.60, 35.2, 39.9),
    ("Wipro",     184, 193749, 1053.0, 20490, 34500,  89088, 18250, 13218,  12.63, 14.9, 17.8),
    ("HCL Tech", 1166, 316630,  271.6,  2150, 11200, 116180, 25480, 15740,  58.02, 22.1, 30.6),
    ("Mphasis",  2326,  44419,   19.1,  1820,  2450,  13496,  2639,  1554,  82.40, 22.7, 30.3),
    ("Coforge",  1483,  63782,   43.0,  1140,  1350,  12051,  1694,   936,  24.29, 20.6, 23.5),
]

TARGET_RAW = {
    "name":         "Meridian Digital Ltd",
    "description":  "Fictional mid-tier Indian IT services. B2B digital transformation, cloud, AI services.",
    "price":        875,
    "shares_cr":    35.0,
    "mktcap_cr":    30625,
    "debt_cr":      500,
    "cash_cr":      1200,
    "net_debt_cr":  -700,
    "ev_cr":        29925,
    "revenue_cr":   8500,
    "ebitda_cr":    1530,
    "ebitda_margin":0.18,
    "pat_cr":       950,
    "eps":          27.14,
    "roe_pct":      19.5,
    "roce_pct":     25.8,
}

# ── Computation ───────────────────────────────────────────────────────────────
def compute_multiples(name, price, mktcap, shares, debt, cash, rev, ebitda, pat, eps, roe, roce):
    net_debt  = debt - cash
    ev        = mktcap + net_debt
    ev_rev    = ev / rev
    ev_ebitda = ev / ebitda
    ebitda_m  = ebitda / rev
    pat_m     = pat / rev
    bvps      = (pat / (roe / 100)) / shares
    pbv       = price / bvps
    pe        = price / eps if eps > 0 else None
    return {
        "name": name, "price": price, "mktcap": mktcap, "shares": shares,
        "net_debt": net_debt, "ev": ev,
        "rev": rev, "ebitda": ebitda, "pat": pat, "eps": eps,
        "ev_rev": ev_rev, "ev_ebitda": ev_ebitda,
        "pe": pe, "pbv": pbv, "bvps": bvps,
        "ebitda_margin": ebitda_m, "pat_margin": pat_m,
        "roe": roe, "roce": roce,
    }

def compute_statistics(peer_multiples, exclude_coforge=False):
    peers = peer_multiples if not exclude_coforge else [p for p in peer_multiples if p["name"] != "Coforge"]
    def stats(vals):
        arr = sorted([v for v in vals if v is not None])
        return {
            "min":    arr[0],
            "q25":    float(np.percentile(arr, 25)),
            "median": float(np.median(arr)),
            "mean":   float(np.mean(arr)),
            "q75":    float(np.percentile(arr, 75)),
            "max":    arr[-1],
        }
    return {
        "ev_rev":    stats([p["ev_rev"]    for p in peers]),
        "ev_ebitda": stats([p["ev_ebitda"] for p in peers]),
        "pe":        stats([p["pe"]        for p in peers]),
        "pbv":       stats([p["pbv"]       for p in peers]),
    }

def implied_valuation(target, stats_dict, stat_key="median"):
    net_debt = target["net_debt_cr"]
    shares   = target["shares_cr"]
    bvps     = (target["pat_cr"] / (target["roe_pct"] / 100)) / shares
    results  = {}

    ev_rev_mult = stats_dict["ev_rev"][stat_key]
    results["EV/Revenue"] = {
        "multiple":       ev_rev_mult,
        "implied_ev":     target["revenue_cr"] * ev_rev_mult,
        "implied_equity": target["revenue_cr"] * ev_rev_mult - net_debt,
        "implied_price":  (target["revenue_cr"] * ev_rev_mult - net_debt) / shares,
    }

    ev_ebitda_mult = stats_dict["ev_ebitda"][stat_key]
    results["EV/EBITDA"] = {
        "multiple":       ev_ebitda_mult,
        "implied_ev":     target["ebitda_cr"] * ev_ebitda_mult,
        "implied_equity": target["ebitda_cr"] * ev_ebitda_mult - net_debt,
        "implied_price":  (target["ebitda_cr"] * ev_ebitda_mult - net_debt) / shares,
    }

    pe_mult = stats_dict["pe"][stat_key]
    results["P/E"] = {
        "multiple":       pe_mult,
        "implied_ev":     target["pat_cr"] * pe_mult + net_debt,
        "implied_equity": target["pat_cr"] * pe_mult,
        "implied_price":  target["eps"] * pe_mult,
    }

    pbv_mult = stats_dict["pbv"][stat_key]
    results["P/BV"] = {
        "multiple":       pbv_mult,
        "implied_ev":     bvps * shares * pbv_mult + net_debt,
        "implied_equity": bvps * shares * pbv_mult,
        "implied_price":  bvps * pbv_mult,
    }

    prices = [v["implied_price"] for v in results.values()]
    results["_summary"] = {
        "low":     min(prices),
        "median":  float(np.median(prices)),
        "high":    max(prices),
        "current": target["price"],
        "upside":  float(np.median(prices)) / target["price"] - 1,
    }
    return results

# ── Session state ─────────────────────────────────────────────────────────────
if "mode" not in st.session_state:
    st.session_state.mode = "demo"
if "peer_multiples" not in st.session_state:
    st.session_state.peer_multiples = [
        compute_multiples(*p) for p in PEERS_RAW
    ]
if "target" not in st.session_state:
    st.session_state.target = TARGET_RAW.copy()
if "stat_key" not in st.session_state:
    st.session_state.stat_key = "median"
if "exclude_coforge" not in st.session_state:
    st.session_state.exclude_coforge = False
if "show_terminal" not in st.session_state:
    st.session_state.show_terminal = False

# ── Helpers ───────────────────────────────────────────────────────────────────
def fmt_cr(v, dp=0):
    if dp == 0:
        return f"₹{v:,.0f} Cr"
    return f"₹{v:,.{dp}f} Cr"

def fmt_price(v):
    return f"₹{v:,.2f}"

def fmt_mult(v, dp=2):
    return f"{v:.{dp}f}x"

def fmt_pct(v):
    return f"{v:.1f}%"

def upside_color(val):
    return COLORS["green"] if val >= 0 else COLORS["red"]

def card_html(title, value, sub="", accent=None):
    c = accent or COLORS["gold"]
    return f"""
    <div style="background:{COLORS['card']};border:1px solid {COLORS['border']};
         border-radius:10px;padding:18px 20px;margin-bottom:4px;">
      <div style="font-family:'Syne',sans-serif;font-size:0.72rem;
           color:{COLORS['text3']};letter-spacing:.1em;text-transform:uppercase;
           margin-bottom:4px;">{title}</div>
      <div style="font-family:'DM Mono',monospace;font-size:1.35rem;
           font-weight:500;color:{c};margin-bottom:2px;">{value}</div>
      <div style="font-size:0.8rem;color:{COLORS['text2']};">{sub}</div>
    </div>
    """

def ghost_html(text):
    return f"""
    <div style="background:{COLORS['card2']};border-left:3px solid {COLORS['navy']};
         border-radius:0 8px 8px 0;padding:12px 16px;margin-top:10px;
         font-family:'Playfair Display',serif;font-style:italic;
         font-size:0.9rem;color:{COLORS['text2']};line-height:1.6;">
      {text}
    </div>
    """

def section_hdr(title, sub=""):
    return f"""
    <div style="margin:28px 0 16px;">
      <div style="font-family:'Syne',sans-serif;font-weight:700;font-size:1.1rem;
           color:{COLORS['gold']};letter-spacing:.04em;">{title}</div>
      {"<div style='font-size:0.82rem;color:" + COLORS['text2'] + ";margin-top:3px;'>" + sub + "</div>" if sub else ""}
    </div>
    """

# ── Dark plotly template ───────────────────────────────────────────────────────
_DARK_AXIS = dict(
    gridcolor=COLORS["border"], zerolinecolor=COLORS["border"],
    tickfont=dict(color=COLORS["text2"], size=10),
    title_font=dict(color=COLORS["text2"]),
)

def dark_layout(**kwargs):
    """Dark Plotly layout. xaxis/yaxis/margin injected after kwargs so callers
    can override any of them without duplicate-keyword crashes."""
    base = dict(
        paper_bgcolor=COLORS["bg"],
        plot_bgcolor=COLORS["card"],
        font=dict(family="DM Mono, monospace", color=COLORS["text1"], size=11),
        hoverlabel=dict(
            bgcolor=COLORS["card"], font_color=COLORS["text1"],
            bordercolor=COLORS["border"],
        ),
        showlegend=False,
    )
    # Apply caller kwargs first so they win over defaults below
    base.update(kwargs)
    # Inject axis/margin defaults only if caller did not supply them
    base.setdefault("xaxis", dict(**_DARK_AXIS))
    base.setdefault("yaxis", dict(**_DARK_AXIS))
    base.setdefault("margin", dict(l=50, r=30, t=50, b=50))
    return base

# ═══════════════════════════════════════════════════════════════════════════════
# HOMEPAGE
# ═══════════════════════════════════════════════════════════════════════════════
if not st.session_state.show_terminal:
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,{COLORS['bg']} 60%,{COLORS['navy_dark']}44 100%);
         padding:60px 24px 40px;text-align:center;border-bottom:1px solid {COLORS['border']};">

      <div style="font-family:'Syne',sans-serif;font-size:0.72rem;font-weight:700;
           letter-spacing:.18em;color:{COLORS['gold']};text-transform:uppercase;
           margin-bottom:20px;display:flex;align-items:center;justify-content:center;gap:10px;">
        <span style="display:inline-block;width:7px;height:7px;border-radius:50%;
             background:{COLORS['green']};animation:pulse 2s infinite;"></span>
        Trading Comps &nbsp;·&nbsp; Peer Multiples &nbsp;·&nbsp; Implied Valuation
      </div>

      <div style="font-family:'Playfair Display',serif;
           font-size:clamp(2.8rem,6vw,5rem);font-weight:700;
           line-height:1.1;color:{COLORS['text1']};margin-bottom:12px;">
        Value by <span style="color:{COLORS['gold']};font-style:italic;">comparison.</span>
      </div>

      <div style="font-family:'Syne',sans-serif;font-size:1.05rem;
           color:{COLORS['text2']};max-width:620px;margin:0 auto 36px;line-height:1.7;">
        Find what the market pays for companies like yours.<br>
        Apply peer multiples. Discover the implied price.
      </div>

      <div style="display:flex;justify-content:center;gap:16px;flex-wrap:wrap;margin-bottom:36px;">
        <span style="background:#111118;border:1px solid #c9a96e44;border-radius:20px;padding:6px 16px;font-family:Syne,sans-serif;font-size:0.78rem;color:#c9a96e;letter-spacing:.06em;">EV/Revenue</span><span style="background:#111118;border:1px solid #c9a96e44;border-radius:20px;padding:6px 16px;font-family:Syne,sans-serif;font-size:0.78rem;color:#c9a96e;letter-spacing:.06em;">EV/EBITDA</span><span style="background:#111118;border:1px solid #c9a96e44;border-radius:20px;padding:6px 16px;font-family:Syne,sans-serif;font-size:0.78rem;color:#c9a96e;letter-spacing:.06em;">P/E</span><span style="background:#111118;border:1px solid #c9a96e44;border-radius:20px;padding:6px 16px;font-family:Syne,sans-serif;font-size:0.78rem;color:#c9a96e;letter-spacing:.06em;">P/BV</span><span style="background:#111118;border:1px solid #c9a96e44;border-radius:20px;padding:6px 16px;font-family:Syne,sans-serif;font-size:0.78rem;color:#c9a96e;letter-spacing:.06em;">Football Field</span>
      </div>
    </div>

    <style>@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.4}}}}</style>
    """, unsafe_allow_html=True)

    # Stats strip
    st.markdown("<div style='padding:24px;'>", unsafe_allow_html=True)
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.markdown(card_html("Verified IT Peers", "6", "FY25 annual data"), unsafe_allow_html=True)
    with s2:
        st.markdown(card_html("Valuation Multiples", "4", "EV/Rev · EV/EBITDA · P/E · P/BV"), unsafe_allow_html=True)
    with s3:
        st.markdown(card_html("Statistical Range", "Min → Max", "Full + ex-outlier stats"), unsafe_allow_html=True)
    with s4:
        st.markdown(card_html("Excel Template", "169 Formulas", "6 sheets · Zero errors"), unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Feature grid
    st.markdown(section_hdr("What CompsDesk does", "Six engines. One verdict."), unsafe_allow_html=True)

    features = [
        ("📋", "Peer Universe",      "6 verified Indian IT peers with FY25 annual financials. Real data, real multiples."),
        ("⚙️", "Multiple Engine",    "Computes EV/Revenue, EV/EBITDA, P/E, P/BV for every peer from first principles."),
        ("📐", "Statistics Engine",  "Min / 25th / Median / Mean / 75th / Max — both including and excluding growth outliers."),
        ("🎯", "Implied Valuation",  "Four methods → four implied prices. See where your target sits vs the peer range."),
        ("⚽", "Football Field",     "The signature comps visual. One chart showing the full implied range across methods."),
        ("🤖", "Custom Mode",        "Paste any company names. Gemini fetches financials and builds your comp set."),
    ]

    c1, c2, c3 = st.columns(3)
    cols = [c1, c2, c3]
    for i, (icon, title, desc) in enumerate(features):
        with cols[i % 3]:
            st.markdown(f"""
            <div style="background:{COLORS['card']};border:1px solid {COLORS['border']};
                 border-radius:12px;padding:22px;margin-bottom:14px;
                 transition:border-color .2s;"
                 onmouseover="this.style.borderColor='{COLORS['gold']}66'"
                 onmouseout="this.style.borderColor='{COLORS['border']}'">
              <div style="font-size:1.6rem;margin-bottom:10px;">{icon}</div>
              <div style="font-family:'Syne',sans-serif;font-weight:700;font-size:0.92rem;
                   color:{COLORS['gold']};margin-bottom:6px;">{title}</div>
              <div style="font-size:0.85rem;color:{COLORS['text2']};line-height:1.5;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    # CTAs
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    cta1, cta2 = st.columns(2)
    with cta1:
        if st.button("→ Launch CompsDesk (Demo Mode)", use_container_width=True):
            st.session_state.show_terminal = True
            st.session_state.mode = "demo"
            st.rerun()
    with cta2:
        if st.button("→ Custom Comp Set (AI-Powered)", use_container_width=True):
            st.session_state.show_terminal = True
            st.session_state.mode = "custom"
            st.rerun()

    st.markdown(f"""
    <div style="text-align:center;padding:32px 0 16px;
         font-family:'DM Mono',monospace;font-size:0.72rem;
         color:{COLORS['text3']};border-top:1px solid {COLORS['border']};margin-top:32px;">
      CompsDesk · Day 19 · 30 Days of AI Finance ·
      Peer data FY25 verified. Meridian Digital Ltd is fictional. Not investment advice.
    </div>
    """, unsafe_allow_html=True)

    st.stop()

# ═══════════════════════════════════════════════════════════════════════════════
# TERMINAL
# ═══════════════════════════════════════════════════════════════════════════════
# Header bar
st.markdown(f"""
<div style="background:{COLORS['card']};border-bottom:1px solid {COLORS['border']};
     padding:14px 24px;display:flex;align-items:center;justify-content:space-between;
     margin-bottom:0;">
  <div>
    <span style="font-family:'Syne',sans-serif;font-weight:700;font-size:1.1rem;
         color:{COLORS['gold']};">📊 CompsDesk</span>
    <span style="font-family:'DM Mono',monospace;font-size:0.75rem;
         color:{COLORS['text3']};margin-left:12px;">Day 19 · 30 Days of AI Finance · Indian IT · FY25</span>
  </div>
</div>
""", unsafe_allow_html=True)

back_col, _ = st.columns([1, 5])
with back_col:
    if st.button("← Back to Home"):
        st.session_state.show_terminal = False
        st.rerun()

st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 Peer Universe",
    "📐 Multiple Statistics",
    "🎯 Implied Valuation",
    "⚽ Football Field",
    "⬇ Download",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — PEER UNIVERSE
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown(section_hdr("Mode", "Demo loads instantly · Custom uses Gemini + Google Search"), unsafe_allow_html=True)
    mode_sel = st.radio(
        "Select mode",
        ["Demo — Indian IT FY25", "Custom — AI-Powered"],
        horizontal=True,
        label_visibility="collapsed",
    )

    if "Custom" in mode_sel:
        st.markdown(section_hdr("Custom Comp Set", "Gemini fetches financials automatically via Google Search"), unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            target_input = st.text_input("Target Company", placeholder="e.g. L&T Technology Services")
            sector_input = st.text_input("Sector", value="Indian IT Services")
        with c2:
            peer_inputs = []
            for i in range(5):
                p = st.text_input(f"Peer {i+1}", placeholder=f"e.g. {'Persistent Systems' if i==0 else 'Zensar Technologies' if i==1 else 'KPIT Technologies' if i==2 else 'Sonata Software' if i==3 else 'Birlasoft'}", key=f"peer_{i}")
                peer_inputs.append(p)

        prov_col, key_col = st.columns(2)
        with prov_col:
            provider = st.selectbox("AI Provider", ["Gemini (recommended)", "OpenAI", "Groq", "DeepSeek", "Anthropic"])
        with key_col:
            api_key = st.text_input("API Key", type="password", placeholder="Paste your API key")

        if st.button("🔍 Fetch & Build Comp Set", use_container_width=True):
            peers_clean = [p.strip() for p in peer_inputs if p.strip()]
            if not target_input or not peers_clean or not api_key:
                st.error("Please fill in the target, at least one peer, and your API key.")
            else:
                with st.spinner("Gemini is searching the web for verified financial data…"):
                    try:
                        import google.generativeai as genai
                        import json
                        genai.configure(api_key=api_key)
                        model = genai.GenerativeModel("gemini-2.0-flash")
                        prompt = f"""
Search the web for the latest annual financial data for these Indian listed companies.
Target: {target_input}
Peers: {', '.join(peers_clean)}
Sector: {sector_input}

Return ONLY raw JSON, no markdown, no backticks:
{{
  "target": {{
    "name":"","ticker":"","price":0,"shares_cr":0,"mktcap_cr":0,
    "debt_cr":0,"cash_cr":0,"revenue_cr":0,"ebitda_cr":0,"pat_cr":0,
    "eps":0,"roe_pct":0,"roce_pct":0,"fy":"FY25"
  }},
  "peers":[{{
    "name":"","ticker":"","price":0,"shares_cr":0,"mktcap_cr":0,
    "debt_cr":0,"cash_cr":0,"revenue_cr":0,"ebitda_cr":0,"pat_cr":0,
    "eps":0,"roe_pct":0,"roce_pct":0,"fy":"FY25"
  }}],
  "sector":"{sector_input}",
  "data_sources":[]
}}
All figures in INR Crores. Return only verified data from your search.
"""
                        response = model.generate_content(
                            prompt,
                            tools=[{"google_search": {}}]
                        )
                        text = response.text.strip()
                        if "```" in text:
                            text = text.split("```")[1]
                            if text.startswith("json"):
                                text = text[4:]
                        data = json.loads(text.strip())

                        if "error" in data:
                            st.error(f"Gemini error: {data['error']}")
                        else:
                            tgt = data["target"]
                            new_target = {
                                "name":         tgt["name"],
                                "description":  f"{tgt['name']} — {sector_input}",
                                "price":        tgt["price"],
                                "shares_cr":    tgt["shares_cr"],
                                "mktcap_cr":    tgt["mktcap_cr"],
                                "debt_cr":      tgt["debt_cr"],
                                "cash_cr":      tgt["cash_cr"],
                                "net_debt_cr":  tgt["debt_cr"] - tgt["cash_cr"],
                                "ev_cr":        tgt["mktcap_cr"] + (tgt["debt_cr"] - tgt["cash_cr"]),
                                "revenue_cr":   tgt["revenue_cr"],
                                "ebitda_cr":    tgt["ebitda_cr"],
                                "ebitda_margin":tgt["ebitda_cr"] / tgt["revenue_cr"] if tgt["revenue_cr"] else 0,
                                "pat_cr":       tgt["pat_cr"],
                                "eps":          tgt["eps"],
                                "roe_pct":      tgt["roe_pct"],
                                "roce_pct":     tgt["roce_pct"],
                            }
                            new_peers = []
                            for p in data["peers"]:
                                try:
                                    m = compute_multiples(
                                        p["name"], p["price"], p["mktcap_cr"],
                                        p["shares_cr"], p["debt_cr"], p["cash_cr"],
                                        p["revenue_cr"], p["ebitda_cr"], p["pat_cr"],
                                        p["eps"], p["roe_pct"], p["roce_pct"]
                                    )
                                    new_peers.append(m)
                                except Exception:
                                    pass
                            st.session_state.peer_multiples = new_peers
                            st.session_state.target = new_target
                            st.session_state.mode = "custom"
                            st.success(f"✓ Loaded {len(new_peers)} peers for {tgt['name']}")
                            if data.get("data_sources"):
                                st.caption("Sources: " + ", ".join(data["data_sources"][:3]))
                    except Exception as e:
                        st.error(f"Failed to fetch data: {str(e)}\n\nCheck your API key and try again.")

    else:
        # Demo mode — reset to default
        if st.session_state.mode != "demo":
            st.session_state.peer_multiples = [compute_multiples(*p) for p in PEERS_RAW]
            st.session_state.target = TARGET_RAW.copy()
            st.session_state.mode = "demo"

    peers = st.session_state.peer_multiples
    target = st.session_state.target

    # Sector label
    st.markdown(f"""
    <div style="background:{COLORS['navy_dark']};border-radius:8px;
         padding:10px 16px;margin:12px 0;display:inline-block;
         font-family:'Syne',sans-serif;font-size:0.8rem;
         color:{COLORS['gold_light']};font-weight:600;">
      🏭 Indian IT Services &nbsp;·&nbsp; FY25 Annual &nbsp;·&nbsp;
      Source: NSE/BSE investor relations, company annual reports
    </div>
    """, unsafe_allow_html=True)

    # Outlier alert
    if any(p["name"] == "Coforge" for p in peers) and st.session_state.mode == "demo":
        st.markdown(f"""
        <div style="background:#3a1f0a;border:1px solid {COLORS['amber']};border-radius:10px;
             padding:14px 18px;margin:12px 0;">
          <span style="color:{COLORS['amber']};font-weight:700;font-family:'Syne',sans-serif;">
            ⚠ Coforge trades at 37.5x EV/EBITDA — a significant premium-growth outlier.
          </span>
          <div style="color:{COLORS['text2']};font-size:0.85rem;margin-top:4px;">
            Statistics are shown both including and excluding Coforge throughout CompsDesk.
            Coforge's elevated valuation reflects market pricing of its high-growth trajectory,
            not necessarily the sector norm.
          </div>
        </div>
        """, unsafe_allow_html=True)

    # Peer cards
    st.markdown(section_hdr("Peer Cards", "Key metrics at a glance"), unsafe_allow_html=True)
    cols = st.columns(min(len(peers), 3))
    for i, p in enumerate(peers):
        with cols[i % 3]:
            color = PEER_COLORS.get(p["name"], COLORS["navy"])
            is_outlier = p["name"] == "Coforge"
            st.markdown(f"""
            <div style="background:{COLORS['card']};border:1px solid {color}44;
                 border-radius:12px;padding:18px;margin-bottom:12px;
                 border-top:3px solid {color};">
              <div style="font-family:'Syne',sans-serif;font-weight:700;font-size:1rem;
                   color:{color};margin-bottom:2px;">{p['name']}
                   {"&nbsp;<span style='font-size:0.65rem;background:#3a1f0a;color:" + COLORS['amber'] + ";padding:2px 6px;border-radius:4px;'>OUTLIER</span>" if is_outlier else ""}
              </div>
              <div style="font-size:0.75rem;color:{COLORS['text3']};margin-bottom:12px;">
                ₹{p['price']:,.0f} &nbsp;|&nbsp; Mkt Cap ₹{p['mktcap']/1000:.0f}K Cr
              </div>
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">
                <div style="background:{COLORS['card2']};border-radius:6px;padding:8px;">
                  <div style="font-size:0.68rem;color:{COLORS['text3']};margin-bottom:2px;">EV/EBITDA</div>
                  <div style="font-family:'DM Mono',monospace;color:{COLORS['gold']};font-size:0.95rem;">{p['ev_ebitda']:.1f}x</div>
                </div>
                <div style="background:{COLORS['card2']};border-radius:6px;padding:8px;">
                  <div style="font-size:0.68rem;color:{COLORS['text3']};margin-bottom:2px;">P/E</div>
                  <div style="font-family:'DM Mono',monospace;color:{COLORS['gold']};font-size:0.95rem;">{p['pe']:.1f}x</div>
                </div>
                <div style="background:{COLORS['card2']};border-radius:6px;padding:8px;">
                  <div style="font-size:0.68rem;color:{COLORS['text3']};margin-bottom:2px;">EBITDA Margin</div>
                  <div style="font-family:'DM Mono',monospace;color:{COLORS['text1']};font-size:0.95rem;">{p['ebitda_margin']*100:.1f}%</div>
                </div>
                <div style="background:{COLORS['card2']};border-radius:6px;padding:8px;">
                  <div style="font-size:0.68rem;color:{COLORS['text3']};margin-bottom:2px;">ROE</div>
                  <div style="font-family:'DM Mono',monospace;color:{COLORS['text1']};font-size:0.95rem;">{p['roe']:.1f}%</div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

    # Bar chart — peer multiples
    st.markdown(section_hdr("Peer Comparison — Multiples Ranked", "Select metric to compare"), unsafe_allow_html=True)
    metric_options = {"EV/Revenue": "ev_rev", "EV/EBITDA": "ev_ebitda", "P/E": "pe", "P/BV": "pbv"}
    selected_metric = st.selectbox("Metric", list(metric_options.keys()), key="peer_bar_metric")
    mkey = metric_options[selected_metric]

    sorted_peers = sorted(peers, key=lambda p: p[mkey] or 0, reverse=True)
    names = [p["name"] for p in sorted_peers]
    vals  = [p[mkey] for p in sorted_peers]
    colors_bar = [PEER_COLORS.get(n, COLORS["navy"]) for n in names]

    fig_bar = go.Figure(go.Bar(
        x=names, y=vals,
        marker_color=colors_bar,
        text=[f"{v:.1f}x" if v is not None else "N/A" for v in vals],
        textposition="outside",
        textfont=dict(color=COLORS["text2"], size=11),
        hovertemplate="<b>%{x}</b><br>" + selected_metric + ": %{y:.2f}x<extra></extra>",
    ))
    fig_bar.update_layout(
        **dark_layout(title=dict(text=f"{selected_metric} — Peer Ranking", font=dict(color=COLORS["gold"], size=14))),
        yaxis_title=f"{selected_metric}",
        height=320,
    )
    st.plotly_chart(fig_bar, use_container_width=True, key="peer_bar_chart")

    # Scatter — quality vs valuation
    st.markdown(section_hdr("Quality vs Valuation Map", "EBITDA Margin (x) vs EV/EBITDA (y) · Bubble = Market Cap"), unsafe_allow_html=True)
    all_points = [*peers, {
        "name": target["name"],
        "ebitda_margin": target["ebitda_margin"],
        "ev_ebitda": target["ev_cr"] / target["ebitda_cr"],
        "mktcap": target["mktcap_cr"],
    }]

    scatter_fig = go.Figure()
    for p in all_points:
        n = p["name"]
        c = PEER_COLORS.get(n, COLORS["navy"])
        is_tgt = n == target["name"]
        scatter_fig.add_trace(go.Scatter(
            x=[p["ebitda_margin"] * 100],
            y=[p["ev_ebitda"]],
            mode="markers+text",
            marker=dict(
                size=max(20, min(60, p["mktcap"] / 12000)),
                color=c,
                line=dict(color=COLORS["text1"] if is_tgt else c, width=2 if is_tgt else 0),
                symbol="star" if is_tgt else "circle",
            ),
            text=[n],
            textposition="top center",
            textfont=dict(color=c, size=10),
            name=n,
            hovertemplate=f"<b>{n}</b><br>EBITDA Margin: %{{x:.1f}}%<br>EV/EBITDA: %{{y:.1f}}x<extra></extra>",
        ))
    scatter_fig.update_layout(
        **dark_layout(showlegend=False,
                      title=dict(text="Quality vs Valuation — Indian IT Peers", font=dict(color=COLORS["gold"], size=13))),
        xaxis_title="EBITDA Margin (%)",
        yaxis_title="EV/EBITDA (x)",
        height=380,
    )
    st.plotly_chart(scatter_fig, use_container_width=True, key="scatter_chart")
    st.markdown(ghost_html(
        "Higher margin should command higher EV/EBITDA. Companies above the diagonal "
        "are expensive relative to their profitability; below it are cheap. "
        "TCS and Infosys earn the most while trading at mid-range multiples — that's quality at fair value. "
        "Coforge's extreme multiple prices in growth the financials don't yet show."
    ), unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — MULTIPLE STATISTICS
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    peers = st.session_state.peer_multiples
    target = st.session_state.target

    stats_full = compute_statistics(peers, exclude_coforge=False)
    stats_exc  = compute_statistics(peers, exclude_coforge=True)

    st.markdown(section_hdr("Multiple Statistics", "Full peer set vs ex-Coforge outlier"), unsafe_allow_html=True)

    stat_labels = ["Minimum", "25th Pct", "Median", "Mean", "75th Pct", "Maximum"]
    stat_keys   = ["min", "q25", "median", "mean", "q75", "max"]
    mult_names  = ["EV/Revenue", "EV/EBITDA", "P/E", "P/BV"]
    mult_keys   = ["ev_rev", "ev_ebitda", "pe", "pbv"]

    def stats_table_plotly(stats_d, title, highlight_row=2):
        """Render stats table as Plotly Table — bypasses Streamlit HTML issues."""
        col_labels = ["Stat"] + mult_names
        rows_data = []
        for label, key in zip(stat_labels, stat_keys):
            row = [label] + [f"{stats_d[mk][key]:.2f}x" for mk in mult_keys]
            rows_data.append(row)

        # Build per-cell fill and font colors
        n_rows = len(rows_data)
        n_cols = len(col_labels)
        fill_colors = []
        font_colors = []
        for ci in range(n_cols):
            col_fill = []
            col_font = []
            for ri in range(n_rows):
                if ri == highlight_row:
                    col_fill.append(COLORS["navy_dark"])
                    col_font.append(COLORS["gold"])
                elif ri % 2 == 0:
                    col_fill.append(COLORS["card"])
                    col_font.append(COLORS["text1"])
                else:
                    col_fill.append(COLORS["card2"])
                    col_font.append(COLORS["text1"])
            fill_colors.append(col_fill)
            font_colors.append(col_font)

        fig = go.Figure(go.Table(
            header=dict(
                values=[f"<b>{c}</b>" for c in col_labels],
                fill_color=COLORS["navy"],
                font=dict(color=COLORS["gold_light"], size=11, family="Syne, sans-serif"),
                align=["left"] + ["right"] * len(mult_names),
                line_color=COLORS["border"],
                height=34,
            ),
            cells=dict(
                values=[[rows_data[r][c] for r in range(n_rows)] for c in range(n_cols)],
                fill_color=fill_colors,
                font=dict(color=font_colors, size=11, family="DM Mono, monospace"),
                align=["left"] + ["right"] * len(mult_names),
                line_color=COLORS["border"],
                height=30,
            ),
        ))
        fig.update_layout(
            paper_bgcolor=COLORS["bg"],
            plot_bgcolor=COLORS["bg"],
            margin=dict(l=0, r=0, t=28, b=0),
            height=240,
            title=dict(text=title, font=dict(color=COLORS["gold"], size=11,
                       family="Syne, sans-serif"), x=0),
        )
        return fig

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(stats_table_plotly(stats_full, "Full Peer Set (n=6)"),
                        use_container_width=True, key="stats_full_tbl")
    with c2:
        st.plotly_chart(stats_table_plotly(stats_exc, "Ex-Coforge (n=5)"),
                        use_container_width=True, key="stats_exc_tbl")

    st.markdown(ghost_html(
        "The median EV/EBITDA of 11.64x means the market typically pays ₹11.64 for every ₹1 of EBITDA "
        "in this sector. Coforge's 37.5x reflects a growth premium the market is pricing in — "
        "if you exclude it, the sector median drops to 11.2x. For implied valuation, "
        "the median is the key row: less distorted by outliers, more representative of where "
        "a typical deal or stock would land."
    ), unsafe_allow_html=True)

    # Box plots
    st.markdown(section_hdr("Distribution — Box Plots", "Visualising outlier impact"), unsafe_allow_html=True)
    box_fig = go.Figure()
    for mk, mn in zip(mult_keys, mult_names):
        vals_all = [p[mk] for p in peers if p[mk] is not None]
        names_all = [p["name"] for p in peers if p[mk] is not None]
        box_fig.add_trace(go.Box(
            y=vals_all,
            name=mn,
            boxpoints="all",
            jitter=0.3,
            pointpos=-1.5,
            marker=dict(color=COLORS["gold"], size=7, line=dict(color=COLORS["navy"], width=1)),
            line=dict(color=COLORS["navy"], width=2),
            fillcolor="rgba(26,58,90,0.5)",
            customdata=names_all,
            hovertemplate="<b>%{customdata}</b><br>" + mn + ": %{y:.2f}x<extra></extra>",
        ))
    box_fig.update_layout(
        **dark_layout(showlegend=False,
                      title=dict(text="Multiple Distribution — All Peers", font=dict(color=COLORS["gold"], size=13))),
        yaxis_title="Multiple (x)",
        height=380,
    )
    st.plotly_chart(box_fig, use_container_width=True, key="box_plots")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — IMPLIED VALUATION
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    peers  = st.session_state.peer_multiples
    target = st.session_state.target

    stats_full = compute_statistics(peers, exclude_coforge=False)
    stats_exc  = compute_statistics(peers, exclude_coforge=True)

    st.markdown(section_hdr("Implied Valuation Settings"), unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    with col_a:
        stat_choice = st.selectbox(
            "Apply statistic",
            ["Minimum", "25th Percentile", "Median", "Mean", "75th Percentile", "Maximum"],
            index=2,
            key="stat_choice_t3",
        )
        stat_key_map = {
            "Minimum": "min", "25th Percentile": "q25",
            "Median": "median", "Mean": "mean",
            "75th Percentile": "q75", "Maximum": "max",
        }
        skey = stat_key_map[stat_choice]
    with col_b:
        exc = st.toggle("Exclude Coforge outlier", value=False, key="exc_coforge_t3")

    stats_use = stats_exc if exc else stats_full
    vals = implied_valuation(target, stats_use, skey)
    summary = vals["_summary"]

    # Method cards
    st.markdown(section_hdr("Implied Prices per Method", f"Using {stat_choice} multiple {'(ex-Coforge)' if exc else '(all peers)'}"), unsafe_allow_html=True)

    method_explanations = {
        "EV/Revenue": (
            "Enterprise Value as a multiple of Revenue",
            lambda v, s: f"At peer {stat_choice.lower()} {v['multiple']:.2f}x revenue, "
            f"₹{target['revenue_cr']:,.0f} Cr revenue implies EV of ₹{v['implied_ev']:,.0f} Cr → "
            f"share price of {fmt_price(v['implied_price'])} vs current {fmt_price(target['price'])}. "
            f"{'Meridian is trading at a premium on this metric.' if target['price'] > v['implied_price'] else 'Meridian looks undervalued on revenue.'}"
        ),
        "EV/EBITDA": (
            "Enterprise Value as a multiple of EBITDA",
            lambda v, s: f"At peer {stat_choice.lower()} {v['multiple']:.2f}x EBITDA, "
            f"₹{target['ebitda_cr']:,.0f} Cr EBITDA implies {fmt_price(v['implied_price'])}/share. "
            f"The market pays ~{target['ev_cr']/target['ebitda_cr']:.1f}x for Meridian vs "
            f"peer {stat_choice.lower()} {v['multiple']:.1f}x — "
            f"a {abs(target['ev_cr']/target['ebitda_cr']/v['multiple']-1)*100:.0f}% "
            f"{'premium' if target['ev_cr']/target['ebitda_cr'] > v['multiple'] else 'discount'} to peers."
        ),
        "P/E": (
            "Price to Earnings ratio",
            lambda v, s: f"Peer {stat_choice.lower()} P/E is {v['multiple']:.1f}x. "
            f"Meridian at {target['price']/target['eps']:.1f}x is "
            f"{'pricing in significantly higher growth' if target['price']/target['eps'] > v['multiple'] else 'trading at a discount to peers on earnings'}. "
            f"Implied price: {fmt_price(v['implied_price'])}."
        ),
        "P/BV": (
            "Price to Book Value ratio",
            lambda v, s: f"At {v['multiple']:.2f}x peer {stat_choice.lower()} book value, "
            f"Meridian's implied price is {fmt_price(v['implied_price'])} — "
            f"{'nearly in line with' if abs(target['price'] - v['implied_price'])/target['price'] < 0.05 else 'vs'} "
            f"current {fmt_price(target['price'])}. "
            f"{'P/BV is the one method where Meridian looks fairly valued.' if abs(target['price'] - v['implied_price'])/target['price'] < 0.05 else ''}"
        ),
    }

    method_keys = ["EV/Revenue", "EV/EBITDA", "P/E", "P/BV"]
    cols_impl = st.columns(2)
    for i, mkey in enumerate(method_keys):
        v = vals[mkey]
        up = v["implied_price"] / target["price"] - 1
        uc = COLORS["green"] if up >= 0 else COLORS["red"]
        up_arrow = "▲" if up >= 0 else "▼"
        mtitle, mexpl = method_explanations[mkey]
        with cols_impl[i % 2]:
            st.markdown(f"""
            <div style="background:{COLORS['card']};border:1px solid {COLORS['border']};
                 border-radius:12px;padding:20px;margin-bottom:14px;
                 border-top:3px solid {COLORS['navy']};">
              <div style="font-family:'Syne',sans-serif;font-weight:700;font-size:0.82rem;
                   color:{COLORS['gold']};text-transform:uppercase;letter-spacing:.08em;
                   margin-bottom:4px;">{mkey}</div>
              <div style="font-size:0.73rem;color:{COLORS['text3']};margin-bottom:12px;">{mtitle}</div>
              <div style="display:flex;align-items:baseline;gap:12px;margin-bottom:8px;">
                <div style="font-family:'DM Mono',monospace;font-size:1.6rem;color:{COLORS['text1']};font-weight:500;">
                  {fmt_price(v['implied_price'])}
                </div>
                <div style="font-family:'DM Mono',monospace;font-size:0.95rem;color:{uc};font-weight:600;">
                  {up_arrow} {abs(up)*100:.1f}%
                </div>
              </div>
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:10px;">
                <div style="background:{COLORS['card2']};border-radius:6px;padding:7px 10px;">
                  <div style="font-size:0.67rem;color:{COLORS['text3']};">Multiple</div>
                  <div style="font-family:'DM Mono',monospace;color:{COLORS['gold']};font-size:0.88rem;">{v['multiple']:.2f}x</div>
                </div>
                <div style="background:{COLORS['card2']};border-radius:6px;padding:7px 10px;">
                  <div style="font-size:0.67rem;color:{COLORS['text3']};">Current</div>
                  <div style="font-family:'DM Mono',monospace;color:{COLORS['text2']};font-size:0.88rem;">{fmt_price(target['price'])}</div>
                </div>
              </div>
              <div style="font-size:0.8rem;color:{COLORS['text2']};line-height:1.5;
                   font-style:italic;border-top:1px solid {COLORS['border']};padding-top:9px;">
                {mexpl(v, stats_use)}
              </div>
            </div>
            """, unsafe_allow_html=True)

    # Summary banner
    up_color = COLORS["green"] if summary["upside"] >= 0 else COLORS["red"]
    st.markdown(f"""
    <div style="background:linear-gradient(90deg,{COLORS['navy_dark']},{COLORS['card']});
         border:1px solid {COLORS['navy']};border-radius:12px;padding:20px 28px;
         margin:12px 0;display:flex;flex-wrap:wrap;gap:24px;align-items:center;">
      <div>
        <div style="font-size:0.72rem;color:{COLORS['text3']};font-family:Syne,sans-serif;text-transform:uppercase;letter-spacing:.1em;">Floor</div>
        <div style="font-family:'DM Mono',monospace;font-size:1.2rem;color:{COLORS['text2']};">{fmt_price(summary['low'])}</div>
      </div>
      <div style="color:{COLORS['border']};font-size:1.4rem;">→</div>
      <div>
        <div style="font-size:0.72rem;color:{COLORS['text3']};font-family:Syne,sans-serif;text-transform:uppercase;letter-spacing:.1em;">Median of Methods</div>
        <div style="font-family:'DM Mono',monospace;font-size:1.5rem;color:{COLORS['gold']};font-weight:700;">{fmt_price(summary['median'])}</div>
      </div>
      <div style="color:{COLORS['border']};font-size:1.4rem;">→</div>
      <div>
        <div style="font-size:0.72rem;color:{COLORS['text3']};font-family:Syne,sans-serif;text-transform:uppercase;letter-spacing:.1em;">Ceiling</div>
        <div style="font-family:'DM Mono',monospace;font-size:1.2rem;color:{COLORS['text2']};">{fmt_price(summary['high'])}</div>
      </div>
      <div style="margin-left:auto;text-align:right;">
        <div style="font-size:0.72rem;color:{COLORS['text3']};font-family:Syne,sans-serif;text-transform:uppercase;letter-spacing:.1em;">Upside vs Current</div>
        <div style="font-family:'DM Mono',monospace;font-size:1.4rem;color:{up_color};font-weight:700;">
          {"▲" if summary['upside']>=0 else "▼"} {abs(summary['upside'])*100:.1f}%
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Target vs peer comparison table
    st.markdown(section_hdr("Target vs Peer Medians", "Where does the target sit?"), unsafe_allow_html=True)

    tgt_ev  = target["ev_cr"]
    tgt_rev = target["revenue_cr"]
    tgt_ebitda = target["ebitda_cr"]
    tgt_eps = target["eps"]
    bvps_tgt = (target["pat_cr"] / (target["roe_pct"] / 100)) / target["shares_cr"]

    compare_data = [
        ("EV/Revenue",  f"{tgt_ev/tgt_rev:.2f}x", f"{stats_use['ev_rev']['median']:.2f}x",
         "Premium" if tgt_ev/tgt_rev > stats_use["ev_rev"]["median"] else "Discount"),
        ("EV/EBITDA",   f"{tgt_ev/tgt_ebitda:.2f}x", f"{stats_use['ev_ebitda']['median']:.2f}x",
         "Premium" if tgt_ev/tgt_ebitda > stats_use["ev_ebitda"]["median"] else "Discount"),
        ("P/E",         f"{target['price']/tgt_eps:.2f}x", f"{stats_use['pe']['median']:.2f}x",
         "Premium" if target["price"]/tgt_eps > stats_use["pe"]["median"] else "Discount"),
        ("P/BV",        f"{target['price']/bvps_tgt:.2f}x", f"{stats_use['pbv']['median']:.2f}x",
         "In Line" if abs(target["price"]/bvps_tgt / stats_use["pbv"]["median"] - 1) < 0.08 else
         "Premium" if target["price"]/bvps_tgt > stats_use["pbv"]["median"] else "Discount"),
    ]

    # Build comparison table as Plotly table — avoids all HTML rendering issues
    cmp_rows = []
    for mult, tgt_v, med_v, signal in compare_data:
        cmp_rows.append([mult, tgt_v, med_v, signal])

    sig_colors_list = []
    for _, _, _, signal in compare_data:
        if "Premium" in signal:
            sig_colors_list.append(COLORS["amber"])
        elif "Discount" in signal:
            sig_colors_list.append(COLORS["green"])
        else:
            sig_colors_list.append(COLORS["navy"])

    fig_cmp = go.Figure(go.Table(
        header=dict(
            values=["<b>Multiple</b>", "<b>Target</b>", "<b>Peer Median</b>", "<b>Signal</b>"],
            fill_color=COLORS["navy"],
            font=dict(color=COLORS["gold_light"], size=12, family="Syne, sans-serif"),
            align=["left", "right", "right", "center"],
            line_color=COLORS["border"],
            height=36,
        ),
        cells=dict(
            values=[
                [r[0] for r in cmp_rows],
                [r[1] for r in cmp_rows],
                [r[2] for r in cmp_rows],
                [r[3] for r in cmp_rows],
            ],
            fill_color=[
                [COLORS["card"], COLORS["card2"], COLORS["card"], COLORS["card2"]],
                [COLORS["card"], COLORS["card2"], COLORS["card"], COLORS["card2"]],
                [COLORS["card"], COLORS["card2"], COLORS["card"], COLORS["card2"]],
                sig_colors_list,
            ],
            font=dict(
                color=[
                    [COLORS["gold"]]*4,
                    [COLORS["text1"]]*4,
                    [COLORS["text2"]]*4,
                    [COLORS["bg"]]*4,
                ],
                size=12,
                family="DM Mono, monospace",
            ),
            align=["left", "right", "right", "center"],
            line_color=COLORS["border"],
            height=32,
        ),
    ))
    fig_cmp.update_layout(
        paper_bgcolor=COLORS["bg"],
        plot_bgcolor=COLORS["bg"],
        margin=dict(l=0, r=0, t=0, b=0),
        height=210,
    )
    st.plotly_chart(fig_cmp, use_container_width=True, key="cmp_table")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — FOOTBALL FIELD
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    peers  = st.session_state.peer_multiples
    target = st.session_state.target

    stats_full = compute_statistics(peers, exclude_coforge=False)
    stats_exc  = compute_statistics(peers, exclude_coforge=True)

    st.markdown(section_hdr("Football Field Chart", "Implied price range across all four valuation methods"), unsafe_allow_html=True)

    exc_ff = st.toggle("Exclude Coforge outlier", value=False, key="exc_ff")
    stats_ff = stats_exc if exc_ff else stats_full

    def football_field_prices(target, stats_d):
        nd = target["net_debt_cr"]
        sh = target["shares_cr"]
        bvps = (target["pat_cr"] / (target["roe_pct"] / 100)) / sh
        result = {}
        for method, mk, fin in [
            ("EV/Revenue",  "ev_rev",    target["revenue_cr"]),
            ("EV/EBITDA",   "ev_ebitda", target["ebitda_cr"]),
        ]:
            s = stats_d[mk]
            result[method] = {k: (fin * s[k] - nd) / sh for k in ["min","q25","median","q75","max"]}

        for method, mk, fin in [
            ("P/E",  "pe",  target["eps"]),
            ("P/BV", "pbv", bvps),
        ]:
            s = stats_d[mk]
            result[method] = {k: fin * s[k] for k in ["min","q25","median","q75","max"]}

        return result

    ff_data = football_field_prices(target, stats_ff)
    methods_ff = ["EV/Revenue", "EV/EBITDA", "P/E", "P/BV"]
    current = target["price"]

    fig_ff = go.Figure()
    method_colors = [COLORS["navy"], "#2a6a7a", "#3a5a4a", "#5a3a6a"]

    for i, method in enumerate(methods_ff):
        d = ff_data[method]
        y = i  # numeric axis — shapes and traces all use integer index

        # Min-max whisker
        fig_ff.add_trace(go.Scatter(
            x=[d["min"], d["max"]], y=[y, y],
            mode="lines",
            line=dict(color=COLORS["text3"], width=1.5, dash="dot"),
            showlegend=False,
            hoverinfo="skip",
        ))
        # 25th-75th band
        mc = method_colors[i % len(method_colors)]
        fig_ff.add_shape(
            type="rect",
            xref="x", yref="y",
            x0=d["q25"], x1=d["q75"],
            y0=i - 0.3, y1=i + 0.3,
            fillcolor=f"rgba({int(mc[1:3],16)},{int(mc[3:5],16)},{int(mc[5:7],16)},0.5)",
            line=dict(color=mc, width=1),
        )
        # Min and max endpoint markers
        fig_ff.add_trace(go.Scatter(
            x=[d["min"], d["max"]], y=[y, y],
            mode="markers",
            marker=dict(color=COLORS["text3"], size=10, symbol="cross-thin",
                        line=dict(color=COLORS["text3"], width=2)),
            showlegend=False,
            hovertemplate=f"<b>{method}</b><br>₹%{{x:,.0f}}<extra></extra>",
        ))
        # Median dot
        fig_ff.add_trace(go.Scatter(
            x=[d["median"]], y=[y],
            mode="markers",
            marker=dict(color=COLORS["gold"], size=12, symbol="diamond"),
            showlegend=False,
            hovertemplate=f"<b>{method}</b> Median<br>₹%{{x:,.0f}}<extra></extra>",
        ))
        # Labels
        for k, label in [("min","Min"), ("median","Med"), ("max","Max")]:
            fig_ff.add_annotation(
                x=d[k], y=i + 0.42,
                text=f"₹{d[k]:,.0f}",
                showarrow=False,
                font=dict(size=9, color=COLORS["gold"] if k == "median" else COLORS["text3"]),
                xanchor="center",
            )

    # Current price vertical line
    fig_ff.add_vline(
        x=current, line=dict(color=COLORS["gold"], width=2, dash="solid"),
    )
    fig_ff.add_annotation(
        x=current, y=len(methods_ff) - 0.6,
        text=f"Current ₹{current:,.0f}",
        showarrow=False,
        font=dict(size=10, color=COLORS["gold"], family="DM Mono"),
        bgcolor=COLORS["card"],
        bordercolor=COLORS["gold"],
        borderpad=4,
        borderwidth=1,
    )

    fig_ff.update_layout(**dark_layout(
        showlegend=False,
        title=dict(
            text=f"Football Field — Implied Price Range {'(Ex-Coforge)' if exc_ff else '(All Peers)'}",
            font=dict(color=COLORS["gold"], size=14),
        ),
        xaxis=dict(
            gridcolor=COLORS["border"], zerolinecolor=COLORS["border"],
            tickfont=dict(color=COLORS["text2"], size=10),
            title_font=dict(color=COLORS["text2"]),
            title=dict(text="Implied Share Price (₹)"),
        ),
        yaxis=dict(
            gridcolor=COLORS["border"], zerolinecolor=COLORS["border"],
            tickmode="array",
            tickvals=list(range(len(methods_ff))),
            ticktext=methods_ff,
            tickfont=dict(color=COLORS["gold"], size=11),
            range=[-0.6, len(methods_ff) - 0.4],
        ),
        margin=dict(l=110, r=50, t=60, b=50),
        height=420,
    ))
    st.plotly_chart(fig_ff, use_container_width=True, key="football_field")

    # Grand summary
    all_implied = [v for d in ff_data.values() for v in d.values()]
    grand_low    = min(all_implied)
    grand_median = float(np.median([d["median"] for d in ff_data.values()]))
    grand_high   = max(all_implied)

    st.markdown(f"""
    <div style="background:linear-gradient(90deg,{COLORS['navy_dark']},{COLORS['card']});
         border:1px solid {COLORS['navy']};border-radius:12px;padding:20px 28px;
         margin:12px 0;text-align:center;">
      <div style="font-family:'Syne',sans-serif;font-size:0.75rem;color:{COLORS['text3']};
           text-transform:uppercase;letter-spacing:.1em;margin-bottom:12px;">
        Football Field — Grand Summary {'(Ex-Coforge)' if exc_ff else '(All Peers)'}
      </div>
      <div style="display:flex;justify-content:center;gap:32px;flex-wrap:wrap;">
        <div>
          <div style="font-size:0.72rem;color:{COLORS['text3']};">Floor</div>
          <div style="font-family:'DM Mono',monospace;font-size:1.2rem;color:{COLORS['text2']};">{fmt_price(grand_low)}</div>
        </div>
        <div>
          <div style="font-size:0.72rem;color:{COLORS['text3']};">Median of Medians</div>
          <div style="font-family:'DM Mono',monospace;font-size:1.6rem;color:{COLORS['gold']};font-weight:700;">{fmt_price(grand_median)}</div>
        </div>
        <div>
          <div style="font-size:0.72rem;color:{COLORS['text3']};">Ceiling</div>
          <div style="font-family:'DM Mono',monospace;font-size:1.2rem;color:{COLORS['text2']};">{fmt_price(grand_high)}</div>
        </div>
        <div>
          <div style="font-size:0.72rem;color:{COLORS['text3']};">Current</div>
          <div style="font-family:'DM Mono',monospace;font-size:1.2rem;color:{COLORS['text1']};">{fmt_price(current)}</div>
        </div>
        <div>
          <div style="font-size:0.72rem;color:{COLORS['text3']};">vs Current</div>
          <div style="font-family:'DM Mono',monospace;font-size:1.2rem;color:{upside_color(grand_median/current-1)};">
            {"▲" if grand_median>=current else "▼"} {abs(grand_median/current-1)*100:.1f}%
          </div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Technical + ghost
    ev_ebitda_impl = ff_data["EV/EBITDA"]["median"]
    st.markdown(f"""
    <div style="background:{COLORS['card']};border:1px solid {COLORS['border']};
         border-radius:10px;padding:14px 18px;margin-top:6px;
         font-family:'DM Mono',monospace;font-size:0.82rem;color:{COLORS['text2']};">
      EV/EBITDA method implies {fmt_price(ev_ebitda_impl)} at peer median
      {stats_ff['ev_ebitda']['median']:.2f}x, vs current {fmt_price(current)} —
      a {abs(current/ev_ebitda_impl-1)*100:.1f}%
      {'premium' if current > ev_ebitda_impl else 'discount'}.
    </div>
    """, unsafe_allow_html=True)

    st.markdown(ghost_html(
        "Three out of four valuation methods say Meridian is expensive vs its peers. "
        "The only one that doesn't is P/BV — which looks at book value, not earnings power. "
        "The market is either right that Meridian will grow into its valuation, "
        "or it's priced for a future that hasn't arrived yet. "
        f"The football field puts the honest range at {fmt_price(grand_low)}–{fmt_price(grand_high)}, "
        f"with {fmt_price(grand_median)} as the most defensible single number."
    ), unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — DOWNLOAD
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown(section_hdr("CompsDesk Excel Template", "6 sheets · 169 formulas · Zero errors · Clean Light Theme"), unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:{COLORS['card']};border:1px solid {COLORS['border']};
         border-radius:12px;padding:22px;margin-bottom:18px;">
      <div style="font-family:'Syne',sans-serif;font-weight:700;font-size:0.88rem;
           color:{COLORS['gold']};margin-bottom:14px;">Sheet Guide</div>
    """, unsafe_allow_html=True)

    sheets = [
        ("1 · Cover",             "Navigation, model overview, and instructions"),
        ("2 · Peer Data",         "FY25 raw financials for 6 verified Indian IT peers (blue = input)"),
        ("3 · Multiple Engine",   "Computed EV/Revenue, EV/EBITDA, P/E, P/BV for each peer"),
        ("4 · Statistics",        "Min / 25th / Median / Mean / 75th / Max — full set and ex-Coforge"),
        ("5 · Target",            "Meridian Digital Ltd — fictional target company (blue = change these)"),
        ("6 · Implied Valuation", "4-method implied prices + football field range table"),
    ]
    for name, desc in sheets:
        st.markdown(f"""
        <div style="display:flex;align-items:flex-start;gap:14px;padding:10px 0;
             border-bottom:1px solid {COLORS['border']};">
          <div style="font-family:'DM Mono',monospace;font-size:0.82rem;color:{COLORS['gold']};
               min-width:140px;font-weight:500;">{name}</div>
          <div style="font-size:0.82rem;color:{COLORS['text2']};">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:{COLORS['navy_dark']};border-radius:10px;padding:14px 18px;
         margin-bottom:18px;font-size:0.85rem;color:{COLORS['text2']};">
      <b style="color:{COLORS['gold']};">How to use:</b> Change any blue cell. Everything recalculates automatically.
      Swap the peer tickers in Sheet 2, update the target in Sheet 5, and the valuation in Sheet 6 updates instantly.
    </div>
    """, unsafe_allow_html=True)

    try:
        with open("CompsDesk_Template_updated.xlsx", "rb") as f:
            excel_bytes = f.read()
        st.download_button(
            label="⬇ Download CompsDesk Excel Template",
            data=excel_bytes,
            file_name="CompsDesk_Template_updated.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
    except FileNotFoundError:
        st.error("Excel template not found. Ensure CompsDesk_Template_updated.xlsx is in the app directory.")

    st.markdown(f"""
    <div style="text-align:center;padding:24px 0 8px;
         font-family:'DM Mono',monospace;font-size:0.72rem;color:{COLORS['text3']};">
      CompsDesk · Day 19 · 30 Days of AI Finance ·
      Peer data FY25 verified. Meridian Digital Ltd is fictional. Not investment advice.
    </div>
    """, unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="text-align:center;padding:28px 0 12px;margin-top:20px;
     border-top:1px solid {COLORS['border']};
     font-family:'DM Mono',monospace;font-size:0.72rem;color:{COLORS['text3']};">
  CompsDesk · Day 19 · 30 Days of AI Finance ·
  Peer data FY25 verified. Meridian Digital Ltd is fictional. Not investment advice.
</div>
""", unsafe_allow_html=True)