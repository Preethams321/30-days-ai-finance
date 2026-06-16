"""
DCFdesk — MCX (Multi Commodity Exchange of India Ltd)
All figures from real public financials (Screener.in, BSE/NSE filings).
Base year = FY26 LTM (Mar 2026 TTM). Figures in ₹ Crores.
"""

# ═══════════════════════════ COMPANY ═══════════════════════════
COMPANY = {
    "name": "Multi Commodity Exchange of India Ltd",
    "short_name": "MCX",
    "sector": "Exchange / Financial Market Infrastructure",
    "description": "India's largest commodity derivatives exchange with 95.9% market share",
    "currency_short": "₹ Cr",
    "currency_long": "₹ Crores",
    "ticker": "NSE: MCX",
    "current_price": 2885,
    "shares_outstanding": 25.5,       # Cr shares (₹51 Cr equity / ₹2 face value)
    "net_debt": -2944,                 # Negative = net cash (Investments ₹2,949 Cr − Borrowings ₹5 Cr)
    "market_cap": 73567.5,            # 2885 × 25.5
    "implied_market_ev": 70623.5,     # Market Cap − Net Cash
    # LTM financials (FY26 TTM, Mar 2026)
    "year_zero_revenue": 2302,
    "year_zero_ebitda": 1720,         # Op Profit 1,642 + D&A 78
    "year_zero_ebitda_margin": 0.747, # 74.7%
    "year_zero_ebit": 1642,           # Operating Profit (Interest expense = 0)
    "year_zero_da": 78,
    "year_zero_capex": 72,            # Fixed assets purchased FY26
    "year_zero_fcff": 1223,           # NOPAT + D&A − Capex − NWC (computed)
    "year_zero_net_profit": 1332,
    "tax_rate": 0.21,
    # Context
    "market_share": "95.9%",
    "fy24_note": "FY24 was depressed (₹83 Cr net profit) due to platform migration. FY26 reflects post-upgrade normalization.",
    "face_value": 2.0,
}

# ═══════════════════════════ SCENARIOS ═══════════════════════════
# Key debate: FY26 revenue (₹2,302 Cr) and margins (74.7%) are post-rebound peaks.
# Bear: volumes normalize/compress. Base: steady ADTV growth, margins hold.
# Bull: commodity super-cycle + new products (options, index futures).

SCENARIOS = {
    "Bear": {
        "color": "#e05c6c",
        "fill": "rgba(224,92,108,0.08)",
        "revenue_growth":     [0.05, 0.05, 0.04, 0.04, 0.03],  # 5yr CAGR ~4%
        "ebitda_margin":      [0.65, 0.62, 0.60, 0.58, 0.56],  # margin compression
        "da_pct":             0.035,
        "capex_pct":          0.035,
        "nwc_pct_delta_rev":  0.010,
        "tax_rate":           0.21,
        "terminal_growth":    0.040,
        "exit_ebitda_mult":   30.0,
        "risk_free":          0.0685,
        "mrp":                0.065,
        "beta":               1.20,
        "cost_of_debt_pretax":0.095,
        "debt_weight":        0.01,
        "label": "Volume normalization, margin compression from rising tech/compliance costs, regulatory risk",
    },
    "Base": {
        "color": "#c9a96e",
        "fill": "rgba(201,169,110,0.08)",
        "revenue_growth":     [0.12, 0.10, 0.09, 0.08, 0.07],  # 5yr CAGR ~9%
        "ebitda_margin":      [0.68, 0.67, 0.67, 0.66, 0.65],  # slight normalisation
        "da_pct":             0.035,
        "capex_pct":          0.035,
        "nwc_pct_delta_rev":  0.010,
        "tax_rate":           0.21,
        "terminal_growth":    0.050,
        "exit_ebitda_mult":   35.0,
        "risk_free":          0.0685,
        "mrp":                0.060,
        "beta":               1.05,
        "cost_of_debt_pretax":0.090,
        "debt_weight":        0.01,
        "label": "Steady ADTV growth, new options products, margins normalise to 65% from peak 75%",
    },
    "Bull": {
        "color": "#4ab87a",
        "fill": "rgba(74,184,122,0.08)",
        "revenue_growth":     [0.18, 0.16, 0.14, 0.12, 0.10],  # 5yr CAGR ~14%
        "ebitda_margin":      [0.72, 0.72, 0.71, 0.70, 0.70],  # margins expand further
        "da_pct":             0.035,
        "capex_pct":          0.030,
        "nwc_pct_delta_rev":  0.010,
        "tax_rate":           0.21,
        "terminal_growth":    0.055,
        "exit_ebitda_mult":   40.0,
        "risk_free":          0.0685,
        "mrp":                0.055,
        "beta":               0.90,
        "cost_of_debt_pretax":0.085,
        "debt_weight":        0.01,
        "label": "Commodity super-cycle, new index futures/options, retail trading boom, international expansion",
    },
}

SCENARIO_NAMES = ["Bear", "Base", "Bull"]

# ═══════════════════════════ GRID RANGES ═══════════════════════════
WACC_RANGE      = [0.085, 0.090, 0.095, 0.100, 0.105, 0.110, 0.115]
TG_RANGE        = [0.025, 0.030, 0.035, 0.040, 0.045, 0.050, 0.055]
EXIT_MULT_RANGE = [25, 28, 30, 32, 35, 38, 40]
REVERSE_CAGRS   = [0.05, 0.08, 0.10, 0.12, 0.15, 0.18, 0.20, 0.25, 0.30]


# ═══════════════════════════ CALCULATIONS ═══════════════════════════
def build_operating_model(scenario):
    s = SCENARIOS[scenario]
    revenue = [COMPANY["year_zero_revenue"]]
    for gr in s["revenue_growth"]:
        revenue.append(revenue[-1] * (1 + gr))
    revenue = revenue[1:]

    margins = s["ebitda_margin"]
    ebitda  = [r * m for r, m in zip(revenue, margins)]
    da      = [r * s["da_pct"] for r in revenue]
    ebit    = [e - d for e, d in zip(ebitda, da)]
    capex   = [r * s["capex_pct"] for r in revenue]
    rev_seq = [COMPANY["year_zero_revenue"]] + revenue
    dnwc    = [(rev_seq[i + 1] - rev_seq[i]) * s["nwc_pct_delta_rev"] for i in range(5)]
    return revenue, ebitda, margins, da, ebit, capex, dnwc


def build_fcff(scenario):
    s = SCENARIOS[scenario]
    revenue, ebitda, margins, da, ebit, capex, dnwc = build_operating_model(scenario)
    nopat = [e * (1 - s["tax_rate"]) for e in ebit]
    fcff  = [n + d - c - nw for n, d, c, nw in zip(nopat, da, capex, dnwc)]
    return fcff, ebit, da, capex, dnwc, revenue, ebitda, margins, nopat


def compute_wacc(scenario):
    s = SCENARIOS[scenario]
    coe           = s["risk_free"] + s["beta"] * s["mrp"]
    cod_posttax   = s["cost_of_debt_pretax"] * (1 - s["tax_rate"])
    equity_weight = 1 - s["debt_weight"]
    wacc          = equity_weight * coe + s["debt_weight"] * cod_posttax
    return wacc, coe, cod_posttax, equity_weight


def dcf_valuation(scenario):
    s = SCENARIOS[scenario]
    fcff, ebit, da, capex, dnwc, revenue, ebitda, margins, nopat = build_fcff(scenario)
    wacc, coe, cod_posttax, equity_weight = compute_wacc(scenario)

    pv_fcffs = sum(f / ((1 + wacc) ** (i + 1)) for i, f in enumerate(fcff))

    # Method 1 — Perpetuity Growth
    terminal_fcf     = fcff[-1] * (1 + s["terminal_growth"])
    tv_perpetuity    = terminal_fcf / (wacc - s["terminal_growth"])
    pv_tv_perpetuity = tv_perpetuity / ((1 + wacc) ** 5)
    implied_ev_perp  = pv_fcffs + pv_tv_perpetuity

    # Method 2 — Exit EBITDA Multiple
    tv_multiple     = ebitda[-1] * s["exit_ebitda_mult"]
    pv_tv_multiple  = tv_multiple / ((1 + wacc) ** 5)
    implied_ev_mult = pv_fcffs + pv_tv_multiple

    avg_ev = (implied_ev_perp + implied_ev_mult) / 2

    # Bridge: EV + Net Cash = Equity Value (MCX is net cash positive)
    implied_equity = avg_ev - COMPANY["net_debt"]  # net_debt is negative, so this adds cash
    implied_price  = implied_equity / COMPANY["shares_outstanding"]
    upside         = implied_price / COMPANY["current_price"] - 1

    tv_pct_perp = pv_tv_perpetuity / implied_ev_perp if implied_ev_perp > 0 else 0
    tv_pct_mult = pv_tv_multiple   / implied_ev_mult  if implied_ev_mult  > 0 else 0

    return {
        "pv_fcffs":              pv_fcffs,
        "terminal_fcf":          terminal_fcf,
        "tv_perpetuity":         tv_perpetuity,
        "pv_tv_perpetuity":      pv_tv_perpetuity,
        "implied_ev_perpetuity": implied_ev_perp,
        "tv_multiple":           tv_multiple,
        "pv_tv_multiple":        pv_tv_multiple,
        "implied_ev_multiple":   implied_ev_mult,
        "avg_implied_ev":        avg_ev,
        "implied_equity":        implied_equity,
        "implied_price":         implied_price,
        "upside":                upside,
        "wacc":                  wacc,
        "coe":                   coe,
        "cod_posttax":           cod_posttax,
        "equity_weight":         equity_weight,
        "fcff":                  fcff,
        "nopat":                 nopat,
        "revenue":               revenue,
        "ebitda":                ebitda,
        "margins":               margins,
        "ebit":                  ebit,
        "da":                    da,
        "capex":                 capex,
        "dnwc":                  dnwc,
        "tv_pct_perpetuity":     tv_pct_perp,
        "tv_pct_multiple":       tv_pct_mult,
    }


def sensitivity_grid(wacc_range, var_range, var_type="terminal_growth"):
    """Returns 2D list of implied prices. Uses Base Case FCFFs."""
    fcff, _, _, _, _, _, ebitda, _, _ = build_fcff("Base")
    net_cash = -COMPANY["net_debt"]  # positive number (2944)
    grid = []
    for wacc in wacc_range:
        row = []
        for var in var_range:
            pv = sum(f / (1 + wacc) ** (i + 1) for i, f in enumerate(fcff))
            if var_type == "terminal_growth":
                if wacc <= var:
                    row.append(None)
                    continue
                tv    = (fcff[-1] * (1 + var)) / (wacc - var)
                pv_tv = tv / (1 + wacc) ** 5
            else:
                tv    = ebitda[-1] * var
                pv_tv = tv / (1 + wacc) ** 5
            ev    = pv + pv_tv
            price = (ev + net_cash) / COMPANY["shares_outstanding"]
            row.append(round(price, 0))
        grid.append(row)
    return grid


def reverse_dcf(test_cagrs, terminal_growth_override=None):
    """What revenue CAGR justifies the current market price?"""
    base = SCENARIOS["Base"]
    wacc, _, _, _ = compute_wacc("Base")
    tg   = terminal_growth_override if terminal_growth_override is not None else base["terminal_growth"]
    rev0 = COMPANY["year_zero_revenue"]
    net_cash = -COMPANY["net_debt"]
    results  = []

    for cagr in test_cagrs:
        revenue = [rev0 * (1 + cagr) ** y for y in range(1, 6)]
        # Use Base margins (test only revenue growth)
        margins = base["ebitda_margin"]
        ebitda  = [r * m for r, m in zip(revenue, margins)]
        da      = [r * base["da_pct"] for r in revenue]
        ebit    = [e - d for e, d in zip(ebitda, da)]
        capex   = [r * base["capex_pct"] for r in revenue]
        nwc     = [(rev0 * (1+cagr)**(i+1) - rev0 * (1+cagr)**i) * base["nwc_pct_delta_rev"]
                   for i in range(5)]
        fcff    = [e * (1 - base["tax_rate"]) + d - c - n
                   for e, d, c, n in zip(ebit, da, capex, nwc)]
        pv      = sum(f / (1 + wacc) ** (i + 1) for i, f in enumerate(fcff))
        if wacc <= tg:
            implied_ev = pv
        else:
            tv         = (ebitda[-1] * base["exit_ebitda_mult"]) / (1 + wacc) ** 5
            implied_ev = pv + tv
        implied_price = (implied_ev + net_cash) / COMPANY["shares_outstanding"]
        results.append({
            "cagr":          cagr,
            "implied_ev":    implied_ev,
            "implied_price": implied_price,
            "vs_market":     implied_ev - COMPANY["implied_market_ev"],
        })
    return results


if __name__ == "__main__":
    for sc in SCENARIO_NAMES:
        r = dcf_valuation(sc)
        print(f"{sc}: WACC={r['wacc']*100:.2f}% | Price=₹{r['implied_price']:.0f} | Upside={r['upside']*100:+.1f}%")

    g = sensitivity_grid(WACC_RANGE, TG_RANGE)
    print(f"\nSensitivity [WACC=10%, g=5%] (row 3, col 4): ₹{g[3][4]}")

    rdcf = reverse_dcf(REVERSE_CAGRS)
    print(f"\nReverse DCF at 20% CAGR: Implied Price ₹{rdcf[6]['implied_price']:.0f}")