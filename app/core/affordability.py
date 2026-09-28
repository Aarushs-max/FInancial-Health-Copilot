"""
Core Affordability & Risk Logic Engine (FIN-02 Core Differentiator).

Unlike generic investment advice that prescribes raw income percentage rules
(e.g., "always invest 20% of income"), this engine determines affordability
based on TRUE DISPOSABLE INCOME after lifestyle spend and recurring obligations,
reinforced by emergency buffer run-rate checks.
"""

from typing import Tuple
from app.models.schemas import UserProfile, AffordabilityResult, RiskTier, ExpenseCategory


def calculate_expense_breakdown(profile: UserProfile) -> Tuple[float, float, float]:
    """
    Computes (fixed_obligations, lifestyle_discretionary, total_monthly_spend).
    Separates hard recurring debt/rent from flexible lifestyle spend.
    """
    fixed_spend = 0.0
    lifestyle_spend = 0.0

    for tx in profile.transactions:
        amt = abs(tx.amount)
        if tx.category in (ExpenseCategory.FIXED_OBLIGATION, ExpenseCategory.UTILITY):
            fixed_spend += amt
        elif tx.category == ExpenseCategory.DISCRETIONARY:
            lifestyle_spend += amt
        elif tx.category == ExpenseCategory.ESSENTIAL_LIVING:
            # Baseline groceries/essentials are treated as essential obligations
            fixed_spend += amt

    total_spend = fixed_spend + lifestyle_spend
    return fixed_spend, lifestyle_spend, total_spend


def evaluate_affordability(profile: UserProfile, tested_amount: float) -> AffordabilityResult:
    """
    Evaluates whether an investment amount is truly affordable for this individual.

    Key Math:
      Disposable Income = Monthly Income - (Fixed Obligations + Lifestyle Spend)
      Remaining Buffer  = Disposable Income - Tested Amount
      Buffer Drain %    = (Tested Amount / Disposable Income) * 100
      Emergency Buffer  = Liquid Savings / Monthly Essential Living Burn
    """
    fixed_spend, lifestyle_spend, total_spend = calculate_expense_breakdown(profile)
    disposable_income = max(0.0, profile.monthly_income - total_spend)
    
    # Calculate emergency fund coverage (months)
    # Essential monthly burn includes fixed commitments + baseline living
    essential_burn = max(1000.0, fixed_spend)
    emergency_months = round(profile.liquid_savings / essential_burn, 1)

    tested_amount = max(0.0, tested_amount)
    remaining_buffer = disposable_income - tested_amount

    # Recommended safe ceiling: capped at 40% of disposable income, or 0 if emergency fund is critical
    if emergency_months < 1.0 or disposable_income <= 0:
        safe_ceiling = 0.0
    else:
        # Scale ceiling based on emergency fund adequacy
        cushion_factor = 0.40 if emergency_months >= 3.0 else 0.20
        safe_ceiling = round(disposable_income * cushion_factor, -2)

    # Determine risk tier based on disposable margin and emergency runway
    if disposable_income <= 0 or remaining_buffer < 0:
        risk_status = RiskTier.CRITICAL
        badge_text = "Highly Risky / Unaffordable"
        headline = f"Exceeds Available Disposable Income by ₹{abs(remaining_buffer):,.0f}"
        rationale = (
            f"Your current monthly burn (₹{total_spend:,.0f}) absorbs virtually all of your ₹{profile.monthly_income:,.0f} income. "
            f"Committing ₹{tested_amount:,.0f} would force you to either default on commitments or draw down emergency savings."
        )
        drain_pct = 100.0 if disposable_income == 0 else round((tested_amount / disposable_income) * 100, 1)

    elif emergency_months < 1.5 and tested_amount > (disposable_income * 0.25):
        risk_status = RiskTier.RISKY
        badge_text = "Risky (Fragile Safety Net)"
        drain_pct = round((tested_amount / disposable_income) * 100, 1)
        headline = f"Emergency cushion dangerously low ({emergency_months} mos)"
        rationale = (
            f"While you mathematically have ₹{disposable_income:,.0f} in monthly disposable buffer, your emergency savings "
            f"(₹{profile.liquid_savings:,.0f}) covers only {emergency_months} months of essential expenses. "
            f"We advise channeling surplus cash into a liquid emergency fund until reaching at least 3 months coverage."
        )

    elif remaining_buffer < 4000 or (disposable_income > 0 and (tested_amount / disposable_income) > 0.70):
        risk_status = RiskTier.RISKY
        badge_text = "Risky (Thin Safety Margin)"
        drain_pct = round((tested_amount / disposable_income) * 100, 1)
        headline = f"Consumes {drain_pct:.0f}% of Disposable Buffer"
        rationale = (
            f"Investing ₹{tested_amount:,.0f} leaves only ₹{remaining_buffer:,.0f} as your monthly unexpected buffer. "
            f"A single unplanned expense (medical, car repair, gadget replacement) would trigger cash-flow distress."
        )

    elif (disposable_income > 0 and (tested_amount / disposable_income) > 0.40):
        risk_status = RiskTier.MODERATE
        badge_text = "Moderate (Acceptable Buffer)"
        drain_pct = round((tested_amount / disposable_income) * 100, 1)
        headline = f"Leaves ₹{remaining_buffer:,.0f} Discretionary Margin"
        rationale = (
            f"Investing ₹{tested_amount:,.0f} consumes {drain_pct:.0f}% of your disposable income, leaving ₹{remaining_buffer:,.0f}. "
            f"This is affordable provided discretionary dining and shopping stay within current patterns."
        )

    else:
        risk_status = RiskTier.SAFE
        badge_text = "Safe & Highly Affordable"
        drain_pct = round((tested_amount / disposable_income) * 100, 1) if disposable_income > 0 else 0.0
        headline = f"Comfortable Buffer of ₹{remaining_buffer:,.0f} Preserved"
        rationale = (
            f"This investment fits securely within your disposable surplus. You preserve ₹{remaining_buffer:,.0f} in free cash flow "
            f"and hold {emergency_months} months of liquid emergency reserves."
        )

    return AffordabilityResult(
        monthly_income=profile.monthly_income,
        fixed_obligations=fixed_spend,
        lifestyle_expenses=lifestyle_spend,
        total_monthly_spend=total_spend,
        disposable_income=disposable_income,
        disposable_income_ratio=round(disposable_income / max(1.0, profile.monthly_income), 3),
        liquid_savings=profile.liquid_savings,
        emergency_fund_months=emergency_months,
        tested_investment_amount=tested_amount,
        remaining_disposable_buffer=remaining_buffer,
        buffer_drain_pct=drain_pct,
        risk_status=risk_status,
        risk_badge_text=badge_text,
        headline_verdict=headline,
        detailed_rationale=rationale,
        safe_recommended_investment_ceiling=safe_ceiling,
    )
