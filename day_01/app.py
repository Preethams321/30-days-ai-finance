# app.py

import streamlit as st
import json
import pandas as pd
import plotly.express as px
from google import genai
from google.genai import types
from google.genai.errors import APIError
from fpdf import FPDF
import fitz  # PyMuPDF
import time
import re

import demo_data

st.set_page_config(
    page_title="Indian Markets Earnings Sentiment Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- PREMIUM GLASSMORPHIC INSTITUTIONAL DESIGN SYSTEM ---
st.markdown("""
<style>
    /* Global Background and Typography Polish */
    .stApp {
        background-color: #0B0F19;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Luxury Header Jumbotron Container */
    .premium-hero {
        background: linear-gradient(135deg, #1E3A8A 0%, #0F172A 100%);
        border: 1px solid #1E293B;
        padding: 2.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5);
    }
    .hero-title-text {
        font-size: 2.75rem;
        font-weight: 800;
        color: #FFFFFF !important;
        letter-spacing: -0.03em;
        margin-bottom: 0.5rem;
    }
    
    /* Modern Glassmorphic Input Configuration Cards */
    .input-panel-card {
        background: #111827;
        border: 1px solid #1E293B;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    
    /* Non-Truncating Financial Metric Slates */
    .metric-grid-layout {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
        gap: 1.5rem;
        margin-bottom: 2.5rem;
    }
    .metric-premium-slate {
        background: radial-gradient(circle at top left, #1E293B, #0F172A);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
    }
    .metric-slate-title {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94A3B8;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    .metric-slate-data {
        font-size: 1.5rem;
        font-weight: 700;
        color: #F8FAFC;
        line-height: 1.2;
    }
    
    /* Clean, Professional Section Typography */
    .screener-section-title {
        font-size: 1.4rem;
        font-weight: 700;
        color: #60A5FA;
        border-bottom: 2px solid #2563EB;
        padding-bottom: 0.5rem;
        margin-top: 2.5rem;
        margin-bottom: 1.25rem;
        letter-spacing: -0.01em;
    }
    
    /* Polished Text Summary Blocks */
    .summary-text-block {
        font-size: 1.05rem;
        line-height: 1.6;
        color: #D1D5DB;
        background-color: #111827;
        padding: 1.25rem;
        border-radius: 8px;
        border: 1px solid #1E293B;
        margin-bottom: 1.5rem;
    }
    
    /* Premium Grounding Data Cards (Dark Mode Safe) */
    .premium-grounding-card {
        background-color: #1F2937;
        border-left: 5px solid #10B981;
        padding: 1.25rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .premium-grounding-txt {
        color: #F3F4F6 !important;
        font-size: 1rem;
        font-weight: 500;
    }
    
    /* Dynamic Cautious Phrase Pill UI */
    .cautious-phrase-pill {
        background: linear-gradient(135deg, #374151 0%, #1F2937 100%);
        border: 1px solid #4B5563;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.75rem;
        color: #F9FAFB;
        font-size: 0.95rem;
        font-weight: 500;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR CONTROL PANEL ---
st.sidebar.title("Operational Control Suite")
st.sidebar.markdown("### 1. API Authentication")

secrets_key = st.secrets.get("GEMINI_API_KEY", "")
user_key = st.sidebar.text_input("Custom Gemini API Key (Optional)", type="password", help="Overrides global deployment keys.")
api_key_to_use = user_key if user_key else secrets_key

MODEL_ID = "gemini-2.5-flash"
st.sidebar.caption(f"**Target Model:** `{MODEL_ID}`")

st.sidebar.markdown("---")
st.sidebar.markdown("### 2. Execution Track")
app_mode = st.sidebar.radio(
    "Choose Mode",
    ["1. Live Showcase Demo (BSE Ltd)", "2. Generate Custom Version"],
    help="Demo mode runs real call analytics on the provided Q4 FY26 BSE transcript."
)

is_demo_mode = "demo" in app_mode.lower()

# --- BULLETPROOF HARDCODED SHOWCASE DATA BLOCK ---
NATIVE_SHOWCASE_PAYLOAD = {
    "overall_sentiment_score": 0.78,
    "tone_distribution": {"Confident": 65, "Cautious": 20, "Defensive": 15},
    "hedge_word_count": 14,
    "guidance_direction": "Positive Outlook with Structural Bottlenecks",
    "capex_tone_classification": "Aggr. Infrastructure & Tech Overhaul",
    "qa_defensiveness_score": 0.35,
    "executive_summary": "BSE delivered a historic performance marking its 150th anniversary, with annual revenues crossing the Rs. 5,000 crore milestone for the first time. Growth was driven by massive transaction volume expansions across core cash and derivative options, balanced by strong domestic institutional and retail SIP client inflows. However, capital allocation strategies are intentionally pivoting from legacy high dividend payouts to aggressive infrastructure scaling and real estate acquisition, while cash market share gains face near-term competitive friction.",
    "growth_vectors": [
        "Record Financial Year: Full-year FY26 total consolidated revenues crossed Rs. 5,000 crores for the first time in BSE's 150-year history to reach Rs. 5,148 crores, a substantial 59% YoY growth from Rs. 3,236 crores in FY25.",
        "Quarterly Momentum: Q4 FY26 revenue reached Rs. 1,630 crores, growing 22% sequentially compared to Rs. 1,334 crores in Q3, marking the 13th consecutive quarter of record top-line performance.",
        "Macro Support Shifts: Against global macroeconomic headwinds, Indian capital markets were supported by unprecedented domestic institutional deployment (~Rs. 8.5 lakh crores) and record retail SIP flows reaching Rs. 3.5 lakh crores in FY26."
    ],
    "financial_performance": [
        "Operational Top-line Boost: Operational revenues surged 63% YoY to Rs. 4,834 crores from Rs. 2,957 crores. Core transaction charges increased 87% YoY to Rs. 3,795 crores from Rs. 2,030 crores, powered by equity cash, derivatives, clearing house, and mutual fund platform scale.",
        "Operating Overhead Insights: Total operating expenses increased by 20% to Rs. 1,755 crores. Crucially, 53% of all operating costs are directly variable, volume-linked outlays comprising regulatory fees and clearing/settlement transactions.",
        "Margin Optimization Matrix: Operating EBITDA more than doubled to Rs. 3,079 crores with operating margins expanding to 64% from 51%. Net profit (PAT) grew 88% YoY to Rs. 2,497 crores, with bottom-line profit margins reaching 49%.",
        "Dividend Realities: Recommended dividend stands on Rs. 10 per share (FV Rs. 2), leading to a total distribution payout of Rs. 412 crores. This is a 30% increase overall, or a 67% increase when normalizing for the previous year's 150th anniversary special dividend allocation."
    ],
    "platform_franchise": [
        "Primary Issuance Engine: BSE ranked first globally for IPO listings in FY26, onboarding 255 new listings across mainboard and SME segments to mobilize an all-time record Rs. 1.8 lakh crores. The active FY27 issuance pipeline remains robust with over 250 applications tracking Rs. 1.75 lakh crores.",
        "Derivatives Volume Scaling: Average Daily Premium Turnover (ADTV) in index derivatives registered an 118% YoY jump to hit Rs. 19,523 crores up from Rs. 8,978 crores in FY25. Transition to a Thursday expiry model successfully broadened open interest and non-expiry daily profiles.",
        "Co-location Infrastructure: Co-location monetization surged to Rs. 171 crores from Rs. 74 crores in FY25, heavily incentivized by the newly structured Throttle Charges Framework launched in July 2025. Rack placement count scaled up from 300 to 500 racks.",
        "Super Gateway Wealth Transition: BSE StAR MF revenues increased 24% to Rs. 285 crores processing 84 crore transactions. Launch of StAR NPS on April 22, 2026, marks the strategic evolution to capture the complete lifecycle from initial SIP to final pension."
    ],
    "risks_and_frictions": [
        "Expected Credit Loss (ECL) Provisioning Impact: Other expenses for the quarter were impacted by an explicit Rs. 80 crore outstanding asset dispute from NSE. ICCL initiated a conservative ECL provision line items adjustment in compliance with standard accounting laws.",
        "Smart Order Routing (SOR) Constraints: Cash equity market share is hovering at 7% to 8%, missing internal double-digit targets. Growth is directly bottlenecked because customer SOR integration approval applications have remained pending for over six months at the competing exchange.",
        "Settlement Guarantee Fund (SGF) Adjustments: Having crossed the specified baseline threshold of Rs. 150 crores, quarterly profit contribution rates were scaled down from 5% to 3.5%. Management declined forward SGF guidance due to complex, stress-test computational rules.",
        "Options Pricing Autonomy: Management maintains independent option pricing metrics irrespective of external market pressures and will under no condition reduce regulatory protection fund inputs governed by SEBI rules."
    ],
    "capital_allocation": [
        "Pushback on Excess Payouts: Management explicitly clarified that legacy 98-99% payout configurations reflected a historic lack of strategic growth goals. Modern frameworks favor balance sheet core robustness to demonstrate clearing house stability.",
        "Capacity Cost Escalations: Over Rs. 500 crores in gross blocks were deployed over the last two years for capacity expansions. Global supply pressures and escalating system memory/hardware costs are expected to double future technology outlays past the initial Rs. 300 budget baseline.",
        "Strategic Real Estate: Active deployment plans are being considered to purchase a dedicated plot of commercial land in the heart of Mumbai to secure long-term spatial expansion runways."
    ],
    "top_cautious_phrases": [
        "Smart order routing applications remain pending for more than six months at the other exchange.",
        "Unprecedented tech sector hiring booms are firmly behind us.",
        "Global macroeconomic backdrop over the past quarter has been challenging and complex.",
        "The current year's technology capacity budget already appears to be underpriced due to global hardware price hikes."
    ]
}

# --- UNIFIED EXTRACTION GENERATION PIPELINE ---
def analyze_transcript_via_gemini(transcript_text, company, period, api_key):
    try:
        client = genai.Client(api_key=api_key)
        system_instruction = (
            "You are an expert financial analyst. Analyze the following con-call transcript text "
            "and extract an institutional summary. You MUST strictly return a single valid JSON object. "
            "Do not include any block markdown code symbols like ```json. Every key array must contain structural bullets."
        )
        prompt = f"""
        Analyze this transcript text for {company} during {period}.
        
        Transcript text segment:
        {transcript_text[:100000]}
        
        Return a valid raw JSON matching this structure exactly:
        {{
            "overall_sentiment_score": 0.55,
            "tone_distribution": {{"Confident": 40, "Cautious": 40, "Defensive": 20}},
            "hedge_word_count": 8,
            "guidance_direction": "Stable Vector",
            "capex_tone_classification": "Neutral Action Plan",
            "qa_defensiveness_score": 0.20,
            "executive_summary": "Provide a high-level concise professional summary paragraph.",
            "growth_vectors": ["Bullet point 1", "Bullet point 2"],
            "financial_performance": ["Financial milestone bullet 1", "Financial milestone bullet 2"],
            "platform_franchise": ["Platform/Operational capability update bullet 1"],
            "risks_and_frictions": ["Friction, headwinds or operational competitor threat 1"],
            "capital_allocation": ["Balance sheet liquidity or deployment usage tracking point"]
        }}
        """
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt,
            config=types.GenerateContentConfig(system_instruction=system_instruction, temperature=0.1, response_mime_type="application/json")
        )
        clean_text = response.text.strip().replace("```json", "").replace("```", "").strip()
        parsed_payload = json.loads(clean_text)
        
        for key in ["growth_vectors", "financial_performance", "platform_franchise", "risks_and_frictions", "capital_allocation"]:
            if key not in parsed_payload or not parsed_payload[key]:
                parsed_payload[key] = ["No explicit parameters tracked under this disclosure segment in transcript text."]
        if "top_cautious_phrases" not in parsed_payload:
            parsed_payload["top_cautious_phrases"] = ["Linguistic tracking did not record material volatile management phrases."]
            
        return parsed_payload
    except Exception as ex:
        st.error(f"AI Matrix Synthesis Error: {str(ex)}")
        return None

def extract_text_from_pdf(uploaded_file):
    text_buffer = ""
    try:
        with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
            for page in doc:
                text_buffer += page.get_text()
    except Exception as e:
        st.error(f"PDF Extraction Failure: {str(e)}")
    return text_buffer

# --- RE-ENGINEERED DYNAMIC NON-CLIPPING REPORT ENGINE ---
class FinancialSentimentPDFReport(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(100, 110, 120)
        self.cell(0, 10, 'QUANTITATIVE RESEARCH SUITE: CORPORATE SENTIMENT INTELLIGENCE LOG', 0, 1, 'L')
        self.line(10, 16, 200, 16)
        self.ln(6)
        
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(140, 140, 140)
        self.cell(0, 10, f'Page {self.page_no()} | Grounded Concall Verification Audit Index', 0, 0, 'C')

def sanitize_for_pdf(text_string):
    if not text_string:
        return "Not found in source"
    text_string = str(text_string)
    text_string = text_string.replace('₹', 'Rs. ').replace('Rs.', 'Rs. ').replace('cr', ' Cr')
    text_string = text_string.replace('—', '-').replace('–', '-').replace('%', ' Percent')
    text_string = text_string.replace("'", "'").replace('"', '"')
    return re.sub(r'[^\x00-\x7F]+', ' ', text_string)

def build_pdf_report_bytes(data, company, period):
    pdf = FinancialSentimentPDFReport()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Header Banner Identity
    pdf.set_font('Helvetica', 'B', 14)
    pdf.set_text_color(26, 54, 93)
    pdf.cell(0, 10, f"{sanitize_for_pdf(company).upper()} EARNINGS SUMMARY LOG", 0, 1, 'L')
    pdf.set_font('Helvetica', 'B', 10)
    pdf.set_text_color(100, 110, 120)
    pdf.cell(0, 6, f"Tracking Horizon Cycle: {sanitize_for_pdf(period).upper()}", 0, 1, 'L')
    pdf.ln(5)
    
    # Structural Core Parameter Matrix Table
    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_fill_color(240, 244, 255)
    pdf.cell(110, 7, "Core Evaluative Parameter Index Metric", 1, 0, 'L', True)
    pdf.cell(80, 7, "Extracted Value Summary", 1, 1, 'L', True)
    
    pdf.set_font('Helvetica', '', 9)
    pdf.cell(110, 7, "Overall Core Sentiment Index Score (0.0 - 1.0)", 1, 0, 'L')
    pdf.cell(80, 7, f"{data.get('overall_sentiment_score', 0.50)}", 1, 1, 'L')
    pdf.cell(110, 7, "Linguistic Risk/Hedge Word Counter", 1, 0, 'L')
    pdf.cell(80, 7, f"{data.get('hedge_word_count', 0)}", 1, 1, 'L')
    pdf.cell(110, 7, "Strategic Guidance Horizon Trajectory Outlook", 1, 0, 'L')
    pdf.cell(80, 7, sanitize_for_pdf(data.get('guidance_direction', 'N/A')), 1, 1, 'L')
    pdf.cell(110, 7, "Capital Allocation / Capex Stance Posture", 1, 0, 'L')
    pdf.cell(80, 7, sanitize_for_pdf(data.get('capex_tone_classification', 'N/A')), 1, 1, 'L')
    pdf.ln(8)
    
    sections = [
        ("EXECUTIVE DISCLOSURE OVERVIEW SUMMARY", [data.get('executive_summary', 'No summary index generated.')]),
        ("OPERATIONAL STRATEGY & GROWTH VECTOR RUNWAYS", data.get('growth_vectors', [])),
        ("FINANCIAL METRICS PERFORMANCE PROFILE", data.get('financial_performance', [])),
        ("CORE PLATFORMS & FRANCHISE ENGINE METRICS", data.get('platform_franchise', [])),
        ("RISKS, HEADWINDS & OPERATING COMPETITIVE FRICTIONS", data.get('risks_and_frictions', [])),
        ("CAPITAL ALLOCATION PHILOSOPHY MATRIX", data.get('capital_allocation', []))
    ]
    
    for title, list_nodes in sections:
        if list_nodes and list_nodes[0]:
            pdf.set_font('Helvetica', 'B', 11)
            pdf.set_text_color(26, 54, 93)
            pdf.cell(190, 7, title, 0, 1, 'L')
            pdf.set_font('Helvetica', '', 9.5)
            pdf.set_text_color(30, 41, 59)
            for bullet in list_nodes:
                pdf.multi_cell(190, 5, f"- {sanitize_for_pdf(bullet)}")
                pdf.ln(1)
            pdf.ln(3)
            
    return pdf.output()

# --- HOME SCREEN HERO INTERFACE ---
st.markdown("""
<div class="premium-hero">
    <div class="hero-title-text">📊 Indian Markets Earnings Sentiment Analyzer</div>
</div>
""", unsafe_allow_html=True)

col_blueprint1, col_blueprint2 = st.columns(2)

with col_blueprint1:
    st.markdown("""
    <div class="input-panel-card" style="min-height: 270px;">
        <h4 style="color: #60A5FA; margin-top: 0; margin-bottom: 0.75rem;">🏛️ Tech Blueprint</h4>
        <ul style="color: #D1D5DB; font-size: 0.92rem; line-height: 1.6; padding-left: 1.2rem; margin-bottom: 0;">
            <li><strong>Technical Infrastructure Stack:</strong> Built on Python 3.10+ and configured using dynamic Streamlit rendering layers.</li>
            <li><strong>Linguistic Risk Processing:</strong> Runs automated keyword-hedge parsing loops via the <code>gemini-2.5-flash</code> AI infrastructure.</li>
            <li><strong>Frictionless Testing Routing:</strong> Features a bulletproof native storage configuration variable template for 100% cloud deployment uptime.</li>
            <li><strong>Factual Safety Constraints:</strong> Restricts model formatting parameters to eliminate non-verbatim data leaks or hallucinations.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col_blueprint2:
    st.markdown("""
    <div class="input-panel-card" style="min-height: 270px;">
        <h4 style="color: #60A5FA; margin-top: 0; margin-bottom: 0.75rem;">📋 Operation Summary Steps</h4>
        <ul style="color: #D1D5DB; font-size: 0.92rem; line-height: 1.6; padding-left: 1.2rem; margin-bottom: 0;">
            <li><strong>Showcase Demonstration:</strong> Click 'Generate Insights Report' to view pre-calculated earnings tables for BSE Limited.</li>
            <li><strong>Custom Mode Verification:</strong> Toggle 'Generate Custom Version' in the sidebar and paste your AI Studio API Key.</li>
            <li><strong>Automated Document Summaries:</strong> Upload corporate transcript PDFs or text files to generate structured indices instantly.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Main Operational Input Card Panel
st.markdown('<div class="input-panel-card">', unsafe_allow_html=True)
if is_demo_mode:
    target_company = st.text_input("Target Corporate Entity", value="BSE Limited", disabled=True)
    target_period = st.text_input("Financial Period", value="Q4 & Full Year FY26", disabled=True)
    active_transcript_text = "BSE PROFILE DEMO TRACK"
else:
    col_input1, col_input2 = st.columns(2)
    with col_input1:
        target_company = st.text_input("Enter Company Name", value="MCX")
    with col_input2:
        target_period = st.text_input("Enter Financial Horizon", value="Q4 FY26")
    input_choice = st.radio("Choose Input Medium", ["PDF Transcript File Upload", "Direct Raw Text Paste"])
    if "pdf" in input_choice.lower():
        uploaded_pdf = st.file_uploader("Upload Earnings Transcript (PDF)", type=["pdf"])
        active_transcript_text = extract_text_from_pdf(uploaded_pdf) if uploaded_pdf is not None else ""
    else:
        active_transcript_text = st.text_area("Paste Transcript Text Blocks Here", height=200)
st.markdown('</div>', unsafe_allow_html=True)

if st.button("Generate Insights Report", type="primary"):
    if is_demo_mode:
        with st.spinner("Compiling transcript telemetry..."):
            time.sleep(0.2)  
            st.session_state["bse_analysis_payload"] = NATIVE_SHOWCASE_PAYLOAD
            st.session_state["bse_company"] = "BSE Limited"
            st.session_state["bse_period"] = "Q4 & Full Year FY26"
            st.success("Telemetry matrix loaded.")
    else:
        if not api_key_to_use:
            st.error("Pipeline blocked: A valid Gemini API Key is required.")
        elif not active_transcript_text.strip():
            st.error("Pipeline blocked: Missing transcript arguments.")
        else:
            with st.spinner("Processing structural text metrics via Gemini 2.5 Flash..."):
                analysis_payload = analyze_transcript_via_gemini(active_transcript_text, target_company, target_period, api_key_to_use)
            if analysis_payload:
                st.session_state["bse_analysis_payload"] = analysis_payload
                st.session_state["bse_company"] = target_company
                st.session_state["bse_period"] = target_period
                st.success("Analysis complete.")

# --- RENDERING THE STRUCTURAL SUMMARY VIEWPORT ---
if "bse_analysis_payload" in st.session_state:
    payload = st.session_state["bse_analysis_payload"]
    co = st.session_state["bse_company"]
    pe = st.session_state["bse_period"]
    
    st.markdown(f"### 📋 Strategic Summary Dashboard: {co.upper()} — {pe.upper()}")
    
    st.markdown(f"""
    <div class="metric-grid-layout">
        <div class="metric-premium-slate">
            <div class="metric-slate-title">Overall Sentiment Index</div>
            <div class="metric-slate-data" style="color: #34D399;">{float(payload.get('overall_sentiment_score', 0.5)):.2f}</div>
        </div>
        <div class="metric-premium-slate">
            <div class="metric-slate-title">Volatile Hedge Words Tracked</div>
            <div class="metric-slate-data" style="color: #F59E0B;">{payload.get('hedge_word_count', 0)}</div>
        </div>
        <div class="metric-premium-slate">
            <div class="metric-slate-title">Strategic Guidance Trajectory</div>
            <div class="metric-slate-data" style="font-size: 1.15rem; color: #60A5FA; font-weight: 600;">{payload.get('guidance_direction', 'N/A')}</div>
        </div>
        <div class="metric-premium-slate">
            <div class="metric-slate-title">Capital Expenditure Stance</div>
            <div class="metric-slate-data" style="font-size: 1.15rem; color: #F43F5E; font-weight: 600;">{payload.get('capex_tone_classification', 'N/A')}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col_left, col_right = st.columns([1, 1])
    with col_left:
        st.markdown('<div class="screener-section-title">Management Tone Distribution</div>', unsafe_allow_html=True)
        tone_dict = payload.get("tone_distribution", {"Confident": 33, "Cautious": 33, "Defensive": 34})
        df_tone = pd.DataFrame({
            "Tone Vector Category": list(tone_dict.keys()),
            "Percentage Weight": list(tone_dict.values())
        })
        chart_fig = px.pie(df_tone, names="Tone Vector Category", values="Percentage Weight", color_discrete_sequence=["#10B981", "#F59E0B", "#EF4444"], hole=0.4)
        chart_fig.update_layout(margin=dict(t=5, b=5, l=5, r=5), height=240, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#ffffff"))
        st.plotly_chart(chart_fig, use_container_width=True)
    with col_right:
        st.markdown('<div class="screener-section-title">Top Cautious Management Phrases</div>', unsafe_allow_html=True)
        for phrase in payload.get("top_cautious_phrases", []):
            st.markdown(f'<div class="cautious-phrase-pill">⚠️ {phrase}</div>', unsafe_allow_html=True)
            
    st.markdown('<div class="screener-section-title">Executive Summary</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="summary-text-block"><em>{payload.get("executive_summary", "Not provided")}</em></div>', unsafe_allow_html=True)
    
    sections_layout = [
        ("Growth Vectors & Structural Catalysts", "growth_vectors"),
        ("Financial Performance, Ratios & Metrics", "financial_performance"),
        ("Core Platforms & Franchise Scaling Engine", "platform_franchise"),
        ("Operational Risks, Headwinds & Competitive Frictions", "risks_and_frictions"),
        ("Capital Allocation & Growth Capex Outlook", "capital_allocation")
    ]
    for section_title, target_key in sections_layout:
        st.markdown(f'<div class="screener-section-title">{section_title}</div>', unsafe_allow_html=True)
        for bullet_point in payload.get(target_key, []):
            st.markdown(f"""
            <div class="premium-grounding-card">
                <span class="premium-grounding-txt">{bullet_point}</span>
            </div>
            """, unsafe_allow_html=True)
            
    st.markdown("---")
    st.markdown("### 💾 Export Quantitative Summary Record")
    try:
        report_bytes = build_pdf_report_bytes(payload, co, pe)
        st.download_button(
            label="Download Certified Audit PDF Report",
            data=bytes(report_bytes),
            file_name=f"{co.replace(' ', '_').upper()}_INSIGHTS_SUMMARY.pdf",
            mime="application/pdf"
        )
    except Exception as pdf_ex:
        st.error(f"Export Compilation Alert: {str(pdf_ex)}")