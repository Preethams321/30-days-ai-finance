import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# --- 1. THEME & MOBILE-RESPONSIVE GRAPHICS LAYOUT ---
st.set_page_config(layout="wide", page_title="EquiCompare")

# Premium Responsive Stylesheet (Locks deep dark theme across desktop & mobile)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght=400;500;600;700&display=swap');
    
    html, body, [class*="css"], .stApp, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background-color: #0B0F17 !important; 
        color: #F3F4F6 !important;
    }
    header, footer, #MainMenu { visibility: hidden !important; }
    
    /* Structural Section Layout Blocks */
    .intro-section {
        background: linear-gradient(135deg, #1E1B4B 0%, #0F172A 100%) !important;
        padding: 35px;
        border-radius: 16px;
        border: 1px solid #1E293B;
        margin-bottom: 30px;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);
    }
    .blueprint-card {
        background-color: #0F131C !important;
        border: 1px solid #1E293B;
        border-radius: 12px;
        padding: 22px;
        height: 100%;
    }
    .page-section {
        background-color: #0F131C !important;
        border: 1px solid #1E293B;
        border-radius: 16px;
        padding: 40px;
        margin-bottom: 60px;
    }
    
    /* Responsive Typography */
    .main-title {
        margin: 0 0 15px 0; 
        color: #FFFFFF !important; 
        font-size: 2.4rem; 
        font-weight: 700;
    }
    .main-bullet-list {
        margin: 0; 
        padding-left: 20px; 
        color: #C7D2FE !important; 
        font-size: 1.05rem; 
        font-weight: 400; 
        line-height: 1.6;
    }
    .main-bullet-list li {
        margin-bottom: 8px;
    }
    .scroll-footer {
        margin-top: 25px;
        color: #64748B !important;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        text-align: center;
    }
    .error-inline {
        color: #F87171 !important;
        font-size: 0.85rem;
        font-weight: 500;
        margin-top: 4px;
        display: block;
    }
    
    /* --- PHONE VIEWPORT OVERRIDES --- */
    @media (max-width: 768px) {
        .intro-section {
            padding: 20px 15px !important;
            margin-bottom: 20px !important;
        }
        .main-title {
            font-size: 1.6rem !important;
            line-height: 1.3 !important;
        }
        .main-bullet-list {
            font-size: 0.92rem !important;
            padding-left: 15px !important;
        }
        .page-section {
            padding: 20px 15px !important;
            margin-bottom: 30px !important;
        }
        .blueprint-card {
            padding: 18px 15px !important;
            margin-bottom: 15px !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Currency Formatter Utility
def format_rupees(val):
    abs_val = abs(val)
    if abs_val >= 10000000: 
        return f"₹{val / 10000000:.2f} Cr"
    elif abs_val >= 100000: 
        return f"₹{val / 100000:.2f} L"
    else:
        return f"₹{val:,.2f}"

# --- 2. DATA ACQUISITION LAYER ---
@st.cache_data(ttl=3600)
def fetch_stock_history(symbol, start_year, end_year):
    ticker_string = symbol if symbol.startswith("^") else f"{symbol.upper()}.NS"
    fallback_string = None if symbol.startswith("^") else f"{symbol.upper()}.BO"
    
    for tk in [ticker_string, fallback_string]:
        if not tk: continue
        data = yf.download(tk, period="max", interval="1d", progress=False, auto_adjust=False)
        
        if not data.empty:
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)
                
            df_close = data['Adj Close'].dropna() if 'Adj Close' in data.columns else data['Close'].dropna()
            if df_close.empty: continue
            
            first_date = df_close.index[0]
            req_start = pd.to_datetime(f"{start_year}-01-01")
            req_end = pd.to_datetime(f"{end_year}-12-31")
            
            if req_start < first_date:
                return {"data": None, "error": f"This stock does not have market data from {start_year}. Earliest available data starts from {first_date.year}."}
            if req_end < req_start:
                return {"data": None, "error": "End year cannot be earlier than the selected start year."}
                
            sliced_df = df_close[(df_close.index >= req_start) & (df_close.index <= req_end)]
            if sliced_df.empty:
                return {"data": None, "error": "No price records found inside the chosen date range."}
                
            return {"data": sliced_df, "error": None, "ticker": tk}
            
    return {"data": None, "error": "We couldn't verify this stock. Please check the company name or NSE/BSE ticker."}

def compute_financial_metrics(series, invested_amount):
    initial_price = float(series.iloc[0])
    current_price = float(series.iloc[-1])
    
    normalized_growth = (series / initial_price) * invested_amount
    final_value = float(normalized_growth.iloc[-1])
    abs_gain = final_value - invested_amount
    abs_pct = ((final_value / invested_amount) - 1) * 100
    
    years = (series.index[-1] - series.index[0]).days / 365.25
    cagr = ((final_value / invested_amount) ** (1 / years) - 1) * 100 if years > 0 else 0
    
    rolling_max = normalized_growth.cummax()
    drawdown_series = (normalized_growth - rolling_max) / rolling_max
    max_dd = drawdown_series.min() * 100
    
    return {
        "normalized_series": normalized_growth, "final_value": final_value,
        "initial_price": initial_price, "current_price": current_price,
        "abs_gain": abs_gain, "abs_pct": abs_pct, "cagr": cagr, "max_dd": max_dd,
        "drawdown_series": drawdown_series
    }

# --- 3. STATE INITIALIZATION ---
if 'portfolio_stocks' not in st.session_state:
    st.session_state.portfolio_stocks = [
        {"symbol": "RELIANCE", "amount": 10000, "start": 2010, "end": 2026},
        {"symbol": "TCS", "amount": 10000, "start": 2010, "end": 2026},
        {"symbol": "HDFCBANK", "amount": 10000, "start": 2010, "end": 2026}
    ]

# --- SECTION 1: WELCOME & INTRODUCTION PAGE ---
st.markdown("""
    <div class="intro-section">
        <h1 class="main-title">📈 EquiCompare</h1>
        <ul class="main-bullet-list">
            <li>Compare exactly how your money would have grown across different Indian stocks over time.</li>
            <li>Choose your custom investment amounts, pick your start years, and analyze historical returns side-by-side against the NIFTY 50 index with zero clutter.</li>
        </ul>
    </div>
""", unsafe_allow_html=True)

home_col1, home_col2 = st.columns(2)
with home_col1:
    st.markdown("""
        <div class="blueprint-card">
            <h3 style="color:#818CF8; margin-top:0;">📊 Core Platform Features</h3>
            <ul style="margin:0; padding-left:20px; line-height:1.7; color:#9CA3AF;">
                <li><b>Real Market Data:</b> Pulled directly from historical exchange prices with zero guesswork.</li>
                <li><b>Fair Comparison:</b> Sets all stocks to the same starting value so you can compare performance accurately.</li>
                <li><b>Automatic Ticker Sourcing:</b> Checks the National Stock Exchange (NSE) first, with a backup for BSE.</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

with home_col2:
    st.markdown("""
        <div class="blueprint-card">
            <h3 style="color:#34D399; margin-top:0;">📋 Quick Setup Guide</h3>
            <ul style="margin:0; padding-left:20px; line-height:1.7; color:#9CA3AF;">
                <li><b>Register Stocks:</b> Enter up to 6 different companies to compare side-by-side.</li>
                <li><b>Set Investment Windows:</b> Adjust your starting money and tracking years instantly.</li>
                <li><b>Analyze Hidden Risks:</b> Turn on market benchmarks and see maximum historical drops.</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="scroll-footer">↓ Scroll Down to Begin Comparison ↓</div><br>', unsafe_allow_html=True)

# --- SECTION 2: INPUT COMPONENT PAGE ---
st.markdown('<div class="page-section">', unsafe_allow_html=True)
input_header_l, input_header_r = st.columns([3, 1])
with input_header_l:
    st.markdown("<h2 style='margin:0 0 20px 0; color:#FFFFFF; font-size:1.5rem;'>1. Portfolio Parameters & Stock Selection</h2>", unsafe_allow_html=True)
with input_header_r:
    if st.button("➕ Add Stock Row", use_container_width=True):
        if len(st.session_state.portfolio_stocks) < 6:
            st.session_state.portfolio_stocks.append({"symbol": "", "amount": 10000, "start": 2015, "end": 2026})
            st.rerun()

user_selections = []
has_inline_errors = False

for idx, item in enumerate(st.session_state.portfolio_stocks):
    grid = st.columns([3, 2.5, 2, 2, 0.5])
    with grid[0]:
        sel_sym = st.text_input("Stock Ticker", value=item['symbol'], key=f"input_sym_{idx}", placeholder="e.g. INFOSYS, SBIN").upper().strip()
    with grid[1]:
        sel_amt = st.number_input("Amount Invested (₹)", value=int(item['amount']), key=f"input_amt_{idx}", step=5000)
    with grid[2]:
        sel_st = st.number_input("Start Year", value=int(item['start']), key=f"input_st_{idx}", min_value=1995, max_value=2026)
    with grid[3]:
        sel_en = st.number_input("End Year", value=int(item['end']), key=f"input_en_{idx}", min_value=1995, max_value=2026)
    with grid[4]:
        st.markdown("<p style='margin-top:28px;'></p>", unsafe_allow_html=True)
        if st.button("🗑️", key=f"input_del_{idx}"):
            st.session_state.portfolio_stocks.pop(idx)
            st.rerun()
            
    st.session_state.portfolio_stocks[idx] = {"symbol": sel_sym, "amount": sel_amt, "start": sel_st, "end": sel_en}
    if sel_sym:
        user_selections.append(st.session_state.portfolio_stocks[idx])

st.markdown("<br>", unsafe_allow_html=True)
control_cols = st.columns([3, 3, 3, 3])
with control_cols[0]: compare_nifty = st.checkbox("Compare against NIFTY 50", value=True)
with control_cols[1]: show_cagr = st.toggle("Show CAGR labels on chart", value=True)
with control_cols[2]: show_drawdown = st.toggle("Show Drawdown shading", value=False)
with control_cols[3]: trigger_calc = st.button("🚀 Run Growth Analysis", type="primary", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

if len(user_selections) < 1:
    st.info("Please enter at least one stock ticker in the parameters section above to generate analysis charts.")
    st.stop()

# --- 4. ENGINE MATH EVALUATION ROUTINES ---
plot_dataframe = pd.DataFrame()
calculated_metrics_map = {}

for stock in user_selections:
    backend_res = fetch_stock_history(stock['symbol'], stock['start'], stock['end'])
    if backend_res['data'] is not None:
        metrics = compute_financial_metrics(backend_res['data'], stock['amount'])
        plot_dataframe[stock['symbol']] = metrics['normalized_series'].resample('W').last()
        calculated_metrics_map[stock['symbol']] = {
            "config": stock, "final_value": metrics['final_value'], "initial_price": metrics['initial_price'],
            "current_price": metrics['current_price'], "abs_gain": metrics['abs_gain'], "abs_pct": metrics['abs_pct'],
            "cagr": metrics['cagr'], "max_dd": metrics['max_dd'], "drawdown_series": metrics['drawdown_series'].resample('W').last()
        }
    else:
        st.markdown(f'<div class="page-section"><span class="error-inline">❌ {stock["symbol"]}: {backend_res["error"]}</span></div>', unsafe_allow_html=True)
        has_inline_errors = True

if has_inline_errors:
    st.stop()

nifty_compiled_package = None
if compare_nifty and not plot_dataframe.empty:
    reference_anchor = user_selections[0]
    nifty_res = fetch_stock_history("^NSEI", reference_anchor['start'], reference_anchor['end'])
    if nifty_res['data'] is not None:
        nifty_metrics = compute_financial_metrics(nifty_res['data'], reference_anchor['amount'])
        nifty_compiled_package = {
            "name": "NIFTY 50", "final_value": nifty_metrics['final_value'], "initial_price": nifty_metrics['initial_price'],
            "current_price": nifty_metrics['current_price'], "abs_pct": nifty_metrics['abs_pct'],
            "cagr": nifty_metrics['cagr'], "max_dd": nifty_metrics['max_dd'], "series": nifty_metrics['normalized_series'].resample('W').last()
        }

# --- SECTION 3: THE CINEMATIC HERO CHART PAGE ---
st.markdown('<div class="page-section">', unsafe_allow_html=True)
st.markdown("<h2 style='margin:0 0 15px 0; color:#FFFFFF; font-size:1.5rem;'>2. Historical Compounded Growth Performance</h2>", unsafe_allow_html=True)

main_chart = go.Figure()
color_palette_hex = ['#38BDF8', '#F59E0B', '#E11D48', '#10B981', '#A855F7', '#6366F1']
color_mapping = {}

if compare_nifty and nifty_compiled_package is not None:
    main_chart.add_trace(go.Scatter(
        x=nifty_compiled_package['series'].index, y=nifty_compiled_package['series'],
        name="NIFTY 50 Benchmark", line=dict(color='#FFFFFF', dash='dash', width=2.5),
        hovertemplate="NIFTY 50: ₹%{y:,.0f}<extra></extra>"
    ))

for idx_color, asset in enumerate(plot_dataframe.columns):
    assigned_color = color_palette_hex[idx_color % len(color_palette_hex)]
    color_mapping[asset] = assigned_color
    main_chart.add_trace(go.Scatter(
        x=plot_dataframe.index, y=plot_dataframe[asset],
        name=asset, line=dict(color=assigned_color, width=3.5),
        hovertemplate=f"{asset}: ₹%{{y:,.0f}}<extra></extra>"
    ))
    
    if show_cagr:
        asset_cagr = calculated_metrics_map[asset]['cagr']
        main_chart.add_annotation(
            x=plot_dataframe.index[-1], y=plot_dataframe[asset].iloc[-1],
            text=f"  {asset_cagr:.1f}% CAGR", showarrow=False,
            xanchor="left", yanchor="middle", font=dict(color=assigned_color, size=12, weight="bold")
        )
        
    if show_drawdown:
        dd_array = calculated_metrics_map[asset]['drawdown_series']
        r_c = int(assigned_color[1:3], 16)
        g_c = int(assigned_color[3:5], 16)
        b_c = int(assigned_color[5:7], 16)
        main_chart.add_trace(go.Scatter(
            x=dd_array.index, y=plot_dataframe[asset] * (1 + dd_array),
            line=dict(width=0), fill='tonexty', fillcolor=f"rgba({r_c}, {g_c}, {b_c}, 0.05)",
            showlegend=False, hoverinfo='none'
        ))

market_crises_timeline = [
    ("2008-09-15", "2008 Crisis"), ("2016-11-08", "Demonetisation"),
    ("2020-03-23", "COVID Crash"), ("2021-10-18", "2021 Bull Run Peak")
]
for date_marker, event_title in market_crises_timeline:
    parsed_dt = pd.to_datetime(date_marker)
    if parsed_dt >= plot_dataframe.index[0] and parsed_dt <= plot_dataframe.index[-1]:
        main_chart.add_vline(x=parsed_dt, line_width=1, line_dash="dot", line_color="#334155")
        main_chart.add_annotation(x=parsed_dt, y=plot_dataframe.max().max() * 0.95, text=f" {event_title}", showarrow=False, xanchor="left", font=dict(color="#64748B", size=10))

# VALUE-ERROR FIXED: Stripped old titlefont/tickfont keys. Layout is completely version-stable.
main_chart.update_layout(
    template="plotly_dark",
    paper_bgcolor='#0F131C', 
    plot_bgcolor='#0F131C',
    font=dict(color="#F3F4F6"),
    hovermode="x unified", 
    yaxis=dict(title="Growth Valuation (₹)", gridcolor="#1E293B", tickformat=",.0f"),
    xaxis=dict(title="Year Horizon Tracks", gridcolor="#1E293B"),
    margin=dict(l=15, r=110, t=30, b=15), height=600,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0)
)

st.plotly_chart(main_chart, use_container_width=True, theme=None)
st.markdown('</div>', unsafe_allow_html=True)

# --- SECTION 4: PERFORMANCE METRICS BREAKDOWN PAGE (SORTED BY HIGHEST VALUE) ---
st.markdown('<div class="page-section">', unsafe_allow_html=True)
st.markdown("<h2 style='margin:0 0 20px 0; color:#FFFFFF; font-size:1.5rem;'>3. Performance Metrics Breakdown</h2>", unsafe_allow_html=True)

sorted_metrics_list = sorted(calculated_metrics_map.items(), key=lambda x: x[1]['final_value'], reverse=True)
grid_card_count = len(sorted_metrics_list) + (1 if (compare_nifty and nifty_compiled_package) else 0)
ui_cards_columns = st.columns(grid_card_count)

for idx_card, (ticker_name, metrics) in enumerate(sorted_metrics_list):
    with ui_cards_columns[idx_card]:
        outperformance_badge = ""
        if nifty_compiled_package:
            if metrics['cagr'] >= nifty_compiled_package['cagr']:
                outperformance_badge = "<p style='margin:12px 0 0 0; font-size:0.8rem; color:#34D399; font-weight:700;'>⚡ OUTPERFORMED NIFTY 50</p>"
            else:
                outperformance_badge = "<p style='margin:12px 0 0 0; font-size:0.8rem; color:#F43F5E; font-weight:700;'>📉 UNDERPERFORMED NIFTY 50</p>"
                
        card_text_color = color_mapping.get(ticker_name, '#FFFFFF')
        
        st.markdown(f"""
            <div style="background-color:#0B0F19; border:1px solid #1E293B; padding:20px; border-radius:12px; height:100%;">
                <h4 style="margin:0 0 12px 0; color:{card_text_color}; font-size:1.25rem; font-weight:700;">{ticker_name}</h4>
                <p style="margin:4px 0; font-size:0.88rem; color:#94A3B8;">Timeline: {metrics['config']['start']} → {metrics['config']['end']}</p>
                <hr style="border-color:#1E293B; margin:8px 0;">
                <p style="margin:4px 0; font-size:0.88rem; color:#E2E8F0;">Start Share Price: <b>₹{metrics['initial_price']:,.2f}</b></p>
                <p style="margin:4px 0; font-size:0.88rem; color:#E2E8F0;">End Share Price: <b>₹{metrics['current_price']:,.2f}</b></p>
                <hr style="border-color:#1E293B; margin:8px 0;">
                <p style="margin:4px 0; font-size:0.88rem; color:#E2E8F0;">Principal Invested: <b>{format_rupees(metrics['config']['amount'])}</b></p>
                <p style="margin:4px 0; font-size:0.88rem; color:#E2E8F0;">Final Value: <b>{format_rupees(metrics['final_value'])}</b></p>
                <p style="margin:4px 0; font-size:0.88rem; color:#34D399;">Absolute Return: <b>+{metrics['abs_pct']:.1f}%</b></p>
                <p style="margin:4px 0; font-size:0.88rem; color:#FBBF24;">Annualized CAGR: <b>{metrics['cagr']:.2f}%</b></p>
                <p style="margin:4px 0; font-size:0.88rem; color:#F43F5E;">Max Drawdown: <b>{metrics['max_dd']:.2f}%</b></p>
                {outperformance_badge}
            </div>
        """, unsafe_allow_html=True)

if compare_nifty and nifty_compiled_package is not None:
    with ui_cards_columns[-1]:
        st.markdown(f"""
            <div style="background-color:#1E293B; border:1px solid #334155; padding:20px; border-radius:12px; height:100%;">
                <h4 style="margin:0 0 12px 0; color:#94A3B8; font-size:1.25rem; font-weight:700;">{nifty_compiled_package['name']}</h4>
                <p style="margin:4px 0; font-size:0.88rem; color:#64748B;">Market Benchmark Index Reference</p>
                <hr style="border-color:#334155; margin:8px 0;">
                <p style="margin:4px 0; font-size:0.88rem; color:#E2E8F0;">Start Index Value: <b>{nifty_compiled_package['initial_price']:,.2f}</b></p>
                <p style="margin:4px 0; font-size:0.88rem; color:#E2E8F0;">End Index Value: <b>{nifty_compiled_package['current_price']:,.2f}</b></p>
                <hr style="border-color:#334155; margin:8px 0;">
                <p style="margin:4px 0; font-size:0.88rem; color:#94A3B8;">Principal Base: Relative Base Scaling</p>
                <p style="margin:4px 0; font-size:0.88rem; color:#E2E8F0;">Final Normalized: <b>{format_rupees(nifty_compiled_package['final_value'])}</b></p>
                <p style="margin:4px 0; font-size:0.88rem; color:#34D399;">Absolute Return: <b>+{nifty_compiled_package['abs_pct']:.1f}%</b></p>
                <p style="margin:4px 0; font-size:0.88rem; color:#FBBF24;">Annualized CAGR: <b>{nifty_compiled_package['cagr']:.2f}%</b></p>
                <p style="margin:4px 0; font-size:0.88rem; color:#F43F5E;">Max Drawdown: <b>{nifty_compiled_package['max_dd']:.2f}%</b></p>
            </div>
        """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- SECTION 5: CLEAN TEXT-ONLY SOCIAL CARD GENERATOR ---
st.markdown('<div class="page-section">', unsafe_allow_html=True)
st.markdown("<h2 style='margin:0 0 10px 0; color:#FFFFFF; font-size:1.5rem;'>4. Export Comparison Card</h2>", unsafe_allow_html=True)
st.write("Compile a high-resolution, unclipped graphic layout optimized cleanly for professional feeds.")

if st.button("🎴 Generate Shareable Card Asset Layout", use_container_width=True):
    card_canvas = go.Figure()
    
    # Solid background configuration layer
    card_canvas.add_shape(type="rect", x0=0, y0=0, x1=100, y1=100, fillcolor="#060913", line=dict(color="#1E293B", width=3))
    
    # Headers positions optimized to eliminate vertical overlaps
    card_canvas.add_annotation(x=4, y=94, text="HISTORICAL INVESTMENT METRICS PROFILE", font=dict(color="#38BDF8", size=16, weight="bold"), showarrow=False, xanchor="left")
    card_canvas.add_annotation(x=96, y=94, text="EQUICOMPARE TERMINAL", font=dict(color="#475569", size=11, weight="bold"), showarrow=False, xanchor="right")
    
    total_assets_count = len(sorted_metrics_list)
    y_start_boundary = 78
    y_spacing_step = 66.0 / max(total_assets_count, 1)
    
    for idx_m, (name, metrics_data) in enumerate(sorted_metrics_list):
        current_y_pos = y_start_boundary - (idx_m * y_spacing_step)
        asset_text_color = color_mapping.get(name, '#FFFFFF')
        
        card_canvas.add_annotation(x=4, y=current_y_pos, text=f"• {name}", font=dict(color=asset_text_color, size=18, weight="bold"), showarrow=False, xanchor="left")
        
        compiled_string_line = (
            f"Invested: {format_rupees(metrics_data['config']['amount'])} ({metrics_data['config']['start']})  ➔  "
            f"Final Value: {format_rupees(metrics_data['final_value'])}  |  "
            f"CAGR: {metrics_data['cagr']:.2f}%  |  "
            f"Max Drop: {metrics_data['max_dd']:.2f}%"
        )
        card_canvas.add_annotation(x=4, y=current_y_pos - (y_spacing_step * 0.35), text=compiled_string_line, font=dict(color="#94A3B8", size=12), showarrow=False, xanchor="left")
        
    if nifty_compiled_package is not None:
        card_canvas.add_annotation(
            x=4, y=6, 
            text=f"• NIFTY 50 Market Benchmark Reference Return: +{nifty_compiled_package['abs_pct']:.1f}%  |  CAGR: {nifty_compiled_package['cagr']:.2f}%", 
            font=dict(color="#64748B", size=11.5), showarrow=False, xanchor="left"
        )

    card_canvas.update_layout(
        xaxis=dict(visible=False, range=[0, 100], autorange=False),
        yaxis=dict(visible=False, range=[0, 100], autorange=False),
        margin=dict(l=0, r=0, t=0, b=0),
        height=500, width=960,
        paper_bgcolor="#060913",
        plot_bgcolor="#060913"
    )
    
    st.plotly_chart(card_canvas, config={'toImageButtonOptions': {'format': 'png', 'filename': 'equicompare_performance_card', 'scale': 2}}, theme=None)
    st.info("Hover above the generated comparison card component and click the camera icon shortcut to download your clean graphic instantly! 📸")
st.markdown('</div>', unsafe_allow_html=True)
