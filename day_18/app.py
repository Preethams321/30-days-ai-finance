import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
import re

# ─── PAGE CONFIG ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DealScout — M&A Target Screener",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── CONSTANTS ────────────────────────────────────────────────────────────────
SECTOR_MA_MULTIPLES = {
    "IT Services":       {"median_ev_ebitda": 12.8, "control_premium": 0.30},
    "Pharma/Healthcare": {"median_ev_ebitda": 12.5, "control_premium": 0.32},
    "FMCG/Consumer":     {"median_ev_ebitda": 8.3,  "control_premium": 0.28},
    "Auto/Auto Anc":     {"median_ev_ebitda": 9.0,  "control_premium": 0.25},
    "Industrials/Mfg":   {"median_ev_ebitda": 6.5,  "control_premium": 0.25},
}
GLOBAL_MEDIAN_MA_MULTIPLE = 9.3
PE_BUYER_MULTIPLE         = 10.1
CORPORATE_BUYER_MULTIPLE  = 8.6

# ─── DEMO UNIVERSE ───────────────────────────────────────────────────────────
# ev_ebitda = (market_cap_cr + net_debt_cr) / ebitda_cr — all internally consistent.
# shares_cr * current_price ≈ market_cap_cr. debt_ebitda * ebitda_cr >= net_debt_cr (cash >= 0).
DEMO_COMPANIES = [
    # IT Services — sector median 12.8x
    {"name": "Meridian IT Solutions",   "sector": "IT Services",       "market_cap_cr": 8500,  "ebitda_cr": 720,  "ev_ebitda": 12.2, "revenue_growth_pct": 18.5, "ebitda_margin_pct": 22.0, "debt_ebitda": 0.5, "promoter_holding_pct": 38, "net_debt_cr": 290,  "shares_cr": 12.5, "current_price": 680, "fcf_positive": True,  "roce_pct": 24.5},
    {"name": "Optima Digital Services", "sector": "IT Services",       "market_cap_cr": 3200,  "ebitda_cr": 310,  "ev_ebitda": 10.1, "revenue_growth_pct": 22.0, "ebitda_margin_pct": 19.5, "debt_ebitda": 0.2, "promoter_holding_pct": 52, "net_debt_cr": -80,  "shares_cr": 8.0,  "current_price": 400, "fcf_positive": True,  "roce_pct": 21.0},
    {"name": "Synapse Tech Infra",      "sector": "IT Services",       "market_cap_cr": 18500, "ebitda_cr": 1450, "ev_ebitda": 12.5, "revenue_growth_pct": 14.0, "ebitda_margin_pct": 28.5, "debt_ebitda": 0.1, "promoter_holding_pct": 71, "net_debt_cr": -320, "shares_cr": 25.0, "current_price": 740, "fcf_positive": True,  "roce_pct": 32.0},
    {"name": "Vertex Software Labs",    "sector": "IT Services",       "market_cap_cr": 1800,  "ebitda_cr": 95,   "ev_ebitda": 20.7, "revenue_growth_pct": 38.0, "ebitda_margin_pct": 12.0, "debt_ebitda": 1.8, "promoter_holding_pct": 29, "net_debt_cr": 170,  "shares_cr": 6.0,  "current_price": 300, "fcf_positive": False, "roce_pct": 14.0},
    {"name": "Arcadia Cloud Systems",   "sector": "IT Services",       "market_cap_cr": 4600,  "ebitda_cr": 420,  "ev_ebitda": 11.9, "revenue_growth_pct": 16.0, "ebitda_margin_pct": 21.0, "debt_ebitda": 1.0, "promoter_holding_pct": 45, "net_debt_cr": 380,  "shares_cr": 10.0, "current_price": 460, "fcf_positive": True,  "roce_pct": 19.5},
    {"name": "Orbis Data Analytics",    "sector": "IT Services",       "market_cap_cr": 920,   "ebitda_cr": 68,   "ev_ebitda": 15.9, "revenue_growth_pct": 28.5, "ebitda_margin_pct": 15.5, "debt_ebitda": 2.4, "promoter_holding_pct": 34, "net_debt_cr": 163,  "shares_cr": 4.0,  "current_price": 230, "fcf_positive": False, "roce_pct": 12.5},
    # Pharma/Healthcare — sector median 12.5x
    {"name": "Bharat Pharma Labs",      "sector": "Pharma/Healthcare", "market_cap_cr": 12000, "ebitda_cr": 980,  "ev_ebitda": 12.7, "revenue_growth_pct": 15.0, "ebitda_margin_pct": 26.0, "debt_ebitda": 0.5, "promoter_holding_pct": 55, "net_debt_cr": 490,  "shares_cr": 18.0, "current_price": 667, "fcf_positive": True,  "roce_pct": 22.0},
    {"name": "Velox Life Sciences",     "sector": "Pharma/Healthcare", "market_cap_cr": 5400,  "ebitda_cr": 390,  "ev_ebitda": 15.0, "revenue_growth_pct": 19.5, "ebitda_margin_pct": 20.5, "debt_ebitda": 1.2, "promoter_holding_pct": 41, "net_debt_cr": 468,  "shares_cr": 9.0,  "current_price": 600, "fcf_positive": True,  "roce_pct": 18.5},
    {"name": "Pristine Generics Ltd",   "sector": "Pharma/Healthcare", "market_cap_cr": 1200,  "ebitda_cr": 180,  "ev_ebitda": 9.9,  "revenue_growth_pct": 9.0,  "ebitda_margin_pct": 16.0, "debt_ebitda": 3.2, "promoter_holding_pct": 62, "net_debt_cr": 576,  "shares_cr": 7.0,  "current_price": 171, "fcf_positive": False, "roce_pct": 10.5},
    {"name": "Novagen Biotech",         "sector": "Pharma/Healthcare", "market_cap_cr": 8800,  "ebitda_cr": 520,  "ev_ebitda": 16.6, "revenue_growth_pct": 32.0, "ebitda_margin_pct": 24.0, "debt_ebitda": 0.3, "promoter_holding_pct": 47, "net_debt_cr": -155, "shares_cr": 14.0, "current_price": 629, "fcf_positive": True,  "roce_pct": 28.0},
    {"name": "Aether Diagnostics",      "sector": "Pharma/Healthcare", "market_cap_cr": 1650,  "ebitda_cr": 155,  "ev_ebitda": 10.3, "revenue_growth_pct": 25.0, "ebitda_margin_pct": 30.0, "debt_ebitda": 0.0, "promoter_holding_pct": 36, "net_debt_cr": -60,  "shares_cr": 5.5,  "current_price": 300, "fcf_positive": True,  "roce_pct": 35.0},
    {"name": "Solus Specialty Pharma",  "sector": "Pharma/Healthcare", "market_cap_cr": 3900,  "ebitda_cr": 290,  "ev_ebitda": 14.2, "revenue_growth_pct": 12.5, "ebitda_margin_pct": 22.5, "debt_ebitda": 0.8, "promoter_holding_pct": 68, "net_debt_cr": 232,  "shares_cr": 8.5,  "current_price": 459, "fcf_positive": True,  "roce_pct": 20.0},
    # FMCG/Consumer — sector median 8.3x
    {"name": "Sunrise Consumer Goods",  "sector": "FMCG/Consumer",     "market_cap_cr": 22000, "ebitda_cr": 2100, "ev_ebitda": 10.3, "revenue_growth_pct": 10.0, "ebitda_margin_pct": 24.0, "debt_ebitda": 0.2, "promoter_holding_pct": 72, "net_debt_cr": -420, "shares_cr": 35.0, "current_price": 629, "fcf_positive": True,  "roce_pct": 38.0},
    {"name": "Horizon Foods Ltd",       "sector": "FMCG/Consumer",     "market_cap_cr": 7200,  "ebitda_cr": 760,  "ev_ebitda": 9.9,  "revenue_growth_pct": 14.0, "ebitda_margin_pct": 20.5, "debt_ebitda": 0.4, "promoter_holding_pct": 43, "net_debt_cr": 304,  "shares_cr": 15.0, "current_price": 480, "fcf_positive": True,  "roce_pct": 29.0},
    {"name": "Kiran Naturals",          "sector": "FMCG/Consumer",     "market_cap_cr": 1500,  "ebitda_cr": 240,  "ev_ebitda": 8.1,  "revenue_growth_pct": 8.5,  "ebitda_margin_pct": 14.5, "debt_ebitda": 1.8, "promoter_holding_pct": 57, "net_debt_cr": 432,  "shares_cr": 8.0,  "current_price": 188, "fcf_positive": False, "roce_pct": 11.5},
    {"name": "Vedanta Beverages",       "sector": "FMCG/Consumer",     "market_cap_cr": 4500,  "ebitda_cr": 420,  "ev_ebitda": 11.4, "revenue_growth_pct": 18.0, "ebitda_margin_pct": 19.0, "debt_ebitda": 0.7, "promoter_holding_pct": 38, "net_debt_cr": 294,  "shares_cr": 10.0, "current_price": 450, "fcf_positive": True,  "roce_pct": 22.5},
    {"name": "Primus Home Care",        "sector": "FMCG/Consumer",     "market_cap_cr": 450,   "ebitda_cr": 105,  "ev_ebitda": 7.1,  "revenue_growth_pct": 6.5,  "ebitda_margin_pct": 11.0, "debt_ebitda": 2.8, "promoter_holding_pct": 33, "net_debt_cr": 294,  "shares_cr": 5.0,  "current_price": 90,  "fcf_positive": False, "roce_pct": 8.5},
    {"name": "Celestia Retail Brands",  "sector": "FMCG/Consumer",     "market_cap_cr": 9800,  "ebitda_cr": 870,  "ev_ebitda": 11.2, "revenue_growth_pct": 22.5, "ebitda_margin_pct": 22.0, "debt_ebitda": 0.1, "promoter_holding_pct": 31, "net_debt_cr": -87,  "shares_cr": 20.0, "current_price": 490, "fcf_positive": True,  "roce_pct": 31.0},
    # Auto/Auto Anc — sector median 9.0x
    {"name": "Indus Auto Components",   "sector": "Auto/Auto Anc",     "market_cap_cr": 5600,  "ebitda_cr": 560,  "ev_ebitda": 11.1, "revenue_growth_pct": 16.0, "ebitda_margin_pct": 17.5, "debt_ebitda": 1.1, "promoter_holding_pct": 48, "net_debt_cr": 616,  "shares_cr": 12.0, "current_price": 467, "fcf_positive": True,  "roce_pct": 18.0},
    {"name": "Apex Transmission Works", "sector": "Auto/Auto Anc",     "market_cap_cr": 1260,  "ebitda_cr": 210,  "ev_ebitda": 8.0,  "revenue_growth_pct": 11.5, "ebitda_margin_pct": 14.0, "debt_ebitda": 2.0, "promoter_holding_pct": 60, "net_debt_cr": 420,  "shares_cr": 7.5,  "current_price": 168, "fcf_positive": False, "roce_pct": 13.0},
    {"name": "Titan EV Systems",        "sector": "Auto/Auto Anc",     "market_cap_cr": 4100,  "ebitda_cr": 285,  "ev_ebitda": 14.9, "revenue_growth_pct": 42.0, "ebitda_margin_pct": 13.5, "debt_ebitda": 0.5, "promoter_holding_pct": 35, "net_debt_cr": 143,  "shares_cr": 10.0, "current_price": 410, "fcf_positive": False, "roce_pct": 15.5},
    {"name": "Durga Castings Ltd",      "sector": "Auto/Auto Anc",     "market_cap_cr": 1200,  "ebitda_cr": 145,  "ev_ebitda": 9.8,  "revenue_growth_pct": 7.0,  "ebitda_margin_pct": 16.5, "debt_ebitda": 1.5, "promoter_holding_pct": 55, "net_debt_cr": 218,  "shares_cr": 5.0,  "current_price": 240, "fcf_positive": True,  "roce_pct": 16.5},
    {"name": "Calibre Auto Tech",       "sector": "Auto/Auto Anc",     "market_cap_cr": 7800,  "ebitda_cr": 720,  "ev_ebitda": 10.5, "revenue_growth_pct": 18.5, "ebitda_margin_pct": 20.0, "debt_ebitda": 0.3, "promoter_holding_pct": 42, "net_debt_cr": -216, "shares_cr": 16.0, "current_price": 488, "fcf_positive": True,  "roce_pct": 25.0},
    {"name": "Pinnacle Tyres & Rubber", "sector": "Auto/Auto Anc",     "market_cap_cr": 3400,  "ebitda_cr": 310,  "ev_ebitda": 12.9, "revenue_growth_pct": 9.0,  "ebitda_margin_pct": 15.0, "debt_ebitda": 1.9, "promoter_holding_pct": 64, "net_debt_cr": 589,  "shares_cr": 9.0,  "current_price": 378, "fcf_positive": False, "roce_pct": 12.0},
    # Industrials/Mfg — sector median 6.5x
    {"name": "Ferrum Steel Products",   "sector": "Industrials/Mfg",   "market_cap_cr": 4200,  "ebitda_cr": 620,  "ev_ebitda": 8.2,  "revenue_growth_pct": 12.0, "ebitda_margin_pct": 18.0, "debt_ebitda": 1.4, "promoter_holding_pct": 50, "net_debt_cr": 868,  "shares_cr": 11.0, "current_price": 382, "fcf_positive": True,  "roce_pct": 17.0},
    {"name": "Atlas Industrial Pumps",  "sector": "Industrials/Mfg",   "market_cap_cr": 2600,  "ebitda_cr": 330,  "ev_ebitda": 8.5,  "revenue_growth_pct": 15.5, "ebitda_margin_pct": 21.0, "debt_ebitda": 0.6, "promoter_holding_pct": 37, "net_debt_cr": 198,  "shares_cr": 8.0,  "current_price": 325, "fcf_positive": True,  "roce_pct": 23.0},
    {"name": "Solaris Power Equipment", "sector": "Industrials/Mfg",   "market_cap_cr": 6800,  "ebitda_cr": 580,  "ev_ebitda": 12.5, "revenue_growth_pct": 28.0, "ebitda_margin_pct": 16.5, "debt_ebitda": 0.8, "promoter_holding_pct": 44, "net_debt_cr": 464,  "shares_cr": 15.0, "current_price": 453, "fcf_positive": True,  "roce_pct": 19.5},
    {"name": "Granite Infra Castings",  "sector": "Industrials/Mfg",   "market_cap_cr": 310,   "ebitda_cr": 105,  "ev_ebitda": 6.8,  "revenue_growth_pct": 6.0,  "ebitda_margin_pct": 12.5, "debt_ebitda": 3.8, "promoter_holding_pct": 66, "net_debt_cr": 399,  "shares_cr": 4.5,  "current_price": 69,  "fcf_positive": False, "roce_pct": 8.0},
    {"name": "Vanguard Chemicals Ltd",  "sector": "Industrials/Mfg",   "market_cap_cr": 3500,  "ebitda_cr": 400,  "ev_ebitda": 9.8,  "revenue_growth_pct": 10.0, "ebitda_margin_pct": 20.5, "debt_ebitda": 1.0, "promoter_holding_pct": 40, "net_debt_cr": 400,  "shares_cr": 10.0, "current_price": 350, "fcf_positive": True,  "roce_pct": 20.5},
    {"name": "Zenith Precision Mfg",    "sector": "Industrials/Mfg",   "market_cap_cr": 1550,  "ebitda_cr": 185,  "ev_ebitda": 9.3,  "revenue_growth_pct": 20.5, "ebitda_margin_pct": 17.0, "debt_ebitda": 0.9, "promoter_holding_pct": 30, "net_debt_cr": 166,  "shares_cr": 6.0,  "current_price": 258, "fcf_positive": True,  "roce_pct": 21.0},
]

# ─── SCORING FUNCTIONS ────────────────────────────────────────────────────────
def rule_of_40(company):
    return company["revenue_growth_pct"] + company["ebitda_margin_pct"]

def deal_fit_score(company):
    score = 0
    sec_med = SECTOR_MA_MULTIPLES[company["sector"]]["median_ev_ebitda"]
    if company["ev_ebitda"] < sec_med * 0.8:   score += 25
    elif company["ev_ebitda"] < sec_med:        score += 15
    else:                                        score += 5

    r40 = rule_of_40(company)
    if r40 > 50:   score += 25
    elif r40 > 40: score += 18
    elif r40 > 30: score += 10
    else:          score += 3

    if company["debt_ebitda"] < 1.0:   score += 20
    elif company["debt_ebitda"] < 2.5: score += 12
    else:                               score += 4

    if company["promoter_holding_pct"] < 40:   score += 15
    elif company["promoter_holding_pct"] < 55: score += 10
    else:                                       score += 3

    if company.get("fcf_positive", True): score += 15
    else:                                  score += 3

    return min(score, 100)

def implied_takeout(company):
    sector     = SECTOR_MA_MULTIPLES[company["sector"]]
    current_ev = company["ebitda_cr"] * company["ev_ebitda"]
    takeout_ev = company["ebitda_cr"] * sector["median_ev_ebitda"] * (1 + sector["control_premium"])
    prem_pct   = (takeout_ev / current_ev - 1) * 100
    imp_price  = (takeout_ev - company["net_debt_cr"]) / company["shares_cr"]
    upside     = (imp_price / company["current_price"] - 1) * 100
    return {
        "current_ev":    current_ev,
        "takeout_ev":    takeout_ev,
        "premium_pct":   prem_pct,
        "implied_price": imp_price,
        "upside_pct":    upside,
        "pe_ev":         company["ebitda_cr"] * PE_BUYER_MULTIPLE,
        "strategic_ev":  company["ebitda_cr"] * CORPORATE_BUYER_MULTIPLE,
    }

def get_size_band(mcap):
    if mcap < 5000:    return "Small"
    elif mcap < 40000: return "Mid"
    else:              return "Large"

def screen_companies(df, sector, max_ev, min_growth, min_margin,
                     max_debt, size_bands, min_promoter, r40_only):
    f = df.copy()
    if sector != "All":            f = f[f["sector"] == sector]
    f = f[f["ev_ebitda"]           <= max_ev]
    f = f[f["revenue_growth_pct"]  >= min_growth]
    f = f[f["ebitda_margin_pct"]   >= min_margin]
    f = f[f["debt_ebitda"]         <= max_debt]
    f = f[f["promoter_holding_pct"] >= min_promoter]
    if size_bands:                 f = f[f["size_band"].isin(size_bands)]
    if r40_only:                   f = f[f["rule_of_40"] >= 40]
    return f

def get_deal_rationale(company):
    r40     = rule_of_40(company)
    sec_med = SECTOR_MA_MULTIPLES[company["sector"]]["median_ev_ebitda"]
    disc    = ((sec_med - company["ev_ebitda"]) / sec_med) * 100
    t       = implied_takeout(company)

    if company["ev_ebitda"] < sec_med and r40 > 40:
        quality, hook = "premium-quality", f"trading at a {abs(disc):.0f}% discount to sector peers despite strong fundamentals"
    elif company["ev_ebitda"] < sec_med:
        quality, hook = "value", f"cheap at {company['ev_ebitda']}x EV/EBITDA vs sector median {sec_med}x"
    elif r40 > 50:
        quality, hook = "high-growth", f"Rule of 40 score of {r40:.0f} places it among the highest-quality targets in its sector"
    else:
        quality, hook = "strategic", "operationally sound with a clear strategic angle for the right buyer"

    debt_note  = "nearly debt-free balance sheet makes it easy to lever up" if company["debt_ebitda"] < 1.0 else f"manageable leverage at {company['debt_ebitda']}x Debt/EBITDA"
    prom_note  = "low promoter holding makes a hostile or negotiated acquisition structurally straightforward" if company["promoter_holding_pct"] < 45 else f"promoter concentration at {company['promoter_holding_pct']}% means deal needs promoter buy-in — risk of deal drag"
    fcf_note   = "FCF-positive, meaning the acquisition is partially self-funding from day one" if company.get("fcf_positive") else "FCF-negative currently — buyer takes execution risk on margin improvement"
    plain      = "This one is cheap for its quality. A buyer gets a fast-growing, profitable business below what the sector usually sells for." if disc > 5 and r40 > 35 else "Strong operational profile. The numbers support a premium, and the structure makes the deal executable."
    closer     = "Low debt and low promoter holding are rare together — a PE firm could walk in, lever it up, and have a clear exit path." if company["debt_ebitda"] < 1.5 and company["promoter_holding_pct"] < 50 else "Getting promoter alignment will be the work, but the underlying business justifies the effort."

    return (f"**Technical:** {company['name']} is a {quality} target — {hook}. "
            f"Rule of 40 score of {r40:.0f} ({company['revenue_growth_pct']}% growth + {company['ebitda_margin_pct']}% margin). "
            f"{debt_note.capitalize()}; {prom_note}. {fcf_note}. "
            f"Implied takeout at ₹{t['implied_price']:.0f}/share represents {t['upside_pct']:.0f}% upside to current price.\n\n"
            f"**Plain English:** {plain} {closer}")

# ─── AI PROVIDER ──────────────────────────────────────────────────────────────
def call_ai_provider(thesis_text, sector, provider, api_key):
    prompt = f"""Search for Indian listed companies matching this M&A acquisition thesis:
"{thesis_text}"
Sector focus: {sector if sector != "All" else "Any sector"}

Find 5-8 real Indian listed companies that would be attractive acquisition targets.

Return ONLY raw JSON, no markdown, no backticks, no preamble:
{{
  "targets": [
    {{
      "name": "company name",
      "ticker": "NSE ticker",
      "sector": "one of: IT Services, Pharma/Healthcare, FMCG/Consumer, Auto/Auto Anc, Industrials/Mfg",
      "market_cap_cr": 0,
      "ebitda_cr": 0,
      "ev_ebitda": 0.0,
      "revenue_growth_pct": 0.0,
      "ebitda_margin_pct": 0.0,
      "debt_ebitda": 0.0,
      "promoter_holding_pct": 0.0,
      "net_debt_cr": 0,
      "shares_cr": 0.0,
      "current_price": 0.0,
      "roce_pct": 0.0,
      "fcf_positive": true,
      "deal_rationale": "2-3 sentence rationale: why attractive target, what buyer gets, key risk",
      "likely_buyer_type": "Strategic or Financial (PE)"
    }}
  ],
  "thesis_summary": "1-2 sentence summary of screening logic applied",
  "data_sources": ["source1"]
}}
All figures in INR Crores. Return only real, verified data."""

    import requests

    if provider == "Gemini 2.0 Flash (Google)":
        import google.genai as genai
        from google.genai import types as gtypes
        client   = genai.Client(api_key=api_key)
        config   = gtypes.GenerateContentConfig(
            tools=[gtypes.Tool(google_search=gtypes.GoogleSearch())],
        )
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=config,
        )
        raw = response.text
    elif provider == "Groq":
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "max_tokens": 3000},
            timeout=30,
        )
        r.raise_for_status()
        raw = r.json()["choices"][0]["message"]["content"]
    elif provider == "OpenAI":
        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}], "max_tokens": 3000},
            timeout=30,
        )
        r.raise_for_status()
        raw = r.json()["choices"][0]["message"]["content"]
    elif provider == "Anthropic":
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": api_key, "anthropic-version": "2023-06-01", "Content-Type": "application/json"},
            json={"model": "claude-3-5-haiku-20241022", "max_tokens": 3000, "messages": [{"role": "user", "content": prompt}]},
            timeout=30,
        )
        r.raise_for_status()
        raw = r.json()["content"][0]["text"]
    else:  # DeepSeek
        r = requests.post(
            "https://api.deepseek.com/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}], "max_tokens": 3000},
            timeout=30,
        )
        r.raise_for_status()
        raw = r.json()["choices"][0]["message"]["content"]

    clean = re.sub(r"```json|```", "", raw).strip()
    return json.loads(clean)

# ─── CSS — forced dark, covers every Streamlit element ───────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400;1,600&family=Syne:wght@400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

html, body,
[data-testid="stApp"], [data-testid="stAppViewContainer"],
[data-testid="stMain"], [data-testid="stBottom"],
.main, .block-container,
section[data-testid="stSidebar"],
[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"] {
    background-color: #09090e !important;
    color: #e8e4dc !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"]    { background: #111118 !important; border-bottom: 1px solid #222230; gap: 0; }
.stTabs [data-baseweb="tab"]         { background: transparent !important; color: #666666 !important; font-family: 'Syne', sans-serif; font-size: 0.8rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; padding: 12px 20px; border: none !important; border-bottom: 2px solid transparent !important; }
.stTabs [aria-selected="true"]       { background: transparent !important; color: #c9a96e !important; border-bottom: 2px solid #c9a96e !important; }
.stTabs [data-baseweb="tab-panel"]   { background: #09090e !important; padding: 0 !important; }

/* Inputs */
.stSelectbox [data-baseweb="select"] > div,
.stMultiSelect [data-baseweb="select"] > div { background-color: #111118 !important; border-color: #222230 !important; color: #e8e4dc !important; }
[data-baseweb="menu"], [data-baseweb="popover"], [role="listbox"], [role="option"] { background-color: #111118 !important; color: #e8e4dc !important; }
[role="option"]:hover, [data-baseweb="menu"] li:hover { background-color: #1e1e2e !important; }
.stTextArea textarea, .stTextInput input, input[type="text"], input[type="password"], input[type="number"] { background-color: #111118 !important; border-color: #222230 !important; color: #e8e4dc !important; caret-color: #c9a96e; }
.stTextArea textarea:focus, .stTextInput input:focus { border-color: #c9a96e !important; box-shadow: 0 0 0 1px rgba(201,169,110,0.2) !important; }

/* Slider */
[data-testid="stSlider"] [role="slider"]    { background-color: #c9a96e !important; border-color: #c9a96e !important; }
[data-testid="stSlider"] > div > div > div  { background-color: #c9a96e !important; }

/* Radio & Checkbox */
[data-testid="stRadio"] label, [data-testid="stCheckbox"] label { color: #b0ac9f !important; font-family: 'Syne', sans-serif !important; }
[data-testid="stRadio"] [data-baseweb="radio"] div,
[data-testid="stCheckbox"] [data-baseweb="checkbox"] div { border-color: #444 !important; background-color: #111118 !important; }

/* Buttons */
.stButton > button { background-color: #c9a96e !important; color: #09090e !important; font-family: 'Syne', sans-serif !important; font-weight: 700 !important; letter-spacing: 0.06em !important; border: none !important; border-radius: 4px !important; padding: 10px 24px !important; transition: background 0.15s ease !important; }
.stButton > button:hover  { background-color: #dbbe85 !important; color: #09090e !important; }
.stButton > button:active { background-color: #b8944e !important; }

/* Expander */
div[data-testid="stExpander"]                          { background-color: #111118 !important; border: 1px solid #222230 !important; border-radius: 6px !important; }
div[data-testid="stExpander"] > details > summary      { color: #e8e4dc !important; font-family: 'Syne', sans-serif !important; }
div[data-testid="stExpander"] > details > summary:hover { color: #c9a96e !important; }
div[data-testid="stExpander"] > details[open] > summary { color: #c9a96e !important; }

/* DataFrame */
[data-testid="stDataFrame"], .stDataFrame { background-color: #111118 !important; border: 1px solid #222230 !important; border-radius: 6px !important; }

/* Multiselect tags */
[data-baseweb="tag"] { background-color: rgba(201,169,110,0.15) !important; color: #c9a96e !important; border: 1px solid rgba(201,169,110,0.3) !important; }

/* Info / alert */
[data-testid="stAlert"], [data-baseweb="notification"] { background-color: #111118 !important; color: #e8e4dc !important; border-color: #222230 !important; }

/* Spinner */
[data-testid="stSpinner"] > div { border-top-color: #c9a96e !important; }

/* General */
label { color: #b0ac9f !important; }
h1, h2, h3, h4 { color: #e8e4dc !important; font-family: 'Playfair Display', serif !important; }

/* Scrollbar */
::-webkit-scrollbar       { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #09090e; }
::-webkit-scrollbar-thumb { background: #222230; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #333344; }

/* ── Custom component classes ── */
.hero-section  { padding: 56px 0 32px 0; border-bottom: 1px solid #222230; margin-bottom: 32px; }
.hero-wordmark {
    font-family: 'Syne', sans-serif;
    font-size: 0.95rem;
    font-weight: 700;
    color: #c9a96e;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    margin-bottom: 16px;
    display: inline-block;
    border: 1px solid rgba(201,169,110,0.3);
    padding: 4px 12px;
    border-radius: 3px;
}
.hero-eyebrow  { font-family: 'DM Mono', monospace; font-size: 0.72rem; letter-spacing: 0.18em; color: #4ab87a; margin-bottom: 14px; display: flex; align-items: center; gap: 8px; }
.live-dot      { width: 7px; height: 7px; background: #4ab87a; border-radius: 50%; display: inline-block; animation: pulse 2s ease-in-out infinite; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.25; } }
.hero-title    { font-family: 'Playfair Display', serif; font-size: clamp(3.2rem, 6.5vw, 5.6rem); font-weight: 700; line-height: 1.04; color: #e8e4dc; margin-bottom: 20px; margin-top: 4px; }
.hero-title em { font-style: italic; color: #c9a96e; }
.hero-sub      { font-family: 'Syne', sans-serif; font-size: 1.0rem; color: #b0ac9f; max-width: 560px; line-height: 1.7; margin-bottom: 36px; }
.stats-strip   { display: flex; gap: 40px; flex-wrap: wrap; margin-bottom: 28px; padding: 20px 0; border-top: 1px solid #222230; border-bottom: 1px solid #222230; }
.stat-num      { font-family: 'DM Mono', monospace; font-size: 1.7rem; font-weight: 500; color: #c9a96e; display: block; }
.stat-label    { font-family: 'Syne', sans-serif; font-size: 0.72rem; letter-spacing: 0.1em; text-transform: uppercase; color: #666666; }
.pill-row      { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 36px; }
.pill          { background: #111118; border: 1px solid #222230; color: #b0ac9f; font-family: 'Syne', sans-serif; font-size: 0.75rem; font-weight: 600; letter-spacing: 0.06em; padding: 6px 14px; border-radius: 20px; }
.feature-grid  { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 36px; }
@media (max-width: 768px) { .feature-grid { grid-template-columns: 1fr 1fr; } }
@media (max-width: 480px) { .feature-grid { grid-template-columns: 1fr; } .stats-strip { gap: 20px; } }
.feature-card       { background: #111118; border: 1px solid #222230; border-radius: 8px; padding: 20px; }
.feature-card-icon  { font-size: 1.4rem; margin-bottom: 10px; display: block; }
.feature-card-title { font-family: 'Playfair Display', serif; font-size: 1.0rem; font-weight: 600; color: #e8e4dc; margin-bottom: 6px; }
.feature-card-desc  { font-family: 'Syne', sans-serif; font-size: 0.8rem; color: #666666; line-height: 1.5; }
.card          { background: #111118; border: 1px solid #222230; border-radius: 8px; padding: 20px 24px; margin-bottom: 16px; }
.metric-label  { font-family: 'DM Mono', monospace; font-size: 0.7rem; letter-spacing: 0.1em; text-transform: uppercase; color: #666666; }
.metric-value  { font-family: 'DM Mono', monospace; font-size: 1.35rem; color: #c9a96e; font-weight: 500; }
.metric-value.green { color: #4ab87a !important; }
.metric-value.red   { color: #e05c6c !important; }
.disclaimer    { background: rgba(201,169,110,0.06); border: 1px solid rgba(201,169,110,0.2); border-radius: 6px; padding: 12px 16px; font-family: 'DM Mono', monospace; font-size: 0.72rem; color: #888; margin-bottom: 20px; }
.section-label { font-family: 'DM Mono', monospace; font-size: 0.7rem; letter-spacing: 0.14em; text-transform: uppercase; color: #3a5a7a; margin-bottom: 8px; }
.section-title { font-family: 'Playfair Display', serif; font-size: 1.45rem; font-weight: 600; color: #e8e4dc; margin-bottom: 4px; }
.footer-bar    { border-top: 1px solid #222230; padding: 20px 0; margin-top: 40px; font-family: 'DM Mono', monospace; font-size: 0.7rem; color: #444444; text-align: center; }
</style>
""", unsafe_allow_html=True)

# ─── SESSION STATE ────────────────────────────────────────────────────────────
for k, v in [("page", "home"), ("screen_results", None), ("selected_company", None), ("custom_results", None)]:
    if k not in st.session_state:
        st.session_state[k] = v

# ─── BUILD DATAFRAME ──────────────────────────────────────────────────────────
df_demo               = pd.DataFrame(DEMO_COMPANIES)
df_demo["rule_of_40"] = df_demo["revenue_growth_pct"] + df_demo["ebitda_margin_pct"]
df_demo["deal_fit"]   = df_demo.apply(deal_fit_score, axis=1)
df_demo["size_band"]  = df_demo["market_cap_cr"].apply(get_size_band)
df_demo["deal_rationale"] = df_demo.apply(lambda r: get_deal_rationale(r), axis=1)
df_demo = pd.concat([df_demo, df_demo.apply(lambda r: pd.Series(implied_takeout(r)), axis=1)], axis=1)

# ─── HOMEPAGE ────────────────────────────────────────────────────────────────
def render_homepage():
    st.markdown("""
    <div class="hero-section">
        <div class="hero-eyebrow"><span class="live-dot"></span>M&A SCREENER &nbsp;·&nbsp; DEAL FIT SCORE &nbsp;·&nbsp; IMPLIED TAKEOUT</div>
        <div class="hero-wordmark">Deal<em>Scout</em></div>
        <div class="hero-title">Find the <em>deal.</em></div>
        <div class="hero-sub">Screen Indian listed companies as M&A targets. Set a thesis, get deal fit scores, implied takeout values, and AI-generated rationale — in 30 seconds. Every PE associate builds this in Excel. You don't have to.</div>
        <div class="stats-strip">
            <div class="stat-item"><span class="stat-num">30</span><span class="stat-label">Demo Targets</span></div>
            <div class="stat-item"><span class="stat-num">5</span><span class="stat-label">Sectors</span></div>
            <div class="stat-item"><span class="stat-num">100</span><span class="stat-label">Deal Fit Score</span></div>
            <div class="stat-item"><span class="stat-num">AI</span><span class="stat-label">Custom Thesis</span></div>
        </div>
        <div class="pill-row">
            <span class="pill">Valuation Screen</span>
            <span class="pill">Rule of 40</span>
            <span class="pill">Implied Takeout</span>
            <span class="pill">Deal Rationale</span>
            <span class="pill">Control Premium</span>
            <span class="pill">Sector Benchmarks</span>
        </div>
        <div class="feature-grid">
            <div class="feature-card"><span class="feature-card-icon">🎯</span><div class="feature-card-title">Deal Fit Score</div><div class="feature-card-desc">Composite 0–100 score across valuation, quality, leverage, control, and cash flow.</div></div>
            <div class="feature-card"><span class="feature-card-icon">📊</span><div class="feature-card-title">Screener Filters</div><div class="feature-card-desc">EV/EBITDA ceiling, revenue growth floor, margin, debt, size band, and Rule of 40.</div></div>
            <div class="feature-card"><span class="feature-card-icon">💰</span><div class="feature-card-title">Implied Takeout</div><div class="feature-card-desc">What a PE or strategic buyer would likely pay, with control premium and per-share upside.</div></div>
            <div class="feature-card"><span class="feature-card-icon">🤖</span><div class="feature-card-title">AI Custom Thesis</div><div class="feature-card-desc">Describe an acquisition thesis in plain English. AI searches live and returns real Indian targets.</div></div>
            <div class="feature-card"><span class="feature-card-icon">🗺️</span><div class="feature-card-title">Value vs Quality Map</div><div class="feature-card-desc">Scatter of every target: EV/EBITDA vs Rule of 40, bubble-sized by market cap.</div></div>
            <div class="feature-card"><span class="feature-card-icon">📚</span><div class="feature-card-title">Sector Benchmarks</div><div class="feature-card-desc">Verified M&A multiples by sector. Why IT/Pharma command premiums. How Rule of 40 moves pricing.</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    col1, col2, _ = st.columns([1, 1, 3])
    with col1:
        if st.button("→ Launch Screener", use_container_width=True):
            st.session_state.page = "terminal"; st.rerun()
    with col2:
        if st.button("→ Custom AI Thesis", use_container_width=True):
            st.session_state.page = "terminal"; st.rerun()

# ─── SCREENER TAB ─────────────────────────────────────────────────────────────
def render_screener_tab():
    mode = st.radio("Mode", ["Demo Universe", "Custom AI Thesis"], horizontal=True, key="screener_mode")

    if mode == "Demo Universe":
        st.markdown('<div class="disclaimer">⚠ Demo companies are illustrative and fictional. Financials are realistic but invented for demonstration purposes only.</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            sector     = st.selectbox("Sector", ["All","IT Services","Pharma/Healthcare","FMCG/Consumer","Auto/Auto Anc","Industrials/Mfg"])
            max_ev     = st.slider("Max EV/EBITDA", 4.0, 22.0, 16.0, 0.5)
            min_growth = st.slider("Min Revenue Growth %", 0.0, 42.0, 0.0, 0.5)
        with c2:
            min_margin  = st.slider("Min EBITDA Margin %", 5.0, 40.0, 10.0, 0.5)
            max_debt    = st.slider("Max Debt/EBITDA", 0.0, 5.0, 4.0, 0.1)
            min_prom    = st.slider("Min Promoter Holding %", 0.0, 75.0, 0.0, 1.0)
        with c3:
            size_bands = st.multiselect("Market Cap Band", ["Small","Mid","Large"], default=["Small","Mid","Large"])
            r40_only   = st.checkbox("Rule of 40 only (≥40)")

        filtered = screen_companies(
            df_demo, sector, max_ev, min_growth, min_margin, max_debt,
            size_bands if size_bands else ["Small","Mid","Large"], min_prom, r40_only
        )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f'<div class="section-label">SCREEN RESULTS</div>'
                    f'<div class="section-title">{len(filtered)} target{"s" if len(filtered)!=1 else ""} match your thesis</div>',
                    unsafe_allow_html=True)
        if len(filtered) == 0:
            st.info("No targets match these filters. Try loosening one or two constraints.")
            return

        sort_col = st.selectbox("Sort by",
            ["deal_fit","ev_ebitda","rule_of_40","upside_pct","market_cap_cr"],
            format_func=lambda x: {"deal_fit":"Deal Fit Score","ev_ebitda":"EV/EBITDA (low→high)",
                                    "rule_of_40":"Rule of 40","upside_pct":"Implied Upside %",
                                    "market_cap_cr":"Market Cap"}[x])
        filtered = filtered.sort_values(sort_col, ascending=(sort_col == "ev_ebitda"))

        def _m(lbl, val):
            return f'<div class="metric-label">{lbl}</div><div style="font-family:DM Mono,monospace;color:#e8e4dc;font-size:1rem">{val}</div>'

        for _, row in filtered.iterrows():
            score    = int(row["deal_fit"])
            r40_flag = " ✓ R40" if row["rule_of_40"] >= 40 else ""
            fcf_flag = " ✓ FCF+" if row["fcf_positive"] else ""
            up_str   = f"{row['upside_pct']:.0f}%↑" if row["upside_pct"] > 0 else f"{row['upside_pct']:.0f}%↓"

            with st.expander(f"**{row['name']}** — {row['sector']} · {row['size_band']} Cap · "
                             f"EV/EBITDA {row['ev_ebitda']}x · DFS {score}{r40_flag}{fcf_flag} · {up_str}"):
                m1,m2,m3,m4,m5 = st.columns(5)
                with m1: st.markdown(f'<div class="metric-label">Deal Fit Score</div><div class="metric-value">{score}/100</div>', unsafe_allow_html=True)
                with m2: st.markdown(f'<div class="metric-label">EV/EBITDA</div><div class="metric-value">{row["ev_ebitda"]}x</div>', unsafe_allow_html=True)
                with m3: st.markdown(f'<div class="metric-label">Rule of 40</div><div class="metric-value">{row["rule_of_40"]:.1f}</div>', unsafe_allow_html=True)
                with m4:
                    ucls = "green" if row["upside_pct"] > 0 else "red"
                    st.markdown(f'<div class="metric-label">Implied Upside</div><div class="metric-value {ucls}">{row["upside_pct"]:.0f}%</div>', unsafe_allow_html=True)
                with m5: st.markdown(f'<div class="metric-label">Mkt Cap (₹Cr)</div><div class="metric-value">{row["market_cap_cr"]:,}</div>', unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                d1,d2,d3,d4 = st.columns(4)
                with d1:
                    st.markdown(_m("EBITDA (₹Cr)", f"{row['ebitda_cr']:,.0f}"), unsafe_allow_html=True)
                    st.markdown("<div style='margin-top:10px'>" + _m("Rev Growth", f"{row['revenue_growth_pct']}%") + "</div>", unsafe_allow_html=True)
                with d2:
                    st.markdown(_m("EBITDA Margin", f"{row['ebitda_margin_pct']}%"), unsafe_allow_html=True)
                    st.markdown("<div style='margin-top:10px'>" + _m("Debt/EBITDA", f"{row['debt_ebitda']}x") + "</div>", unsafe_allow_html=True)
                with d3:
                    st.markdown(_m("Promoter %", f"{row['promoter_holding_pct']}%"), unsafe_allow_html=True)
                    st.markdown("<div style='margin-top:10px'>" + _m("ROCE", f"{row['roce_pct']}%") + "</div>", unsafe_allow_html=True)
                with d4:
                    st.markdown(f'<div class="metric-label">Implied Price</div><div style="font-family:DM Mono,monospace;color:#c9a96e;font-size:1rem">₹{row["implied_price"]:.0f}</div>', unsafe_allow_html=True)
                    st.markdown("<div style='margin-top:10px'>" + _m("Current Price", f"₹{row['current_price']:.0f}") + "</div>", unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(row["deal_rationale"])

    else:  # Custom AI Mode
        st.markdown('<div class="disclaimer">⚠ Custom mode uses live AI. Returns real Indian listed companies based on public data. Always verify before use. Not investment advice.</div>', unsafe_allow_html=True)
        provider = st.selectbox("AI Provider", ["Gemini 2.0 Flash (Google)","Groq","OpenAI","Anthropic","DeepSeek"])
        api_key  = st.text_input(f"{provider} API Key", type="password", placeholder="Paste your API key...")
        sector   = st.selectbox("Sector Focus", ["All","IT Services","Pharma/Healthcare","FMCG/Consumer","Auto/Auto Anc","Industrials/Mfg"], key="custom_sector")
        thesis   = st.text_area("Describe your acquisition thesis",
                                placeholder='e.g. "Profitable Indian specialty chemicals companies under ₹5000Cr market cap, low debt, founder-led, suitable for PE buyout"',
                                height=120)

        if st.button("→ Find Targets", disabled=not (api_key and thesis)):
            with st.spinner("Searching for targets..."):
                try:
                    st.session_state.custom_results = call_ai_provider(thesis, sector, provider, api_key)
                except Exception as e:
                    st.error(f"Error: {e}. Check your API key and try again.")

        if st.session_state.custom_results:
            result  = st.session_state.custom_results
            targets = result.get("targets", [])
            summary = result.get("thesis_summary", "")
            if summary:
                st.markdown(f'<div class="card"><div class="section-label">THESIS APPLIED</div>'
                            f'<div style="color:#b0ac9f;font-size:0.9rem;margin-top:6px">{summary}</div></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="section-title">{len(targets)} target{"s" if len(targets)!=1 else ""} found</div><br>', unsafe_allow_html=True)

            for t in targets:
                sec = t.get("sector","Industrials/Mfg")
                if sec not in SECTOR_MA_MULTIPLES: sec = "Industrials/Mfg"
                t["sector"] = sec
                t.setdefault("fcf_positive", True)
                score = deal_fit_score(t)
                r40   = t.get("revenue_growth_pct",0) + t.get("ebitda_margin_pct",0)
                with st.expander(f"**{t['name']}** ({t.get('ticker','NSE')}) · {t['sector']} · "
                                 f"EV/EBITDA {t.get('ev_ebitda',0)}x · DFS {score} · {t.get('likely_buyer_type','')}"):
                    cc1,cc2,cc3,cc4 = st.columns(4)
                    with cc1: st.markdown(f'<div class="metric-label">Deal Fit Score</div><div class="metric-value">{score}/100</div>', unsafe_allow_html=True)
                    with cc2: st.markdown(f'<div class="metric-label">EV/EBITDA</div><div class="metric-value">{t.get("ev_ebitda",0)}x</div>', unsafe_allow_html=True)
                    with cc3: st.markdown(f'<div class="metric-label">Rule of 40</div><div class="metric-value">{r40:.1f}</div>', unsafe_allow_html=True)
                    with cc4: st.markdown(f'<div class="metric-label">Mkt Cap (₹Cr)</div><div class="metric-value">{t.get("market_cap_cr",0):,}</div>', unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown(f"**Deal Rationale:** {t.get('deal_rationale','')}")

# ─── DEAL FIT RANKING TAB ─────────────────────────────────────────────────────
def render_ranking_tab():
    st.markdown('<div class="section-label">RANKINGS</div><div class="section-title">Deal Fit Ranking & Value Map</div><br>', unsafe_allow_html=True)

    top10 = df_demo.nlargest(10, "deal_fit")
    sec_colors = {"IT Services":"#3a5a7a","Pharma/Healthcare":"#c9a96e","FMCG/Consumer":"#4ab87a","Auto/Auto Anc":"#e0a04a","Industrials/Mfg":"#e05c6c"}

    fig_bar = go.Figure(go.Bar(
        x=top10["deal_fit"], y=top10["name"], orientation="h",
        marker_color=[sec_colors.get(s,"#666") for s in top10["sector"]],
        text=top10["deal_fit"].astype(str)+"/100", textposition="outside",
        textfont=dict(family="DM Mono", size=11, color="#e8e4dc"),
    ))
    fig_bar.update_layout(
        title=dict(text="Top 10 Targets by Deal Fit Score", font=dict(family="Playfair Display", size=16, color="#e8e4dc")),
        paper_bgcolor="#09090e", plot_bgcolor="#09090e",
        xaxis=dict(range=[0,120], showgrid=False, tickfont=dict(family="DM Mono", color="#666")),
        yaxis=dict(showgrid=False, tickfont=dict(family="Syne", size=11, color="#b0ac9f"), autorange="reversed"),
        margin=dict(l=180, r=80, t=50, b=20), height=400, showlegend=False,
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">DEAL MAP</div><div class="section-title">Value vs Quality</div>', unsafe_allow_html=True)
    st.markdown('<p style="color:#666;font-size:0.82rem;margin-bottom:16px">x = EV/EBITDA (cheaper → left) · y = Rule of 40 (better → up) · bubble size = market cap · color = deal fit score</p>', unsafe_allow_html=True)

    fig_s = go.Figure()
    first_sec = list(df_demo["sector"].unique())[0]
    for sec_name, sdf in df_demo.groupby("sector"):
        fig_s.add_trace(go.Scatter(
            x=sdf["ev_ebitda"], y=sdf["rule_of_40"],
            mode="markers+text", name=sec_name,
            text=sdf["name"].apply(lambda n: n.split()[0]),
            textposition="top center",
            textfont=dict(family="Syne", size=9, color="#b0ac9f"),
            marker=dict(
                size=sdf["market_cap_cr"]/1500+8,
                color=sdf["deal_fit"],
                colorscale=[[0,"#e05c6c"],[0.5,"#e0a04a"],[1.0,"#4ab87a"]],
                cmin=0, cmax=100,
                showscale=(sec_name == first_sec),
                colorbar=dict(
                    title=dict(text="DFS", font=dict(color="#666", family="DM Mono")),
                    tickfont=dict(color="#666", family="DM Mono"),
                    bordercolor="#222230",
                    x=1.02, xanchor="left",
                    thickness=14, len=0.75,
                ),
                line=dict(color="#222230", width=1),
            ),
            hovertemplate="<b>%{text}</b><br>EV/EBITDA: %{x}x<br>Rule of 40: %{y:.1f}<br>Deal Fit: %{marker.color}<extra></extra>",
        ))

    # ✅ rgba() instead of 8-digit hex — valid in all Plotly versions
    fig_s.add_hline(y=40, line_dash="dot", line_color="rgba(201,169,110,0.33)",
                    annotation_text="Rule of 40 threshold", annotation_font_color="#666666")
    avg_med = sum(v["median_ev_ebitda"] for v in SECTOR_MA_MULTIPLES.values()) / len(SECTOR_MA_MULTIPLES)
    fig_s.add_vline(x=avg_med, line_dash="dot", line_color="rgba(58,90,122,0.53)",
                    annotation_text="Avg sector median", annotation_font_color="#666666")
    fig_s.update_layout(
        paper_bgcolor="#09090e", plot_bgcolor="#111118",
        xaxis=dict(title="EV/EBITDA (x)", showgrid=True, gridcolor="#222230", tickfont=dict(family="DM Mono", color="#666")),
        yaxis=dict(title="Rule of 40",    showgrid=True, gridcolor="#222230", tickfont=dict(family="DM Mono", color="#666")),
        legend=dict(
            font=dict(family="Syne", size=11, color="#b0ac9f"),
            bgcolor="rgba(17,17,24,0.85)",
            bordercolor="#222230",
            borderwidth=1,
            orientation="h",
            yanchor="bottom", y=-0.22,
            xanchor="left",   x=0,
        ),
        margin=dict(l=10, r=80, t=20, b=80), height=500,
    )
    st.plotly_chart(fig_s, use_container_width=True)

    top_t = df_demo.loc[df_demo["deal_fit"].idxmax()]
    st.markdown(f"""<div class="card">
        <div class="section-label">TOP TARGET</div>
        <div class="section-title" style="font-size:1.1rem">{top_t['name']}</div>
        <p style="color:#b0ac9f;font-size:0.88rem;margin-top:8px">
            Deal Fit Score <strong style="color:#4ab87a">{int(top_t['deal_fit'])}/100</strong> &nbsp;·&nbsp;
            {top_t['sector']} &nbsp;·&nbsp;
            EV/EBITDA <strong style="color:#c9a96e">{top_t['ev_ebitda']}x</strong> &nbsp;·&nbsp;
            Rule of 40 <strong style="color:#c9a96e">{top_t['rule_of_40']:.1f}</strong> &nbsp;·&nbsp;
            Implied upside <strong style="color:#4ab87a">{top_t['upside_pct']:.0f}%</strong>
        </p>
    </div>""", unsafe_allow_html=True)

# ─── IMPLIED TAKEOUT TAB ──────────────────────────────────────────────────────
def render_takeout_tab():
    st.markdown('<div class="section-label">ANALYSIS</div><div class="section-title">Implied Takeout Analysis</div><br>', unsafe_allow_html=True)

    names       = df_demo["name"].tolist()
    default_idx = names.index(df_demo.loc[df_demo["deal_fit"].idxmax(), "name"])
    sel_name    = st.selectbox("Select target company", names, index=default_idx)
    company     = df_demo[df_demo["name"] == sel_name].iloc[0].to_dict()
    t           = implied_takeout(company)
    sec_med     = SECTOR_MA_MULTIPLES[company["sector"]]["median_ev_ebitda"]
    cp_pct      = SECTOR_MA_MULTIPLES[company["sector"]]["control_premium"] * 100

    tc1,tc2,tc3,tc4 = st.columns(4)
    with tc1: st.markdown(f'<div class="metric-label">Current EV (₹Cr)</div><div class="metric-value">{t["current_ev"]:,.0f}</div>', unsafe_allow_html=True)
    with tc2: st.markdown(f'<div class="metric-label">Implied Takeout EV</div><div class="metric-value green">{t["takeout_ev"]:,.0f}</div>', unsafe_allow_html=True)
    with tc3: st.markdown(f'<div class="metric-label">Deal Premium</div><div class="metric-value green">{t["premium_pct"]:.1f}%</div>', unsafe_allow_html=True)
    with tc4:
        ucls = "green" if t["upside_pct"] > 0 else "red"
        st.markdown(f'<div class="metric-label">Share Price Upside</div><div class="metric-value {ucls}">{t["upside_pct"]:.1f}%</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    wf_vals = [t["current_ev"], t["takeout_ev"] - t["current_ev"], t["takeout_ev"]]
    fig_wf = go.Figure(go.Waterfall(
        orientation="v",
        measure=["absolute","relative","total"],
        x=["Current EV", "Control Premium + Re-rating", "Implied Takeout EV"],
        y=wf_vals,
        connector=dict(line=dict(color="#222230")),
        increasing=dict(marker=dict(color="#4ab87a")),
        decreasing=dict(marker=dict(color="#e05c6c")),
        totals=dict(marker=dict(color="#c9a96e")),
        text=[f"₹{v:,.0f}Cr" for v in wf_vals],
        textposition="outside",
        textfont=dict(family="DM Mono", color="#e8e4dc"),
    ))
    fig_wf.update_layout(
        title=dict(text=f"EV Bridge — {sel_name}", font=dict(family="Playfair Display", size=15, color="#e8e4dc")),
        paper_bgcolor="#09090e", plot_bgcolor="#111118",
        yaxis=dict(showgrid=True, gridcolor="#222230", tickfont=dict(family="DM Mono", color="#666"), tickprefix="₹", ticksuffix="Cr"),
        xaxis=dict(tickfont=dict(family="Syne", color="#b0ac9f")),
        showlegend=False, margin=dict(l=10, r=10, t=70, b=20), height=380,
    )
    st.plotly_chart(fig_wf, use_container_width=True)

    st.markdown('<div class="section-label" style="margin-top:20px">BUYER COMPARISON</div>', unsafe_allow_html=True)
    bc1,bc2,bc3 = st.columns(3)
    pe_p    = (t["pe_ev"]       - company["net_debt_cr"]) / company["shares_cr"]
    st_p    = (t["strategic_ev"] - company["net_debt_cr"]) / company["shares_cr"]
    pe_up   = (pe_p / company["current_price"] - 1) * 100
    st_up   = (st_p / company["current_price"] - 1) * 100

    with bc1:
        st.markdown(f'<div class="card"><div class="section-label">CURRENT MARKET</div>'
                    f'<div style="font-family:DM Mono;font-size:1.3rem;color:#e8e4dc">₹{company["current_price"]:.0f}</div>'
                    f'<div style="font-family:Syne;font-size:0.8rem;color:#666;margin-top:4px">{company["ev_ebitda"]}x EV/EBITDA</div></div>', unsafe_allow_html=True)
    with bc2:
        c = "#4ab87a" if st_up > 0 else "#e05c6c"
        st.markdown(f'<div class="card"><div class="section-label">STRATEGIC BUYER ({CORPORATE_BUYER_MULTIPLE}x)</div>'
                    f'<div style="font-family:DM Mono;font-size:1.3rem;color:#c9a96e">₹{st_p:.0f}</div>'
                    f'<div style="font-family:Syne;font-size:0.8rem;color:{c};margin-top:4px">{st_up:+.1f}% vs current</div></div>', unsafe_allow_html=True)
    with bc3:
        c = "#4ab87a" if pe_up > 0 else "#e05c6c"
        st.markdown(f'<div class="card"><div class="section-label">PE BUYER ({PE_BUYER_MULTIPLE}x)</div>'
                    f'<div style="font-family:DM Mono;font-size:1.3rem;color:#c9a96e">₹{pe_p:.0f}</div>'
                    f'<div style="font-family:Syne;font-size:0.8rem;color:{c};margin-top:4px">{pe_up:+.1f}% vs current</div></div>', unsafe_allow_html=True)

    st.markdown(f"""<div class="card" style="margin-top:16px">
        <div class="section-label">CONTROL PREMIUM BREAKDOWN</div>
        <p style="color:#b0ac9f;font-size:0.88rem;margin-top:8px">
            Sector median EV/EBITDA: <strong style="color:#c9a96e">{sec_med}x</strong> &nbsp;·&nbsp;
            Current EV/EBITDA: <strong style="color:#e8e4dc">{company['ev_ebitda']}x</strong> &nbsp;·&nbsp;
            Control premium: <strong style="color:#c9a96e">{cp_pct:.0f}%</strong><br>
            <span style="color:#666;font-size:0.8rem">Takeout EV = EBITDA × Sector Median × (1 + Control Premium) =
            ₹{company['ebitda_cr']:,.0f}Cr × {sec_med}x × {1+cp_pct/100:.2f} = ₹{t['takeout_ev']:,.0f}Cr</span>
        </p>
    </div>""", unsafe_allow_html=True)

# ─── SECTOR BENCHMARKS TAB ────────────────────────────────────────────────────
def render_benchmarks_tab():
    st.markdown('<div class="section-label">REFERENCE</div><div class="section-title">Sector M&A Multiple Benchmarks</div><br>', unsafe_allow_html=True)

    sectors  = list(SECTOR_MA_MULTIPLES.keys())
    medians  = [SECTOR_MA_MULTIPLES[s]["median_ev_ebitda"] for s in sectors]
    clrs     = ["#3a5a7a","#c9a96e","#4ab87a","#e0a04a","#e05c6c"]

    fig_m = go.Figure(go.Bar(
        x=sectors, y=medians, marker_color=clrs,
        text=[f"{m}x" for m in medians], textposition="outside",
        textfont=dict(family="DM Mono", size=12, color="#e8e4dc"),
    ))
    # ✅ rgba() for the reference line — no 8-digit hex
    fig_m.add_hline(y=GLOBAL_MEDIAN_MA_MULTIPLE, line_dash="dot",
                    line_color="rgba(201,169,110,0.53)",
                    annotation_text=f"Global median {GLOBAL_MEDIAN_MA_MULTIPLE}x",
                    annotation_font_color="#c9a96e")
    fig_m.update_layout(
        title=dict(text="Median M&A EV/EBITDA by Sector", font=dict(family="Playfair Display", size=16, color="#e8e4dc")),
        paper_bgcolor="#09090e", plot_bgcolor="#111118",
        xaxis=dict(tickfont=dict(family="Syne", color="#b0ac9f"), showgrid=False),
        yaxis=dict(title="EV/EBITDA (x)", showgrid=True, gridcolor="#222230",
                   tickfont=dict(family="DM Mono", color="#666"), range=[0, max(medians)*1.2]),
        showlegend=False, margin=dict(l=10, r=10, t=60, b=20), height=360,
    )
    st.plotly_chart(fig_m, use_container_width=True)

    ref = [{"Sector": s,
            "Median EV/EBITDA": f"{SECTOR_MA_MULTIPLES[s]['median_ev_ebitda']}x",
            "Control Premium":  f"{SECTOR_MA_MULTIPLES[s]['control_premium']*100:.0f}%",
            "vs Global Median": f"{SECTOR_MA_MULTIPLES[s]['median_ev_ebitda'] - GLOBAL_MEDIAN_MA_MULTIPLE:+.1f}x"}
           for s in sectors]
    st.dataframe(pd.DataFrame(ref), use_container_width=True, hide_index=True)

    st.markdown("<br>", unsafe_allow_html=True)
    sc1, sc2 = st.columns(2)
    with sc1:
        st.markdown("""<div class="card">
            <div class="section-label">WHY IT & PHARMA COMMAND PREMIUMS</div>
            <p style="color:#b0ac9f;font-size:0.85rem;line-height:1.7;margin-top:8px">
                <strong style="color:#e8e4dc">IT Services</strong> trades at 12.8x because buyers pay for recurring revenue, low capex, and IP moats. In cross-border M&A, Indian IT companies give global buyers instant delivery capability at 40–60% the cost of Western equivalents.<br><br>
                <strong style="color:#e8e4dc">Pharma/Healthcare</strong> trades at 12.5x for its regulatory complexity — USFDA approvals, CMC filings, and ANDAs are irreplicable assets. A generic molecule pipeline at 80% completion is worth far more than its book value to a strategic acquirer.
            </p>
        </div>""", unsafe_allow_html=True)
    with sc2:
        st.markdown("""<div class="card">
            <div class="section-label">RULE OF 40 — HOW IT MOVES PRICING</div>
            <p style="color:#b0ac9f;font-size:0.85rem;line-height:1.7;margin-top:8px">
                Rule of 40 = Revenue Growth % + EBITDA Margin %. A score above 40 signals a company that is simultaneously growing well and profitable — rare and valued by buyers.<br><br>
                Companies scoring above 40 trade at <strong style="color:#c9a96e">2–3x the EV/Revenue</strong> of those below. For PE buyers it's a quality proxy: high R40 targets can sustain deal leverage because cash flows are predictable.<br><br>
                Below 30? The company either grows by burning margin, or is profitable but stagnant. Both tell a harder story at the deal table.
            </p>
        </div>""", unsafe_allow_html=True)

    st.markdown("""<div class="card" style="margin-top:4px">
        <div class="section-label">GLOBAL REFERENCE MULTIPLES (Jun 2025)</div>
        <p style="color:#b0ac9f;font-size:0.85rem;line-height:1.7;margin-top:8px">
            Global median M&A EV/EBITDA: <strong style="color:#c9a96e">9.3x</strong> (all transactions) &nbsp;·&nbsp;
            PE buyers: <strong style="color:#c9a96e">10.1x</strong> avg &nbsp;·&nbsp;
            Corporate/strategic buyers: <strong style="color:#c9a96e">8.6x</strong> avg<br>
            <span style="color:#666;font-size:0.78rem">Source: IB M&A multiple references, June 2025</span>
        </p>
    </div>""", unsafe_allow_html=True)

# ─── TERMINAL ─────────────────────────────────────────────────────────────────
def render_terminal():
    st.markdown("""
    <div style="display:flex;align-items:center;justify-content:space-between;padding:16px 0 8px 0;border-bottom:1px solid #222230;margin-bottom:8px">
        <div>
            <span style="font-family:Playfair Display,serif;font-size:1.5rem;font-weight:700;color:#e8e4dc">Deal<em style="font-style:italic;color:#c9a96e">Scout</em></span>
            <span style="font-family:DM Mono,monospace;font-size:0.7rem;color:#666;margin-left:12px;letter-spacing:0.1em">M&A TARGET SCREENER · DAY 18</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("← Back to home", key="back_btn"):
        st.session_state.page = "home"; st.rerun()
    st.markdown("<br>", unsafe_allow_html=True)
    tab1,tab2,tab3,tab4 = st.tabs(["⚡ Screener","🏆 Deal Fit Ranking","💰 Implied Takeout","📚 Sector Benchmarks"])
    with tab1: render_screener_tab()
    with tab2: render_ranking_tab()
    with tab3: render_takeout_tab()
    with tab4: render_benchmarks_tab()

# ─── ROUTER ───────────────────────────────────────────────────────────────────
if   st.session_state.page == "home":     render_homepage()
elif st.session_state.page == "terminal": render_terminal()

# ─── FOOTER ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer-bar">
    DealScout &nbsp;·&nbsp; Day 18 &nbsp;·&nbsp; 30 Days of AI Finance &nbsp;·&nbsp;
    Demo companies are fictional and illustrative &nbsp;·&nbsp;
    Custom mode uses live AI search &nbsp;·&nbsp;
    Not investment advice. Not an M&A advisory.
</div>
""", unsafe_allow_html=True)