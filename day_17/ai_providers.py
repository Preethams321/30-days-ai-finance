"""
CompeteIQ — AI provider integrations for Custom Mode.
Gemini 2.0 Flash is the recommended provider (Google Search grounding = current financials).
Groq / DeepSeek / OpenAI / Anthropic are training-knowledge fallbacks (no live web search).
"""
import json

SCHEMA_PROMPT_TEMPLATE = """Search the web and find the latest annual financial data for these Indian companies: {companies}

For each company, return ONLY a JSON object with this exact structure:
{{
  "companies": [
    {{
      "name": "company name",
      "ticker": "NSE ticker",
      "fy": "FY25 or latest available",
      "nii_cr": 0,
      "other_income_cr": 0,
      "net_profit_cr": 0,
      "total_assets_cr": 0,
      "net_worth_cr": 0,
      "total_income_cr": 0,
      "nim_pct": 0.0,
      "gnpa_pct": 0.0,
      "nnpa_pct": 0.0,
      "crar_pct": 0.0,
      "roa_pct": 0.0,
      "roe_pct": 0.0,
      "cost_to_income_pct": 0.0,
      "advances_growth_pct": 0.0,
      "deposits_growth_pct": 0.0,
      "net_profit_growth_pct": 0.0,
      "pbv": 0.0,
      "pe": 0.0,
      "book_value_per_share": 0.0,
      "current_price": 0.0,
      "porter": {{
        "buyer_power": 0,
        "supplier_power": 0,
        "threat_of_entry": 0,
        "substitutes": 0,
        "rivalry": 0
      }},
      "moat_score": 0,
      "moat_factors": ["factor1", "factor2"],
      "competitive_summary": "2-3 sentence plain English summary"
    }}
  ],
  "sector_overview": "2-3 sentence overview of the sector's competitive dynamics",
  "data_sources": ["source1", "source2"]
}}

Porter's 5 Forces scores: 1-10 where 10 = highest force intensity.
Moat score: 0-100 composite.
total_income_cr should be GROSS total income (interest earned + other income, before deducting interest expense) — not net interest income plus other income.
Return ONLY raw JSON, no markdown, no backticks, no explanation.
All financial figures in INR Crores.
"""


def _clean_json_text(text):
    text = text.strip()
    if text.startswith("```"):
        parts = text.split("```")
        text = parts[1] if len(parts) > 1 else text
        if text.startswith("json"):
            text = text[4:]
    return text.strip()


def fetch_financials_via_gemini(company_names, api_key):
    try:
        import google.generativeai as genai
    except ImportError:
        return {"error": "google-generativeai package not installed. Run: pip install google-generativeai"}

    prompt = SCHEMA_PROMPT_TEMPLATE.format(companies=", ".join(company_names))
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")
        
        # Version-agnostic dictionary mapping for unblocked Google Search Grounding
        search_tool = {"google_search_retrieval": {}}
        
        response = model.generate_content(prompt, tools=[search_tool])
        text = _clean_json_text(response.text)
        return json.loads(text)
    except json.JSONDecodeError as e:
        return {"error": f"Gemini returned non-JSON output, could not parse: {e}"}
    except Exception as e:
        return {"error": str(e)}


def fetch_financials_via_groq(company_names, api_key):
    try:
        from groq import Groq
    except ImportError:
        return {"error": "groq package not installed. Run: pip install groq"}
    prompt = SCHEMA_PROMPT_TEMPLATE.format(companies=", ".join(company_names))
    try:
        client = Groq(api_key=api_key)
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
        )
        text = _clean_json_text(resp.choices[0].message.content)
        return json.loads(text)
    except json.JSONDecodeError as e:
        return {"error": f"Groq returned non-JSON output, could not parse: {e}"}
    except Exception as e:
        return {"error": str(e)}


def fetch_financials_via_deepseek(company_names, api_key):
    try:
        from openai import OpenAI
    except ImportError:
        return {"error": "openai package not installed. Run: pip install openai"}
    prompt = SCHEMA_PROMPT_TEMPLATE.format(companies=", ".join(company_names))
    try:
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
        )
        text = _clean_json_text(resp.choices[0].message.content)
        return json.loads(text)
    except json.JSONDecodeError as e:
        return {"error": f"DeepSeek returned non-JSON output, could not parse: {e}"}
    except Exception as e:
        return {"error": str(e)}


def fetch_financials_via_openai(company_names, api_key):
    try:
        from openai import OpenAI
    except ImportError:
        return {"error": "openai package not installed. Run: pip install openai"}
    prompt = SCHEMA_PROMPT_TEMPLATE.format(companies=", ".join(company_names))
    try:
        client = OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
        )
        text = _clean_json_text(resp.choices[0].message.content)
        return json.loads(text)
    except json.JSONDecodeError as e:
        return {"error": f"OpenAI returned non-JSON output, could not parse: {e}"}
    except Exception as e:
        return {"error": str(e)}


def fetch_financials_via_anthropic(company_names, api_key):
    try:
        import anthropic
    except ImportError:
        return {"error": "anthropic package not installed. Run: pip install anthropic"}
    prompt = SCHEMA_PROMPT_TEMPLATE.format(companies=", ".join(company_names))
    try:
        client = anthropic.Anthropic(api_key=api_key)
        resp = client.messages.create(
            model="claude-3-5-sonnet-latest",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}],
        )
        text = _clean_json_text(resp.content[0].text)
        return json.loads(text)
    except json.JSONDecodeError as e:
        return {"error": f"Claude returned non-JSON output, could not parse: {e}"}
    except Exception as e:
        return {"error": str(e)}


PROVIDERS = {
    "Gemini 2.0 Flash (free, web search — recommended)": ("gemini", fetch_financials_via_gemini, True),
    "Groq Llama 3.3 (free, fast, no web search)": ("groq", fetch_financials_via_groq, False),
    "DeepSeek (free, no web search)": ("deepseek", fetch_financials_via_deepseek, False),
    "OpenAI GPT-4o (paid)": ("openai", fetch_financials_via_openai, False),
    "Anthropic Claude (paid)": ("anthropic", fetch_financials_via_anthropic, False),
}


def normalize_ai_company(raw):
    """Fill missing optional fields so AI-fetched companies behave like DEMO_DATA companies."""
    raw.setdefault("other_income_cr", None)
    raw.setdefault("opex_cr", None)
    raw.setdefault("ppop_cr", None)
    raw.setdefault("loan_book_cr", None)
    raw.setdefault("deposits_cr", None)
    raw.setdefault("net_profit_growth_pct", 0)
    raw.setdefault("advances_growth_pct", None)
    raw.setdefault("deposits_growth_pct", None)
    raw.setdefault("growth_note", None)
    raw.setdefault("market_cap_cr", None)
    raw.setdefault("ticker", raw.get("ticker", "").upper())
    return raw