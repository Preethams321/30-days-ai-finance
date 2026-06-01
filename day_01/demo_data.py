# demo_data.py

COMPANY_NAME = "BSE Limited"
PERIOD = "Q4 & Full Year FY26"
NSE_TICKER = "BSE"

# Pre-analyzed institutional intelligence schema matching screener.in standards
PRE_ANALYZED_PAYLOAD = {
    "overall_sentiment_score": 0.78,
    "tone_distribution": {
        "Confident": 65,
        "Cautious": 20,
        "Defensive": 15
    },
    "hedge_word_count": 14,
    "guidance_direction": "POSITIVE OUTLOOK WITH STRUCTURAL BOTTLENECKS",
    "capex_tone_classification": "AGGR. INFRASTRUCTURE & TECH OVERHAUL",
    "qa_defensiveness_score": 0.35,
    
    "executive_summary": "BSE delivered a historic performance marking its 150th anniversary, with annual revenues crossing the Rs. 5,000 crore milestone for the first time. Growth was driven by massive transaction volume expansions across core cash and derivative options, balanced by strong domestic institutional and retail SIP client inflows. However, capital allocation strategies are intentionally pivoting from legacy high dividend payouts to aggressive infrastructure scaling and real estate acquisition, while cash market share gains face near-term competitive friction.",
    
    "growth_vectors": [
        "Record Financial Year: Full-year FY26 total consolidated revenues crossed Rs. 5,000 crores for the first time in BSE's 150-year history to reach Rs. 5,148 crores, a substantial 59% YoY growth from Rs. 3,236 crores in FY25.",
        "Quarterly Momentum: Q4 FY26 revenue reached Rs. 1,630 crores, growing 22% sequentially compared to Rs. 1,334 crores in Q3, marking the 13th consecutive quarter of record top-line performance.",
        "Macro Support Shifts: Despite external global macroeconomic headwinds and volatile foreign portfolio streams, Indian capital markets were supported by unprecedented domestic institutional deployment (~Rs. 8.5 lakh crores) and record retail SIP flows reaching Rs. 3.5 lakh crores in FY26."
    ],
    
    "financial_performance": [
        "Operational Top-line Boost: Operational revenues surged 63% YoY to Rs. 4,834 crores from Rs. 2,957 crores. Core transaction charges increased 87% YoY to Rs. 3,795 crores from Rs. 2,030 crores, powered by equity cash, derivatives, clearing house, and mutual fund platform scale.",
        "Operating Overhead Insights: Total operating expenses increased by 20% to Rs. 1,755 crores. Crucially, 53% of all operating costs are directly variable, volume-linked outlays comprising regulatory fees and clearing/settlement transactions.",
        "Margin Optimization Matrix: Operating EBITDA more than doubled to Rs. 3,079 crores with operating margins expanding to 64% from 51%. Net profit (PAT) grew 88% YoY to Rs. 2,497 crores, with bottom-line profit margins reaching 49%.",
        "Dividend Realities: Recommended dividend stands at Rs. 10 per share (FV Rs. 2), leading to a total distribution payout of Rs. 412 crores. This is a 30% increase overall, or a 67% increase when normalizing for the previous year's 150th anniversary special dividend allocation."
    ],
    
    "platform_franchise": [
        "Primary Issuance Engine: BSE ranked first globally for IPO listings in FY26, onboarding 255 new listings across mainboard and SME segments to mobilize an all-time record Rs. 1.8 lakh crores. The active FY27 issuance pipeline remains robust with over 250 applications tracking Rs. 1.75 lakh crores.",
        "Derivatives Volume Scaling: Average Daily Premium Turnover (ADTV) in index derivatives registered an 118% YoY jump to hit Rs. 19,523 crores up from Rs. 8,978 crores. Transition to a Thursday expiry model successfully broadened open interest and non-expiry daily profiles.",
        "Co-location Infrastructure: Co-location monetization surged to Rs. 171 crores from Rs. 74 crores in FY25, heavily incentivized by the newly structured Throttle Charges Framework launched in July 2025. Rack placement count scaled up from 300 to 500 racks.",
        "Super Gateway Wealth Transition: BSE StAR MF revenues increased 24% to Rs. 285 crores processing 84 crore transactions. Platform reach expanded via an active live integration with India Post (Dak Sevaks). Launch of StAR NPS on April 22, 2026, marks the strategic evolution to capture the complete lifecycle from initial SIP to final pension."
    ],
    
    "risks_and_frictions": [
        "Expected Credit Loss (ECL) Provisioning Impact: Other expenses for the quarter were impacted by an explicit Rs. 80 crore outstanding asset dispute from NSE. ICCL initiated a conservative ECL provision line items adjustment in compliance with standard accounting laws.",
        "Smart Order Routing (SOR) Constraints: Cash equity market share is hovering at 7% to 8%, missing internal double-digit targets. Growth is directly bottlenecked because customer SOR integration approval applications have remained pending for over six months at the competing exchange.",
        "Settlement Guarantee Fund (SGF) Adjustments: Having crossed the specified baseline threshold of Rs. 150 crores by hitting 150% of the required fund pool, quarterly profit contribution rates were scaled down from 5% to 3.5%. Management declined forward SGF guidance due to complex, stress-test computational rules.",
        "Options Pricing Autonomy: Management maintains independent option pricing metrics irrespective of external market pressures and will under no condition reduce regulatory protection fund inputs governed by SEBI rules."
    ],
    
    "capital_allocation": [
        "Pushback on Excess Payouts: Management explicitly clarified that legacy 98-99% payout configurations reflected a historic lack of strategic growth goals. Modern frameworks favor balance sheet core robustness to demonstrate clearing house stability.",
        "Capacity Cost Escalations: Over Rs. 500 crores in gross blocks were deployed over the last two years for capacity expansions. Global supply pressures and escalating system memory/hardware costs are expected to double future technology outlays past the initial Rs. 300 crore budget baseline.",
        "Strategic Real Estate: Active deployment plans are being considered to purchase a dedicated plot of commercial land in the heart of Mumbai to secure long-term spatial expansion runways."
    ],
    
    "top_cautious_phrases": [
        "Smart order routing applications remain pending for more than six months at the other exchange.",
        "Unprecedented tech sector hiring booms are firmly behind us.",
        "Global macroeconomic backdrop over the past quarter has been challenging and complex.",
        "The current year's technology capacity budget already appears to be underpriced due to global hardware price hikes."
    ]
}

MOCK_TRANSCRIPT = "BSE LIMITED CONCALL TRANSCRIPT FILE PLACEHOLDER DATA STRUCTURES"