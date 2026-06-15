import numpy as np

# ── FIXED ASSUMPTIONS (illustrative) ──
YEAR_0_REVENUE = 500.0
YEAR_0_EBITDA_MARGIN = 0.18
DA_PCT_REVENUE = 0.035
CAPEX_PCT_REVENUE = 0.04
NWC_PCT_INCREMENTAL_REVENUE = 0.02
TAX_RATE = 0.25
HOLD_PERIOD_YEARS = 5
TRANSACTION_FEES_PCT = 0.02
SENIOR_DEBT_RATE = 0.10
SENIOR_DEBT_AMORT_PCT = 0.10
SUB_DEBT_RATE = 0.14
RISK_FREE_RATE = 0.0685
MARKET_RISK_PREMIUM = 0.06
LEVERED_BETA = 1.1
TERMINAL_EBITDA_MULTIPLE = 8.0
PERPETUITY_GROWTH_RATE = 0.04

YEAR_0_EBITDA = YEAR_0_REVENUE * YEAR_0_EBITDA_MARGIN  # 90.0


def build_operating_model(revenue_growth, ebitda_margin_year5, year_zero_revenue=YEAR_0_REVENUE):
    revenue, prev = [], year_zero_revenue
    for _ in range(HOLD_PERIOD_YEARS):
        prev = prev * (1 + revenue_growth)
        revenue.append(prev)

    margins = [YEAR_0_EBITDA_MARGIN + (ebitda_margin_year5 - YEAR_0_EBITDA_MARGIN) * (y / HOLD_PERIOD_YEARS)
               for y in range(1, HOLD_PERIOD_YEARS + 1)]
    ebitda = [r * m for r, m in zip(revenue, margins)]
    da = [r * DA_PCT_REVENUE for r in revenue]
    ebit = [e - d for e, d in zip(ebitda, da)]
    capex = [r * CAPEX_PCT_REVENUE for r in revenue]

    rev_with_y0 = [year_zero_revenue] + revenue
    nwc = [(rev_with_y0[i + 1] - rev_with_y0[i]) * NWC_PCT_INCREMENTAL_REVENUE for i in range(HOLD_PERIOD_YEARS)]

    nopat = [e * (1 - TAX_RATE) for e in ebit]
    fcff = [n + d - c - w for n, d, c, w in zip(nopat, da, capex, nwc)]

    return {
        "revenue": revenue, "margins": margins, "ebitda": ebitda, "da": da,
        "ebit": ebit, "capex": capex, "nwc": nwc, "nopat": nopat, "fcff": fcff,
    }


def build_debt_schedule(ebit, da, capex, nwc, senior_debt, sub_debt):
    senior_balance, sub_balance = senior_debt, sub_debt
    senior_original = senior_debt
    rows = []
    for y in range(HOLD_PERIOD_YEARS):
        senior_interest = senior_balance * SENIOR_DEBT_RATE
        sub_interest = sub_balance * SUB_DEBT_RATE
        total_interest = senior_interest + sub_interest

        ebt = ebit[y] - total_interest
        tax = max(0.0, ebt * TAX_RATE)
        net_income = ebt - tax

        fcf_before_sweep = net_income + da[y] - capex[y] - nwc[y]

        mandatory_amort = min(senior_original * SENIOR_DEBT_AMORT_PCT, senior_balance)
        cash_after_mandatory = fcf_before_sweep - mandatory_amort
        senior_after_mandatory = senior_balance - mandatory_amort

        senior_sweep = max(0.0, min(cash_after_mandatory, senior_after_mandatory))
        cash_after_senior_sweep = cash_after_mandatory - senior_sweep
        senior_end = senior_after_mandatory - senior_sweep

        sub_sweep = max(0.0, min(cash_after_senior_sweep, sub_balance))
        sub_end = sub_balance - sub_sweep

        rows.append({
            "year": y + 1, "senior_beg": senior_balance, "sub_beg": sub_balance,
            "senior_interest": senior_interest, "sub_interest": sub_interest, "total_interest": total_interest,
            "ebt": ebt, "tax": tax, "net_income": net_income, "fcf_before_sweep": fcf_before_sweep,
            "mandatory_amort": mandatory_amort, "senior_sweep": senior_sweep, "sub_sweep": sub_sweep,
            "senior_end": senior_end, "sub_end": sub_end,
        })

        senior_balance, sub_balance = senior_end, sub_end
    return rows


def calculate_wacc(senior_debt, sub_debt, sponsor_equity):
    cost_of_equity = RISK_FREE_RATE + LEVERED_BETA * MARKET_RISK_PREMIUM
    total_debt = senior_debt + sub_debt
    cost_of_debt_pretax = (senior_debt * SENIOR_DEBT_RATE + sub_debt * SUB_DEBT_RATE) / total_debt
    cost_of_debt_posttax = cost_of_debt_pretax * (1 - TAX_RATE)
    total_capital = total_debt + sponsor_equity
    wacc = (sponsor_equity / total_capital) * cost_of_equity + (total_debt / total_capital) * cost_of_debt_posttax
    return {
        "cost_of_equity": cost_of_equity, "cost_of_debt_pretax": cost_of_debt_pretax,
        "cost_of_debt_posttax": cost_of_debt_posttax, "wacc": wacc,
        "equity_weight": sponsor_equity / total_capital, "debt_weight": total_debt / total_capital,
    }


def dcf_crosscheck(fcff, ebitda_final, wacc):
    pv_fcff = sum(f / (1 + wacc) ** (i + 1) for i, f in enumerate(fcff))

    tv_multiple = ebitda_final * TERMINAL_EBITDA_MULTIPLE
    pv_tv_multiple = tv_multiple / (1 + wacc) ** HOLD_PERIOD_YEARS
    implied_ev_multiple = pv_fcff + pv_tv_multiple

    terminal_fcf = fcff[-1] * (1 + PERPETUITY_GROWTH_RATE)
    tv_perp = terminal_fcf / (wacc - PERPETUITY_GROWTH_RATE)
    pv_tv_perp = tv_perp / (1 + wacc) ** HOLD_PERIOD_YEARS
    implied_ev_perp = pv_fcff + pv_tv_perp

    return {
        "pv_fcff": pv_fcff, "tv_multiple": tv_multiple, "pv_tv_multiple": pv_tv_multiple,
        "implied_ev_multiple": implied_ev_multiple, "terminal_fcf": terminal_fcf,
        "tv_perp": tv_perp, "pv_tv_perp": pv_tv_perp, "implied_ev_perp": implied_ev_perp,
    }


def calculate_returns(debt_schedule, exit_ev_ebitda, ebitda_final, sponsor_equity):
    exit_ev = ebitda_final * exit_ev_ebitda
    exit_net_debt = debt_schedule[-1]["senior_end"] + debt_schedule[-1]["sub_end"]
    exit_equity_value = exit_ev - exit_net_debt
    moic = exit_equity_value / sponsor_equity
    irr = moic ** (1 / HOLD_PERIOD_YEARS) - 1 if moic > 0 else -1.0
    return {
        "exit_ev": exit_ev, "exit_net_debt": exit_net_debt,
        "exit_equity_value": exit_equity_value, "moic": moic, "irr": irr,
    }


def irr_sensitivity_grid(debt_schedule, ebitda_final, senior_debt, sub_debt, year_zero_ebitda=YEAR_0_EBITDA):
    entry_mults = [6, 7, 8, 9, 10]
    exit_mults = [6, 7, 8, 9, 10]
    exit_net_debt = debt_schedule[-1]["senior_end"] + debt_schedule[-1]["sub_end"]
    grid = np.full((len(entry_mults), len(exit_mults)), np.nan)
    for i, em in enumerate(entry_mults):
        entry_ev = year_zero_ebitda * em
        total_uses = entry_ev * (1 + TRANSACTION_FEES_PCT)
        sponsor_equity = total_uses - senior_debt - sub_debt
        if sponsor_equity <= 0:
            continue  # leverage exceeds purchase price at this entry multiple -- not a viable structure
        for j, xm in enumerate(exit_mults):
            exit_equity_value = ebitda_final * xm - exit_net_debt
            moic = exit_equity_value / sponsor_equity
            irr = moic ** (1 / HOLD_PERIOD_YEARS) - 1 if moic > 0 else -1.0
            grid[i, j] = irr
    return entry_mults, exit_mults, grid


def run_model(entry_ev_ebitda, exit_ev_ebitda, senior_debt_mult, sub_debt_mult,
               revenue_growth, ebitda_margin_year5, year_zero_revenue=YEAR_0_REVENUE):
    year_zero_ebitda = year_zero_revenue * YEAR_0_EBITDA_MARGIN
    om = build_operating_model(revenue_growth, ebitda_margin_year5, year_zero_revenue)

    entry_ev = year_zero_ebitda * entry_ev_ebitda
    fees = entry_ev * TRANSACTION_FEES_PCT
    total_uses = entry_ev + fees

    senior_debt = year_zero_ebitda * senior_debt_mult
    sub_debt = year_zero_ebitda * sub_debt_mult
    sponsor_equity = total_uses - senior_debt - sub_debt

    debt_schedule = build_debt_schedule(om["ebit"], om["da"], om["capex"], om["nwc"], senior_debt, sub_debt)

    wacc = calculate_wacc(senior_debt, sub_debt, sponsor_equity)
    dcf = dcf_crosscheck(om["fcff"], om["ebitda"][-1], wacc["wacc"])
    returns = calculate_returns(debt_schedule, exit_ev_ebitda, om["ebitda"][-1], sponsor_equity)
    entry_mults, exit_mults, grid = irr_sensitivity_grid(debt_schedule, om["ebitda"][-1], senior_debt, sub_debt, year_zero_ebitda)

    return {
        "om": om, "entry_ev": entry_ev, "fees": fees, "total_uses": total_uses,
        "senior_debt": senior_debt, "sub_debt": sub_debt, "sponsor_equity": sponsor_equity,
        "debt_schedule": debt_schedule, "wacc": wacc, "dcf": dcf, "returns": returns,
        "entry_mults": entry_mults, "exit_mults": exit_mults, "grid": grid,
        "year_zero_revenue": year_zero_revenue, "year_zero_ebitda": year_zero_ebitda,
    }


if __name__ == "__main__":
    r = run_model(8.0, 8.0, 4.0, 1.5, 0.08, 0.20)
    print("Entry EV:", r["entry_ev"], "Total Uses:", r["total_uses"])
    print("Senior:", r["senior_debt"], "Sub:", r["sub_debt"], "Sponsor Equity:", r["sponsor_equity"])
    print("EBITDA Y5:", r["om"]["ebitda"][-1])
    print("Final senior:", r["debt_schedule"][-1]["senior_end"], "Final sub:", r["debt_schedule"][-1]["sub_end"])
    print("WACC:", r["wacc"]["wacc"])
    print("DCF implied EV (multiple):", r["dcf"]["implied_ev_multiple"])
    print("DCF implied EV (perpetuity):", r["dcf"]["implied_ev_perp"])
    print("Exit equity value:", r["returns"]["exit_equity_value"])
    print("MOIC:", r["returns"]["moic"], "IRR:", r["returns"]["irr"])
    print("Grid[2,2] (8x entry, 8x exit):", r["grid"][2, 2])
