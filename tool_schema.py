COMPANY_KEYS = ["adani_ar25", "inf_ar25", "rel_ar25", "sbi_ar25", "tatamotors_ar25"]

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_documents",
            "description": "Search annual report filings for qualitative information - risk factors, strategy, management commentary, business descriptions. NOT for precise numbers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search question"},
                    "company_key": {
                        "type": "string",
                        "enum": COMPANY_KEYS,
                        "description": "Optional - filter to one company"
                    },
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_live_price",
            "description": "Get current stock price and market data for a company.",
            "parameters": {
                "type": "object",
                "properties": {
                    "company_key": {"type": "string", "enum": COMPANY_KEYS},
                },
                "required": ["company_key"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_financial_metrics",
            "description": "Get exact fiscal-year financial figures (total_revenue, ebitda, net_income, diluted_eps) for a company. Use for questions about a specific fiscal year like 'FY26'. Returns raw figures only - does NOT calculate ratios or margins.",
            "parameters": {
                "type": "object",
                "properties": {
                    "company_key": {"type": "string", "enum": COMPANY_KEYS},
                    "fiscal_year": {
                        "type": "string",
                        "description": "Exact format 'YYYY-MM-DD' only, e.g. '2026-03-31' for FY26, '2025-03-31' for FY25. Omit entirely if unsure - defaults to most recent year."
                    },
                },
                "required": ["company_key"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_pe_ratio",
            "description": "Calculate Price-to-Earnings ratio. Requires REAL numeric price and eps values already retrieved from other tools - never call with placeholder or missing values.",
            "parameters": {
                "type": "object",
                "properties": {
                    "price": {"type": "number", "description": "Actual current price, a real number"},
                    "eps": {"type": "number", "description": "Actual diluted EPS, a real number"},
                },
                "required": ["price", "eps"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_yoy_growth",
            "description": "Calculate year-over-year growth percentage. Requires REAL numeric current_value and previous_value already retrieved from get_financial_metrics calls for two different fiscal years - never call with placeholder or missing values.",
            "parameters": {
                "type": "object",
                "properties": {
                    "current_value": {"type": "number", "description": "Actual value for the more recent period"},
                    "previous_value": {"type": "number", "description": "Actual value for the earlier period"},
                    "metric_name": {"type": "string"},
                },
                "required": ["current_value", "previous_value"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_profit_margin",
            "description": "Calculate net profit margin percentage. Requires REAL numeric net_income and revenue values from get_financial_metrics - do NOT use eps or diluted_eps for this, those are different fields.",
            "parameters": {
                "type": "object",
                "properties": {
                    "net_income": {"type": "number"},
                    "revenue": {"type": "number"},
                },
                "required": ["net_income", "revenue"]
            }
        }
    },
]