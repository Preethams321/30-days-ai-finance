from io import BytesIO
import xlsxwriter
from xlsxwriter.utility import xl_col_to_name

# ── Row map: Assumptions sheet ──
A_YEAR0_REV, A_YEAR0_MARGIN, A_ENTRY_MULT = 4, 5, 6
A_REV_GROWTH, A_MARGIN_Y5, A_DA_PCT, A_CAPEX_PCT, A_NWC_PCT, A_TAX_RATE, A_HOLD_YEARS = 9, 10, 11, 12, 13, 14, 15
A_FEES_PCT, A_SENIOR_MULT, A_SENIOR_RATE, A_SENIOR_AMORT, A_SUB_MULT, A_SUB_RATE = 18, 19, 20, 21, 22, 23
A_EXIT_MULT = 26
A_RF, A_MRP, A_BETA = 29, 30, 31
A_TERMINAL_MULT, A_PERP_GROWTH = 34, 35

# ── Row map: Operating Model sheet (cols B..G = Year0..Year5) ──
OM_REVENUE, OM_MARGIN, OM_EBITDA, OM_DA, OM_EBIT, OM_CAPEX, OM_NWC, OM_NOPAT, OM_FCFF = 4, 5, 6, 7, 8, 9, 10, 11, 12

# ── Row map: Sources & Uses sheet ──
SU_ENTRY_EV, SU_FEES, SU_TOTAL_USES = 4, 5, 6
SU_SENIOR, SU_SUB, SU_SPONSOR_EQ, SU_TOTAL_SOURCES, SU_CHECK = 9, 10, 11, 12, 14
SU_LEVERAGE, SU_EQUITY_PCT = 16, 17

# ── Row map: Debt Schedule sheet (cols B..F = Year1..Year5) ──
(DS_SR_BEG, DS_SR_INT, DS_SUB_BEG, DS_SUB_INT, DS_TOT_INT, DS_EBIT, DS_EBT, DS_TAX, DS_NI,
 DS_DA, DS_CAPEX, DS_NWC, DS_FCF_PRE, DS_MAND, DS_CASH_A, DS_SR_AFTER, DS_SR_SWEEP,
 DS_CASH_B, DS_SR_END, DS_SUB_SWEEP, DS_SUB_END, DS_TOTAL_DEBT) = range(4, 26)

# ── Row map: WACC sheet ──
W_RF, W_BETA, W_MRP, W_COE = 4, 5, 6, 7
W_SR_DEBT, W_SR_RATE, W_SUB_DEBT, W_SUB_RATE, W_TOT_DEBT, W_PRETAX_COD, W_TAXRATE, W_POSTTAX_COD = 10, 11, 12, 13, 14, 15, 16, 17
W_EQUITY, W_TOTCAP, W_EQ_WT, W_DEBT_WT, W_WACC = 20, 21, 22, 23, 24

# ── Row map: DCF CrossCheck sheet (cols B..F = Year1..Year5) ──
DCF_FCFF, DCF_DF, DCF_PV = 4, 5, 6
DCF_SUM_PV = 8
DCF_TERM_EBITDA, DCF_TERM_MULT, DCF_TV1, DCF_PV_TV1, DCF_EV1 = 11, 12, 13, 14, 15
DCF_TERM_FCFF, DCF_PERP_G, DCF_TERM_FCF_NEXT, DCF_TV2, DCF_PV_TV2, DCF_EV2 = 18, 19, 20, 21, 22, 23
DCF_ENTRY_EV, DCF_CMP1, DCF_CMP2, DCF_PREM1, DCF_PREM2 = 26, 27, 28, 29, 30

# ── Row map: Returns sheet ──
R_EXIT_EBITDA, R_EXIT_MULT, R_EXIT_EV, R_EXIT_SR, R_EXIT_SUB, R_EXIT_ND, R_EXIT_EQ = 4, 5, 6, 7, 8, 9, 10
R_INIT_EQ, R_MOIC, R_HOLD, R_IRR = 13, 14, 15, 16
R_CF_HEADER, R_CF_ROW, R_IRR_CHECK = 19, 20, 21
R_SENS_HEADER, R_SENS_START = 25, 26  # 5 rows: 26-30


def generate_excel(p):
    """p = dict with entry_ev_ebitda, exit_ev_ebitda, senior_debt_mult, sub_debt_mult,
    revenue_growth, ebitda_margin_year5, and optionally company_name, sector,
    currency_short, currency_long, year_zero_revenue, is_fictional"""
    company_name = p.get("company_name", "Bharat Precision Components Ltd")
    sector = p.get("sector", "Auto Ancillary / Precision Manufacturing")
    currency_short = p.get("currency_short", "\u20b9 Cr")
    currency_long = p.get("currency_long", "\u20b9 Crores")
    year_zero_revenue = p.get("year_zero_revenue", 500.0)
    is_fictional = p.get("is_fictional", True)

    output = BytesIO()
    wb = xlsxwriter.Workbook(output, {"in_memory": True})

    NAVY = "#3a5a7a"
    GOLD = "#c9a96e"
    LIGHT_YELLOW = "#FFF6D9"

    fmt_title = wb.add_format({"bold": True, "font_size": 13, "font_color": "#FFFFFF",
                                "bg_color": NAVY, "valign": "vcenter", "border": 1})
    fmt_section = wb.add_format({"bold": True, "font_color": "#FFFFFF", "bg_color": GOLD, "border": 1})
    fmt_label = wb.add_format({"font_name": "Arial", "font_size": 10})
    fmt_label_b = wb.add_format({"font_name": "Arial", "font_size": 10, "bold": True})
    fmt_input = wb.add_format({"font_name": "Arial", "font_size": 10, "font_color": "#0000FF",
                                "bg_color": LIGHT_YELLOW, "num_format": "#,##0.0", "border": 1})
    fmt_input_pct = wb.add_format({"font_name": "Arial", "font_size": 10, "font_color": "#0000FF",
                                    "bg_color": LIGHT_YELLOW, "num_format": "0.0%", "border": 1})
    fmt_input_mult = wb.add_format({"font_name": "Arial", "font_size": 10, "font_color": "#0000FF",
                                     "bg_color": LIGHT_YELLOW, "num_format": '0.00"x"', "border": 1})
    fmt_input_int = wb.add_format({"font_name": "Arial", "font_size": 10, "font_color": "#0000FF",
                                    "bg_color": LIGHT_YELLOW, "num_format": "0", "border": 1})
    fmt_num = wb.add_format({"font_name": "Arial", "font_size": 10, "num_format": "#,##0.0;(#,##0.0);\"-\""})
    fmt_num3 = wb.add_format({"font_name": "Arial", "font_size": 10, "num_format": "#,##0.000;(#,##0.000)"})
    fmt_num_b = wb.add_format({"font_name": "Arial", "font_size": 10, "bold": True,
                                "num_format": "#,##0.0;(#,##0.0);\"-\"", "top": 1})
    fmt_pct = wb.add_format({"font_name": "Arial", "font_size": 10, "num_format": "0.0%"})
    fmt_pct_b = wb.add_format({"font_name": "Arial", "font_size": 10, "bold": True, "num_format": "0.0%", "top": 1})
    fmt_mult = wb.add_format({"font_name": "Arial", "font_size": 10, "num_format": '0.00"x"'})
    fmt_mult_b = wb.add_format({"font_name": "Arial", "font_size": 10, "bold": True, "num_format": '0.00"x"', "top": 1})
    fmt_link = wb.add_format({"font_name": "Arial", "font_size": 10, "font_color": "#008000",
                               "num_format": "#,##0.0;(#,##0.0);\"-\""})
    fmt_link_pct = wb.add_format({"font_name": "Arial", "font_size": 10, "font_color": "#008000", "num_format": "0.0%"})
    fmt_link_mult = wb.add_format({"font_name": "Arial", "font_size": 10, "font_color": "#008000", "num_format": '0.00"x"'})
    fmt_year = wb.add_format({"font_name": "Arial", "font_size": 10, "bold": True, "align": "center",
                               "bg_color": "#E8E8E8", "border": 1})
    fmt_big = wb.add_format({"font_name": "Arial", "font_size": 16, "bold": True, "font_color": NAVY,
                              "num_format": '0.00"x"'})
    fmt_big_pct = wb.add_format({"font_name": "Arial", "font_size": 16, "bold": True, "font_color": NAVY,
                                  "num_format": "0.0%"})
    fmt_wrap = wb.add_format({"font_name": "Arial", "font_size": 10, "text_wrap": True, "valign": "top"})
    fmt_header_text = wb.add_format({"font_name": "Arial", "font_size": 16, "bold": True, "font_color": NAVY})

    # ════════════════════════ ASSUMPTIONS ════════════════════════
    ws = wb.add_worksheet("Assumptions")
    ws.set_column("A:A", 46)
    ws.set_column("B:B", 14)
    ws.merge_range("A1:C1", f"{company_name.upper()} \u2014 LBO MODEL ASSUMPTIONS", fmt_title)
    ws.write_comment("A1", "Edit only the blue cells in this tab. Every other tab recalculates automatically.")

    def section(row, text):
        ws.merge_range(row - 1, 0, row - 1, 2, text, fmt_section)

    section(3, "ENTRY ASSUMPTIONS")
    ws.write(A_YEAR0_REV - 1, 0, f"Year 0 Revenue ({currency_short})", fmt_label)
    ws.write(A_YEAR0_REV - 1, 1, year_zero_revenue, fmt_input)
    ws.write(A_YEAR0_MARGIN - 1, 0, "Year 0 EBITDA Margin", fmt_label)
    ws.write(A_YEAR0_MARGIN - 1, 1, 0.18, fmt_input_pct)
    ws.write(A_ENTRY_MULT - 1, 0, "Entry EV / EBITDA Multiple", fmt_label)
    ws.write(A_ENTRY_MULT - 1, 1, p["entry_ev_ebitda"], fmt_input_mult)

    section(8, "OPERATING ASSUMPTIONS (5-Year Hold)")
    ws.write(A_REV_GROWTH - 1, 0, "Revenue Growth Rate (YoY)", fmt_label)
    ws.write(A_REV_GROWTH - 1, 1, p["revenue_growth"], fmt_input_pct)
    ws.write(A_MARGIN_Y5 - 1, 0, "EBITDA Margin \u2014 Year 5 Target", fmt_label)
    ws.write(A_MARGIN_Y5 - 1, 1, p["ebitda_margin_year5"], fmt_input_pct)
    ws.write(A_DA_PCT - 1, 0, "D&A (% of Revenue)", fmt_label)
    ws.write(A_DA_PCT - 1, 1, 0.035, fmt_input_pct)
    ws.write(A_CAPEX_PCT - 1, 0, "Capex (% of Revenue)", fmt_label)
    ws.write(A_CAPEX_PCT - 1, 1, 0.04, fmt_input_pct)
    ws.write(A_NWC_PCT - 1, 0, "Incremental NWC (% of Revenue Increase)", fmt_label)
    ws.write(A_NWC_PCT - 1, 1, 0.02, fmt_input_pct)
    ws.write(A_TAX_RATE - 1, 0, "Tax Rate", fmt_label)
    ws.write(A_TAX_RATE - 1, 1, 0.25, fmt_input_pct)
    ws.write(A_HOLD_YEARS - 1, 0, "Hold Period (Years)", fmt_label)
    ws.write(A_HOLD_YEARS - 1, 1, 5, fmt_input_int)

    section(17, "FINANCING STRUCTURE")
    ws.write(A_FEES_PCT - 1, 0, "Transaction Fees (% of EV)", fmt_label)
    ws.write(A_FEES_PCT - 1, 1, 0.02, fmt_input_pct)
    ws.write(A_SENIOR_MULT - 1, 0, "Senior Debt / EBITDA", fmt_label)
    ws.write(A_SENIOR_MULT - 1, 1, p["senior_debt_mult"], fmt_input_mult)
    ws.write(A_SENIOR_RATE - 1, 0, "Senior Debt Interest Rate", fmt_label)
    ws.write(A_SENIOR_RATE - 1, 1, 0.10, fmt_input_pct)
    ws.write(A_SENIOR_AMORT - 1, 0, "Senior Debt Mandatory Amortization (% of original p.a.)", fmt_label)
    ws.write(A_SENIOR_AMORT - 1, 1, 0.10, fmt_input_pct)
    ws.write(A_SUB_MULT - 1, 0, "Subordinated Debt / EBITDA", fmt_label)
    ws.write(A_SUB_MULT - 1, 1, p["sub_debt_mult"], fmt_input_mult)
    ws.write(A_SUB_RATE - 1, 0, "Subordinated Debt Interest Rate", fmt_label)
    ws.write(A_SUB_RATE - 1, 1, 0.14, fmt_input_pct)

    section(25, "EXIT ASSUMPTIONS")
    ws.write(A_EXIT_MULT - 1, 0, "Exit EV / EBITDA Multiple", fmt_label)
    ws.write(A_EXIT_MULT - 1, 1, p["exit_ev_ebitda"], fmt_input_mult)

    section(28, "WACC / CAPM INPUTS")
    ws.write(A_RF - 1, 0, "Risk-Free Rate (India 10Y G-Sec)", fmt_label)
    ws.write(A_RF - 1, 1, 0.0685, fmt_input_pct)
    ws.write(A_MRP - 1, 0, "Market Risk Premium", fmt_label)
    ws.write(A_MRP - 1, 1, 0.06, fmt_input_pct)
    ws.write(A_BETA - 1, 0, "Levered Beta", fmt_label)
    ws.write(A_BETA - 1, 1, 1.1, fmt_input_mult)

    section(33, "DCF CROSS-CHECK ASSUMPTIONS")
    ws.write(A_TERMINAL_MULT - 1, 0, "Terminal EBITDA Multiple", fmt_label)
    ws.write(A_TERMINAL_MULT - 1, 1, 8.0, fmt_input_mult)
    ws.write(A_PERP_GROWTH - 1, 0, "Perpetuity Growth Rate", fmt_label)
    ws.write(A_PERP_GROWTH - 1, 1, 0.04, fmt_input_pct)

    # ════════════════════════ OPERATING MODEL ════════════════════════
    ws = wb.add_worksheet("Operating Model")
    ws.set_column("A:A", 34)
    ws.set_column("B:G", 12)
    ws.merge_range("A1:G1", f"OPERATING MODEL ({currency_short})", fmt_title)
    ws.write(2, 0, "", fmt_year)
    for i, label in enumerate(["Year 0", "Year 1", "Year 2", "Year 3", "Year 4", "Year 5"]):
        ws.write_string(2, 1 + i, label, fmt_year)

    cols = [xl_col_to_name(c) for c in range(1, 7)]  # B..G

    ws.write(OM_REVENUE - 1, 0, "Revenue", fmt_label)
    ws.write_formula(OM_REVENUE - 1, 1, "=Assumptions!B4", fmt_link)
    for i in range(1, 6):
        ws.write_formula(OM_REVENUE - 1, 1 + i, f"={cols[i-1]}{OM_REVENUE}*(1+Assumptions!$B${A_REV_GROWTH})", fmt_num)

    ws.write(OM_MARGIN - 1, 0, "EBITDA Margin %", fmt_label)
    ws.write_formula(OM_MARGIN - 1, 1, "=Assumptions!B5", fmt_link_pct)
    for i in range(1, 6):
        ws.write_formula(OM_MARGIN - 1, 1 + i,
                          f"=Assumptions!$B${A_YEAR0_MARGIN}+(Assumptions!$B${A_MARGIN_Y5}-Assumptions!$B${A_YEAR0_MARGIN})*({i}/Assumptions!$B${A_HOLD_YEARS})",
                          fmt_pct)

    ws.write(OM_EBITDA - 1, 0, "EBITDA", fmt_label_b)
    for i in range(0, 6):
        c = cols[i]
        ws.write_formula(OM_EBITDA - 1, 1 + i, f"={c}{OM_REVENUE}*{c}{OM_MARGIN}", fmt_num_b)

    ws.write(OM_DA - 1, 0, "D&A", fmt_label)
    for i in range(0, 6):
        c = cols[i]
        ws.write_formula(OM_DA - 1, 1 + i, f"={c}{OM_REVENUE}*Assumptions!$B${A_DA_PCT}", fmt_num)

    ws.write(OM_EBIT - 1, 0, "EBIT", fmt_label_b)
    for i in range(0, 6):
        c = cols[i]
        ws.write_formula(OM_EBIT - 1, 1 + i, f"={c}{OM_EBITDA}-{c}{OM_DA}", fmt_num_b)

    ws.write(OM_CAPEX - 1, 0, "Capex", fmt_label)
    for i in range(0, 6):
        c = cols[i]
        ws.write_formula(OM_CAPEX - 1, 1 + i, f"={c}{OM_REVENUE}*Assumptions!$B${A_CAPEX_PCT}", fmt_num)

    ws.write(OM_NWC - 1, 0, "Incremental NWC Investment", fmt_label)
    ws.write_number(OM_NWC - 1, 1, 0, fmt_num)
    for i in range(1, 6):
        c, prev = cols[i], cols[i - 1]
        ws.write_formula(OM_NWC - 1, 1 + i, f"=({c}{OM_REVENUE}-{prev}{OM_REVENUE})*Assumptions!$B${A_NWC_PCT}", fmt_num)

    ws.write(OM_NOPAT - 1, 0, "NOPAT (EBIT \u00d7 (1-Tax))", fmt_label)
    for i in range(0, 6):
        c = cols[i]
        ws.write_formula(OM_NOPAT - 1, 1 + i, f"={c}{OM_EBIT}*(1-Assumptions!$B${A_TAX_RATE})", fmt_num)

    ws.write(OM_FCFF - 1, 0, "Unlevered FCF (FCFF)", fmt_label_b)
    for i in range(0, 6):
        c = cols[i]
        ws.write_formula(OM_FCFF - 1, 1 + i, f"={c}{OM_NOPAT}+{c}{OM_DA}-{c}{OM_CAPEX}-{c}{OM_NWC}", fmt_num_b)

    # ════════════════════════ SOURCES & USES ════════════════════════
    ws = wb.add_worksheet("Sources & Uses")
    ws.set_column("A:A", 38)
    ws.set_column("B:B", 14)
    ws.merge_range("A1:B1", f"SOURCES & USES ({currency_short})", fmt_title)

    section(3, "USES OF FUNDS")
    ws.write(SU_ENTRY_EV - 1, 0, "Entry Enterprise Value", fmt_label)
    ws.write_formula(SU_ENTRY_EV - 1, 1, f"='Operating Model'!B{OM_EBITDA}*Assumptions!B{A_ENTRY_MULT}", fmt_link)
    ws.write(SU_FEES - 1, 0, "Transaction Fees", fmt_label)
    ws.write_formula(SU_FEES - 1, 1, f"=B{SU_ENTRY_EV}*Assumptions!B{A_FEES_PCT}", fmt_num)
    ws.write(SU_TOTAL_USES - 1, 0, "Total Uses", fmt_label_b)
    ws.write_formula(SU_TOTAL_USES - 1, 1, f"=B{SU_ENTRY_EV}+B{SU_FEES}", fmt_num_b)

    section(8, "SOURCES OF FUNDS")
    ws.write(SU_SENIOR - 1, 0, "Senior Debt", fmt_label)
    ws.write_formula(SU_SENIOR - 1, 1, f"='Operating Model'!B{OM_EBITDA}*Assumptions!B{A_SENIOR_MULT}", fmt_link)
    ws.write(SU_SUB - 1, 0, "Subordinated Debt", fmt_label)
    ws.write_formula(SU_SUB - 1, 1, f"='Operating Model'!B{OM_EBITDA}*Assumptions!B{A_SUB_MULT}", fmt_link)
    ws.write(SU_SPONSOR_EQ - 1, 0, "Sponsor Equity (Plug)", fmt_label)
    ws.write_formula(SU_SPONSOR_EQ - 1, 1, f"=B{SU_TOTAL_USES}-B{SU_SENIOR}-B{SU_SUB}", fmt_num)
    ws.write(SU_TOTAL_SOURCES - 1, 0, "Total Sources", fmt_label_b)
    ws.write_formula(SU_TOTAL_SOURCES - 1, 1, f"=B{SU_SENIOR}+B{SU_SUB}+B{SU_SPONSOR_EQ}", fmt_num_b)

    ws.write(SU_CHECK - 1, 0, "Check: Uses \u2212 Sources (must be 0)", fmt_label)
    ws.write_formula(SU_CHECK - 1, 1, f"=B{SU_TOTAL_USES}-B{SU_TOTAL_SOURCES}", fmt_num)

    section(SU_LEVERAGE - 1, "CAPITAL STRUCTURE METRICS")
    ws.write(SU_LEVERAGE - 1, 0, "Total Debt / EBITDA (Entry Leverage)", fmt_label)
    ws.write_formula(SU_LEVERAGE - 1, 1, f"=(B{SU_SENIOR}+B{SU_SUB})/'Operating Model'!B{OM_EBITDA}", fmt_mult)
    ws.write(SU_EQUITY_PCT - 1, 0, "Sponsor Equity % of Total Capital", fmt_label)
    ws.write_formula(SU_EQUITY_PCT - 1, 1, f"=B{SU_SPONSOR_EQ}/B{SU_TOTAL_SOURCES}", fmt_pct)

    # ════════════════════════ DEBT SCHEDULE ════════════════════════
    ws = wb.add_worksheet("Debt Schedule")
    ws.set_column("A:A", 40)
    ws.set_column("B:F", 12)
    ws.merge_range("A1:F1", f"DEBT SCHEDULE \u2014 CASH SWEEP ({currency_short})", fmt_title)
    ws.write(2, 0, "", fmt_year)
    for i, label in enumerate(["Year 1", "Year 2", "Year 3", "Year 4", "Year 5"]):
        ws.write_string(2, 1 + i, label, fmt_year)

    ds_cols = [xl_col_to_name(c) for c in range(1, 6)]  # B..F
    om_cols = [xl_col_to_name(c) for c in range(2, 7)]  # C..G (Operating Model Year1..5)

    labels = {
        DS_SR_BEG: "Senior Debt \u2014 Beginning Balance",
        DS_SR_INT: "Senior Debt \u2014 Interest Expense",
        DS_SUB_BEG: "Subordinated Debt \u2014 Beginning Balance",
        DS_SUB_INT: "Subordinated Debt \u2014 Interest Expense",
        DS_TOT_INT: "Total Interest Expense",
        DS_EBIT: "EBIT (from Operating Model)",
        DS_EBT: "EBT (EBIT \u2212 Interest)",
        DS_TAX: "Taxes",
        DS_NI: "Net Income",
        DS_DA: "D&A (from Operating Model)",
        DS_CAPEX: "Capex (from Operating Model)",
        DS_NWC: "Incremental NWC Investment",
        DS_FCF_PRE: "Free Cash Flow Before Sweep",
        DS_MAND: "Mandatory Senior Amortization",
        DS_CASH_A: "Cash Available After Mandatory Amort",
        DS_SR_AFTER: "Senior Balance After Mandatory Amort",
        DS_SR_SWEEP: "Senior Debt \u2014 Cash Sweep",
        DS_CASH_B: "Cash Available After Senior Sweep",
        DS_SR_END: "Senior Debt \u2014 Ending Balance",
        DS_SUB_SWEEP: "Subordinated Debt \u2014 Cash Sweep",
        DS_SUB_END: "Subordinated Debt \u2014 Ending Balance",
        DS_TOTAL_DEBT: "Total Debt \u2014 Ending Balance",
    }
    bold_rows = {DS_TOT_INT, DS_NI, DS_FCF_PRE, DS_SR_END, DS_SUB_END, DS_TOTAL_DEBT}
    for r, lbl in labels.items():
        ws.write(r - 1, 0, lbl, fmt_label_b if r in bold_rows else fmt_label)

    for i in range(5):  # i = 0..4 -> Year1..5, column letters
        c = ds_cols[i]
        omc = om_cols[i]
        prev = ds_cols[i - 1] if i > 0 else None

        f_num = fmt_num_b if False else fmt_num
        if i == 0:
            ws.write_formula(DS_SR_BEG - 1, 1 + i, f"='Sources & Uses'!B{SU_SENIOR}", fmt_link)
            ws.write_formula(DS_SUB_BEG - 1, 1 + i, f"='Sources & Uses'!B{SU_SUB}", fmt_link)
        else:
            ws.write_formula(DS_SR_BEG - 1, 1 + i, f"={prev}{DS_SR_END}", fmt_num)
            ws.write_formula(DS_SUB_BEG - 1, 1 + i, f"={prev}{DS_SUB_END}", fmt_num)

        ws.write_formula(DS_SR_INT - 1, 1 + i, f"={c}{DS_SR_BEG}*Assumptions!$B${A_SENIOR_RATE}", fmt_num)
        ws.write_formula(DS_SUB_INT - 1, 1 + i, f"={c}{DS_SUB_BEG}*Assumptions!$B${A_SUB_RATE}", fmt_num)
        ws.write_formula(DS_TOT_INT - 1, 1 + i, f"={c}{DS_SR_INT}+{c}{DS_SUB_INT}", fmt_num_b)

        ws.write_formula(DS_EBIT - 1, 1 + i, f"='Operating Model'!{omc}{OM_EBIT}", fmt_link)
        ws.write_formula(DS_EBT - 1, 1 + i, f"={c}{DS_EBIT}-{c}{DS_TOT_INT}", fmt_num)
        ws.write_formula(DS_TAX - 1, 1 + i, f"=MAX(0,{c}{DS_EBT}*Assumptions!$B${A_TAX_RATE})", fmt_num)
        ws.write_formula(DS_NI - 1, 1 + i, f"={c}{DS_EBT}-{c}{DS_TAX}", fmt_num_b)

        ws.write_formula(DS_DA - 1, 1 + i, f"='Operating Model'!{omc}{OM_DA}", fmt_link)
        ws.write_formula(DS_CAPEX - 1, 1 + i, f"='Operating Model'!{omc}{OM_CAPEX}", fmt_link)
        ws.write_formula(DS_NWC - 1, 1 + i, f"='Operating Model'!{omc}{OM_NWC}", fmt_link)

        ws.write_formula(DS_FCF_PRE - 1, 1 + i, f"={c}{DS_NI}+{c}{DS_DA}-{c}{DS_CAPEX}-{c}{DS_NWC}", fmt_num_b)

        ws.write_formula(DS_MAND - 1, 1 + i, f"=MIN('Sources & Uses'!$B${SU_SENIOR}*Assumptions!$B${A_SENIOR_AMORT},{c}{DS_SR_BEG})", fmt_num)
        ws.write_formula(DS_CASH_A - 1, 1 + i, f"={c}{DS_FCF_PRE}-{c}{DS_MAND}", fmt_num)
        ws.write_formula(DS_SR_AFTER - 1, 1 + i, f"={c}{DS_SR_BEG}-{c}{DS_MAND}", fmt_num)
        ws.write_formula(DS_SR_SWEEP - 1, 1 + i, f"=MAX(0,MIN({c}{DS_CASH_A},{c}{DS_SR_AFTER}))", fmt_num)
        ws.write_formula(DS_CASH_B - 1, 1 + i, f"={c}{DS_CASH_A}-{c}{DS_SR_SWEEP}", fmt_num)
        ws.write_formula(DS_SR_END - 1, 1 + i, f"={c}{DS_SR_AFTER}-{c}{DS_SR_SWEEP}", fmt_num_b)
        ws.write_formula(DS_SUB_SWEEP - 1, 1 + i, f"=MAX(0,MIN({c}{DS_CASH_B},{c}{DS_SUB_BEG}))", fmt_num)
        ws.write_formula(DS_SUB_END - 1, 1 + i, f"={c}{DS_SUB_BEG}-{c}{DS_SUB_SWEEP}", fmt_num_b)
        ws.write_formula(DS_TOTAL_DEBT - 1, 1 + i, f"={c}{DS_SR_END}+{c}{DS_SUB_END}", fmt_num_b)

    # ════════════════════════ WACC ════════════════════════
    ws = wb.add_worksheet("WACC")
    ws.set_column("A:A", 38)
    ws.set_column("B:B", 14)
    ws.merge_range("A1:B1", "WACC / CAPM", fmt_title)

    section(3, "COST OF EQUITY (CAPM)")
    ws.write(W_RF - 1, 0, "Risk-Free Rate", fmt_label)
    ws.write_formula(W_RF - 1, 1, f"=Assumptions!B{A_RF}", fmt_link_pct)
    ws.write(W_BETA - 1, 0, "Levered Beta", fmt_label)
    ws.write_formula(W_BETA - 1, 1, f"=Assumptions!B{A_BETA}", fmt_link_mult)
    ws.write(W_MRP - 1, 0, "Market Risk Premium", fmt_label)
    ws.write_formula(W_MRP - 1, 1, f"=Assumptions!B{A_MRP}", fmt_link_pct)
    ws.write(W_COE - 1, 0, "Cost of Equity", fmt_label_b)
    ws.write_formula(W_COE - 1, 1, f"=B{W_RF}+B{W_BETA}*B{W_MRP}", fmt_pct_b)

    section(9, "COST OF DEBT")
    ws.write(W_SR_DEBT - 1, 0, "Senior Debt", fmt_label)
    ws.write_formula(W_SR_DEBT - 1, 1, f"='Sources & Uses'!B{SU_SENIOR}", fmt_link)
    ws.write(W_SR_RATE - 1, 0, "Senior Debt Rate", fmt_label)
    ws.write_formula(W_SR_RATE - 1, 1, f"=Assumptions!B{A_SENIOR_RATE}", fmt_link_pct)
    ws.write(W_SUB_DEBT - 1, 0, "Subordinated Debt", fmt_label)
    ws.write_formula(W_SUB_DEBT - 1, 1, f"='Sources & Uses'!B{SU_SUB}", fmt_link)
    ws.write(W_SUB_RATE - 1, 0, "Subordinated Debt Rate", fmt_label)
    ws.write_formula(W_SUB_RATE - 1, 1, f"=Assumptions!B{A_SUB_RATE}", fmt_link_pct)
    ws.write(W_TOT_DEBT - 1, 0, "Total Debt", fmt_label_b)
    ws.write_formula(W_TOT_DEBT - 1, 1, f"=B{W_SR_DEBT}+B{W_SUB_DEBT}", fmt_num_b)
    ws.write(W_PRETAX_COD - 1, 0, "Blended Pre-Tax Cost of Debt", fmt_label)
    ws.write_formula(W_PRETAX_COD - 1, 1, f"=(B{W_SR_DEBT}*B{W_SR_RATE}+B{W_SUB_DEBT}*B{W_SUB_RATE})/B{W_TOT_DEBT}", fmt_pct)
    ws.write(W_TAXRATE - 1, 0, "Tax Rate", fmt_label)
    ws.write_formula(W_TAXRATE - 1, 1, f"=Assumptions!B{A_TAX_RATE}", fmt_link_pct)
    ws.write(W_POSTTAX_COD - 1, 0, "Post-Tax Cost of Debt", fmt_label_b)
    ws.write_formula(W_POSTTAX_COD - 1, 1, f"=B{W_PRETAX_COD}*(1-B{W_TAXRATE})", fmt_pct_b)

    section(19, "WACC")
    ws.write(W_EQUITY - 1, 0, "Sponsor Equity", fmt_label)
    ws.write_formula(W_EQUITY - 1, 1, f"='Sources & Uses'!B{SU_SPONSOR_EQ}", fmt_link)
    ws.write(W_TOTCAP - 1, 0, "Total Capital (Debt + Equity)", fmt_label)
    ws.write_formula(W_TOTCAP - 1, 1, f"=B{W_TOT_DEBT}+B{W_EQUITY}", fmt_num)
    ws.write(W_EQ_WT - 1, 0, "Equity Weight", fmt_label)
    ws.write_formula(W_EQ_WT - 1, 1, f"=B{W_EQUITY}/B{W_TOTCAP}", fmt_pct)
    ws.write(W_DEBT_WT - 1, 0, "Debt Weight", fmt_label)
    ws.write_formula(W_DEBT_WT - 1, 1, f"=B{W_TOT_DEBT}/B{W_TOTCAP}", fmt_pct)
    ws.write(W_WACC - 1, 0, "WACC", fmt_label_b)
    ws.write_formula(W_WACC - 1, 1, f"=B{W_EQ_WT}*B{W_COE}+B{W_DEBT_WT}*B{W_POSTTAX_COD}", fmt_pct_b)

    # ════════════════════════ DCF CROSSCHECK ════════════════════════
    ws = wb.add_worksheet("DCF CrossCheck")
    ws.set_column("A:A", 42)
    ws.set_column("B:F", 12)
    ws.merge_range("A1:F1", f"DCF CROSS-CHECK ({currency_short})", fmt_title)
    ws.write(2, 0, "", fmt_year)
    for i, label in enumerate(["Year 1", "Year 2", "Year 3", "Year 4", "Year 5"]):
        ws.write_string(2, 1 + i, label, fmt_year)

    dcf_cols = [xl_col_to_name(c) for c in range(1, 6)]  # B..F
    for i in range(5):
        c, omc = dcf_cols[i], om_cols[i]
        ws.write_formula(DCF_FCFF - 1, 1 + i, f"='Operating Model'!{omc}{OM_FCFF}", fmt_link)
        ws.write_formula(DCF_DF - 1, 1 + i, f"=1/(1+WACC!$B${W_WACC})^{i+1}", fmt_num3)
        ws.write_formula(DCF_PV - 1, 1 + i, f"={c}{DCF_FCFF}*{c}{DCF_DF}", fmt_num)
    ws.write(DCF_FCFF - 1, 0, "Unlevered FCF (FCFF)", fmt_label)
    ws.write(DCF_DF - 1, 0, "Discount Factor", fmt_label)
    ws.write(DCF_PV - 1, 0, "PV of FCFF", fmt_label_b)

    ws.write(DCF_SUM_PV - 1, 0, "Sum of PV of FCFF, Years 1\u20135", fmt_label_b)
    ws.write_formula(DCF_SUM_PV - 1, 1, f"=SUM(B{DCF_PV}:F{DCF_PV})", fmt_num_b)

    section(10, "METHOD 1 \u2014 EBITDA EXIT MULTIPLE")
    ws.write(DCF_TERM_EBITDA - 1, 0, "Terminal EBITDA (Year 5)", fmt_label)
    ws.write_formula(DCF_TERM_EBITDA - 1, 1, f"='Operating Model'!G{OM_EBITDA}", fmt_link)
    ws.write(DCF_TERM_MULT - 1, 0, "Terminal EV/EBITDA Multiple", fmt_label)
    ws.write_formula(DCF_TERM_MULT - 1, 1, f"=Assumptions!B{A_TERMINAL_MULT}", fmt_link_mult)
    ws.write(DCF_TV1 - 1, 0, "Terminal Value", fmt_label)
    ws.write_formula(DCF_TV1 - 1, 1, f"=B{DCF_TERM_EBITDA}*B{DCF_TERM_MULT}", fmt_num)
    ws.write(DCF_PV_TV1 - 1, 0, "PV of Terminal Value", fmt_label)
    ws.write_formula(DCF_PV_TV1 - 1, 1, f"=B{DCF_TV1}/(1+WACC!$B${W_WACC})^Assumptions!B{A_HOLD_YEARS}", fmt_num)
    ws.write(DCF_EV1 - 1, 0, "Implied EV \u2014 EBITDA Multiple Method", fmt_label_b)
    ws.write_formula(DCF_EV1 - 1, 1, f"=B{DCF_SUM_PV}+B{DCF_PV_TV1}", fmt_num_b)

    section(17, "METHOD 2 \u2014 PERPETUITY GROWTH")
    ws.write(DCF_TERM_FCFF - 1, 0, "Terminal Year (Year 5) FCFF", fmt_label)
    ws.write_formula(DCF_TERM_FCFF - 1, 1, f"=F{DCF_FCFF}", fmt_num)
    ws.write(DCF_PERP_G - 1, 0, "Perpetuity Growth Rate", fmt_label)
    ws.write_formula(DCF_PERP_G - 1, 1, f"=Assumptions!B{A_PERP_GROWTH}", fmt_link_pct)
    ws.write(DCF_TERM_FCF_NEXT - 1, 0, "Terminal Year+1 FCF", fmt_label)
    ws.write_formula(DCF_TERM_FCF_NEXT - 1, 1, f"=B{DCF_TERM_FCFF}*(1+B{DCF_PERP_G})", fmt_num)
    ws.write(DCF_TV2 - 1, 0, "Terminal Value (Perpetuity)", fmt_label)
    ws.write_formula(DCF_TV2 - 1, 1, f"=B{DCF_TERM_FCF_NEXT}/(WACC!$B${W_WACC}-B{DCF_PERP_G})", fmt_num)
    ws.write(DCF_PV_TV2 - 1, 0, "PV of Terminal Value", fmt_label)
    ws.write_formula(DCF_PV_TV2 - 1, 1, f"=B{DCF_TV2}/(1+WACC!$B${W_WACC})^Assumptions!B{A_HOLD_YEARS}", fmt_num)
    ws.write(DCF_EV2 - 1, 0, "Implied EV \u2014 Perpetuity Method", fmt_label_b)
    ws.write_formula(DCF_EV2 - 1, 1, f"=B{DCF_SUM_PV}+B{DCF_PV_TV2}", fmt_num_b)

    section(25, "COMPARISON TO LBO ENTRY EV")
    ws.write(DCF_ENTRY_EV - 1, 0, "LBO Entry Enterprise Value", fmt_label)
    ws.write_formula(DCF_ENTRY_EV - 1, 1, f"='Sources & Uses'!B{SU_ENTRY_EV}", fmt_link)
    ws.write(DCF_CMP1 - 1, 0, "Implied EV \u2014 EBITDA Multiple Method", fmt_label)
    ws.write_formula(DCF_CMP1 - 1, 1, f"=B{DCF_EV1}", fmt_num)
    ws.write(DCF_CMP2 - 1, 0, "Implied EV \u2014 Perpetuity Method", fmt_label)
    ws.write_formula(DCF_CMP2 - 1, 1, f"=B{DCF_EV2}", fmt_num)
    ws.write(DCF_PREM1 - 1, 0, "Implied EV (EBITDA Multiple Method) vs Entry", fmt_label)
    ws.write_formula(DCF_PREM1 - 1, 1, f"=B{DCF_CMP1}/B{DCF_ENTRY_EV}-1", fmt_pct)
    ws.write(DCF_PREM2 - 1, 0, "Implied EV (Perpetuity Growth Method) vs Entry", fmt_label)
    ws.write_formula(DCF_PREM2 - 1, 1, f"=B{DCF_CMP2}/B{DCF_ENTRY_EV}-1", fmt_pct)
    ws.write(DCF_PREM2, 0, "Positive % = DCF suggests entry price is conservative (room for upside)", fmt_label)
    ws.write(DCF_PREM2 + 1, 0, "Negative % = DCF suggests entry price is rich vs standalone value", fmt_label)

    # ════════════════════════ RETURNS ════════════════════════
    ws = wb.add_worksheet("Returns")
    ws.set_column("A:A", 42)
    ws.set_column("B:G", 13)
    ws.merge_range("A1:G1", "RETURNS TO SPONSOR EQUITY", fmt_title)

    section(3, "EXIT VALUE")
    ws.write(R_EXIT_EBITDA - 1, 0, "Exit EBITDA (Year 5)", fmt_label)
    ws.write_formula(R_EXIT_EBITDA - 1, 1, f"='Operating Model'!G{OM_EBITDA}", fmt_link)
    ws.write(R_EXIT_MULT - 1, 0, "Exit EV/EBITDA Multiple", fmt_label)
    ws.write_formula(R_EXIT_MULT - 1, 1, f"=Assumptions!B{A_EXIT_MULT}", fmt_link_mult)
    ws.write(R_EXIT_EV - 1, 0, "Exit Enterprise Value", fmt_label_b)
    ws.write_formula(R_EXIT_EV - 1, 1, f"=B{R_EXIT_EBITDA}*B{R_EXIT_MULT}", fmt_num_b)
    ws.write(R_EXIT_SR - 1, 0, "Exit Senior Debt Balance", fmt_label)
    ws.write_formula(R_EXIT_SR - 1, 1, f"='Debt Schedule'!F{DS_SR_END}", fmt_link)
    ws.write(R_EXIT_SUB - 1, 0, "Exit Subordinated Debt Balance", fmt_label)
    ws.write_formula(R_EXIT_SUB - 1, 1, f"='Debt Schedule'!F{DS_SUB_END}", fmt_link)
    ws.write(R_EXIT_ND - 1, 0, "Exit Net Debt", fmt_label)
    ws.write_formula(R_EXIT_ND - 1, 1, f"=B{R_EXIT_SR}+B{R_EXIT_SUB}", fmt_num)
    ws.write(R_EXIT_EQ - 1, 0, "Exit Equity Value", fmt_label_b)
    ws.write_formula(R_EXIT_EQ - 1, 1, f"=B{R_EXIT_EV}-B{R_EXIT_ND}", fmt_num_b)

    section(12, "SPONSOR RETURNS")
    ws.write(R_INIT_EQ - 1, 0, "Initial Sponsor Equity", fmt_label)
    ws.write_formula(R_INIT_EQ - 1, 1, f"='Sources & Uses'!B{SU_SPONSOR_EQ}", fmt_link)
    ws.write(R_MOIC - 1, 0, "MOIC", fmt_label_b)
    ws.write_formula(R_MOIC - 1, 1, f"=B{R_EXIT_EQ}/B{R_INIT_EQ}", fmt_big)
    ws.write(R_HOLD - 1, 0, "Hold Period (Years)", fmt_label)
    ws.write_formula(R_HOLD - 1, 1, f"=Assumptions!B{A_HOLD_YEARS}", fmt_link)
    ws.write(R_IRR - 1, 0, "IRR", fmt_label_b)
    ws.write_formula(R_IRR - 1, 1, f"=B{R_MOIC}^(1/B{R_HOLD})-1", fmt_big_pct)

    section(18, "CASH FLOW CHECK (Excel IRR Function)")
    for i, label in enumerate(["Year 0", "Year 1", "Year 2", "Year 3", "Year 4", "Year 5"]):
        ws.write_string(R_CF_HEADER - 1, 1 + i, label, fmt_year)
    ws.write(R_CF_HEADER - 1, 0, "", fmt_year)
    ws.write(R_CF_ROW - 1, 0, "Sponsor Cash Flow", fmt_label)
    ws.write_formula(R_CF_ROW - 1, 1, f"=-B{R_INIT_EQ}", fmt_num)
    for i in range(1, 5):
        ws.write_number(R_CF_ROW - 1, 1 + i, 0, fmt_num)
    ws.write_formula(R_CF_ROW - 1, 6, f"=B{R_EXIT_EQ}", fmt_num)
    ws.write(R_IRR_CHECK - 1, 0, "IRR (Excel IRR() function \u2014 cross-check)", fmt_label)
    ws.write_formula(R_IRR_CHECK - 1, 1, f"=IRR(B{R_CF_ROW}:G{R_CF_ROW})", fmt_pct)

    section(R_SENS_HEADER, "SENSITIVITY \u2014 EXIT MULTIPLE vs RETURNS")
    headers = ["Exit Multiple", "Exit EV", "Exit Equity Value", "MOIC", "IRR"]
    for i, h in enumerate(headers):
        ws.write_string(R_SENS_HEADER, i, h, fmt_year)
    for k in range(5):  # 5 rows, offsets -1,-0.5,0,+0.5,+1
        row = R_SENS_START + k
        offset = (k - 2) * 0.5
        sign = "+" if offset >= 0 else "-"
        ws.write_formula(row - 1, 0, f"=Assumptions!$B${A_EXIT_MULT}{sign}{abs(offset)}", fmt_mult)
        ws.write_formula(row - 1, 1, f"=$B${R_EXIT_EBITDA}*A{row}", fmt_num)
        ws.write_formula(row - 1, 2, f"=B{row}-$B${R_EXIT_ND}", fmt_num)
        ws.write_formula(row - 1, 3, f"=C{row}/$B${R_INIT_EQ}", fmt_mult)
        ws.write_formula(row - 1, 4, f"=D{row}^(1/$B${R_HOLD})-1", fmt_pct)

    # ── 5x5 ENTRY x EXIT GRIDS (fixed multiples 6-10, matches Streamlit sensitivity grid) ──
    grid_mults = [6, 7, 8, 9, 10]

    def write_grid(section_row_1idx, title, fmt_val, moic_only):
        section(section_row_1idx, title)
        header_0idx = section_row_1idx  # = (section_row_1idx+1) - 1
        ws.write_string(header_0idx, 0, "Entry \u2193 / Exit \u2192", fmt_year)
        for j, xm in enumerate(grid_mults):
            ws.write_number(header_0idx, 1 + j, xm, fmt_year)
        header_excel_row = section_row_1idx + 1
        for i, em in enumerate(grid_mults):
            data_row_0idx = section_row_1idx + 1 + i
            ws.write_number(data_row_0idx, 0, em, fmt_year)
            entry_ev_f = f"'Operating Model'!$B${OM_EBITDA}*{em}"
            sponsor_eq_f = f"(({entry_ev_f})*(1+Assumptions!$B${A_FEES_PCT})-'Sources & Uses'!$B${SU_SENIOR}-'Sources & Uses'!$B${SU_SUB})"
            for j in range(len(grid_mults)):
                c = xl_col_to_name(1 + j)
                exit_eq_f = f"('Operating Model'!$G${OM_EBITDA}*{c}${header_excel_row}-('Debt Schedule'!$F${DS_SR_END}+'Debt Schedule'!$F${DS_SUB_END}))"
                moic_f = f"({exit_eq_f})/{sponsor_eq_f}"
                if moic_only:
                    formula = f'=IFERROR(IF({sponsor_eq_f}<=0,"N/M",{moic_f}),"N/M")'
                else:
                    formula = f'=IFERROR(IF({sponsor_eq_f}<=0,"N/M",IF({moic_f}<=0,-1,({moic_f})^(1/Assumptions!$B${A_HOLD_YEARS})-1)),"N/M")'
                ws.write_formula(data_row_0idx, 1 + j, formula, fmt_val)
        return section_row_1idx + 1 + len(grid_mults)  # next free 1-indexed row

    next_row = write_grid(R_SENS_START + 6, "SENSITIVITY \u2014 IRR BY ENTRY \u00d7 EXIT EV/EBITDA MULTIPLE", fmt_pct, moic_only=False)
    next_row = write_grid(next_row + 1, "SENSITIVITY \u2014 MOIC BY ENTRY \u00d7 EXIT EV/EBITDA MULTIPLE", fmt_mult, moic_only=True)
    ws.write(next_row, 0, "Base case is set by the Entry/Exit multiple inputs on the Assumptions tab. "
             "'N/M' = leverage exceeds purchase price at that entry multiple (not a viable structure).", fmt_wrap)

    # ════════════════════════ READ ME ════════════════════════
    ws = wb.add_worksheet("Read Me")
    ws.set_column("A:A", 100)
    ws.write(0, 0, "LBOdesk \u2014 LEVERAGED BUYOUT MODEL TEMPLATE", fmt_title)
    notes = [
        "WHAT THIS IS",
        "This is a simplified 'paper LBO' \u2014 the model structure used in PE/IB interviews. It captures Sources "
        "& Uses, an Operating Model, a 3-tranche Debt Schedule with cash sweep, a WACC/DCF cross-check, and "
        "Returns (IRR/MOIC) with an Entry \u00d7 Exit sensitivity grid.",
        "",
        "ABOUT THIS MODEL",
        (f"'{company_name}' is a FICTIONAL composite {sector.lower()} company used purely to illustrate the "
         f"model. All figures are in {currency_long}."
         if is_fictional else
         f"This model is configured for {company_name} ({sector}). All figures are in {currency_long}. "
         f"Replace the illustrative operating assumptions (margins, growth, leverage, WACC drivers) on the "
         f"Assumptions tab with figures specific to this company before relying on the output."),
        "",
        "HOW TO USE THIS TEMPLATE",
        "1. Go to the 'Assumptions' tab \u2014 every blue cell on a yellow background is an input.\n"
        "2. Change any input \u2014 revenue, margins, growth, leverage, multiples, WACC drivers.\n"
        "3. Every other tab recalculates automatically via linked formulas.\n"
        "4. Check 'Sources & Uses' row 'Check' \u2014 should always read 0.0 (Sources = Uses).",
        "",
        "SHEET GUIDE",
        "Assumptions \u2014 all editable inputs (blue text, yellow fill)\n"
        "Operating Model \u2014 Revenue to FCF build, 6-year view (Year 0 to Year 5)\n"
        "Sources & Uses \u2014 entry financing structure; Sponsor Equity is the 'plug'\n"
        "Debt Schedule \u2014 year-by-year senior/sub debt paydown via cash sweep\n"
        "WACC \u2014 CAPM cost of equity, blended cost of debt, WACC\n"
        "DCF CrossCheck \u2014 implied EV via EBITDA-multiple and Perpetuity-growth methods, compared against "
        "the LBO entry price\n"
        "Returns \u2014 exit equity value, MOIC, IRR, plus 1D exit-multiple and 5\u00d75 Entry \u00d7 Exit sensitivity grids",
        "",
        "CASH SWEEP LOGIC",
        "100% of free cash flow after the mandatory senior amortization sweeps to pay down debt, in priority "
        "order: (1) mandatory senior amortization, (2) senior debt cash sweep, (3) subordinated debt cash "
        "sweep. The sweep is capped with MIN()/MAX() formulas so balances never go negative.",
        "",
        "COLOR CONVENTION",
        "Blue text = hardcoded input (change these)\nBlack text = formula on this sheet\nGreen text = formula "
        "linking to another sheet",
        "",
        "LIMITATIONS \u2014 READ THIS",
        "This is a simplified skeleton for learning and quick screening, NOT a live deal model. It uses 3 "
        "financing tranches (Senior Debt, Subordinated Debt, Sponsor Equity) instead of the 6-8 tranches a "
        "real deal might have. Working capital, capex, and D&A are modeled as simple % of revenue rather than "
        "full balance sheet roll-forwards. For a real transaction, extend the Debt Schedule tab with "
        "additional tranches following the same pattern, and replace the simplified operating drivers with a "
        "full 3-statement model.",
        "",
        "Not investment advice. Illustrative only.",
    ]
    bold_lines = {"WHAT THIS IS", "ABOUT THIS MODEL", "HOW TO USE THIS TEMPLATE", "SHEET GUIDE",
                   "CASH SWEEP LOGIC", "COLOR CONVENTION", "LIMITATIONS \u2014 READ THIS"}
    for i, line in enumerate(notes):
        ws.write(1 + i, 0, line, fmt_label_b if line in bold_lines else fmt_wrap)
        if line and line not in bold_lines:
            ws.set_row(1 + i, 18 * (line.count("\n") + 1) + 27)

    wb.close()
    output.seek(0)
    return output


if __name__ == "__main__":
    params = {"entry_ev_ebitda": 8.0, "exit_ev_ebitda": 8.0, "senior_debt_mult": 4.0,
              "sub_debt_mult": 1.5, "revenue_growth": 0.08, "ebitda_margin_year5": 0.20}
    buf = generate_excel(params)
    with open("test_output.xlsx", "wb") as f:
        f.write(buf.read())
    print("written")
