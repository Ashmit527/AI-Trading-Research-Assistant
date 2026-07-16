from live_data import get_financial_metrics
from calculator import calculate_yoy_growth

fy26 = get_financial_metrics("tatamotors_ar25", fiscal_year="2026-03-31 00:00:00")
fy25 = get_financial_metrics("tatamotors_ar25", fiscal_year="2025-03-31 00:00:00")

result = calculate_yoy_growth(
    current_value=fy26["total_revenue"],
    previous_value=fy25["total_revenue"],
    metric_name="Tata Motors revenue"
)
print(result)