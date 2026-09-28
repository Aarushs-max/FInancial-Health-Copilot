"""
Forward-Looking Cash-Flow Warning Engine.

Proactively monitors the next 5-7 days of scheduled debits (Rent, Loan EMIs,
utility bills, credit card payment dates) against current available liquid balance.
Surfaces exact shortfall amounts and root driving obligations.
"""

from typing import List
from datetime import datetime, timedelta
from app.models.schemas import UserProfile, CashFlowForecast, UpcomingObligation, ExpenseCategory


def analyze_7day_cashflow(profile: UserProfile, reference_day: int = 28) -> CashFlowForecast:
    """
    Evaluates upcoming obligations over a 7-day rolling window starting from reference_day.
    Defaults to day 28 (common end-of-month crunch point in Indian salary cycles).
    """
    window_days = 7
    upcoming: List[UpcomingObligation] = []
    total_due = 0.0

    # Scan transactions with due_day_of_month
    for tx in profile.transactions:
        if not tx.is_recurring or tx.due_day_of_month is None:
            continue

        due_day = tx.due_day_of_month
        # Calculate days until due wrapping across month boundary (assuming 30-day month)
        if due_day >= reference_day:
            days_away = due_day - reference_day
        else:
            days_away = (30 - reference_day) + due_day

        if 0 <= days_away <= window_days:
            upcoming.append(UpcomingObligation(
                description=tx.description,
                amount=abs(tx.amount),
                due_date_formatted=f"Due in {days_away} day{'s' if days_away != 1 else ''} (Day {due_day})",
                days_until_due=days_away,
                category=tx.category.value
            ))
            total_due += abs(tx.amount)

    # Sort obligations by urgency (days until due)
    upcoming.sort(key=lambda x: x.days_until_due)

    balance = profile.liquid_savings
    shortfall = max(0.0, total_due - balance)
    closing_balance = balance - total_due

    has_warning = shortfall > 0.0

    if has_warning:
        driver_names = ", ".join([f"{u.description} (₹{u.amount:,.0f})" for u in upcoming[:2]])
        warning_title = f"Impending Liquidity Deficit: Shortfall of ₹{shortfall:,.0f}"
        warning_msg = (
            f"You have ₹{total_due:,.0f} in recurring obligations due within the next {window_days} days, "
            f"but your available liquid balance is only ₹{balance:,.0f}. "
            f"Primary drivers: {driver_names}."
        )
        reco = (
            f"Action Required: Transfer at least ₹{shortfall:,.0f} into your primary checking account immediately "
            f"or defer discretionary expenses to avoid auto-debit bounce fees and credit score penalties."
        )
    else:
        warning_title = "Cash Flow Stable for Upcoming 7 Days"
        warning_msg = (
            f"Upcoming commitments totaling ₹{total_due:,.0f} are fully covered by your "
            f"current liquid balance of ₹{balance:,.0f}. Net surplus after scheduled debits: ₹{closing_balance:,.0f}."
        )
        reco = "All upcoming automated debits are well-funded. No immediate liquidity action required."

    return CashFlowForecast(
        has_cashflow_warning=has_warning,
        evaluation_window_days=window_days,
        liquid_available_balance=balance,
        total_upcoming_bills=total_due,
        projected_shortfall=shortfall,
        projected_closing_balance=closing_balance,
        driving_obligations=upcoming,
        warning_title=warning_title,
        warning_message=warning_msg,
        recommended_action=reco
    )
