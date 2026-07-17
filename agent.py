import ollama
import json

from tools_document_search import search_documents
from tools_live_data import get_live_price, get_ttm_metrics, get_financial_metrics
from tools_calculator import (
    calculate_pe_ratio, calculate_yoy_growth, calculate_profit_margin,
    calculate_debt_to_equity, calculate_roe, calculate_roa,
    calculate_ebitda_margin, calculate_cagr, calculate_interest_coverage,
    calculate_dividend_yield
)

COMPANY_KEYS = ["adani_ar25", "inf_ar25", "rel_ar25", "sbi_ar25", "tatamotors_ar25"]

# --- Tool definitions in Ollama's expected schema ---
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_documents",
            "description": "Search annual report filings for qualitative information - risk factors, strategy, management commentary, business descriptions. NOT for precise numbers (use financial data tools instead).",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search question"},
                    "company_key": {"type": "string", "description": f"Optional - one of {COMPANY_KEYS}, to filter to one company"},
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
                    "company_key": {"type": "string", "description": f"One of {COMPANY_KEYS}"},
                },
                "required": ["company_key"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_financial_metrics",
            "description": "Get exact fiscal-year financial figures (revenue, EBITDA, net income, EPS) for a company. Use for questions mentioning a specific fiscal year like 'FY26'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "company_key": {"type": "string", "description": f"One of {COMPANY_KEYS}"},
                    "fiscal_year": {"type": "string", "description": "Exact format 'YYYY-MM-DD' only, e.g. '2026-03-31' for FY26, '2025-03-31' for FY25. Omit entirely if unsure or asking about the most recent year."},
                },
                "required": ["company_key"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_pe_ratio",
            "description": "Calculate Price-to-Earnings ratio given price and EPS.",
            "parameters": {
                "type": "object",
                "properties": {
                    "price": {"type": "number"},
                    "eps": {"type": "number"},
                },
                "required": ["price", "eps"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_yoy_growth",
            "description": "Calculate year-over-year growth percentage between two values.",
            "parameters": {
                "type": "object",
                "properties": {
                    "current_value": {"type": "number"},
                    "previous_value": {"type": "number"},
                    "metric_name": {"type": "string"},
                },
                "required": ["current_value", "previous_value"]
            }
        }
    },
]

# Map tool names (strings) to actual Python functions
TOOL_FUNCTIONS = {
    "search_documents": search_documents,
    "get_live_price": get_live_price,
    "get_financial_metrics": get_financial_metrics,
    "calculate_pe_ratio": calculate_pe_ratio,
    "calculate_yoy_growth": calculate_yoy_growth,
}
def run_agent(user_question: str, max_steps: int = 5) -> str:
    messages = [
        {
            "role": "system",
            "content": f"""You are a financial research assistant for NSE-listed companies.
Available companies: {COMPANY_KEYS}.
Tool usage rules:
- For qualitative questions (risk, strategy, commentary), use search_documents.
- For numeric/financial questions (price, revenue, ratios), use the financial data tools.
- For fiscal_year parameters, use EXACT format 'YYYY-MM-DD' (e.g. '2026-03-31'). Omit if unsure - it defaults to the most recent year.
- For ANY calculation (growth, ratios, margins), you MUST use the calculator tools - never compute or state a percentage/ratio yourself, even if you see a similar figure in retrieved text. Always verify with the calculator tool.
- For growth/comparison questions, fetch BOTH periods' data with separate tool calls BEFORE attempting any calculation. Never call a calculator tool with missing or placeholder values.
- Do not invent explanations, formulas, or reasoning not directly supported by tool results or retrieved documents.
- If no available tool can answer the question, say so clearly rather than guessing.
- Always state which tool/source your information came from.
"""
        },
        {"role": "user", "content": user_question}
    ]

    trace = []

    for step in range(max_steps):
        response = ollama.chat(model='llama3.2:3b', messages=messages, tools=TOOLS)
        message = response['message']
        messages.append(message)

        if not message.get('tool_calls'):
            return message['content'], trace

        for tool_call in message['tool_calls']:
            func_name = tool_call['function']['name']
            func_args = tool_call['function']['arguments']
            trace.append({"tool": func_name, "args": func_args})

            if func_name not in TOOL_FUNCTIONS:
                result = {"error": f"Unknown tool: {func_name}"}
            else:
                try:
                    result = TOOL_FUNCTIONS[func_name](**func_args)
                except Exception as e:
                    result = {"error": f"Tool execution failed: {str(e)}"}

            messages.append({"role": "tool", "content": json.dumps(result, default=str)})

    return "Agent reached max steps without a final answer.", trace

if __name__ == "__main__":
    question = "What was Tata Motors' revenue in FY26 and how does that compare to what they reported in their annual report?"
    print(f"QUESTION: {question}\n")
    answer = run_agent(question)
    print(f"\nFINAL ANSWER:\n{answer}")