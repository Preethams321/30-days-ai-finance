import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import yfinance as yf
from datetime import datetime, timedelta

# --- I. SYSTEM THEME SHIELD & CUSTOM FINTECH INTERACTIVE UI CSS ---
st.set_page_config(layout="wide", page_title="Nifty Sector Rotation Dashboard")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght=400;500;600;700&family=JetBrains+Mono:wght=400;700&display=swap');
    
    html, body, .main, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #06090F !important;
        color: #F3F4F6 !important;
    }
    
    /* THEME SHIELD */
    [data-testid="stMarkdownContainer"] h1, 
    [data-testid="stMarkdownContainer"] h2, 
    [data-testid="stMarkdownContainer"] h3, 
    [data-testid="stMarkdownContainer"] h4, 
    [data-testid="stMarkdownContainer"] h5, 
    [data-testid="stMarkdownContainer"] p, 
    [data-testid="stMarkdownContainer"] li, 
    [data-testid="stMarkdownContainer"] div, 
    [data-testid="stMarkdownContainer"] span, 
    [data-testid="stMarkdownContainer"] b {
        color: #E5E7EB !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .banner-container {
        background: linear-gradient(135deg, #1E1B4B 0%, #030712 100%) !important;
        padding: 35px !important; border-radius: 12px !important; border: 1px solid #1F2937 !important; 
        margin-bottom: 25px !important; box-shadow: 0 15px 35px rgba(0, 0, 0, 0.6) !important;
    }
    .banner-container h1 { color: #FFFFFF !important; font-size: 2.2rem !important; font-weight: 700 !important; margin: 0 0 6px 0 !important; }
    .banner-container p { color: #C7D2FE !important; font-size: 0.95rem !important; margin: 0 !important; }
    
    .page-section {
        background-color: #0B0F17 !important; border: 1px solid #1F2937 !important;
        border-radius: 12px !important; padding: 30px !important; margin-bottom: 35px !important;
    }
    
    .metric-summary-card {
        background-color: #0E1626 !important; border: 1px solid #1F2937 !important;
        padding: 22px !important; border-radius: 10px !important; height: 140px !important;
        transition: transform 0.2s ease, border-color 0.2s ease !important;
    }
    .metric-summary-card:hover {
        transform: translateY(-4px) !important;
        border-color: #38BDF8 !important;
    }
    .metric-title { font-size: 0.75rem !important; color: #9CA3AF !important; font-weight: 700 !important; letter-spacing: 0.05em !important; margin: 0 !important; }
    .metric-value { font-size: 1.8rem !important; font-weight: 700 !important; margin: 6px 0 !important; font-family: 'JetBrains Mono', monospace !important; color: #FFFFFF !important; }
    
    .leaderboard-row-card {
        background-color: #06090F !important; border: 1px solid #1F2937 !important;
        border-radius: 8px !important; padding: 18px !important; margin-bottom: 12px !important;
        transition: transform 0.2s ease, background-color 0.2s ease !important;
    }
    .leaderboard-row-card:hover {
        transform: scale(1.01) !important;
        background-color: #0E1626 !important;
    }
    .lead-name { font-weight: 700 !important; font-size: 1.05rem !important; color: #FFFFFF !important; }
    
    .badge-leading { background-color: rgba(16, 185, 129, 0.1) !important; color: #10B981 !important; border: 1px solid #10B981 !important; padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 700; }
    .badge-improving { background-color: rgba(56, 189, 248, 0.1) !important; color: #38BDF8 !important; border: 1px solid #38BDF8 !important; padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 700; }
    .badge-weakening { background-color: rgba(245, 158, 11, 0.1) !important; color: #F59E0B !important; border: 1px solid #F59E0B !important; padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 700; }
    .badge-lagging { background-color: rgba(239, 68, 68, 0.1) !important; color: #EF4444 !important; border: 1px solid #EF4444 !important; padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 700; }

    .scroll-indicator {
        text-align: center !important; font-family: 'JetBrains Mono', monospace !important;
        font-weight: 700 !important; font-size: 0.78rem !important; letter-spacing: 0.1em !important;
        color: #6B7280 !important; margin: 20px 0 35px 0 !important; text-transform: uppercase !important;
    }
    
    .verdict-box {
        background-color: #0E1626 !important; border: 1px solid #1F2937 !important;
        border-left: 4px solid #38BDF8 !important; padding: 22px !important; border-radius: 8px !important;
    }

    .export-card-frame {
        background-color: #0E1626 !important; border: 1px solid #1F2937 !important;
        padding: 30px !important; border-radius: 12px 12px 0 0 !important; margin-top: 15px !important;
    }
    .export-headline { color: #38BDF8 !important; font-family: 'JetBrains Mono', monospace !important; font-weight: 700 !important; font-size: 1.1rem !important; letter-spacing: 0.05em !important; }
    .export-sub-item { font-size: 0.92rem !important; color: #9CA3AF !important; margin-bottom: 12px !important; line-height: 1.5 !important; }
    
    .footer-container {
        text-align: center !important; border-top: 1px solid #1F2937 !important;
        padding: 25px 0 !important; margin-top: 50px !important; font-size: 0.85rem !important; color: #6B7280 !important;
    }
    </style>
""", unsafe_allow_html=True)

if "show_summary" not in st.session_state:
    st.session_state.show_summary = False

def activate_summary_card():
    st.session_state.show_summary = True

# --- SECTION 3: HOMEPAGE HERO HEADER ---
st.markdown("""
    <div class="banner-container">
        <h1>📊 Nifty Sector Rotation Dashboard</h1>
        <p style="margin-bottom: 8px !important;">• Track which Nifty sectors are leading, lagging, and rotating over time through a relative-strength analytical core.</p>
        <p>• Compute absolute historical returns across multi-period windows and evaluate true momentum trajectories relative to the Nifty 50 index.</p>
    </div>
""", unsafe_allow_html=True)

feature_cols = st.columns(2)
with feature_cols[0]:
    st.markdown("""
        <div class="page-section" style="height: 100%;">
            <h3 style="margin-top: 0; color: #FFFFFF;">📋 Core Platform Features</h3>
            <p style="font-size: 0.9rem; line-height: 1.6; margin-bottom: 12px;"><b>• Cross-Timeframe Analysis:</b> Tracks performance distribution profiles across 1-Week, 1-Month, 3-Month, 6-Month, and 1-Year tracking blocks.</p>
            <p style="font-size: 0.9rem; line-height: 1.6; margin-bottom: 12px;"><b>• Relative Strength Engine:</b> Subtracts baseline index performance to instantly expose net alpha outperformance values.</p>
            <p style="font-size: 0.9rem; line-height: 1.6; margin-bottom: 0;"><b>• Modular Rotation Quadrant:</b> Plots mathematical strength against immediate short-term changes to group assets into leadership segments.</p>
        </div>
    """, unsafe_allow_html=True)

with feature_cols[1]:
    st.markdown("""
        <div class="page-section" style="height: 100%;">
            <h3 style="margin-top: 0; color: #FFFFFF;">⚙️ Quick Setup Guide</h3>
            <p style="font-size: 0.9rem; line-height: 1.6; margin-bottom: 12px;"><b>1. Data Synchronization:</b> Historical pricing data streams are fetched live from Yahoo Finance using cached API protocols.</p>
            <p style="font-size: 0.9rem; line-height: 1.6; margin-bottom: 12px;"><b>2. Filter Selections:</b> Use the check selectors inside the layout segments below to modify normalized line chart overlays.</p>
            <p style="font-size: 0.9rem; line-height: 1.6; margin-bottom: 0;"><b>3. Isolate Alpha Traps:</b> Track sectors displaying declining momentum profiles to manage industrial allocation risks.</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="scroll-indicator">↓ Scroll Down to Begin Analysis ↓</div>', unsafe_allow_html=True)

# --- II. TICKER universe MAP LAYER ---
BENCHMARK_TICKER = "^NSEI"
SECTOR_TICKER_MAP = {
    "Nifty Bank": {"ticker": "^NSEBANK", "type": "index"},
    "Nifty Auto": {"ticker": "^CNXAUTO", "type": "index"},
    "Nifty FMCG": {"ticker": "^CNXFMCG", "type": "index"},
    "Nifty IT": {"ticker": "^CNXIT", "type": "index"},
    "Nifty Metal": {"ticker": "^CNXMETAL", "type": "index"},
    "Nifty Pharma": {"ticker": "^CNXPHARMA", "type": "index"},
    "Nifty Realty": {"ticker": "^CNXREALTY", "type": "index"},
    "Nifty Financial Services": {"ticker": "NIFTY_FIN_SERVICE.NS", "type": "index"},
    "Nifty PSU Bank": {"ticker": "PSUBNKBEES.NS", "type": "proxy"}
}

@st.cache_data(ttl=3600)
def fetch_historical_market_matrices():
    all_tickers = [BENCHMARK_TICKER] + [v["ticker"] for v in SECTOR_TICKER_MAP.values()]
    end_date = datetime.today()
    start_date = end_date - timedelta(days=500)
    try:
        raw_download = yf.download(all_tickers, start=start_date, end=end_date, progress=False)
        
        # --- FIX: DETECT MULTIINDEX AND FLATTEN SECURELY FOR CLOUD DEPLOYMENTS ---
        if isinstance(raw_download.columns, pd.MultiIndex):
            # Select Adj Close if present, fallback to Close, and drop the metric layer name
            df_metric = raw_download["Adj Close"] if "Adj Close" in raw_download else raw_download["Close"]
            return df_metric
        
        return raw_download["Adj Close"] if "Adj Close" in raw_download else raw_download["Close"]
    except Exception as e:
        st.error(f"Failed to fetch market data from yfinance: {str(e)}")
        st.stop()

price_matrix = fetch_historical_market_matrices()

# --- ANALYTICS ENGINE COMPUTATION ---
def calculate_historical_returns(series):
    cleaned = series.dropna()
    if len(cleaned) < 2: return [0.0]*5
    latest_val = cleaned.iloc[-1]
    intervals = {"1W": 5, "1M": 21, "3M": 63, "6M": 126, "1Y": 252}
    returns = []
    for window in ["1W", "1M", "3M", "6M", "1Y"]:
        offset = intervals[window]
        if len(cleaned) > offset:
            past_val = cleaned.iloc[-(offset + 1)]
            returns.append(((latest_val - past_val) / past_val) * 100)
        else:
            returns.append(((latest_val - cleaned.iloc[0]) / cleaned.iloc[0]) * 100)
    return returns

nifty_returns = calculate_historical_returns(price_matrix[BENCHMARK_TICKER])

sector_analytics_data = []
for name, meta in SECTOR_TICKER_MAP.items():
    if meta["ticker"] in price_matrix.columns:
        s_returns = calculate_historical_returns(price_matrix[meta["ticker"]])
        rel_returns = [s - n for s, n in zip(s_returns, nifty_returns)]
        m_score = (s_returns[0]*0.10) + (s_returns[1]*0.20) + (s_returns[2]*0.30) + (s_returns[3]*0.20) + (s_returns[4]*0.20)
        
        med_term_rel = rel_returns[2]  # 3M
        short_term_rel = rel_returns[1] # 1M
        
        if med_term_rel >= 0 and short_term_rel >= 0: label = "Leading"
        elif med_term_rel < 0 and short_term_rel >= 0: label = "Improving"
        elif med_term_rel >= 0 and short_term_rel < 0: label = "Weakening"
        else: label = "Lagging"
        
        sector_analytics_data.append({
            "sector": name, "ticker": meta["ticker"], "type": meta["type"],
            "returns": s_returns, "relative": rel_returns, "momentum": m_score, "quadrant": label
        })

df_analytics = pd.DataFrame(sector_analytics_data).sort_values(by="momentum", ascending=False).reset_index(drop=True)

# --- SECTION 6: KPI CARDS GRIDS ---
st.markdown('<div class="page-section">', unsafe_allow_html=True)
kpi_cols = st.columns(4)

beating_bench_count = sum(1 for s in sector_analytics_data if s["relative"][1] > 0)
positive_sectors_count = sum(1 for s in sector_analytics_data if s["returns"][1] > 0)

with kpi_cols[0]:
    st.markdown(f"""<div class="metric-summary-card">
        <p class="metric-title">BENCHMARK RETURN (NIFTY 50 1M)</p>
        <p class="metric-value">{nifty_returns[1]:+.2f}%</p>
        <p style="margin:0; font-size:0.8rem; color:#6B7280;">Ticker Node: {BENCHMARK_TICKER}</p>
    </div>""", unsafe_allow_html=True)

with kpi_cols[1]:
    st.markdown(f"""<div class="metric-summary-card">
        <p class="metric-title">MARKET BREADTH (OUTPERFORMING BASES)</p>
        <p class="metric-value" style="color:#38BDF8;">{beating_bench_count} / {len(SECTOR_TICKER_MAP)}</p>
        <p style="margin:0; font-size:0.8rem; color:#6B7280;">Sectors outperforming Nifty 50</p>
    </div>""", unsafe_allow_html=True)

with kpi_cols[2]:
    st.markdown(f"""<div class="metric-summary-card">
        <p class="metric-title">ABSOLUTE POSITIVE CLUSTERS</p>
        <p class="metric-value" style="color:#10B981;">{positive_sectors_count} / {len(SECTOR_TICKER_MAP)}</p>
        <p style="margin:0; font-size:0.8rem; color:#6B7280;">Sectors with green 1M returns</p>
    </div>""", unsafe_allow_html=True)

with kpi_cols[3]:
    st.markdown(f"""<div class="metric-summary-card">
        <p class="metric-title">MOMENTUM CONCENTRATION LEAD</p>
        <p class="metric-value" style="color:#A855F7; font-size:1.5rem; overflow:hidden; white-space:nowrap; text-overflow:ellipsis;">{df_analytics.iloc[0]['sector']}</p>
        <p style="margin:0; font-size:0.8rem; color:#6B7280;">Highest multi-window momentum rank</p>
    </div>""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- SECTION 7: MARKET LEADERSHIP SIGNAL PROFILE ---
st.markdown('<div class="page-section">', unsafe_allow_html=True)
leading_list = [s["sector"] for s in sector_analytics_data if s["quadrant"] == "Leading"]
improving_list = [s["sector"] for s in sector_analytics_data if s["quadrant"] == "Improving"]
weakening_list = [s["sector"] for s in sector_analytics_data if s["quadrant"] == "Weakening"]
lagging_list = [s["sector"] for s in sector_analytics_data if s["quadrant"] == "Lagging"]

verdict_html = "<div class='verdict-box'><p style='margin:0; font-size:1rem; line-height:1.6; color:#E5E7EB;'>🏁 <b>Market Leadership Signal Profile:</b><br>"
if leading_list:
    verdict_html += f"🔥 <b>Leading Sectors:</b> <span style='color:#10B981; font-weight:bold;'>{', '.join(leading_list)}</span> are outperforming across near and medium-term windows.<br>"
if improving_list:
    verdict_html += f"⚡ <b>Improving Sectors:</b> <span style='color:#38BDF8; font-weight:bold;'>{', '.join(improving_list)}</span> show expanding short-term strength and are cycling upward.<br>"
if weakening_list:
    verdict_html += f"⚠️ <b>Weakening Sectors:</b> <span style='color:#F59E0B; font-weight:bold;'>{', '.join(weakening_list)}</span> are losing structural short-term acceleration.<br>"
if lagging_list:
    verdict_html += f"❄️ <b>Lagging Sectors:</b> <span style='color:#EF4444; font-weight:bold;'>{', '.join(lagging_list)}</span> remain under pressure, systematically trail-tracking the headline benchmark index."
verdict_html += "</p></div>"
st.markdown(verdict_html, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- SECTION 8: PERFORMANCE HEATMAP ---
st.markdown('<div class="page-section">', unsafe_allow_html=True)
st.markdown("<h3 style='margin:0 0 20px 0; color:#FFFFFF; font-size:1.4rem;'>Absolute Sector Performance Heatmap</h3>", unsafe_allow_html=True)

heatmap_records = []
for row in sector_analytics_data:
    heatmap_records.append({
        "Sector Profile": row["sector"],
        "1W Return": row["returns"][0], "1M Return": row["returns"][1],
        "3M Return": row["returns"][2], "6M Return": row["returns"][3],
        "1Y Return": row["returns"][4]
    })
df_heat = pd.DataFrame(heatmap_records).set_index("Sector Profile")

heat_fig = px.imshow(
    df_heat, text_auto=".2f",
    color_continuous_scale=[[0, "#EF4444"], [0.5, "#06090F"], [1, "#10B981"]],
    color_continuous_midpoint=0.0, aspect="auto"
)
heat_fig.update_layout(
    paper_bgcolor='#0B0F17', plot_bgcolor='#0B0F17', font=dict(color="#F3F4F6", family="Inter"),
    margin=dict(l=40, r=40, t=10, b=10), height=480, coloraxis_showscale=False
)
st.plotly_chart(heat_fig, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- SECTION 9: LEADERBOARD & SCATTER QUADRANT ---
split_cols = st.columns([4, 6])

with split_cols[0]:
    st.markdown('<div class="page-section" style="height:100%;">', unsafe_allow_html=True)
    st.markdown("<h3 style='margin:0 0 20px 0; color:#FFFFFF; font-size:1.3rem;'>Momentum Leaderboard</h3>", unsafe_allow_html=True)
    
    for idx, row in df_analytics.iterrows():
        badge_map = {"Leading": "badge-leading", "Improving": "badge-improving", "Weakening": "badge-weakening", "Lagging": "badge-lagging"}
        proxy_tag = " <span style='font-size:0.7rem; color:#6B7280;'>[Proxy]</span>" if row["type"] == "proxy" else ""
        
        st.markdown(f"""
            <div class="leaderboard-row-card">
                <div style="display:flex; justify-content:space-between; align-items:center; width:100%;">
                    <div>
                        <span class="lead-name">{row['sector']}</span>{proxy_tag}
                        <div style="font-size:0.8rem; color:#6B7280; margin-top:2px;">Score: {row['momentum']:.2f} // 1M Rel Alpha: {row['relative'][1]:+.2f}%</div>
                    </div>
                    <span class="{badge_map[row['quadrant']]}">{row['quadrant'].upper()}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with split_cols[1]:
    st.markdown('<div class="page-section" style="height:100%;">', unsafe_allow_html=True)
    st.markdown("<h3 style='margin:0 0 20px 0; color:#FFFFFF; font-size:1.3rem;'>Sector Momentum Quadrant</h3>", unsafe_allow_html=True)
    
    scatter_df = pd.DataFrame([{
        "Sector": r["sector"],
        "Long-Term Relative Strength (3M)": r["relative"][2],
        "Short-Term Relative Momentum (1M)": r["relative"][1],
        "Status": r["quadrant"]
    } for r in sector_analytics_data])
    
    quad_colors = {"Leading": "#10B981", "Improving": "#38BDF8", "Weakening": "#F59E0B", "Lagging": "#EF4444"}
    
    quad_fig = px.scatter(
        scatter_df, x="Long-Term Relative Strength (3M)", y="Short-Term Relative Momentum (1M)",
        color="Status", color_discrete_map=quad_colors,
        hover_name="Sector", 
        labels={"Long-Term Relative Strength (3M)": "Medium-Term Relative Strength (3M vs Nifty 50)",
                "Short-Term Relative Momentum (1M)": "Short-Term Relative Momentum (1M vs Nifty 50)"}
    )
    
    quad_fig.update_traces(marker=dict(size=18, line=dict(width=1.5, color='#FFFFFF')))
    
    max_x = max(abs(scatter_df["Long-Term Relative Strength (3M)"]))
    max_y = max(abs(scatter_df["Short-Term Relative Momentum (1M)"]))
    boundary = max(max_x, max_y, 2) * 1.3
    
    quad_fig.update_layout(
        paper_bgcolor='#0B0F17', plot_bgcolor='#0B0F17', font=dict(color="#F3F4F6", family="Inter"),
        margin=dict(l=40, r=40, t=15, b=40), height=580, showlegend=True,
        xaxis=dict(gridcolor="#1F2937", zerolinecolor="#4B5563", zerolinewidth=2, range=[-boundary, boundary]),
        yaxis=dict(gridcolor="#1F2937", zerolinecolor="#4B5563", zerolinewidth=2, range=[-boundary, boundary])
    )
    st.plotly_chart(quad_fig, use_container_width=True)
    st.markdown("<p style='font-size:0.8rem; color:#6B7280; text-align:center;'>💡 Hover over scatter circles to isolate exact overlapping segment targets.</p>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- SECTION 10: PERFORMANCE COMPARISON (BASE 100) WITH FLUID LINES FIX ---
st.markdown('<div class="page-section">', unsafe_allow_html=True)
st.markdown("<h3 style='margin:0 0 15px 0; color:#FFFFFF; font-size:1.4rem;'>Normalized Performance Comparison (Base 100)</h3>", unsafe_allow_html=True)

all_valid_sectors = list(SECTOR_TICKER_MAP.keys())
selected_sectors = st.multiselect(
    "Select specific sector metrics to chart overlay lines against Nifty 50 baseline index:",
    options=all_valid_sectors, default=all_valid_sectors[:3]
)

lookback_days = st.radio("Lookback Window Horizon:", options=["3 Months", "6 Months", "1 Year"], horizontal=True)
days_mapping = {"3 Months": 90, "6 Months": 180, "1 Year": 365}

trimmed_prices = price_matrix.tail(days_mapping[lookback_days]).copy()

line_fig = go.Figure()

nifty_series = trimmed_prices[BENCHMARK_TICKER].dropna()
if not nifty_series.empty:
    nifty_normalized = (nifty_series / nifty_series.iloc[0]) * 100
    line_fig.add_trace(go.Scatter(
        x=nifty_series.index, y=nifty_normalized, 
        name="Nifty 50 (Benchmark)", 
        line=dict(color="#FFFFFF", width=3),
        connectgaps=True
    ))

for name in selected_sectors:
    ticker_id = SECTOR_TICKER_MAP[name]["ticker"]
    if ticker_id in trimmed_prices.columns:
        s_series = trimmed_prices[ticker_id].dropna()
        if not s_series.empty:
            s_normalized = (s_series / s_series.iloc[0]) * 100
            line_fig.add_trace(go.Scatter(
                x=s_series.index, y=s_normalized, 
                name=name, 
                line=dict(width=2),
                connectgaps=True
            ))

line_fig.update_layout(
    paper_bgcolor='#0B0F17', plot_bgcolor='#0B0F17', font=dict(color="#F3F4F6", family="Inter"),
    margin=dict(l=40, r=20, t=10, b=40), height=420,
    xaxis=dict(gridcolor="#1F2937", tickfont=dict(color="#6B7280")),
    yaxis=dict(gridcolor="#1F2937", tickfont=dict(color="#6B7280")),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)
st.plotly_chart(line_fig, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- SECTION 11: EXPORT SNAPS SNIPPET REGISTER ---
st.markdown('<div class="page-section">', unsafe_allow_html=True)
st.markdown("<h3 style='margin:0 0 15px 0; color:#FFFFFF; font-size:1.4rem;'>🗂️ Export Performance Snapshot</h3>", unsafe_allow_html=True)

st.button("📸 Compile High Resolution LinkedIn Summary Card", on_click=activate_summary_card, use_container_width=True)

if st.session_state.show_summary:
    current_time_str = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    st.markdown(f"""
    <div class="export-card-frame">
        <div style="display:flex; justify-content:space-between; margin-bottom:20px;">
            <span class="export-headline">SECTOR DIAGNOSTICS // EXPORT REPORT MATRICES</span>
            <span style="font-family:'JetBrains Mono', monospace; font-size:0.8rem; color:#6B7280;">NIFTY MOMENTUM ENGINE GATEWAY</span>
        </div>
        <p class="export-sub-item"><b>• Nifty 50 Baseline Momentum (1M):</b> {nifty_returns[1]:+.2f}% absolute index drift metrics.</p>
        <p class="export-sub-item"><b>• Alpha Concentration Expansion Index:</b> {beating_bench_count} out of {len(SECTOR_TICKER_MAP)} tracked indices outpaced market benchmarks.</p>
        <p class="export-sub-item" style="margin-bottom:25px;"><b>• Market Rotation Lead Quadrant Posture:</b> <span style="color:#10B981; font-weight:bold;">{', '.join(leading_list[:3]) if leading_list else 'No active clusters'}</span> sectors leading current cycles.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="background-color:#0E1626; padding:12px 30px; border-radius:0 0 12px 12px; border:1px solid #1F2937; border-top:none; font-family:'JetBrains Mono', monospace; font-size:0.75rem; color:#6B7280;">
        Generated via Nifty Intelligence Core Terminal // Timestamp: {current_time_str} UTC Context
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# --- XII. TERMINAL SYSTEM FOOTER ---
st.markdown(f"""
    <div class="footer-container">
        <b>Nifty Sector Rotation Dashboard</b> // 30 Days of AI Finance Challenge — Day 05 Build<br>
        Sourced Ingestion Status: <span style="color:#10B981;">● YAHOO FINANCE DATA TIMELINES SYNCED</span> // Engine Context: Deterministic Rule Matrix
    </div>
""", unsafe_allow_html=True)
