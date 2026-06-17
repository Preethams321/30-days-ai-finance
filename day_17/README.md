# CompeteIQ — Day 17 / 30 Days of AI Finance

Competitive intelligence engine for Indian banking. DuPont ROE decomposition,
9-metric peer comparison, Porter's 5 Forces, and competitive moat scoring —
in a hardcoded demo mode (5 Indian banks, FY25 audited standalone financials)
and an AI-powered custom mode (point it at any 5 listed companies).

## Run it

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Custom mode

You'll need your own API key for whichever provider you pick in the dropdown.
Gemini 2.0 Flash is the only one with live web search (Google Search grounding) —
everyone else answers from training data, which may be stale on recent quarters.

## Data notes (demo mode)

- All five banks' financials are FY25 **audited standalone** figures (not consolidated).
- "Total Income" is **gross** (interest earned + other income, pre interest-expense) —
  this matters for the DuPont Asset Utilisation ratio, so don't substitute net interest
  income figures from other sources without adjusting.
- HDFC Bank's YoY advances/deposits growth are marked N/A — the HDFC–HDFC Ltd merger
  makes FY24 YoY comparisons not meaningful. Net profit growth is used as a fallback
  input for HDFC's moat-score growth component.
- `roe_computed` (from the DuPont identity, using period-end net worth) differs from
  `roe_reported` (sourced figure) for every bank. For HDFC, ICICI, and Axis the gap is
  small and in the expected direction (reported ROE uses average net worth, which is
  typically lower than period-end for a growing bank). For **Kotak and SBI the gap
  reverses direction** — worth a manual cross-check against the source filing if you're
  using this for anything beyond illustration, since it may indicate a consolidated vs.
  standalone net-worth base mismatch in the reported figure.

Not investment advice.
