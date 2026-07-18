import json

def sanitize_tool_args(func_name: str, raw_args: dict, expected_params: set) -> dict:
    """
    Clean up arguments the model produced before calling the real function.
    Catches common small-model failure patterns:
    - literal string "null" instead of Python None
    - empty bracket strings like "[]" or "[[]]"
    - empty strings ""
    - unexpected extra parameters the function doesn't accept
    Returns a dict with either 'clean_args' or 'error'.
    """
    cleaned = {}
    problems = []

    for key, value in raw_args.items():
        if key not in expected_params:
            problems.append(f"unexpected parameter '{key}' ignored")
            continue

        if isinstance(value, str) and value.strip().lower() == "null":
            problems.append(f"'{key}' was literal string 'null'")
            continue

        if isinstance(value, str) and value.strip() in ("", "[]", "[[]]", "{}"):
            problems.append(f"'{key}' was empty/malformed ('{value}')")
            continue

        cleaned[key] = value

    if problems:
        return {
            "error": f"Cannot execute {func_name} - invalid arguments: {'; '.join(problems)}. "
                     f"Re-fetch the required data with a proper tool call before retrying.",
            "clean_args": None
        }

    return {"error": None, "clean_args": cleaned}


EXPECTED_PARAMS = {
    "search_documents": {"query", "company_key", "k"},
    "get_live_price": {"company_key"},
    "get_ttm_metrics": {"company_key"},
    "get_financial_metrics": {"company_key", "fiscal_year"},
    "calculate_pe_ratio": {"price", "eps"},
    "calculate_yoy_growth": {"current_value", "previous_value", "metric_name"},
    "calculate_profit_margin": {"net_income", "revenue"},
    "calculate_ebitda_margin": {"ebitda", "revenue"},
    "calculate_debt_to_equity": {"total_debt", "total_equity"},
    "calculate_roe": {"net_income", "shareholders_equity"},
    "calculate_roa": {"net_income", "total_assets"},
    "calculate_cagr": {"ending_value", "beginning_value", "num_years"},
    "calculate_interest_coverage": {"ebit", "interest_expense"},
    "calculate_dividend_yield": {"annual_dividend_per_share", "price"},
}

# Which tool names are "calculator" tools - their numeric args must be
# grounded in real, previously-retrieved values, not invented by the model
CALCULATOR_TOOLS = {
    "calculate_pe_ratio", "calculate_yoy_growth", "calculate_profit_margin",
    "calculate_ebitda_margin", "calculate_debt_to_equity", "calculate_roe",
    "calculate_roa", "calculate_cagr", "calculate_interest_coverage",
    "calculate_dividend_yield",
}


def extract_numeric_values(obj, collected=None) -> set:
    """
    Recursively walk any tool result (dict/list/nested) and collect every
    numeric value found, rounded to a stable precision for comparison.
    Used to build a 'ground truth pool' of real numbers actually retrieved
    during this conversation.
    """
    if collected is None:
        collected = set()

    if isinstance(obj, dict):
        for v in obj.values():
            extract_numeric_values(v, collected)
    elif isinstance(obj, list):
        for v in obj:
            extract_numeric_values(v, collected)
    elif isinstance(obj, (int, float)):
        try:
            collected.add(round(float(obj), 4))
        except (ValueError, TypeError):
            pass

    return collected


def verify_calculator_grounding(func_name: str, clean_args: dict, retrieved_values: set,
                                  relative_tolerance: float = 0.01) -> str:
    """
    For calculator tools only: check every numeric argument actually matches
    (within a small tolerance, to allow for rounding) a value that was
    genuinely returned by an earlier tool call this conversation.

    Returns an error string if any argument looks fabricated, or None if
    everything checks out. metric_name-style string args are ignored.
    """
    if func_name not in CALCULATOR_TOOLS:
        return None  # grounding check only applies to calculator tools

    if not retrieved_values:
        return (f"Cannot execute {func_name} - no data has been fetched yet this conversation. "
                f"Call a data-fetching tool (get_live_price / get_financial_metrics) first, "
                f"then use the REAL returned numbers as inputs.")

    unmatched = []
    for key, value in clean_args.items():
        if not isinstance(value, (int, float)):
            continue  # skip non-numeric args like metric_name

        value_rounded = round(float(value), 4)
        # Check for a close match against anything actually retrieved
        matched = any(
            abs(value_rounded - real_val) <= abs(real_val) * relative_tolerance + 1e-6
            for real_val in retrieved_values
        )
        if not matched:
            unmatched.append(f"{key}={value}")

    if unmatched:
        return (f"Cannot execute {func_name} - these values don't match any data actually "
                f"retrieved this conversation: {', '.join(unmatched)}. "
                f"Fetch the real values with a data tool first, then retry with the exact "
                f"numbers returned.")

    return None