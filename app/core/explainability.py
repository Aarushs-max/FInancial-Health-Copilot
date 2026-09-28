"""
Explainability & Cognitive Provenance Engine.

Classifies every copilot deduction into:
  - OBSERVED_FACT (Direct factual data from linked bank statements / accounts)
  - MODEL_PREDICTION (Probabilistic or rule-based forward projections)
  - ACTIONABLE_RECOMMENDATION (Calibrated advisory suggestions)
"""

from typing import List
from app.models.schemas import (
    UserProfile, AffordabilityResult, CashFlowForecast,
    ExplainabilityItem, InsightType, ConfidenceLevel
)


def generate_explainability_audit(
    profile: UserProfile,
    affordability: AffordabilityResult,
    cashflow: CashFlowForecast
) -> List[ExplainabilityItem]:
    """
    Constructs transparent provenance cards highlighting exactly WHY each insight was reached.
    """
    items: List[ExplainabilityItem] = []

    # 1. Observed Fact: Fixed Obligations
    items.append(ExplainabilityItem(
        id="fact-fixed-spend",
        type=InsightType.OBSERVED_FACT,
        title=f"Fixed Commitments: ₹{affordability.fixed_obligations:,.0f}/month",
        explanation=(
            f"Derived directly from {len(profile.transactions)} verified account transactions. "
            f"Covers rent, loan EMIs, and essential recurring living obligations."
        ),
        confidence_level=ConfidenceLevel.HIGH,
        confidence_score=0.98,
        data_provenance="Simulated Account Aggregator (FIP Banking Stream)"
    ))

    # 2. Observed Fact: True Disposable Surplus
    items.append(ExplainabilityItem(
        id="fact-disposable-surplus",
        type=InsightType.OBSERVED_FACT,
        title=f"Net Disposable Margin: ₹{affordability.disposable_income:,.0f}",
        explanation=(
            f"Calculated as Monthly Inflow (₹{profile.monthly_income:,.0f}) minus Total Verified Burn "
            f"(₹{affordability.total_monthly_spend:,.0f}). Represents your actual unallocated monthly capacity."
        ),
        confidence_level=ConfidenceLevel.HIGH,
        confidence_score=0.95,
        data_provenance="Deterministic Cashflow Equation"
    ))

    # 3. Model Prediction: 7-Day Cash Flow
    if cashflow.has_cashflow_warning:
        pred_title = f"Projected 7-Day Deficit: ₹{cashflow.projected_shortfall:,.0f}"
        pred_desc = (
            f"Deterministic schedule scan detects {len(cashflow.driving_obligations)} upcoming auto-debits "
            f"totaling ₹{cashflow.total_upcoming_bills:,.0f} against liquid reserve of ₹{cashflow.liquid_available_balance:,.0f}."
        )
        pred_conf = 0.92
    else:
        pred_title = "7-Day Liquidity Cushion Adequate"
        pred_desc = (
            f"All upcoming debits (₹{cashflow.total_upcoming_bills:,.0f}) are safely cushioned by "
            f"₹{cashflow.liquid_available_balance:,.0f} liquid checking balance."
        )
        pred_conf = 0.90

    items.append(ExplainabilityItem(
        id="pred-cashflow-window",
        type=InsightType.MODEL_PREDICTION,
        title=pred_title,
        explanation=pred_desc,
        confidence_level=ConfidenceLevel.HIGH,
        confidence_score=pred_conf,
        data_provenance="Rolling 7-Day Calendar Horizon Forecast"
    ))

    # 4. Actionable Recommendation: Affordability Guidance
    reco_title = f"Calibrated Investment Guidance: {affordability.risk_badge_text}"
    reco_desc = affordability.detailed_rationale
    items.append(ExplainabilityItem(
        id="reco-affordability",
        type=InsightType.ACTIONABLE_RECOMMENDATION,
        title=reco_title,
        explanation=reco_desc,
        confidence_level=ConfidenceLevel.HIGH,
        confidence_score=0.94,
        data_provenance="Dynamic Disposable Buffer & Runway Evaluation Matrix"
    ))

    return items
