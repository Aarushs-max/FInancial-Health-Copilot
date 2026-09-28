"""
Impact Projection Engine.

Projects future wealth accumulation over 1, 3, 5, and 10 years across:
  1. Balanced Equity SIP (~12.0% historical benchmark)
  2. Conservative Debt / Fixed Deposit (~6.5% benchmark)
  3. No-Growth Cash Baseline (0% cash mattress / savings baseline)
"""

from typing import List
from app.models.schemas import ImpactProjectionResult, ProjectionPoint


def calculate_sip_future_value(monthly_amt: float, annual_rate_pct: float, years: int) -> float:
    """
    Standard monthly SIP future value formula:
      FV = P * [((1 + r)^n - 1) / r] * (1 + r)
      where r = annual_rate / 12, n = years * 12
    """
    if annual_rate_pct <= 0:
        return monthly_amt * years * 12

    monthly_rate = (annual_rate_pct / 100.0) / 12.0
    months = years * 12
    fv = monthly_amt * (((1.0 + monthly_rate) ** months - 1.0) / monthly_rate) * (1.0 + monthly_rate)
    return round(fv, 2)


def generate_impact_projections(monthly_amount: float) -> ImpactProjectionResult:
    """
    Generates multi-scenario wealth impact data for a given monthly investment contribution.
    """
    sip_cagr = 12.0
    conservative_cagr = 6.5
    milestones = [1, 3, 5, 10]

    scenarios: List[ProjectionPoint] = []
    labels: List[str] = [f"Year {yr}" for yr in milestones]
    sip_series: List[float] = []
    conservative_series: List[float] = []
    cash_series: List[float] = []

    for yr in milestones:
        invested = round(monthly_amount * yr * 12, 2)
        sip_val = calculate_sip_future_value(monthly_amount, sip_cagr, yr)
        cons_val = calculate_sip_future_value(monthly_amount, conservative_cagr, yr)

        point = ProjectionPoint(
            year=yr,
            total_invested=invested,
            conservative_value=cons_val,
            balanced_sip_value=sip_val,
            cash_baseline_value=invested
        )
        scenarios.append(point)

        sip_series.append(sip_val)
        conservative_series.append(cons_val)
        cash_series.append(invested)

    disclaimer = (
        "Regulatory Notice: Projections are mathematical illustrations based on compounding assumptions "
        "(SIP @ 12.0% CAGR, Conservative @ 6.5% CAGR). Market investments are subject to risk; past performance "
        "does not guarantee future returns. Output is decision-support guidance, not SEBI-registered advice."
    )

    return ImpactProjectionResult(
        monthly_investment=monthly_amount,
        scenarios=scenarios,
        assumed_sip_cagr_pct=sip_cagr,
        assumed_conservative_cagr_pct=conservative_cagr,
        chart_labels=labels,
        sip_series=sip_series,
        conservative_series=conservative_series,
        cash_series=cash_series,
        regulatory_disclaimer=disclaimer
    )
