"""
Copilot Conversational & Voice Narrator Engine.

Generates concise, human-sounding financial summaries and voice-ready scripts
for the Web Speech API demo.
"""

from app.models.schemas import UserProfile, AffordabilityResult, CashFlowForecast


def synthesize_copilot_narrative(
    profile: UserProfile,
    affordability: AffordabilityResult,
    cashflow: CashFlowForecast
) -> dict:
    """
    Synthesizes conversational text and a concise voice pitch.
    """
    # 1. Headline summary
    if cashflow.has_cashflow_warning:
        headline = f"⚠️ Heads up {profile.name.split()[0]}! You have an upcoming cash flow shortfall of ₹{cashflow.projected_shortfall:,.0f}."
        voice_script = (
            f"Attention {profile.name.split()[0]}. You have bills of rupees {int(cashflow.total_upcoming_bills):,} "
            f"due in the next 7 days, but only rupees {int(cashflow.liquid_available_balance):,} in your account. "
            f"You have a projected shortfall of rupees {int(cashflow.projected_shortfall):,}. "
            f"I advise transferring funds or pausing discretionary spending before bills bounce."
        )
    else:
        if affordability.risk_status == "SAFE":
            headline = f"✅ Looking solid, {profile.name.split()[0]}! Investing ₹{affordability.tested_investment_amount:,.0f} is safe."
            voice_script = (
                f"Hello {profile.name.split()[0]}. Investing rupees {int(affordability.tested_investment_amount):,} monthly "
                f"is fully affordable. You retain rupees {int(affordability.remaining_disposable_buffer):,} as a monthly buffer, "
                f"backed by {affordability.emergency_fund_months} months of emergency reserves."
            )
        elif affordability.risk_status == "MODERATE":
            headline = f"⚖️ Caution, {profile.name.split()[0]}. This investment consumes {affordability.buffer_drain_pct:.0f}% of your buffer."
            voice_script = (
                f"Rupees {int(affordability.tested_investment_amount):,} is moderately affordable. It leaves "
                f"rupees {int(affordability.remaining_disposable_buffer):,} in monthly margin. Keep discretionary spends in check."
            )
        else:
            headline = f"🛑 Warning, {profile.name.split()[0]}. Committing ₹{affordability.tested_investment_amount:,.0f} is high risk."
            voice_script = (
                f"Caution {profile.name.split()[0]}. Committing rupees {int(affordability.tested_investment_amount):,} "
                f"is flagged risky. It cuts too deeply into your disposable income. "
                f"I recommend a safer ceiling of rupees {int(affordability.safe_recommended_investment_ceiling):,}."
            )

    copilot_takeaway = (
        f"{affordability.headline_verdict}. Your disposable income is ₹{affordability.disposable_income:,.0f}/month "
        f"after accounting for ₹{affordability.fixed_obligations:,.0f} in fixed commitments and ₹{affordability.lifestyle_expenses:,.0f} "
        f"in lifestyle spend. Emergency runway stands at {affordability.emergency_fund_months} months."
    )

    return {
        "headline": headline,
        "copilot_takeaway": copilot_takeaway,
        "voice_script": voice_script,
        "safe_ceiling": affordability.safe_recommended_investment_ceiling
    }
