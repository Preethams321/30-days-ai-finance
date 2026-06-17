"""
CompeteIQ — Data module
Day 17 / 30 Days of AI Finance
Hardcoded demo dataset (FY25 standalone, audited) + DuPont / moat scoring engines.
"""

COLORS = {
    "bg":    "#09090e",
    "card":  "#111118",
    "gold":  "#c9a96e",
    "navy":  "#3a5a7a",
    "green": "#4ab87a",
    "red":   "#e05c6c",
    "amber": "#e0a04a",
    "text1": "#e8e4dc",
    "text2": "#b0ac9f",
    "text3": "#666666",
}

# Keyed by NSE ticker — robust against name-string mismatches from AI-fetched custom data
BANK_COLORS = {
    "HDFCBANK":  "#004C97",
    "ICICIBANK": "#F58220",
    "KOTAKBANK": "#EE3124",
    "AXISBANK":  "#97144D",
    "SBIN":      "#22409A",
}

DEFAULT_CHART_COLORS = ["#c9a96e", "#3a5a7a", "#4ab87a", "#e0a04a", "#e05c6c", "#7a9bc4", "#b06fb0"]

# -----------------------------------------------------------------------
# Sector-level Porter's 5 Forces (demo mode). Custom mode aggregates
# per-company AI-generated scores into an equivalent sector view.
# -----------------------------------------------------------------------
SECTOR_PORTER = {
    "buyer_power": 6,
    "supplier_power": 3,
    "threat_of_entry": 4,
    "substitutes": 7,
    "rivalry": 8,
    "notes": {
        "buyer_power": "Retail customers have moderate power — FD rates are competitive but switching current accounts is friction-heavy. Corporate customers have high power.",
        "supplier_power": "Deposits are the raw material. RBI repo rate sets the floor. Banks compete on rates but no single depositor has pricing power.",
        "threat_of_entry": "RBI banking licenses are extremely rare. Payments bank licenses exist but a full banking license is a 5-10 year process.",
        "substitutes": "Biggest structural threat — UPI displaced cash, fintechs took personal loans, mutual funds took savings. Banking must keep evolving.",
        "rivalry": "HDFC, ICICI, Kotak, Axis all target the same urban salaried segment. SBI has scale. Competition on rates, products, and digital experience is intense.",
    },
}

# -----------------------------------------------------------------------
# DEMO DATA — FY25 audited standalone financials, 5 Indian banks
# Gross Total Income = Interest Earned + Other Income (pre interest-expense)
# NII = Net Interest Income (post interest-expense)
# -----------------------------------------------------------------------
DEMO_DATA = {
    "sector": "Indian Private & Public Sector Banking",
    "fy": "FY2025",
    "sector_overview": (
        "Indian banking remains well-capitalised with improving asset quality across both "
        "private and public sector banks. HDFC Bank commands the highest balance-sheet scale "
        "while Kotak posts the strongest margin and capital profile despite being the smallest "
        "of the five. Net interest margins face structural pressure as deposit costs reprice "
        "faster than lending yields, and fintech substitution continues to erode fee pools."
    ),
    "porter": SECTOR_PORTER,
    "companies": [
        {
            "name": "HDFC Bank", "ticker": "HDFCBANK", "fy": "FY25",
            "nii_cr": 122670.09, "other_income_cr": 45632.28, "total_income_cr": 346149.32,
            "opex_cr": 68174.89, "ppop_cr": 100127.48, "net_profit_cr": 67347.36,
            "total_assets_cr": 3910198.94, "loan_book_cr": 2619608.61,
            "deposits_cr": 2714714.90, "net_worth_cr": 488899.89,
            "nim_pct": 3.90, "roa_pct": 1.91, "roe_pct": 14.10, "cost_to_income_pct": 19.70,
            "gnpa_pct": 1.33, "nnpa_pct": 0.43, "crar_pct": 19.55,
            "advances_growth_pct": None, "deposits_growth_pct": None, "net_profit_growth_pct": 10.75,
            "growth_note": "Post-merger baseline (HDFC–HDFC Ltd merger) — YoY growth not comparable",
            "pbv": 2.74, "pe": 17.40, "book_value_per_share": 577.00, "current_price": 1578.50,
            "market_cap_cr": 1204412,
        },
        {
            "name": "ICICI Bank", "ticker": "ICICIBANK", "fy": "FY25",
            "nii_cr": 81164.44, "other_income_cr": 28506.70, "total_income_cr": 191770.48,
            "opex_cr": 42372.32, "ppop_cr": 67298.82, "net_profit_cr": 47226.99,
            "total_assets_cr": 2118239.97, "loan_book_cr": 1341766.16,
            "deposits_cr": 1610348.02, "net_worth_cr": 282055.56,
            "nim_pct": 4.41, "roa_pct": 2.41, "roe_pct": 18.20, "cost_to_income_pct": 22.09,
            "gnpa_pct": 1.67, "nnpa_pct": 0.39, "crar_pct": 16.55,
            "advances_growth_pct": 13.29, "deposits_growth_pct": 13.98, "net_profit_growth_pct": 15.50,
            "growth_note": None,
            "pbv": 2.84, "pe": 16.71, "book_value_per_share": 394.30, "current_price": 1123.40,
            "market_cap_cr": 787513,
        },
        {
            "name": "Axis Bank", "ticker": "AXISBANK", "fy": "FY25",
            "nii_cr": 54347.82, "other_income_cr": 25257.06, "total_income_cr": 147934.10,
            "opex_cr": 37499.95, "ppop_cr": 42104.93, "net_profit_cr": 26373.48,
            "total_assets_cr": 1609929.88, "loan_book_cr": 1040811.32,
            "deposits_cr": 1172952.02, "net_worth_cr": 173051.25,
            "nim_pct": 3.98, "roa_pct": 1.74, "roe_pct": 16.89, "cost_to_income_pct": 25.35,
            "gnpa_pct": 1.28, "nnpa_pct": 0.33, "crar_pct": 17.07,
            "advances_growth_pct": 7.85, "deposits_growth_pct": 9.76, "net_profit_growth_pct": 6.08,
            "growth_note": None,
            "pbv": 2.29, "pe": 13.80, "book_value_per_share": 487.30, "current_price": 1114.60,
            "market_cap_cr": 343656,
        },
        {
            "name": "Kotak Mahindra Bank", "ticker": "KOTAKBANK", "fy": "FY25",
            "nii_cr": 28341.83, "other_income_cr": 11418.49, "total_income_cr": 64338.22,
            "opex_cr": 18753.70, "ppop_cr": 21006.57, "net_profit_cr": 16450.08,
            "total_assets_cr": 693624.18, "loan_book_cr": 426909.20,
            "deposits_cr": 499055.13, "net_worth_cr": 116897.69,
            "nim_pct": 4.91, "roa_pct": 2.65, "roe_pct": 11.20, "cost_to_income_pct": 29.15,
            "gnpa_pct": 1.42, "nnpa_pct": 0.31, "crar_pct": 22.25,
            "advances_growth_pct": 13.52, "deposits_growth_pct": 11.16, "net_profit_growth_pct": 19.36,
            "growth_note": None,
            "pbv": 3.39, "pe": 19.20, "book_value_per_share": 511.00, "current_price": 1732.10,
            "market_cap_cr": 344839,
        },
        {
            "name": "State Bank of India", "ticker": "SBIN", "fy": "FY25",
            "nii_cr": 189994.46, "other_income_cr": 172405.53, "total_income_cr": 663343.32,
            "opex_cr": 236573.52, "ppop_cr": 125826.47, "net_profit_cr": 70900.63,
            "total_assets_cr": 6676053.27, "loan_book_cr": 4163312.10,
            "deposits_cr": 5382189.53, "net_worth_cr": 389071.49,
            "nim_pct": 3.32, "roa_pct": 1.12, "roe_pct": 15.65, "cost_to_income_pct": 35.66,
            "gnpa_pct": 1.82, "nnpa_pct": 0.47, "crar_pct": 14.25,
            "advances_growth_pct": 12.40, "deposits_growth_pct": 9.48, "net_profit_growth_pct": 16.08,
            "growth_note": None,
            "pbv": 1.88, "pe": 10.02, "book_value_per_share": 422.00, "current_price": 794.20,
            "market_cap_cr": 709353,
        },
    ],
    "data_sources": ["Audited FY25 standalone financial statements", "Company investor presentations", "Screener.in (market data)"],
}


# -----------------------------------------------------------------------
# MODIFIED DUPONT DECOMPOSITION FOR BANKS
# ROE = Net Profit Margin × Asset Utilisation × Equity Multiplier
# -----------------------------------------------------------------------
def dupont_decomposition(companies):
    results = []
    for co in companies:
        npm = co["net_profit_cr"] / co["total_income_cr"] if co["total_income_cr"] else 0
        au = co["total_income_cr"] / co["total_assets_cr"] if co["total_assets_cr"] else 0
        em = co["total_assets_cr"] / co["net_worth_cr"] if co["net_worth_cr"] else 0
        roe_computed = npm * au * em
        results.append({
            "name": co["name"], "ticker": co.get("ticker", ""),
            "npm": npm, "au": au, "em": em,
            "roe_computed": roe_computed,
            "roe_reported": co["roe_pct"] / 100,
            "delta_pp": (roe_computed - co["roe_pct"] / 100) * 100,
            "insight": _dupont_insight(co["name"], npm, au, em),
        })
    return results


def _dupont_insight(name, npm, au, em):
    drivers = []
    if npm > 0.20:
        drivers.append("high net profit margins")
    if au > 0.08:
        drivers.append("efficient asset utilisation")
    if em > 12:
        drivers.append("significant financial leverage")
    if not drivers:
        drivers.append("a balanced contribution across all three factors")
    return f"{name}'s ROE is primarily driven by {' and '.join(drivers)}."


# -----------------------------------------------------------------------
# COMPETITIVE MOAT SCORING — composite 0-100
# -----------------------------------------------------------------------
def compute_moat_score(co):
    score = 0
    if co["gnpa_pct"] < 1.5:
        score += 25
    elif co["gnpa_pct"] < 3.0:
        score += 15
    else:
        score += 5

    if co["nim_pct"] > 4.0:
        score += 20
    elif co["nim_pct"] > 3.0:
        score += 12
    else:
        score += 5

    if co["cost_to_income_pct"] < 40:
        score += 20
    elif co["cost_to_income_pct"] < 50:
        score += 12
    else:
        score += 5

    if co["crar_pct"] > 18:
        score += 15
    elif co["crar_pct"] > 15:
        score += 10
    else:
        score += 5

    growth = co["advances_growth_pct"] if co.get("advances_growth_pct") is not None else co.get("net_profit_growth_pct", 0)
    if growth > 20:
        score += 10
    elif growth > 12:
        score += 6
    else:
        score += 2

    if co["pbv"] > 3.0:
        score += 10
    elif co["pbv"] > 1.5:
        score += 6
    else:
        score += 2

    return min(score, 100)


def moat_breakdown(co):
    """Returns list of (factor_label, points, max_points, note) for the gauge-adjacent breakdown."""
    parts = []
    g = co["gnpa_pct"]
    parts.append(("Asset quality (GNPA)", 25 if g < 1.5 else 15 if g < 3.0 else 5, 25, f"GNPA {g:.2f}%"))
    n = co["nim_pct"]
    parts.append(("Margin strength (NIM)", 20 if n > 4.0 else 12 if n > 3.0 else 5, 20, f"NIM {n:.2f}%"))
    c = co["cost_to_income_pct"]
    parts.append(("Operating efficiency", 20 if c < 40 else 12 if c < 50 else 5, 20, f"Cost/Income {c:.2f}%"))
    cr = co["crar_pct"]
    parts.append(("Capital buffer (CRAR)", 15 if cr > 18 else 10 if cr > 15 else 5, 15, f"CRAR {cr:.2f}%"))
    growth = co["advances_growth_pct"] if co.get("advances_growth_pct") is not None else co.get("net_profit_growth_pct", 0)
    growth_label = "Advances growth" if co.get("advances_growth_pct") is not None else "Profit growth (proxy)"
    parts.append((growth_label, 10 if growth > 20 else 6 if growth > 12 else 2, 10, f"{growth:.2f}%"))
    p = co["pbv"]
    parts.append(("Valuation premium (P/BV)", 10 if p > 3.0 else 6 if p > 1.5 else 2, 10, f"P/BV {p:.2f}x"))
    return parts


def moat_factors_and_summary(co, score):
    parts = moat_breakdown(co)
    strong = [label for label, pts, mx, _ in parts if pts == mx]
    weak = [label for label, pts, mx, _ in parts if pts <= mx * 0.3]

    factors = strong[:3] if strong else [label for label, pts, mx, _ in sorted(parts, key=lambda x: -x[1])[:2]]

    tier = "wide-moat" if score >= 80 else "moderate-moat" if score >= 60 else "narrow-moat"
    edge = strong[0].lower() if strong else "a mix of average fundamentals"
    drag = f" Its main drag is {weak[0].lower()}." if weak else ""
    summary = (
        f"{co['name']} scores as a {tier} franchise ({score}/100), anchored by {edge}.{drag} "
        f"At {co['pbv']:.2f}x book, the market is {'paying a clear premium for' if co['pbv'] > 2.5 else 'pricing in moderate confidence in'} this quality."
    )
    return factors, summary


def normalize_for_radar(companies, invert_keys=("gnpa_pct",)):
    """Min-max normalise each metric across companies to 0-100, inverting metrics in invert_keys."""
    keys = ["nim_pct", "roa_pct", "roe_pct", "gnpa_pct", "crar_pct"]
    out = {co["name"]: {} for co in companies}
    growth_vals = [co["advances_growth_pct"] if co.get("advances_growth_pct") is not None else co.get("net_profit_growth_pct", 0) for co in companies]
    for k in keys:
        vals = [co[k] for co in companies]
        lo, hi = min(vals), max(vals)
        rng = (hi - lo) or 1
        for co in companies:
            v = co[k]
            norm = (v - lo) / rng * 100
            if k in invert_keys:
                norm = 100 - norm
            out[co["name"]][k] = norm
    lo, hi = min(growth_vals), max(growth_vals)
    rng = (hi - lo) or 1
    for co, g in zip(companies, growth_vals):
        out[co["name"]]["growth_pct"] = (g - lo) / rng * 100
    return out
