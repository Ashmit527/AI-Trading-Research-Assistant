def calculate_pe_ratio(price: float, eps: float) -> dict:
    """Price-to-Earnings ratio."""
    if eps is None or eps == 0:
        return {"error": "EPS is missing or zero, cannot compute P/E ratio"}

    pe_ratio = price / eps
    return {
        "calculation": "P/E ratio",
        "inputs": {"price": price, "eps": eps},
        "result": round(pe_ratio, 2)
    }


def calculate_yoy_growth(current_value: float, previous_value: float, metric_name: str = "value") -> dict:
    """Year-over-year growth percentage."""
    if previous_value is None or previous_value == 0:
        return {"error": f"Previous {metric_name} is missing or zero, cannot compute growth"}
    if current_value is None:
        return {"error": f"Current {metric_name} is missing"}

    growth_pct = ((current_value - previous_value) / previous_value) * 100
    return {
        "calculation": f"{metric_name} YoY growth",
        "inputs": {"current": current_value, "previous": previous_value},
        "result_percent": round(growth_pct, 2)
    }


def calculate_cagr(ending_value: float, beginning_value: float, num_years: float) -> dict:
    """Compound Annual Growth Rate over multiple years."""
    if beginning_value is None or beginning_value <= 0:
        return {"error": "Beginning value is missing or non-positive, cannot compute CAGR"}
    if ending_value is None:
        return {"error": "Ending value is missing"}
    if num_years is None or num_years <= 0:
        return {"error": "Number of years must be positive"}

    cagr = ((ending_value / beginning_value) ** (1 / num_years) - 1) * 100
    return {
        "calculation": "CAGR",
        "inputs": {"ending_value": ending_value, "beginning_value": beginning_value, "num_years": num_years},
        "result_percent": round(cagr, 2)
    }


def calculate_profit_margin(net_income: float, revenue: float) -> dict:
    """Net profit margin percentage."""
    if revenue is None or revenue == 0:
        return {"error": "Revenue is missing or zero, cannot compute profit margin"}
    if net_income is None:
        return {"error": "Net income is missing"}

    margin_pct = (net_income / revenue) * 100
    return {
        "calculation": "Net profit margin",
        "inputs": {"net_income": net_income, "revenue": revenue},
        "result_percent": round(margin_pct, 2)
    }


def calculate_ebitda_margin(ebitda: float, revenue: float) -> dict:
    """EBITDA margin percentage - core operating efficiency, independent of financing/depreciation choices."""
    if revenue is None or revenue == 0:
        return {"error": "Revenue is missing or zero, cannot compute EBITDA margin"}
    if ebitda is None:
        return {"error": "EBITDA is missing (common for banks/financial institutions, which don't report EBITDA in a standard way)"}

    margin_pct = (ebitda / revenue) * 100
    return {
        "calculation": "EBITDA margin",
        "inputs": {"ebitda": ebitda, "revenue": revenue},
        "result_percent": round(margin_pct, 2)
    }


def calculate_debt_to_equity(total_debt: float, total_equity: float) -> dict:
    """Debt-to-equity ratio."""
    if total_equity is None or total_equity == 0:
        return {"error": "Total equity is missing or zero, cannot compute debt-to-equity"}
    if total_debt is None:
        return {"error": "Total debt is missing"}

    ratio = total_debt / total_equity
    return {
        "calculation": "Debt-to-equity ratio",
        "inputs": {"total_debt": total_debt, "total_equity": total_equity},
        "result": round(ratio, 2)
    }


def calculate_roe(net_income: float, shareholders_equity: float) -> dict:
    """Return on Equity - how efficiently the company generates profit from shareholder capital."""
    if shareholders_equity is None or shareholders_equity == 0:
        return {"error": "Shareholders' equity is missing or zero, cannot compute ROE"}
    if net_income is None:
        return {"error": "Net income is missing"}

    roe_pct = (net_income / shareholders_equity) * 100
    return {
        "calculation": "Return on Equity (ROE)",
        "inputs": {"net_income": net_income, "shareholders_equity": shareholders_equity},
        "result_percent": round(roe_pct, 2)
    }


def calculate_roa(net_income: float, total_assets: float) -> dict:
    """Return on Assets - profit efficiency against ALL assets, including debt-funded ones."""
    if total_assets is None or total_assets == 0:
        return {"error": "Total assets is missing or zero, cannot compute ROA"}
    if net_income is None:
        return {"error": "Net income is missing"}

    roa_pct = (net_income / total_assets) * 100
    return {
        "calculation": "Return on Assets (ROA)",
        "inputs": {"net_income": net_income, "total_assets": total_assets},
        "result_percent": round(roa_pct, 2)
    }


def calculate_interest_coverage(ebit: float, interest_expense: float) -> dict:
    """Interest coverage ratio - can the company comfortably pay interest on its debt from operating profit?"""
    if interest_expense is None or interest_expense == 0:
        return {"error": "Interest expense is missing or zero, cannot compute interest coverage"}
    if ebit is None:
        return {"error": "EBIT is missing"}

    coverage = ebit / interest_expense
    return {
        "calculation": "Interest coverage ratio",
        "inputs": {"ebit": ebit, "interest_expense": interest_expense},
        "result": round(coverage, 2)
    }


def calculate_dividend_yield(annual_dividend_per_share: float, price: float) -> dict:
    """Dividend yield - return from dividends alone, at current price."""
    if price is None or price == 0:
        return {"error": "Price is missing or zero, cannot compute dividend yield"}
    if annual_dividend_per_share is None:
        return {"error": "Annual dividend per share is missing"}

    yield_pct = (annual_dividend_per_share / price) * 100
    return {
        "calculation": "Dividend yield",
        "inputs": {"annual_dividend_per_share": annual_dividend_per_share, "price": price},
        "result_percent": round(yield_pct, 2)
    }


if __name__ == "__main__":
    print("--- Original 4 ---")
    print(calculate_pe_ratio(price=420.05, eps=8.23))
    print(calculate_yoy_growth(current_value=833900000000, previous_value=577880000000, metric_name="revenue"))
    print(calculate_profit_margin(net_income=30300000000, revenue=833900000000))
    print(calculate_debt_to_equity(total_debt=56150000000, total_equity=200000000000))

    print("\n--- New additions ---")
    print(calculate_cagr(ending_value=833900000000, beginning_value=431212000000, num_years=2))
    print(calculate_ebitda_margin(ebitda=74820000000, revenue=833900000000))
    print(calculate_roe(net_income=30300000000, shareholders_equity=200000000000))
    print(calculate_roa(net_income=30300000000, total_assets=500000000000))
    print(calculate_interest_coverage(ebit=55370000000, interest_expense=8740000000))
    print(calculate_dividend_yield(annual_dividend_per_share=4.0, price=420.05))

    print("\n--- Error handling checks ---")
    print(calculate_pe_ratio(price=420.05, eps=None))
    print(calculate_ebitda_margin(ebitda=None, revenue=1000))